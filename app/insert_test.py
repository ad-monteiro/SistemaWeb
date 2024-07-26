from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

# Configuração da aplicação
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///C:/Users/martinez/Documents/Bancos/Site/site.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Inicialização do banco de dados
db = SQLAlchemy(app)

# Definição dos modelos
class Paciente(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(120), nullable=False)
    cpf_cnpj = db.Column(db.String(20), unique=True, nullable=False)
    cep = db.Column(db.String(20), nullable=False)
    endereco = db.Column(db.String(200), nullable=False)
    cidade = db.Column(db.String(100), nullable=False)
    estado = db.Column(db.String(2), nullable=False)
    telefone = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    consultas = db.relationship('Consulta', backref='paciente', lazy=True)

class Consulta(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    paciente_id = db.Column(db.Integer, db.ForeignKey('paciente.id'), nullable=False)
    especialidade = db.Column(db.String(64), nullable=False)
    data = db.Column(db.Date, nullable=False)
    hora = db.Column(db.Time, nullable=False)
    status = db.Column(db.String(20), nullable=False)
    procedimento_id = db.Column(db.Integer, db.ForeignKey('procedimento.id'), nullable=False)
    receitas = db.relationship('Receita', backref='consulta', lazy=True)

class Procedimento(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(120), nullable=False)
    consultas = db.relationship('Consulta', backref='procedimento', lazy=True)

class Receita(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    consulta_id = db.Column(db.Integer, db.ForeignKey('consulta.id'), nullable=False)
    instrucoes = db.Column(db.Text, nullable=False)
    medicamentos = db.relationship('ReceitaMedicamento', backref='receita', lazy=True)

class ReceitaMedicamento(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    receita_id = db.Column(db.Integer, db.ForeignKey('receita.id'), nullable=False)
    medicamento_id = db.Column(db.Integer, db.ForeignKey('medicamento.id'), nullable=False)
    quantidade = db.Column(db.Integer, nullable=False)

class Medicamento(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(120), nullable=False)

# Função principal para inserção
def insert_receita():
    with app.app_context():
        try:
            # Verifique se os objetos necessários existem
            paciente = Paciente.query.first()
            procedimento = Procedimento.query.first()

            if not paciente or not procedimento:
                print("Paciente ou Procedimento não encontrados.")
                return

            # Criar uma nova consulta
            nova_consulta = Consulta(
                paciente_id=paciente.id,
                especialidade="Cardiologia",
                data=datetime.strptime("2023-07-22", '%Y-%m-%d').date(),
                hora=datetime.strptime("14:00", '%H:%M').time(),
                status="agendado",
                procedimento_id=procedimento.id
            )

            db.session.add(nova_consulta)
            db.session.commit()
            print("Consulta agendada com sucesso!")

            # Criar uma nova receita
            nova_receita = Receita(
                consulta_id=nova_consulta.id,
                instrucoes="Tomar 1 comprimido após as refeições."
            )

            db.session.add(nova_receita)
            db.session.commit()
            print("Receita criada com sucesso!")

            # Criar medicamentos
            medicamento1 = Medicamento(nome='Medicamento A')
            medicamento2 = Medicamento(nome='Medicamento B')
            db.session.add(medicamento1)
            db.session.add(medicamento2)
            db.session.commit()
            print(f"Medicamentos criados: {medicamento1}, {medicamento2}")

            # Associar medicamentos à receita
            receita_medicamento1 = ReceitaMedicamento(
                receita_id=nova_receita.id,
                medicamento_id=medicamento1.id,
                quantidade=2
            )
            receita_medicamento2 = ReceitaMedicamento(
                receita_id=nova_receita.id,
                medicamento_id=medicamento2.id,
                quantidade=1
            )
            db.session.add(receita_medicamento1)
            db.session.add(receita_medicamento2)
            db.session.commit()
            print(f"ReceitaMedicamentos criados: {receita_medicamento1}, {receita_medicamento2}")

            print("Todos os dados foram inseridos com sucesso!")
        except Exception as e:
            db.session.rollback()
            print(f"Erro ao inserir dados: {e}")

if __name__ == "__main__":
    insert_receita()
