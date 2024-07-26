from . import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.username}>'

class Paciente(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(120), nullable=False)
    cpf_cnpj = db.Column(db.String(20), unique=True, nullable=False)
    cep = db.Column(db.String(20), nullable=False)
    endereco = db.Column(db.String(200), nullable=False)
    numero_residencia = db.Column(db.String(20), nullable=True)
    cidade = db.Column(db.String(100), nullable=False)
    estado = db.Column(db.String(2), nullable=False)
    telefone = db.Column(db.String(20), nullable=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    data_nascimento = db.Column(db.Date, nullable=True)
    genero = db.Column(db.String(1), nullable=True)
    convenio = db.Column(db.String(120), nullable=True)
    numero_convenio = db.Column(db.String(120), nullable=True)
    consultas = db.relationship('Consulta', backref='paciente', lazy=True)


    def __repr__(self):
        return f'<Paciente {self.nome}>'

class Consulta(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    paciente_id = db.Column(db.Integer, db.ForeignKey('paciente.id'), nullable=False)
    especialidade = db.Column(db.String(64), nullable=False)
    data = db.Column(db.Date, nullable=False)
    hora = db.Column(db.Time, nullable=False)
    status = db.Column(db.String(20), nullable=False)
    procedimento_id = db.Column(db.Integer, db.ForeignKey('procedimento.id'), nullable=False)
    receitas = db.relationship('Receita', backref='consulta', lazy=True)

    def __repr__(self):
        return f'<Consulta {self.especialidade} - {self.data} {self.hora}>'

class Procedimento(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(120), nullable=False)
    consultas = db.relationship('Consulta', backref='procedimento', lazy=True)

    def __repr__(self):
        return f'<Procedimento {self.nome}>'

class Medicamento(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(120), nullable=False)
    receitas_medicamento = db.relationship('ReceitaMedicamento', backref='medicamento', lazy=True)

    def __repr__(self):
        return f'<Medicamento {self.nome}>'

class Receita(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    consulta_id = db.Column(db.Integer, db.ForeignKey('consulta.id'), nullable=False)
    instrucoes = db.Column(db.Text, nullable=False)
    medicamentos = db.relationship('ReceitaMedicamento', backref='receita', lazy=True)

    def __repr__(self):
        return f'<Receita {self.consulta_id} - {self.instrucoes}>'

class ReceitaMedicamento(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    receita_id = db.Column(db.Integer, db.ForeignKey('receita.id'), nullable=False)
    medicamento_id = db.Column(db.Integer, db.ForeignKey('medicamento.id'), nullable=False)
    quantidade = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return f'<ReceitaMedicamento {self.receita_id} - {self.medicamento_id} - {self.quantidade}>'
