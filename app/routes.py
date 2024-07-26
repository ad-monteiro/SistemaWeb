from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_user, current_user, logout_user, login_required
from . import db
from .models import User, Paciente, Consulta, Procedimento, Medicamento, Receita, ReceitaMedicamento
from .forms import LoginForm, CadastroPacienteForm, AgendamentoConsultaForm, RegistrationForm, ReceitaForm, EditarPacienteForm
from datetime import datetime

bp = Blueprint('main', __name__)

@bp.route('/')
@login_required
def index():
    return render_template('admin.html')

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember.data)
            return redirect(url_for('main.index'))
        else:
            flash('Invalid username or password.')
    return render_template('login.html', form=form)

@bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.login'))

@bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('main.login'))
    return render_template('register.html', form=form)

@bp.route('/cadastro_paciente', methods=['GET', 'POST'])
@login_required
def cadastro_paciente():
    form = CadastroPacienteForm()
    if form.validate_on_submit():
        try:
            paciente = Paciente(
                nome=form.nome.data,
                cpf_cnpj=form.cpf_cnpj.data,
                cep=form.cep.data,
                endereco=form.endereco.data,
                numero_residencia=form.numero_residencia.data,
                cidade=form.cidade.data,
                estado=form.estado.data,
                telefone=form.telefone.data,
                email=form.email.data,
                data_nascimento=form.data_nascimento.data,
                genero=form.genero.data,
                convenio=form.convenio.data,
                numero_convenio=form.numero_convenio.data
            )
            db.session.add(paciente)
            db.session.commit()
            idade = form.calcular_idade()
            flash(f'Paciente cadastrado com sucesso! Idade: {idade} anos')
            return redirect(url_for('main.index'))
        except Exception as e:
            flash(f'Erro ao cadastrar paciente: {e}')
            db.session.rollback()
    return render_template('cadastro_paciente.html', form=form)

@bp.route('/agendar_consulta', methods=['GET', 'POST'])
@login_required
def agendar_consulta():
    form = AgendamentoConsultaForm()
    if form.validate_on_submit():
        try:
            print("Formulário validado com sucesso")
            consulta = Consulta(
                paciente_id=form.paciente_id.data,
                especialidade=form.especialidade.data,
                data=form.data.data,
                hora=form.hora.data,
                procedimento_id=form.procedimento_id.data,
                status='agendado'
            )
            db.session.add(consulta)
            db.session.commit()
            print("Consulta agendada com sucesso")
            flash('Consulta agendada com sucesso!')
            return redirect(url_for('main.index'))
        except Exception as e:
            print(f"Erro ao agendar consulta: {e}")
            flash(f'Erro ao agendar consulta: {e}')
            db.session.rollback()
    else:
        print("Formulário não validado")
        # Exibir dados do formulário e erros de validação
        print("Dados do formulário:")
        print(f"Paciente ID: {form.paciente_id.data}")
        print(f"Especialidade: {form.especialidade.data}")
        print(f"Data: {form.data.data}")
        print(f"Hora: {form.hora.data}")
        print(f"Procedimento ID: {form.procedimento_id.data}")

        print("Erros de validação:")
        for field, errors in form.errors.items():
            for error in errors:
                print(f"Erro no campo {field}: {error}")

    return render_template('agendamento_consulta.html', form=form)

@bp.route('/consultas', methods=['GET'])
@login_required
def get_consultas():
    consultas = Consulta.query.filter(Consulta.status == 'agendado').all()
    eventos = []
    for consulta in consultas:
        eventos.append({
            'title': f"{consulta.especialidade} - {consulta.procedimento.nome}",
            'start': f"{consulta.data}T{consulta.hora}",
            'status': consulta.status
        })
    return jsonify(eventos)

@bp.route('/consultas_dia', methods=['GET'])
@login_required
def consultas_dia():
    date_str = request.args.get('date')
    date = datetime.strptime(date_str, '%Y-%m-%d').date()
    consultas = Consulta.query.filter_by(data=date).all()
    return render_template('consultas_dia.html', consultas=consultas, date=date)

@bp.route('/consulta/<int:id>/gerar_receita', methods=['GET', 'POST'])
@login_required
def gerar_receita(id):
    consulta = Consulta.query.get_or_404(id)
    form = ReceitaForm()
    
    if form.validate_on_submit():
        try:
            receita = Receita(
                consulta_id=consulta.id,
                instrucoes=form.instrucoes.data
            )
            db.session.add(receita)
            db.session.commit()
            
            for medicamento_entry in form.medicamentos.entries:
                medicamento_nome = medicamento_entry.medicamento_id.data
                quantidade = medicamento_entry.quantidade.data
                medicamento = Medicamento.query.filter_by(nome=medicamento_nome).first()
                if not medicamento:
                    flash(f'Medicamento {medicamento_nome} não encontrado')
                    continue
                receita_medicamento = ReceitaMedicamento(
                    receita_id=receita.id,
                    medicamento_id=medicamento.id,
                    quantidade=quantidade
                )
                db.session.add(receita_medicamento)
            db.session.commit()
            
            flash('Receita gerada com sucesso!')
            return redirect(url_for('main.gerar_receita', id=consulta.id))  # Redireciona para a mesma página
        except Exception as e:
            db.session.rollback()
            flash(f'Erro ao gerar receita: {e}')
    else:
        # Exibir dados do formulário e erros de validação
        print("Formulário não validado")
        print("Dados do formulário:")
        print(f"Instruções: {form.instrucoes.data}")
        for field in form.medicamentos.entries:
            print(f"Medicamento ID: {field.medicamento_id.data}, Quantidade: {field.quantidade.data}")

        print("Erros de validação:")
        for field, errors in form.errors.items():
            for error in errors:
                print(f"Erro no campo {field}: {error}")

    return render_template('gerar_receita.html', form=form, consulta=consulta)

@bp.route('/receita/<int:id>/imprimir', methods=['GET'])
@login_required
def imprimir_receita(id):
    receita = Receita.query.get_or_404(id)
    return render_template('imprimir_receita.html', receita=receita)

@bp.route('/pesquisar_paciente', methods=['GET'])
@login_required
def pesquisar_paciente():
    query = request.args.get('query')
    pacientes = Paciente.query.filter(Paciente.nome.like(f'%{query}%')).all()
    return jsonify([{'id': pac.id, 'nome': pac.nome} for pac in pacientes])

@bp.route('/pesquisar_procedimento', methods=['GET'])
@login_required
def pesquisar_procedimento():
    query = request.args.get('query')
    procedimentos = Procedimento.query.filter(Procedimento.nome.ilike(f'%{query}%')).all()
    results = [{'id': proc.id, 'nome': proc.nome} for proc in procedimentos]
    return jsonify(results)

@bp.route('/consulta/<int:id>/atualizar_status', methods=['POST'])
@login_required
def atualizar_status_consulta(id):
    consulta = Consulta.query.get_or_404(id)
    status = request.form.get('status')
    if status:
        consulta.status = status
        db.session.commit()
        flash('Status da consulta atualizado com sucesso!')
    else:
        flash('Nenhum status fornecido.')
    return redirect(url_for('main.consultas_dia', date=consulta.data.strftime('%Y-%m-%d')))

@bp.route('/pesquisar_medicamento', methods=['GET'])
@login_required
def pesquisar_medicamento():
    query = request.args.get('query')
    medicamentos = Medicamento.query.filter(Medicamento.nome.like(f'%{query}%')).all()
    return jsonify([{'id': med.id, 'nome': med.nome} for med in medicamentos])

@bp.route('/buscar_paciente', methods=['GET', 'POST'])
@login_required
def buscar_paciente():
    if request.method == 'POST':
        query = request.form.get('query')
        pacientes = Paciente.query.filter(Paciente.nome.like(f'%{query}%')).all()
        return render_template('buscar_paciente.html', pacientes=pacientes)
    return render_template('buscar_paciente.html')

@bp.route('/paciente/<int:id>', methods=['GET'])
@login_required
def visualizar_paciente(id):
    paciente = Paciente.query.get_or_404(id)
    consultas = Consulta.query.filter_by(paciente_id=id).all()
    return render_template('visualizar_paciente.html', paciente=paciente, consultas=consultas, datetime=datetime)


@bp.route('/pacientes')
@login_required
def listar_pacientes():
    pacientes = Paciente.query.all()
    return render_template('listar_pacientes.html', pacientes=pacientes)

@bp.route('/paciente/<int:id>/editar', methods=['GET', 'POST'])
@login_required
def editar_paciente(id):
    paciente = Paciente.query.get_or_404(id)
    form = EditarPacienteForm(obj=paciente)
    if form.validate_on_submit():
        form.populate_obj(paciente)
        db.session.commit()
        flash('Informações do paciente atualizadas com sucesso!')
        return redirect(url_for('main.listar_pacientes'))
    return render_template('editar_paciente.html', form=form, paciente=paciente)

