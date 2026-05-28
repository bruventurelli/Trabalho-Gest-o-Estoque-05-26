# Trabalho-Gest-o-Estoque-05-26
Trabalho de faculdade em python e SQLite sobre gestão de estoques.
# Sistema de Gestao de Estoque

Este repositorio contem o projeto academico desenvolvido para a disciplina de Programacao de Computadores. O sistema consiste em uma aplicacao baseada em terminal voltada ao monitoramento, controle de fluxos de mercadorias, gerenciamento de saldos e emissao de alertas de niveis criticos para ambientes comerciais e industriais.




## Objetivo do Projeto

Aplicar conceitos praticos de programacao estruturada em linguagem Python, com enfase em manipulacao de estruturas de dados compostas (dicionarios), modularizacao por meio de funcao com escopo delimitado, validacoes de consistencia e tratamento de entradas de dados para simular um cenario corporativo real de controle de inventario.



## Funcionalidades Implementadas

O programa possui um menu dinamico e interativo via console equipado com as seguintes rotinas de negocio:

* **Cadastro de produtos (Opcao 1):** Registra itens capturando nome, categoria, preco unitario e saldo inicial. Gera IDs numericos e sequenciais automaticamente.
* **Registrar entrada (Opcao 2):** Adiciona quantidades positivas ao saldo de um produto especifico com base no ID fornecido.
* **Registrar saida (Opcao 3):** Deduz itens do estoque de forma segura, acionando barreiras de validacao para impedir que o saldo fique negativo.
* **Consultar produto (Opcao 4):** Retorna uma ficha descritiva formatada com todos os metadados do produto consultado.
* **Listar todos os produtos (Opcao 5):** Exibe o inventario consolidado em uma tabela organizada por colunas com o total geral de itens.
* **Alerta de estoque baixo (Opcao 6):** Identifica em tempo real quais produtos possuem quantidade em estoque estritamente abaixo do teto configurado pelo operador.

### Tratamento de Erros e Robustez
O sistema foi projetado para evitar interrupcoes abruptas do script (crashes), implementando:
* Tratamento de excecoes (`ValueError`) via funcoes auxiliares de leitura para impedir a quebra do programa caso o usuario digite caracteres alfabeticos em campos numericos.
* Validacao de valores negativos para precos, limites e quantidades.
* Mensagens informativas estruturadas caso o usuario pesquise por IDs inexistentes ou tente realizar operacoes superiores ao volume disponivel (Estoque insuficiente).



## Estrutura de Dados e Funcoes Obrigatorias

O projeto centraliza seus registros em um dicionario global chamado `estoque`, onde cada chave unica representa o ID do produto e o valor armazena um sub-dicionario com os atributos da mercadoria.

### Funcoes Obrigatorias do Escopo:
* `def cadastrar_produto(nome, categoria, preco, quantidade):` Registra um novo produto apos sanitizacao das strings e validacao numerica.
* `def registrar_entrada(produto_id, quantidade):` Localiza a chave correspondente no dicionario global e atualiza o montante.
* `def registrar_saida(produto_id, quantidade):` Verifica a elegibilidade da baixa e atualiza o saldo fisico.
* `def consultar_estoque(produto_id):` Imprime e retorna o dicionario especifico do produto.
* `def alertar_estoque_baixo(limite):` Filtra elementos estruturados via list comprehension, gerando um relatorio analitico de urgencia.



## Instrucoes de Execucao

### Pre-requisitos
* Ambiente de execucao **Python 3.x** instalado e configurado.

### Passo a Passo para Execucao

1. Clonar o repositorio para o ambiente local:
   ```bash
   git clone [https://github.com/]# Sistema de Gestao de Estoque

Este repositorio contem o projeto academico desenvolvido para a disciplina de Programacao Estruturada. O sistema consiste em uma aplicacao baseada em terminal voltada ao monitoramento, controle de fluxos de mercadorias, gerenciamento de saldos e emissao de alertas de niveis criticos para ambientes comerciais e industriais.

**Valor do Projeto:** 2,0 pontos  
**Estudante:** [Seu Nome Completo]  
**Link do Repositorio:** [Link do seu GitHub]



## Objetivo do Projeto

Aplicar conceitos praticos de programacao estruturada em linguagem Python, com enfase em manipulacao de estruturas de dados compostas (dicionarios), modularizacao por meio de funcao com escopo delimitado, validacoes de consistencia e tratamento de entradas de dados para simular um cenario corporativo real de controle de inventario.



## Funcionalidades Implementadas

O programa possui um menu dinamico e interativo via console equipado com as seguintes rotinas de negocio:

* **Cadastro de produtos (Opcao 1):** Registra itens capturando nome, categoria, preco unitario e saldo inicial. Gera IDs numericos e sequenciais automaticamente.
* **Registrar entrada (Opcao 2):** Adiciona quantidades positivas ao saldo de um produto especifico com base no ID fornecido.
* **Registrar saida (Opcao 3):** Deduz itens do estoque de forma segura, acionando barreiras de validacao para impedir que o saldo fique negativo.
* **Consultar produto (Opcao 4):** Retorna uma ficha descritiva formatada com todos os metadados do produto consultado.
* **Listar todos os produtos (Opcao 5):** Exibe o inventario consolidado em uma tabela organizada por colunas com o total geral de itens.
* **Alerta de estoque baixo (Opcao 6):** Identifica em tempo real quais produtos possuem quantidade em estoque estritamente abaixo do teto configurado pelo operador.

### Tratamento de Erros e Robustez
O sistema foi projetado para evitar interrupcoes abruptas do script (crashes), implementando:
* Tratamento de excecoes (`ValueError`) via funcoes auxiliares de leitura para impedir a quebra do programa caso o usuario digite caracteres alfabeticos em campos numericos.
* Validacao de valores negativos para precos, limites e quantidades.
* Mensagens informativas estruturadas caso o usuario pesquise por IDs inexistentes ou tente realizar operacoes superiores ao volume disponivel (Estoque insuficiente).



## Estrutura de Dados e Funcoes Obrigatorias

O projeto centraliza seus registros em um dicionario global chamado `estoque`, onde cada chave unica representa o ID do produto e o valor armazena um sub-dicionario com os atributos da mercadoria.

### Funcoes Obrigatorias do Escopo:
* `def cadastrar_produto(nome, categoria, preco, quantidade):` Registra um novo produto apos sanitizacao das strings e validacao numerica.
* `def registrar_entrada(produto_id, quantidade):` Localiza a chave correspondente no dicionario global e atualiza o montante.
* `def registrar_saida(produto_id, quantidade):` Verifica a elegibilidade da baixa e atualiza o saldo fisico.
* `def consultar_estoque(produto_id):` Imprime e retorna o dicionario especifico do produto.
* `def alertar_estoque_baixo(limite):` Filtra elementos estruturados via list comprehension, gerando um relatorio analitico de urgencia.



### Pre-requisitos
* Ambiente de execucao **Python 3.x** instalado e configurado.

