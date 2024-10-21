import flask
import jinja2
import mysql.connector
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from jinja2 import pass_context
from datetime import datetime

blueprint = flask.Blueprint('filters', __name__)

app = Flask(__name__)

app.register_blueprint(blueprint)

app.config['SECRET_KEY'] = '29cecf8afd6176f06bb3f55472d490d1'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
#app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///sistema.db'
#app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:sistemaapurador@localhost/sistema'
#app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root@localhost/sistema'
#app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://b6d4b17dca4b6b:fa6bba9c@us-cdbr-east-05.cleardb.net/heroku_c7f16e3a08a9c82'
#app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://b2e27851b08bb1:ccf4b5fb@us-cdbr-east-06.cleardb.net/heroku_813be3ee8adffef'
#app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://himbrasi_heber:UrF72K91xQz9@144.76.57.69/himbrasi_erp'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:123456@35.198.30.135:3306/sistema'


database = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'alert-info'

from app import routes

# Filtros
@app.template_filter('format_moeda')
def format_moeda(value):
    if value is None:
      value = 'R$ 0,00'
    return f'R$ {value:,.2f}'.replace(',', 'X').replace('.', ',').replace('X', '.')

@app.template_filter('format_data')
def format_data(value):
    return value.strftime('%d/%m/%Y')

@app.template_filter('format_tipo_movimentacao')
def format_tipo_movimentacao(value):
    if(value == 1):
      return 'Compra'
    else:
      return 'Venda'
'''
@app.template_filter('format_porcentagem')
def format_porcentagem(value):
    if value is None:
      value = '0%'
    return f'{value:,.2f}%'.replace(',', 'X').replace('.', ',').replace('X', '.')
'''

@app.template_filter('format_porcentagem')
def format_porcentagem(value):
    if value is None:
        value = 0  # Define um valor padrão se for None
    try:
        # Tenta garantir que o valor seja numérico antes da formatação
        value = float(value)
        return f'{value:,.2f}%'.replace(',', 'X').replace('.', ',').replace('X', '.')
    except ValueError:
        # Se não conseguir converter para float, retorna como está
        return f'{value}%'