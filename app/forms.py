from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, HiddenField, DateField, TimeField, FieldList, FormField, SelectField
from wtforms.validators import DataRequired, Length, EqualTo, ValidationError, Email, Optional
from .models import User, Procedimento
from datetime import date

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('That username is taken. Please choose a different one.')

class CadastroPacienteForm(FlaskForm):
    nome = StringField('Nome', validators=[DataRequired()])
    cpf_cnpj = StringField('CPF/CNPJ', validators=[DataRequired(), Length(min=11, max=14)])
    cep = StringField('CEP', validators=[DataRequired()])
    endereco = StringField('Endereço', validators=[DataRequired()])
    numero_residencia = StringField('Número da Residência', validators=[DataRequired()])
    cidade = StringField('Cidade', validators=[DataRequired()])
    estado = StringField('Estado', validators=[DataRequired()])
    telefone = StringField('Telefone')
    email = StringField('Email', validators=[Email()])
    data_nascimento = DateField('Data de Nascimento', format='%Y-%m-%d', validators=[DataRequired()])
    genero = SelectField('Gênero', choices=[('M', 'Masculino'), ('F', 'Feminino'), ('O', 'Outro')])
    convenio = StringField('Convênio')
    numero_convenio = StringField('Número do Convênio')
    submit = SubmitField('Cadastrar')

    def calcular_idade(self):
        today = date.today()
        return today.year - self.data_nascimento.data.year - (
            (today.month, today.day) < (self.data_nascimento.data.month, self.data_nascimento.data.day)
        )

class AgendamentoConsultaForm(FlaskForm):
    paciente_id = HiddenField('Paciente ID', validators=[DataRequired()])
    especialidade = StringField('Especialidade', validators=[DataRequired()])
    data = DateField('Data', format='%Y-%m-%d', validators=[DataRequired()], render_kw={"placeholder": "YYYY-MM-DD"})
    hora = TimeField('Hora', format='%H:%M', validators=[DataRequired()], render_kw={"placeholder": "HH:MM"})
    procedimento_id = HiddenField('Procedimento ID', validators=[DataRequired()])
    submit = SubmitField('Agendar Consulta')

class MedicamentoForm(FlaskForm):
    csrf_token = HiddenField()  # Adiciona o campo de token CSRF
    medicamento_id = StringField('Medicamento ID', validators=[DataRequired()])
    quantidade = StringField('Quantidade', validators=[DataRequired()])

class ReceitaForm(FlaskForm):
    instrucoes = StringField('Instruções', validators=[DataRequired()])
    medicamentos = FieldList(FormField(MedicamentoForm), min_entries=1, validators=[DataRequired()])
    submit = SubmitField('Gerar Receita')


class EditarPacienteForm(FlaskForm):
    nome = StringField('Nome', validators=[DataRequired()])
    cpf_cnpj = StringField('CPF/CNPJ', validators=[DataRequired(), Length(min=11, max=14)])
    cep = StringField('CEP', validators=[DataRequired()])
    endereco = StringField('Endereço', validators=[DataRequired()])
    numero_residencia = StringField('Número', validators=[DataRequired()])
    cidade = StringField('Cidade', validators=[DataRequired()])
    estado = StringField('Estado', validators=[DataRequired()])
    telefone = StringField('Telefone')
    email = StringField('Email')
    data_nascimento = DateField('Data de Nascimento', format='%Y-%m-%d', validators=[Optional()])
    genero = SelectField('Gênero', choices=[('M', 'Masculino'), ('F', 'Feminino'), ('O', 'Outro')])
    convenio = StringField('Convênio')
    numero_convenio = StringField('Número do Convênio')
    submit = SubmitField('Atualizar')