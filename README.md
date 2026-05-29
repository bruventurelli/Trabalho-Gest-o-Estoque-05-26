# Sistema de Gestão de Estoque

Sistema de controle de estoque desenvolvido em **Python**, com persistência em banco de dados **SQLite**, histórico de movimentações, relatórios financeiros e exportação para CSV.

Projeto acadêmico evoluído de uma versão em programação estruturada (dicionário em memória) para uma versão profissional com banco de dados relacional e funcionalidades diferenciais.

---

## Funcionalidades

### Funcionalidades principais
- Cadastro de produtos (nome, quantidade inicial, preço unitário, estoque mínimo)
- Registro de entradas no estoque
- Registro de saídas com validação de saldo
- Consulta do estoque atual em formato de tabela
- Alerta de estoque baixo (produtos abaixo do mínimo definido)

### Diferenciais implementados (versão 2.0)
- **Persistência em SQLite** — os dados não se perdem ao fechar o programa
- **Histórico de movimentações** — toda entrada/saída é registrada com data/hora
- **Relatório financeiro** — valor total imobilizado no estoque
- **Exportação para CSV** — compatível com Excel (separador `;`, encoding `utf-8-sig`)
- **Queries parametrizadas** — proteção contra SQL Injection
- **Constraints no banco** — `CHECK` para quantidades/preços não negativos e `FOREIGN KEY` para integridade referencial

---

## Estrutura do banco de dados

O arquivo `estoque.db` é criado automaticamente na primeira execução, com duas tabelas:

### `produtos`
| Campo           | Tipo    | Descrição                          |
|-----------------|---------|------------------------------------|
| id              | INTEGER | Chave primária (AUTOINCREMENT)     |
| nome            | TEXT    | Nome do produto (único)            |
| quantidade      | INTEGER | Quantidade atual em estoque (>= 0) |
| preco           | REAL    | Preço unitário (>= 0)              |
| estoque_minimo  | INTEGER | Quantidade mínima de alerta (>= 0) |

### `movimentacoes`
| Campo       | Tipo    | Descrição                                  |
|-------------|---------|--------------------------------------------|
| id          | INTEGER | Chave primária (AUTOINCREMENT)             |
| produto_id  | INTEGER | FK -> `produtos.id`                        |
| tipo        | TEXT    | `'ENTRADA'` ou `'SAIDA'`                   |
| quantidade  | INTEGER | Quantidade movimentada                     |
| data_hora   | TEXT    | Data/hora da movimentação (ISO 8601)       |

---

## Tecnologias utilizadas

- **Python 3.8+**
- **sqlite3** (biblioteca nativa — sem dependências externas)
- **csv** (biblioteca nativa)
- **datetime** (biblioteca nativa)

> Nenhuma dependência externa é necessária. Basta ter Python instalado.

---

## Como executar

```bash
# Clone o repositório
git clone https://github.com/seu-usuario/sistema-estoque.git
cd sistema-estoque

# Execute o sistema
python sistema_estoque.py
```

Na primeira execução, o banco `estoque.db` é criado automaticamente e alguns produtos de exemplo são carregados.

---

## Menu do sistema

```
=================================================================
              SISTEMA DE GESTÃO DE ESTOQUE
=================================================================
  1. Cadastrar produto
  2. Registrar entrada
  3. Registrar saída
  4. Consultar estoque
  5. Alertar estoque baixo
  6. Relatório financeiro
  7. Exportar CSV
  8. Histórico de movimentações
  0. Sair
=================================================================
```

---

## Arquivos gerados

| Arquivo                  | Descrição                                          |
|--------------------------|----------------------------------------------------|
| `estoque.db`             | Banco de dados SQLite (criado automaticamente)     |
| `relatorio_estoque.csv`  | Relatório exportável para Excel/Google Sheets      |

---

## O que mudou da versão 1.0 para a 2.0

| Aspecto              | Versão 1.0 (estruturada)        | Versão 2.0 (com SQLite)              |
|----------------------|----------------------------------|--------------------------------------|
| Persistência         | Dicionário em memória (`{}`)     | Banco SQLite (`estoque.db`)          |
| Dados após fechar    | Perdidos                         | Mantidos                             |
| Histórico            | Não existe                       | Tabela `movimentacoes`               |
| Relatório financeiro | Não existe                       | Implementado                         |
| Exportação           | Não existe                       | CSV compatível com Excel             |
| Segurança            | —                                | Queries parametrizadas (`?`)         |
| Integridade          | —                                | `CHECK` + `FOREIGN KEY`              |

---

## Projeto acadêmico

Desenvolvido como trabalho da disciplina de **Programação**, com foco em demonstrar:
- Boas práticas de organização de código em Python
- Uso de banco de dados relacional embarcado
- Tratamento de entradas inválidas e exceções
- Funcionalidades extras que agregam valor real ao sistema

---

## Licença

Projeto livre para fins acadêmicos e educacionais.
