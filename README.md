# 📦 Sistema de Gerenciamento de Estoque

Aplicação web desenvolvida com **Flask** e **SQLite** para controle de produtos, alertas de estoque baixo, movimentações de estoque e visualização de métricas em um painel de controle.

---

## Stack Tecnológica

| Camada | Tecnologias |
|---|---|
| **Back-end** | Python, Flask (`Blueprint`) |
| **Banco de Dados** | SQLite (`sqlite3`) |
| **Front-end** | HTML5, CSS3, Jinja2, Bootstrap 5 e Bootstrap Icons |

---

## Funcionalidades

### Painel de Controle (`/`)
Exibe métricas consolidadas:
- Total de produtos cadastrados
- Quantidade de produtos com estoque baixo
- Valor total em estoque (soma de `preço × quantidade`)

Também lista os **5 itens mais críticos** para reposição urgente.

### Gestão de Produtos (`/produtos`)
- **Listagem paginada** (10 itens por página) com busca por nome ou SKU
- **Cadastro** de produtos (`/produtos/adicionar`) com validação de campos e SKU único
- **Edição** (`/produtos/editar/<int:id>`)
- **Exclusão** com confirmação no navegador (`/produtos/deletar/<int:id>`)

Cada produto possui: nome, SKU, descrição, preço, quantidade, localização e data de adição.

### Movimentação de Estoque (`/produtos/<int:id>/transacao`)
Registro de **entradas** e **saídas** com atualização do saldo. Saídas maiores que o estoque atual são recusadas.

### Relatório de Estoque Baixo (`/relatorios/estoque-baixo`)
Consulta dedicada aos produtos com quantidade **menor ou igual a 5 unidades** (limiar definido em `LIMIAR_ESTOQUE_BAIXO`, no arquivo `db.py`).

---

## Rotas

| Método | Rota | Descrição |
|---|---|---|
| `GET` | `/` | Painel de controle |
| `GET` | `/produtos` | Lista, busca (`?q=`) e paginação (`?pagina=`) |
| `GET/POST` | `/produtos/adicionar` | Cadastro de produto |
| `GET/POST` | `/produtos/editar/<int:id>` | Edição de produto |
| `POST` | `/produtos/deletar/<int:id>` | Exclusão de produto |
| `GET/POST` | `/produtos/<int:id>/transacao` | Entrada/saída de estoque |
| `GET` | `/relatorios/estoque-baixo` | Relatório de estoque baixo |

---

## Estrutura do Projeto

```text
inventory-system/
├── app.py              # Inicialização da aplicação Flask e registro do Blueprint
├── routes.py           # Rotas e regras de controle da aplicação
├── db.py               # Conexão com SQLite, inicialização e consultas ao banco
├── schema.sql          # Script de criação da tabela de produtos
├── estoque.db          # Banco de dados SQLite (criado/atualizado ao iniciar)
├── requirements.txt    # Dependências Python do projeto
├── LICENSE             # Licença MIT
├── static/
│   └── css/
│       └── style.css   # Estilos customizados complementares ao Bootstrap
└── templates/
    ├── base.html           # Template base (layout, navbar, mensagens flash)
    ├── index.html          # Painel de controle
    ├── produtos/
    │   ├── lista.html      # Listagem, busca e paginação
    │   ├── adicionar.html  # Formulário de cadastro
    │   ├── editar.html     # Formulário de edição
    │   └── transacao.html  # Movimentação de estoque
    └── relatorios/
        └── estoque_baixo.html  # Relatório de estoque baixo
```

---

## Como Executar

### Pré-requisitos
- [Python 3.9+](https://www.python.org/downloads/)
- `pip`
- Conexão com a internet (Bootstrap e Bootstrap Icons são carregados via CDN)

### Passo a passo

1. **Clone o repositório**
   ```bash
   git clone <url-do-repositorio>
   cd inventory-system
   ```

2. **Crie e ative um ambiente virtual** 
   ```bash
   # Linux / macOS
   python3 -m venv venv
   source venv/bin/activate

   # Windows
   python -m venv venv
   venv\Scripts\activate
   ```

3. **Instale as dependências**
   ```bash
   pip install -r requirements.txt
   ```

4. **Execute a aplicação**
   ```bash
   python app.py
   ```

5. **Acesse no navegador**
   ```
   http://127.0.0.1:5000
   ```
---

## Arquitetura

- **`app.py`** — cria a instância do Flask, registra o `Blueprint` `main` e inicializa o banco antes de subir o servidor.
- **`routes.py`** — concentra as rotas e as regras de controle (validações, mensagens flash e redirecionamentos).
- **`db.py`** — camada de acesso a dados: conexão com o SQLite, inicialização, CRUD de produtos, métricas do painel e movimentações de estoque.
- **`templates/`** — views em Jinja2, todas herdando de `base.html`, estilizadas com Bootstrap 5.

---

## Configuração

| Item | Onde | Padrão |
|---|---|---|
| Limiar de estoque baixo | `LIMIAR_ESTOQUE_BAIXO` em `db.py` | `5` |
| Arquivo do banco | `DATABASE` em `db.py` | `estoque.db` |
| Itens por página | `por_pagina` em `routes.py` | `10` |

---

## Licença

Distribuído sob a licença **MIT**. Veja o arquivo [`LICENSE`](LICENSE) para mais detalhes.