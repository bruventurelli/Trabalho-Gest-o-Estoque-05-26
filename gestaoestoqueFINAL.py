import sqlite3
import csv
import logging
from datetime import datetime
from contextlib import contextmanager

DB_NAME = "estoque.db"
PAGE_SIZE = 20

logging.basicConfig(
    filename="estoque.log",
    level=logging.ERROR,
    format="%(asctime)s %(levelname)s - %(message)s",
)


@contextmanager
def get_conn():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    try:
        yield conn
        conn.commit()
    except Exception as exc:
        conn.rollback()
        logging.error("Erro na transação: %s", exc, exc_info=True)
        raise
    finally:
        conn.close()


def inicializar_banco():
    with get_conn() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS produtos (
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                nome       TEXT    NOT NULL,
                categoria  TEXT    NOT NULL,
                preco      REAL    NOT NULL CHECK (preco >= 0),
                quantidade INTEGER NOT NULL DEFAULT 0 CHECK (quantidade >= 0),
                UNIQUE (nome, categoria)
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS movimentacoes (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                produto_id  INTEGER NOT NULL,
                tipo        TEXT    NOT NULL CHECK (tipo IN ('ENTRADA','SAIDA')),
                quantidade  INTEGER NOT NULL CHECK (quantidade > 0),
                data_hora   TEXT    NOT NULL,
                FOREIGN KEY (produto_id) REFERENCES produtos(id)
            )
        """)
        conn.execute("CREATE INDEX IF NOT EXISTS idx_produtos_nome ON produtos (nome COLLATE NOCASE)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_produtos_categoria ON produtos (categoria COLLATE NOCASE)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_mov_produto ON movimentacoes (produto_id)")


def cadastrar_produto(nome, categoria, preco, quantidade):
    if not nome.strip():
        print("  Nome não pode ser vazio.")
        return None
    if not categoria.strip():
        print("  Categoria não pode ser vazia.")
        return None
    if preco < 0:
        print("  Preço inválido.")
        return None
    if quantidade < 0:
        print("  Quantidade inválida.")
        return None

    try:
        with get_conn() as conn:
            cur = conn.execute(
                "INSERT INTO produtos (nome, categoria, preco, quantidade) VALUES (?, ?, ?, ?)",
                (nome.strip(), categoria.strip(), round(preco, 2), int(quantidade))
            )
            produto_id = cur.lastrowid

            if quantidade > 0:
                conn.execute(
                    "INSERT INTO movimentacoes (produto_id, tipo, quantidade, data_hora) VALUES (?, 'ENTRADA', ?, ?)",
                    (produto_id, int(quantidade), datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                )

        print(f"  Produto '{nome}' cadastrado. (ID: {produto_id})")
        return produto_id

    except sqlite3.IntegrityError:
        print(f"  Produto '{nome}' já existe nessa categoria.")
        return None


def registrar_entrada(produto_id, quantidade):
    if quantidade <= 0:
        print("  Quantidade precisa ser maior que zero.")
        return

    try:
        with get_conn() as conn:
            produto = conn.execute("SELECT * FROM produtos WHERE id = ?", (produto_id,)).fetchone()

            if produto is None:
                print(f"  Produto ID {produto_id} não encontrado.")
                return

            novo_saldo = produto["quantidade"] + quantidade
            conn.execute("UPDATE produtos SET quantidade = ? WHERE id = ?", (novo_saldo, produto_id))
            conn.execute(
                "INSERT INTO movimentacoes (produto_id, tipo, quantidade, data_hora) VALUES (?, 'ENTRADA', ?, ?)",
                (produto_id, quantidade, datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            )

        print(f"  +{quantidade} unidade(s) de '{produto['nome']}'. Saldo atual: {novo_saldo}.")

    except Exception as exc:
        logging.error("registrar_entrada(%s, %s): %s", produto_id, quantidade, exc)
        print("  Algo deu errado. Verifique o log.")


def registrar_saida(produto_id, quantidade):
    if quantidade <= 0:
        print("  Quantidade precisa ser maior que zero.")
        return

    try:
        with get_conn() as conn:
            produto = conn.execute("SELECT * FROM produtos WHERE id = ?", (produto_id,)).fetchone()

            if produto is None:
                print(f"  Produto ID {produto_id} não encontrado.")
                return

            if quantidade > produto["quantidade"]:
                print(f"  Estoque insuficiente. Disponível: {produto['quantidade']}.")
                return

            novo_saldo = produto["quantidade"] - quantidade
            conn.execute("UPDATE produtos SET quantidade = ? WHERE id = ?", (novo_saldo, produto_id))
            conn.execute(
                "INSERT INTO movimentacoes (produto_id, tipo, quantidade, data_hora) VALUES (?, 'SAIDA', ?, ?)",
                (produto_id, quantidade, datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            )

        print(f"  -{quantidade} unidade(s) de '{produto['nome']}'. Saldo atual: {novo_saldo}.")

    except Exception as exc:
        logging.error("registrar_saida(%s, %s): %s", produto_id, quantidade, exc)
        print("  Algo deu errado. Verifique o log.")


def consultar_estoque(produto_id):
    with get_conn() as conn:
        p = conn.execute("SELECT * FROM produtos WHERE id = ?", (produto_id,)).fetchone()

    if p is None:
        print(f"  Produto ID {produto_id} não encontrado.")
        return None

    print(f"""
  ID        : {p['id']}
  Nome      : {p['nome']}
  Categoria : {p['categoria']}
  Preco     : R$ {p['preco']:.2f}
  Qtd       : {p['quantidade']}
  Em estoque: R$ {p['preco'] * p['quantidade']:.2f}""")

    return dict(p)


def alertar_estoque_baixo(limite):
    if limite < 0:
        print("  Limite inválido.")
        return

    with get_conn() as conn:
        criticos = conn.execute(
            "SELECT * FROM produtos WHERE quantidade < ? ORDER BY quantidade ASC", (limite,)
        ).fetchall()

    if not criticos:
        print(f"  Nenhum produto abaixo de {limite} unidade(s).")
        return

    print(f"\n  Produtos com menos de {limite} unidade(s):")
    print(f"  {'ID':<6} {'Nome':<22} {'Categoria':<14} {'Qtd':>5}")
    print("  " + "-" * 50)
    for p in criticos:
        print(f"  {p['id']:<6} {p['nome']:<22} {p['categoria']:<14} {p['quantidade']:>5}")
    print(f"  Total: {len(criticos)} produto(s)")


def buscar_produto(termo):
    with get_conn() as conn:
        resultados = conn.execute(
            "SELECT * FROM produtos WHERE nome LIKE ? ORDER BY nome COLLATE NOCASE",
            (f"%{termo}%",)
        ).fetchall()

    if not resultados:
        print(f"  Nenhum resultado para '{termo}'.")
        return []

    print(f"  {'ID':<6} {'Nome':<22} {'Categoria':<14} {'Preco':>10} {'Qtd':>6}")
    print("  " + "-" * 60)
    for p in resultados:
        print(f"  {p['id']:<6} {p['nome']:<22} {p['categoria']:<14} R$ {p['preco']:>7.2f} {p['quantidade']:>6}")

    return [dict(p) for p in resultados]


def filtrar_por_categoria(categoria):
    with get_conn() as conn:
        produtos = conn.execute(
            "SELECT * FROM produtos WHERE categoria LIKE ? ORDER BY nome COLLATE NOCASE",
            (f"%{categoria}%",)
        ).fetchall()

    if not produtos:
        print(f"  Nenhum produto na categoria '{categoria}'.")
        return

    total = 0.0
    print(f"  {'ID':<6} {'Nome':<24} {'Preco':>10} {'Qtd':>6} {'Valor':>12}")
    print("  " + "-" * 60)
    for p in produtos:
        valor = p['preco'] * p['quantidade']
        total += valor
        print(f"  {p['id']:<6} {p['nome']:<24} R$ {p['preco']:>7.2f} {p['quantidade']:>6} R$ {valor:>9.2f}")
    print(f"  {len(produtos)} produto(s) | Total: R$ {total:.2f}")


def editar_produto(produto_id):
    with get_conn() as conn:
        p = conn.execute("SELECT * FROM produtos WHERE id = ?", (produto_id,)).fetchone()

    if p is None:
        print(f"  Produto ID {produto_id} não encontrado.")
        return

    print(f"  Editando '{p['nome']}' — deixe em branco para manter o valor atual")

    novo_nome = input(f"  Nome [{p['nome']}]: ").strip() or p['nome']
    nova_categoria = input(f"  Categoria [{p['categoria']}]: ").strip() or p['categoria']

    while True:
        entrada = input(f"  Preco [R$ {p['preco']:.2f}]: ").strip()
        if not entrada:
            novo_preco = p['preco']
            break
        try:
            novo_preco = float(entrada)
            if novo_preco < 0:
                print("  Preco não pode ser negativo.")
                continue
            break
        except ValueError:
            print("  Valor inválido.")

    try:
        with get_conn() as conn:
            conn.execute(
                "UPDATE produtos SET nome = ?, categoria = ?, preco = ? WHERE id = ?",
                (novo_nome, nova_categoria, round(novo_preco, 2), produto_id)
            )
        print("  Produto atualizado.")
    except sqlite3.IntegrityError:
        print(f"  Já existe '{novo_nome}' na categoria '{nova_categoria}'.")


def remover_produto(produto_id):
    with get_conn() as conn:
        p = conn.execute("SELECT * FROM produtos WHERE id = ?", (produto_id,)).fetchone()

    if p is None:
        print(f"  Produto ID {produto_id} não encontrado.")
        return

    print(f"  {p['nome']} | Qtd: {p['quantidade']} | R$ {p['preco']:.2f}")
    confirmacao = input("  Digite o nome do produto para confirmar exclusão: ").strip()

    if confirmacao != p['nome']:
        print("  Nome incorreto. Operação cancelada.")
        return

    with get_conn() as conn:
        conn.execute("DELETE FROM produtos WHERE id = ?", (produto_id,))
    print(f"  '{p['nome']}' removido.")


def relatorio_financeiro():
    with get_conn() as conn:
        linhas = conn.execute(
            "SELECT nome, preco, quantidade, (preco * quantidade) AS subtotal FROM produtos ORDER BY subtotal DESC"
        ).fetchall()
        total = conn.execute(
            "SELECT COALESCE(SUM(preco * quantidade), 0) AS total FROM produtos"
        ).fetchone()["total"]

    if not linhas:
        print("  Nenhum produto cadastrado.")
        return

    print(f"  {'Produto':<24} {'Preco':>10} {'Qtd':>6} {'Subtotal':>14}")
    print("  " + "-" * 58)
    for l in linhas:
        print(f"  {l['nome']:<24} R$ {l['preco']:>7.2f} {l['quantidade']:>6} R$ {l['subtotal']:>11.2f}")
    print("  " + "-" * 58)
    print(f"  Total em estoque: R$ {total:.2f}")


def exportar_csv(arquivo="relatorio_estoque.csv"):
    with get_conn() as conn:
        produtos = conn.execute(
            "SELECT id, nome, categoria, preco, quantidade, (preco * quantidade) AS valor_total FROM produtos ORDER BY id"
        ).fetchall()

    if not produtos:
        print("  Nenhum produto para exportar.")
        return

    with open(arquivo, mode="w", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f, delimiter=";")
        writer.writerow(["ID", "Nome", "Categoria", "Preco", "Quantidade", "Valor Total"])
        for p in produtos:
            writer.writerow([
                p["id"], p["nome"], p["categoria"],
                f"{p['preco']:.2f}".replace(".", ","),
                p["quantidade"],
                f"{p['valor_total']:.2f}".replace(".", ",")
            ])

    print(f"  Exportado para '{arquivo}' ({len(produtos)} produto(s)).")


def ver_historico(produto_id=None, limite=30):
    with get_conn() as conn:
        if produto_id:
            movs = conn.execute("""
                SELECT m.data_hora, m.tipo, m.quantidade, p.nome AS produto
                FROM movimentacoes m
                LEFT JOIN produtos p ON p.id = m.produto_id
                WHERE m.produto_id = ?
                ORDER BY m.id DESC LIMIT ?
            """, (produto_id, limite)).fetchall()
        else:
            movs = conn.execute("""
                SELECT m.data_hora, m.tipo, m.quantidade, p.nome AS produto
                FROM movimentacoes m
                LEFT JOIN produtos p ON p.id = m.produto_id
                ORDER BY m.id DESC LIMIT ?
            """, (limite,)).fetchall()

    if not movs:
        print("  Nenhuma movimentação encontrada.")
        return

    print(f"  {'Data/Hora':<20} {'Tipo':<8} {'Qtd':>5}  Produto")
    print("  " + "-" * 65)
    for m in movs:
        nome = m["produto"] or "(removido)"
        sinal = "+" if m["tipo"] == "ENTRADA" else "-"
        print(f"  {m['data_hora']:<20} {m['tipo']:<8} {sinal}{m['quantidade']:>4}  {nome}")


def listar_todos(pagina=1):
    with get_conn() as conn:
        total = conn.execute("SELECT COUNT(*) AS c FROM produtos").fetchone()["c"]

        if total == 0:
            print("  Nenhum produto cadastrado.")
            return

        total_paginas = max(1, -(-total // PAGE_SIZE))
        pagina = max(1, min(pagina, total_paginas))
        offset = (pagina - 1) * PAGE_SIZE

        produtos = conn.execute(
            "SELECT * FROM produtos ORDER BY id LIMIT ? OFFSET ?",
            (PAGE_SIZE, offset)
        ).fetchall()

    print(f"\n  Pagina {pagina}/{total_paginas} ({total} produto(s))")
    print(f"  {'ID':<6} {'Nome':<22} {'Categoria':<14} {'Preco':>10} {'Qtd':>6}")
    print("  " + "-" * 63)
    for p in produtos:
        print(f"  {p['id']:<6} {p['nome']:<22} {p['categoria']:<14} R$ {p['preco']:>7.2f} {p['quantidade']:>6}")

    if total_paginas > 1:
        print("  [P] Proxima  [A] Anterior  [I] Ir para pagina")
        nav = input("  > ").strip().upper()
        if nav == "P" and pagina < total_paginas:
            listar_todos(pagina + 1)
        elif nav == "A" and pagina > 1:
            listar_todos(pagina - 1)
        elif nav == "I":
            try:
                listar_todos(int(input("  Pagina: ")))
            except ValueError:
                pass


def ler_inteiro(mensagem, minimo=None, maximo=None):
    while True:
        try:
            valor = int(input(mensagem))
            if minimo is not None and valor < minimo:
                print(f"  Minimo permitido: {minimo}")
                continue
            if maximo is not None and valor > maximo:
                print(f"  Maximo permitido: {maximo}")
                continue
            return valor
        except ValueError:
            print("  Digite um numero inteiro.")


def ler_float(mensagem, minimo=None):
    while True:
        try:
            valor = float(input(mensagem))
            if minimo is not None and valor < minimo:
                print(f"  Minimo permitido: {minimo}")
                continue
            return valor
        except ValueError:
            print("  Valor invalido.")


def menu_principal():
    print("""
  +-----------------------------------------+
  |  SISTEMA DE ESTOQUE                     |
  +-----------------------------------------+
  |  1 - Cadastrar produto                  |
  |  2 - Editar produto                     |
  |  3 - Remover produto                    |
  |  4 - Buscar por nome                    |
  |  5 - Filtrar por categoria              |
  |  6 - Listar todos                       |
  |  7 - Consultar produto                  |
  +-----------------------------------------+
  |  8 - Registrar entrada                  |
  |  9 - Registrar saida                    |
  | 10 - Alerta estoque baixo               |
  +-----------------------------------------+
  | 11 - Relatorio financeiro               |
  | 12 - Exportar CSV                       |
  | 13 - Historico de movimentacoes         |
  +-----------------------------------------+
  |  0 - Sair                               |
  +-----------------------------------------+""")
    return input("  Opcao: ").strip()


def carregar_dados_exemplo_se_vazio():
    with get_conn() as conn:
        total = conn.execute("SELECT COUNT(*) AS c FROM produtos").fetchone()["c"]
    if total == 0:
        cadastrar_produto("Arroz 5 kg",        "Alimentos", 12.90, 50)
        cadastrar_produto("Feijao 1 kg",        "Alimentos",  8.50, 30)
        cadastrar_produto("Oleo de Soja 1 L",   "Alimentos",  9.00,  4)
        cadastrar_produto("Detergente 500 ml",  "Limpeza",    3.75, 80)
        cadastrar_produto("Agua Sanitaria",     "Limpeza",    4.20,  2)


def main():
    print("Sistema de Gestao de Estoque v2.0")
    inicializar_banco()
    carregar_dados_exemplo_se_vazio()

    while True:
        opcao = menu_principal()

        if opcao == "1":
            nome       = input("  Nome: ")
            categoria  = input("  Categoria: ")
            preco      = ler_float("  Preco R$: ", minimo=0)
            quantidade = ler_inteiro("  Quantidade: ", minimo=0)
            cadastrar_produto(nome, categoria, preco, quantidade)

        elif opcao == "2":
            pid = ler_inteiro("  ID: ", minimo=1)
            editar_produto(pid)

        elif opcao == "3":
            pid = ler_inteiro("  ID: ", minimo=1)
            remover_produto(pid)

        elif opcao == "4":
            termo = input("  Buscar: ").strip()
            if termo:
                buscar_produto(termo)

        elif opcao == "5":
            cat = input("  Categoria: ").strip()
            if cat:
                filtrar_por_categoria(cat)

        elif opcao == "6":
            listar_todos()

        elif opcao == "7":
            pid = ler_inteiro("  ID: ", minimo=1)
            consultar_estoque(pid)

        elif opcao == "8":
            listar_todos()
            pid = ler_inteiro("  ID: ", minimo=1)
            qtd = ler_inteiro("  Quantidade: ", minimo=1)
            registrar_entrada(pid, qtd)

        elif opcao == "9":
            listar_todos()
            pid = ler_inteiro("  ID: ", minimo=1)
            qtd = ler_inteiro("  Quantidade: ", minimo=1)
            registrar_saida(pid, qtd)

        elif opcao == "10":
            limite = ler_inteiro("  Limite minimo: ", minimo=0)
            alertar_estoque_baixo(limite)

        elif opcao == "11":
            relatorio_financeiro()

        elif opcao == "12":
            exportar_csv()

        elif opcao == "13":
            filtrar = input("  ID do produto (ENTER para todos): ").strip()
            lim = 30
            if input("  Alterar limite de linhas? (s/N): ").strip().lower() == "s":
                lim = ler_inteiro("  Quantas linhas: ", minimo=1)
            ver_historico(
                produto_id=int(filtrar) if filtrar.isdigit() else None,
                limite=lim
            )

        elif opcao == "0":
            print("  Encerrando...")
            break

        else:
            print("  Opcao invalida.")

        input("\n  Enter para continuar...")


if __name__ == "__main__":
    main()
