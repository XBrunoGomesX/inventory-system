import sqlite3
from tkinter import INSERT

DATABASE = 'estoque.db'
LIMIAR_ESTOQUE_BAIXO = 5

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    with open('schema.sql', 'r', encoding='utf-8') as f:
        conn.executescript(f.read())
    conn.commit()
    conn.close()
    print("Banco de dados inicializado")

# --------------
# PRODUTOS
# --------------

def criar_produto(nome,sku,descricao,preco,quantidade,localizacao):
    conn = get_db_connection()
    conn.execute(
        '''INSERT INTO produtos (nome, sku, descricao, preco, quantidade, localizacao)
            VALUES (?, ?, ?, ?, ?, ?)''', (nome, sku, descricao, preco, quantidade, localizacao)
    )
    conn.commit()
    conn.close()

def atualizar_produto(produto_id,nome,sku,descricao,preco,quantidade,localizacao):
    conn = get_db_connection()
    conn.execute(
        '''UPDATE produtos SET nome = ?, sku = ?, descricao = ?, preco = ?, quantidade = ?, localizacao = ?
            WHERE id = ?''', (nome, sku, descricao, preco, quantidade, localizacao, produto_id)
    )
    conn.commit()
    conn.close()

def get_todos_produtos(busca=None, pagina=1, por_pagina=10):
    conn = get_db_connection()
    offset = (pagina - 1) * por_pagina
    if busca:
        filtro = f"%{busca}%"
        produtos = conn.execute(
            '''SELECT * FROM produtos WHERE nome LIKE ? OR sku LIKE ? ORDER BY nome ASC LIMIT ? OFFSET ?''',
            (filtro, filtro, por_pagina, offset)
        ).fetchall()
        total = conn.execute(
            '''SELECT COUNT(*) as total FROM produtos WHERE nome LIKE ? OR sku LIKE ?''',
            (filtro, filtro)
        ).fetchone()[0]
    else:
        produtos = conn.execute(    
            '''SELECT * FROM produtos ORDER BY nome ASC LIMIT ? OFFSET ?''',
            (por_pagina, offset)
        ).fetchall()
        total = conn.execute(
            '''SELECT COUNT(*) as total FROM produtos'''
        ).fetchone()[0]

    conn.close()
    return produtos, total

def get_produto_por_id(produto_id):
    conn = get_db_connection()
    produto = conn.execute(
        '''SELECT * FROM produtos WHERE id = ?''', (produto_id,)
    ).fetchone()
    conn.close()
    return produto

def get_produto_por_sku(sku, excluir_id=None):
    conn = get_db_connection()
    if excluir_id:
        produto = conn.execute(
            '''SELECT * FROM produtos WHERE sku = ? AND id != ?''', (sku, excluir_id)
        ).fetchone()
    else: 
        produto = conn.execute(
            '''SELECT * FROM produtos WHERE sku = ?''', (sku,)
        ).fetchone()
    conn.close()
    return produto

def get_produtos_estoque_baixo():
    conn = get_db_connection()
    produtos = conn.execute(
        '''SELECT * FROM produtos WHERE quantidade <= ? ORDER BY quantidade ASC''', (LIMIAR_ESTOQUE_BAIXO,)
    ).fetchall()
    conn.close()
    return produtos

def deletar_produto(produto_id):
    conn = get_db_connection()
    conn.execute(
        '''DELETE FROM produtos WHERE id = ?''', (produto_id,)
    )
    conn.commit()
    conn.close()

# DASHBOARD

def get_metricas_dashboard():
    conn = get_db_connection()
    total_produtos = conn.execute(
        '''SELECT COUNT(*) as total FROM produtos'''
    ).fetchone()[0]
    produtos_estoque_baixo = conn.execute(
        '''SELECT COUNT(*) as total FROM produtos WHERE quantidade <= ?''', (LIMIAR_ESTOQUE_BAIXO,)
    ).fetchone()[0]

    valor_total = conn.execute(
        '''SELECT COALESCE(SUM(preco * quantidade), 0.0) as total FROM produtos'''
    ).fetchone()[0]
    conn.close()
    return {
        'total_produtos': total_produtos or 0,
        'total_estoque_baixo': produtos_estoque_baixo or 0,
        'valor_total': float(valor_total or 0.0)
    }

# MOVIMENTAÇÕES DE ESTOQUE

def registrar_transacao(produto_id, tipo, quantidade_transacao):
    conn = get_db_connection()
    produto = conn.execute(
        'SELECT quantidade, nome FROM produtos WHERE id = ?', (produto_id,)
    ).fetchone()
    if not produto:
        conn.close()
        return False, "Produto não encontrado."

    estoque_atual = produto['quantidade']

    if tipo == 'entrada':
        novo_estoque = estoque_atual + quantidade_transacao
        msg_tipo = "Entrada"
    elif tipo == 'saida':
        if quantidade_transacao > estoque_atual:
            conn.close()
            return False, "Quantidade de saída maior que o estoque atual."
        novo_estoque = estoque_atual - quantidade_transacao
        msg_tipo = "Saída"
    else:
        conn.close()
        return False, "Tipo de transação inválido."
    conn.execute(
        'UPDATE produtos SET quantidade = ? WHERE id = ?', (novo_estoque, produto_id)
    )
    conn.commit()
    conn.close()
    return True, f"{msg_tipo} de {quantidade_transacao} unidades do produto '{produto['nome']}' registrada com sucesso."