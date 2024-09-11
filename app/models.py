from app import database, login_manager
from datetime import datetime
from flask_login import UserMixin

@login_manager.user_loader
def load_usuario(id_usuario):
    return Usuarios.query.get(int(id_usuario))


class Usuarios(database.Model, UserMixin):
    __tablename__ = 'usuarios'
    id = database.Column(database.Integer, primary_key=True)
    username = database.Column(database.String, nullable=False)
    email = database.Column(database.String, nullable=False, unique=True)
    senha = database.Column(database.String, nullable=False)
    foto_perfil = database.Column(database.String, default='undraw_profile.svg')
    movimentacoes = database.relationship('Movimentacoes', backref='autor', lazy=True)

class Acoes(database.Model):
    __tablename__ = 'acoes'
    id = database.Column(database.Integer, primary_key=True, autoincrement=True)
    ticker = database.Column(database.String, nullable=False, unique=True)
    nome = database.Column(database.String, nullable=False, default='')
    preco_atual = database.Column(database.Numeric, nullable=False, default=0)
    preco_minimo = database.Column(database.Numeric, nullable=False, default=0)
    preco_maximo = database.Column(database.Numeric, nullable=False, default=0)
    preco_medio_alvo = database.Column(database.Numeric, nullable=False, default=0)
    preco_medio_desejado = database.Column(database.Numeric, nullable=False, default=0)
    preco_data = database.Column(database.Integer, nullable=False, default='1900-01-01')
    setor = database.Column(database.String, nullable=False, default='')
    sub_setor = database.Column(database.String, nullable=False, default='')
    recomendacao = database.Column(database.String, nullable=False, default='')

    movimentacoes = database.relationship(
        "Movimentacoes", foreign_keys="[Movimentacoes.id_acao]", back_populates="acao"
    )

    def __init__(self, ticker):
        self.ticker = ticker

class Movimentacoes(database.Model):
    __tablename__ = 'movimentacoes'
    id = database.Column(database.Integer, primary_key=True, autoincrement=True)
    id_acao = database.Column(database.Integer, database.ForeignKey("acoes.id"), nullable=False)
    id_usuario = database.Column(database.Integer, database.ForeignKey('usuarios.id'), nullable=False)
    data = database.Column(database.Integer, nullable=False)
    cd_tipo = database.Column(database.Integer, nullable=False)
    quantidade = database.Column(database.Integer, nullable=False)
    valor_unitario = database.Column(database.Numeric, nullable=False)
    total_taxas = database.Column(database.Numeric, nullable=False)

    acao = database.relationship(
        "Acoes", foreign_keys=[id_acao], back_populates="movimentacoes"
    )

    def valor_total(self):
        if self.cd_tipo == 1:
            return (self.quantidade * self.valor_unitario) + self.total_taxas
        else:
            return (self.quantidade * self.valor_unitario) - self.total_taxas

class Carteira(database.Model):
    __tablename__ = 'carteira'
    id_usuario = database.Column(database.Integer, primary_key=True)
    id_acao = database.Column(database.Integer, primary_key=True)
    ticker = database.Column(database.String, nullable=False, unique=True)
    nome = database.Column(database.String, nullable=False)
    preco_atual = database.Column(database.Numeric, nullable=False)
    quantidade = database.Column(database.Integer, nullable=False)
    valor = database.Column(database.Numeric, nullable=False)
    valor_medio = database.Column(database.Numeric, nullable=False)
    rentabilidade_percentual = database.Column(database.Numeric, nullable=False)
    rentabilidade_valor = database.Column(database.Numeric, nullable=False)

class CarteiraPorUsuario(database.Model):
    __tablename__ = 'carteira_por_usuario'
    id_usuario = database.Column(database.Integer, primary_key=True)
    quantidade = database.Column(database.Integer, nullable=False)
    valor = database.Column(database.Numeric, nullable=False)
    rentabilidade_percentual = database.Column(database.Numeric, nullable=False)
    rentabilidade_valor = database.Column(database.Numeric, nullable=False)

class Resultado(database.Model):
    __tablename__ = 'resultado'
    id_usuario = database.Column(database.Integer, primary_key=True)
    periodo = database.Column(database.String, primary_key=True)
    id_acao = database.Column(database.Integer, primary_key=True)
    total_compras = database.Column(database.Numeric, nullable=False)
    total_quantidade_comprada = database.Column(database.Integer, nullable=False)
    total_vendas = database.Column(database.Numeric, nullable=False)
    total_quantidade_vendida = database.Column(database.Integer, nullable=False)
    custo_medio = database.Column(database.Numeric, nullable=False)
    lucro_prejuizo = database.Column(database.Numeric, nullable=False)
    rentabilidade_percentual = database.Column(database.Numeric, nullable=False)

class ResultadoPorTicker(database.Model):
    __tablename__ = 'resultado_por_ticker'
    id_usuario = database.Column(database.Integer, primary_key=True)
    periodo = database.Column(database.String, primary_key=True)
    id_acao = database.Column(database.Integer, primary_key=True)
    ticker = database.Column(database.String, nullable=False, unique=True)
    nome = database.Column(database.String, nullable=False)    
    total_compras = database.Column(database.Numeric, nullable=False)
    total_quantidade_comprada = database.Column(database.Integer, nullable=False)
    total_vendas = database.Column(database.Numeric, nullable=False)
    total_quantidade_vendida = database.Column(database.Integer, nullable=False)
    total_taxas = database.Column(database.Numeric, nullable=False)
    custo_medio = database.Column(database.Numeric, nullable=False)
    lucro_prejuizo = database.Column(database.Numeric, nullable=False)
    rentabilidade_percentual = database.Column(database.Numeric, nullable=False)

class ResultadoPorPeriodo(database.Model):
    __tablename__ = 'resultado_por_periodo'
    id_usuario = database.Column(database.Integer, primary_key=True)
    periodo = database.Column(database.String, primary_key=True)
    total_compras = database.Column(database.Numeric, nullable=False)
    total_quantidade_comprada = database.Column(database.Integer, nullable=False)
    total_vendas = database.Column(database.Numeric, nullable=False)
    total_quantidade_vendida = database.Column(database.Integer, nullable=False)
    total_taxas = database.Column(database.Numeric, nullable=False)
    custo_medio = database.Column(database.Numeric, nullable=False)
    lucro_prejuizo = database.Column(database.Numeric, nullable=False)
    rentabilidade_percentual = database.Column(database.Numeric, nullable=False)

    def imposto_a_pagar(self):
        if self.total_vendas > 20000 and self.lucro_prejuizo > 0:
            return (self.lucro_prejuizo) * 15 / 100
        else:
            return 0




