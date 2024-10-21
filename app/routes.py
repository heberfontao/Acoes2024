from flask import render_template, redirect, url_for, flash, request, abort
from app import app, database, bcrypt
from app.forms import FormLogin, FormCriarConta, FormEditarPerfil, FormAcoes, FormApuracao, FormBusca, FormMovimentacoes
from app.models import Usuarios, Acoes, Movimentacoes, Carteira, CarteiraPorUsuario, Resultado, ResultadoPorPeriodo, ResultadoPorTicker
from flask_login import login_user, logout_user, current_user, login_required
from PIL import Image
from datetime import date, datetime
from app import database

import calendar
import datetime
import locale
import secrets
import os
import requests
import yfinance as yf

# Home
@app.route('/')
def home():
    if current_user.is_authenticated:
        total_compras = 0
        total_vendas = 0
        total_taxas = 0
        imposto_a_pagar = 0
        periodo = datetime.datetime.today().strftime('%m/%Y')
        rentabilidade_valor = 0
        rentabilidade_percentual = 0
        resultado_por_periodo = ResultadoPorPeriodo.query.filter(ResultadoPorPeriodo.id_usuario==current_user.id,ResultadoPorPeriodo.periodo==periodo).first()
        ultimos_resultados_por_periodo = ResultadoPorPeriodo.query.filter(ResultadoPorPeriodo.id_usuario==current_user.id)
        resultados_periodos = []
        resultados_valores = []
        if(resultado_por_periodo != None):
            total_compras = resultado_por_periodo.total_compras
            total_vendas = resultado_por_periodo.total_vendas
            total_taxas = resultado_por_periodo.total_taxas
            imposto_a_pagar = resultado_por_periodo.imposto_a_pagar()
        if(ultimos_resultados_por_periodo != None):
            for resultado in ultimos_resultados_por_periodo:
                resultados_periodos.append(resultado.periodo)
                resultados_valores.append(resultado.lucro_prejuizo)
        return render_template('home.html', total_compras=total_compras, total_vendas=total_vendas, total_taxas=total_taxas, imposto_a_pagar=imposto_a_pagar, resultados_periodos=resultados_periodos,resultados_valores=resultados_valores)
    return redirect(url_for('login'))

# Autenticação
@app.route('/login', methods=['GET', 'POST'])
def login():
    form_login = FormLogin()
    if form_login.validate_on_submit() and 'botao_submit_login' in request.form:
        usuario = Usuarios.query.filter_by(email=form_login.email.data).first()
        if usuario and bcrypt.check_password_hash(usuario.senha, form_login.senha.data):
            login_user(usuario, remember=form_login.lembrar_dados.data)
            par_next = request.args.get('next')
            if par_next:
                return redirect(par_next)
            else:
                return redirect(url_for('home'))
        else:
            flash(f'Falha no Login. E-mail ou Senha Incorretos', 'alert-danger')
    return render_template('login.html', form_login=form_login)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

# Usuário
@app.route('/usuarios')
@login_required
def usuarios():
    lista_usuarios = Usuarios.query.all()
    return render_template('usuarios.html', lista_usuarios=lista_usuarios)

@app.route('/usuario/conta/nova', methods=['GET', 'POST'])
def usuarios_inserir():
    form_criarconta = FormCriarConta()
    if form_criarconta.validate_on_submit() and 'botao_submit_criarconta' in request.form:
        senha_cript = bcrypt.generate_password_hash(form_criarconta.senha.data)
        usuario = Usuarios(username=form_criarconta.username.data, email=form_criarconta.email.data, senha=senha_cript)
        database.session.add(usuario)
        database.session.commit()
        flash(f'Conta criada para o e-mail: {form_criarconta.email.data}', 'alert-success')
        return redirect(url_for('home'))
    return render_template('usuarios-novo.html', form_criarconta=form_criarconta)

@app.route('/usuarios/perfil', methods=['GET', 'POST'])
@login_required
def usuarios_perfil():
    form = FormEditarPerfil()
    form.email.data = current_user.email
    form.username.data = current_user.username
    foto_perfil = url_for('static', filename='fotos_perfil/{}'.format(current_user.foto_perfil))
    return render_template('usuarios-perfil.html', foto_perfil=foto_perfil, form=form)

@app.route('/usuarios/perfil/editar', methods=['GET', 'POST'])
@login_required
def usuarios_perfil_editar():
    form = FormEditarPerfil()
    if form.validate_on_submit():
        current_user.email = form.email.data
        current_user.username = form.username.data
        if form.foto_perfil.data:
            nome_imagem = salvar_imagem(form.foto_perfil.data)
            current_user.foto_perfil = nome_imagem

        database.session.commit()
        flash('Perfil atualizado com Sucesso', 'alert-success')
        return redirect(url_for('usuarios_perfil'))
    elif request.method == "GET":
        form.email.data = current_user.email
        form.username.data = current_user.username
    foto_perfil = url_for('static', filename='fotos_perfil/{}'.format(current_user.foto_perfil))
    return render_template('usuarios-perfil-edicao.html', foto_perfil=foto_perfil, form=form)

def salvar_imagem(imagem):
    codigo = secrets.token_hex(8)
    nome, extensao = os.path.splitext(imagem.filename)
    nome_arquivo = nome + codigo + extensao
    caminho_completo = os.path.join(app.root_path, 'static/fotos_perfil', nome_arquivo)
    tamanho = (400, 400)
    imagem_reduzida = Image.open(imagem)
    imagem_reduzida.thumbnail(tamanho)
    imagem_reduzida.save(caminho_completo)
    return nome_arquivo

# Ações
@app.route('/acoes')
@login_required
def acoes_listar():
    acoes = Acoes.query.order_by(Acoes.id.asc())
    form_acoes = FormAcoes()
    return render_template('acoes-lista.html', acoes=acoes, form_acoes=form_acoes)

@app.route('/acoes/nova', methods=['POST'])
@login_required
def acoes_inserir():
    form_acoes = FormAcoes()
    if form_acoes.validate_on_submit():
        acao = Acoes(form_acoes.ticker.data)
        acao = acoes_obter_dados(acao)
        acao = database.session.add(acao)
        database.session.commit()
        flash('Ação cadastrada com sucesso', 'alert-success')
    
    return redirect(url_for('acoes_listar'))

@app.route('/acoes/atualizar', methods=['GET'])
def acoes_atualizar():
    acoes = Acoes.query.order_by(Acoes.id.asc())
    for acao in acoes:
        acao = acoes_obter_dados(acao)
    database.session.commit()
    return redirect(url_for('acoes_listar'))

def acoes_obter_dados(acao):
    ticker = yf.Ticker(acao.ticker + '.SA')
    if(ticker):
        acao.nome = ticker.info.get('longName', 'Nome não disponível')
        acao.setor = ticker.info.get('sectorDisp', '')
        acao.sub_setor = ticker.info.get('industryDisp', '')
        acao.preco_atual = ticker.info.get('currentPrice', -1)
        acao.preco_minimo = ticker.info.get('targetLowPrice', -1)
        acao.preco_maximo = ticker.info.get('targetHighPrice', -1)
        acao.preco_medio_alvo = ticker.info.get('targetMeanPrice', -1)
        acao.preco_medio_desejado = ticker.info.get('targetMedianPrice', -1)
        acao.recomendacao = ticker.info.get('recommendationKey', '').replace('buy','Comprar').replace('underperform','Abaixo do Desempenho').replace('outperform ','Acima do Esperado').replace('hold','Segurar')
        acao.preco_data = datetime.datetime.today()
        #print(ticker.info)
    return acao

# Movimentações
@app.route('/movimentacoes')
@login_required
def movimentacoes_listar():
    movimentacoes = Movimentacoes.query.filter(Movimentacoes.id_usuario==current_user.id).order_by(Movimentacoes.id.desc())
    form_movimentacoes = FormMovimentacoes()
    return render_template('movimentacoes-lista.html', movimentacoes=movimentacoes, form_movimentacoes=form_movimentacoes)

@app.route('/movimentacoes/nova', methods=['POST'])
@login_required
def movimentacoes_inserir():
    print("Formulário validado com sucesso!")
    print("Entrou na função movimentacoes_inserir")  # Verifique se esse print aparece
    form_movimentacoes = FormMovimentacoes()
    if form_movimentacoes.validate_on_submit():
        # Verificar o valor de total_taxas
        print(f"Total Taxas: {form_movimentacoes.total_taxas.data}")
        movimentacoes = Movimentacoes(cd_tipo=(form_movimentacoes.cd_tipo).data,id_acao=(form_movimentacoes.id_acao.data).id, autor=current_user, data=form_movimentacoes.data.data, quantidade=form_movimentacoes.quantidade.data, valor_unitario=form_movimentacoes.valor_unitario.data, total_taxas=form_movimentacoes.total_taxas.data)
        database.session.add(movimentacoes)
        database.session.commit()
        flash('Movimentação cadastrada com sucesso', 'alert-success')
    
    else:
        print("Erro na validação do formulário:", form_movimentacoes.errors)  # Exibir os erros de validação
    
    return redirect(url_for('movimentacoes_listar'))

# Carteira
@app.route('/carteira')
@login_required
def carteira_listar():
    carteira_valor = 0
    carteira_quantidade = 0
    carteira_rentabilidade_valor = 0
    carteira_rentabilidade_percentual = 0
    carteira_por_usuario = CarteiraPorUsuario.query.filter(CarteiraPorUsuario.id_usuario==current_user.id).first()
    carteira = Carteira.query.filter(Carteira.id_usuario==current_user.id).order_by(Carteira.ticker.asc())
    if(carteira_por_usuario != None):
            carteira_valor = carteira_por_usuario.valor
            carteira_quantidade = carteira_por_usuario.quantidade
            carteira_rentabilidade_valor = carteira_por_usuario.rentabilidade_valor
            carteira_rentabilidade_percentual = carteira_por_usuario.rentabilidade_percentual
    return render_template('carteira-lista.html', carteira_valor=carteira_valor, carteira_quantidade=carteira_quantidade, carteira_rentabilidade_valor=carteira_rentabilidade_valor, carteira_rentabilidade_percentual=carteira_rentabilidade_percentual, carteira=carteira)

# Relatórios
@app.route('/relatorios/resultados')
@login_required
def relatorios_resultados():
    resultados = ResultadoPorPeriodo.query.filter(ResultadoPorPeriodo.id_usuario==current_user.id)
    return render_template('relatorios-resultados.html', resultados=resultados)

@app.route('/relatorios/apuracao', methods=['GET', 'POST'])
@login_required
def relatorios_apuracao():
    form_apuracao = FormApuracao()
    resultado_por_periodo = ResultadoPorPeriodo()
    if form_apuracao.validate_on_submit():
        resultado_por_periodo = ResultadoPorPeriodo.query.filter(ResultadoPorPeriodo.id_usuario==current_user.id,ResultadoPorPeriodo.periodo==form_apuracao.data.data).first()
        resultados_por_ticker = ResultadoPorTicker.query.filter(ResultadoPorTicker.id_usuario==current_user.id,ResultadoPorTicker.periodo==form_apuracao.data.data)
        return render_template('relatorios-apuracao.html', form_apuracao=form_apuracao,resultado_por_periodo=resultado_por_periodo,resultados_por_ticker=resultados_por_ticker)
    
    return render_template('relatorios-apuracao.html', form_apuracao=form_apuracao)

# Contato
@app.route('/contato')
def contato():
    return render_template('contato.html')



