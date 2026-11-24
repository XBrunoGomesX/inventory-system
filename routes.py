import math
from flask import Blueprint, flash, redirect, render_template, request, url_for
import db

main = Blueprint('main', __name__)

# PAINEL DE CONTROLE

@main.route('/')
def dashboard():
    metricas = db.get_metricas_dashboard()
    criticos = db.get_produtos_estoque_baixo()[:5]
    return render_template(
        'index.html',
        metricas=metricas,
        produtos_criticos=criticos
    )

# PRODUTOS

@main.route('/produtos')
def lista_produtos():
    busca = request.args.get('q', '').strip()
    pagina = request.args.get('pagina', 1, type=int)
    por_pagina = 10

    produtos, total = db.get_todos_produtos(busca=busca, pagina=pagina, por_pagina=por_pagina)
    total_paginas = math.ceil(total / por_pagina) if total > 0 else 1

    return render_template(
        'produtos/lista.html',
        produtos=produtos,
        busca=busca,
        pagina=pagina,
        total_paginas=total_paginas,
        total=total
    )

@main.route('/produtos/adicionar', methods=['GET', 'POST'])
def adicionar_produto():
    if request.method == 'POST':
        nome = request.form.get('nome', '').strip()
        sku = request.form.get('sku', '').strip().upper()
        descricao = request.form.get('descricao', '').strip()
        preco_str = request.form.get('preco', '0').replace(',', '.')
        quantidade_str = request.form.get('quantidade', '0')
        localizacao = request.form.get('localizacao', '').strip()

        erros = []

        if not nome:
            erros.append('O nome do produto é obrigatório.')
        if not sku:
            erros.append('O SKU do produto é obrigatório.')

        try:
            preco = float(preco_str)
            if preco < 0:
                erros.append('O preço não pode ser negativo.')
        except ValueError:
            erros.append('O preço deve ser um número válido.')
            preco = 0.0

        try:
            quantidade = int(quantidade_str)
            if quantidade < 0:
                erros.append('A quantidade não pode ser negativa.')
        except ValueError:
            erros.append('A quantidade deve ser um número válido.')
            quantidade = 0

        if sku and db.get_produto_por_sku(sku):
            erros.append('O SKU informado já está em uso por outro produto.')

        if erros:
            for erro in erros:
                flash(erro, 'danger')
            return render_template(
                'produtos/adicionar.html', form_data=request.form
            )

        db.criar_produto(nome, sku, descricao, preco, quantidade, localizacao)
        flash(f"Produto '{nome}' adicionado com sucesso!", 'success')
        return redirect(url_for('main.lista_produtos'))

    return render_template('produtos/adicionar.html', form_data={})

# EDITAR PRODUTO
@main.route('/produtos/editar/<int:id>', methods=['GET', 'POST'])
def editar_produto(id):
    produto = db.get_produto_por_id(id)

    if not produto:
        flash('Produto não encontrado.', 'danger')
        return redirect(url_for('main.lista_produtos'))

    if request.method == 'POST':
        nome = request.form.get('nome', '').strip()
        sku = request.form.get('sku', '').strip().upper()
        descricao = request.form.get('descricao', '').strip()
        preco_str = request.form.get('preco', '0').replace(',', '.')
        quantidade_str = request.form.get('quantidade', '0')
        localizacao = request.form.get('localizacao', '').strip()

        erros = []

        if not nome:
            erros.append('O nome do produto é obrigatório.')
        if not sku:
            erros.append('O SKU do produto é obrigatório.')

        try:
            preco = float(preco_str)
            if preco < 0:
                erros.append('O preço não pode ser negativo.')
        except ValueError:
            erros.append('O preço deve ser um número válido.')
            preco = 0.0

        try:
            quantidade = int(quantidade_str)
            if quantidade < 0:
                erros.append('A quantidade não pode ser negativa.')
        except ValueError:
            erros.append('A quantidade deve ser um número válido.')
            quantidade = 0

        if sku and db.get_produto_por_sku(sku, excluir_id=produto['id']):
            erros.append('O SKU informado já está em uso por outro produto.')

        if erros:
            for erro in erros:
                flash(erro, 'danger')
            return render_template(
                'produtos/editar.html', form_data=request.form, produto=produto
            )

        db.atualizar_produto(id, nome, sku, descricao, preco, quantidade, localizacao)
        flash(f"Produto '{nome}' atualizado com sucesso!", 'success')
        return redirect(url_for('main.lista_produtos'))

    return render_template('produtos/editar.html', produto=produto, form_data=produto)

# DELETAR PRODUTO
@main.route('/produtos/deletar/<int:id>', methods=['POST'])
def deletar_produto(id):
    produto = db.get_produto_por_id(id)
    if produto:
        nome = produto['nome']
        db.deletar_produto(id)
        flash(f"Produto '{nome}' deletado com sucesso!", 'success')
    else:
        flash('Produto não encontrado.', 'danger')
    return redirect(url_for('main.lista_produtos'))

# ESTOQUE BAIXO
@main.route('/relatorios/estoque-baixo')
def relatorio_estoque_baixo():
    produtos = db.get_produtos_estoque_baixo()
    return render_template('relatorios/estoque_baixo.html', produtos=produtos, limiar=db.LIMIAR_ESTOQUE_BAIXO)

# TRANSAÇÕES DE ESTOQUE
@main.route('/produtos/<int:id>/transacao', methods=['GET', 'POST'])
def transacao_estoque(id):
    produto = db.get_produto_por_id(id)
    if not produto:
        flash('Produto não encontrado.', 'danger')
        return redirect(url_for('main.lista_produtos'))

    if request.method == 'POST':
        tipo = request.form.get('tipo')
        quantidade_str = request.form.get('quantidade', '0')

        try:
            quantidade = int(quantidade_str)
            if quantidade <= 0:
                raise ValueError('A quantidade deve ser um número positivo.')
        except ValueError:
            flash('A quantidade deve ser um número válido e positivo.', 'danger')
            return render_template('produtos/transacao.html', produto=produto)

        sucesso, mensagem = db.registrar_transacao(id, tipo, quantidade)
        if sucesso:
            flash(mensagem, 'success')
            return redirect(url_for('main.lista_produtos'))
        else:
            flash(mensagem, 'danger')

    return render_template('produtos/transacao.html', produto=produto)