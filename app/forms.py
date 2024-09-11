from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField, IntegerField, FloatField, DateField, EmailField,  HiddenField, SelectField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from app.models import Usuarios
from flask_login import current_user
from wtforms_sqlalchemy.fields import QuerySelectField
from app.models import Acoes

CHOICE_TiposMovimentacao = [('1', 'Compra'), ('2', 'Venda')]

# Usuário
class FormCriarConta(FlaskForm):
    username = StringField('Nome', validators=[DataRequired()])
    email = StringField('E-mail', validators=[DataRequired(), Email()])
    senha = PasswordField('Senha', validators=[DataRequired(), Length(6, 20)])
    confirmacao_senha = PasswordField('Confirmação da Senha', validators=[DataRequired(), EqualTo('senha')])
    botao_submit_criarconta = SubmitField('Criar Conta')

    def validate_email(self, email):
        usuario = Usuarios.query.filter_by(email=email.data).first()
        if usuario:
            raise ValidationError('E-mail já cadastrado. Cadastre-se com outro e-mail ou faça login para continuar')

class FormLogin(FlaskForm):
    email = EmailField('E-mail', validators=[DataRequired(), Email()])
    senha = PasswordField('Senha', validators=[DataRequired(), Length(6, 20)])
    lembrar_dados = BooleanField('Lembrar')
    botao_submit_login = SubmitField('Entrar')

class FormEditarPerfil(FlaskForm):
    username = StringField('Nome', validators=[DataRequired()])
    email = EmailField('E-mail', validators=[DataRequired(), Email()])
    foto_perfil = FileField('Foto', validators=[FileAllowed(['jpg', 'png'])])

    botao_submit_editarperfil = SubmitField('Salvar')

    def validate_email(self, email):
        if current_user.email != email.data:
            usuario = Usuarios.query.filter_by(email=email.data).first()
            if usuario:
                raise ValidationError('Já existe um usuário com esse e-mail. Cadastre outro e-mail')

# Ações 
class FormAcoes(FlaskForm):
    ticker = StringField('Ticker', validators=[DataRequired(), Length(2, 140)])
    botao_submit_acao = SubmitField('Salvar')

class FormMovimentacoes(FlaskForm):
    id_acao = QuerySelectField('Ação', query_factory=lambda: Acoes.query.order_by(Acoes.ticker.asc()).all(), allow_blank=False, get_label='ticker', validators=[DataRequired()])
    data = DateField('Data', validators=[DataRequired()])
    cd_tipo = SelectField('Tipo',choices=CHOICE_TiposMovimentacao, validators=[DataRequired()])
    quantidade = IntegerField('Quantidade', validators=[DataRequired()])
    valor_unitario = FloatField('Valor Unitário', validators=[DataRequired()])
    total_taxas = FloatField('Demais Taxas', validators=[DataRequired()])

    botao_submit_movimentacoes = SubmitField('Salvar')

class FormApuracao(FlaskForm):
    data = StringField('Período', validators=[DataRequired()])
    botao_submit_apuracao = SubmitField('Gerar')


class FormBusca(FlaskForm):
    data = StringField('Ticker da Ação', validators=[DataRequired()])
    botao_submit_busca = SubmitField('Buscar Cotação')
