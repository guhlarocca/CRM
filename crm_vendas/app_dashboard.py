from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, session
from sqlalchemy import func, desc, inspect
from database.conexao import ConexaoBanco
from database.repositorio import LeadRepositorio, TimeRepositorio
from database.usuario_repositorio import UsuarioRepositorio
from database.modelos import Lead, Time, Base, Usuario
from datetime import datetime, timedelta
import os
import calendar
from werkzeug.utils import secure_filename
from sqlalchemy.orm import sessionmaker
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = os.urandom(24)
app.config['SESSION_TYPE'] = 'filesystem'
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=30)
app.config['SESSION_PERMANENT'] = True

# Configurações de segurança
app.config['SESSION_COOKIE_SECURE'] = False
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'

# Configuração para upload de arquivos
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static', 'profile_photos')
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def save_profile_photo(file):
    if file and file.filename:
        filename = secure_filename(file.filename)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_')
        unique_filename = timestamp + filename
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
        file.save(file_path)
        return unique_filename
    return 'default_profile.png'

# Conexão com o banco
conexao = ConexaoBanco()
engine = conexao.criar_engine()
Session = sessionmaker(bind=engine)
sessao = Session()

def get_sessao():
    global sessao
    try:
        if not sessao or not sessao.is_active:
            sessao = Session()
        return sessao
    except Exception as e:
        print(f"Erro ao obter sessão: {e}")
        sessao = Session()
        return sessao

def fechar_sessao():
    global sessao
    try:
        if sessao and sessao.is_active:
            sessao.close()
    except Exception as e:
        print(f"Erro ao fechar sessão: {e}")

@app.teardown_appcontext
def shutdown_session(exception=None):
    fechar_sessao()

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Por favor, faça login para acessar esta página.', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        senha = request.form.get('senha')
        
        if not email or not senha:
            flash('Por favor, preencha todos os campos.', 'danger')
            return redirect(url_for('login'))
        
        usuario_repo = UsuarioRepositorio(get_sessao())
        usuario = usuario_repo.buscar_por_email(email)
        
        if usuario and check_password_hash(usuario.senha, senha):
            session['user_id'] = usuario.id
            session['user_name'] = usuario.nome
            session['user_email'] = usuario.email
            session['is_admin'] = usuario.is_admin
            session['profile_photo'] = usuario.profile_photo if usuario.profile_photo else 'default_profile.png'
            session.permanent = True
            
            flash(f'Bem-vindo(a), {usuario.nome}!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Email ou senha incorretos.', 'danger')
            return redirect(url_for('login'))
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('Você foi desconectado com sucesso.', 'success')
    return redirect(url_for('login'))

@app.route('/')
@login_required
def index():
    try:
        lead_repo = LeadRepositorio(get_sessao())
        time_repo = TimeRepositorio(get_sessao())

        if not time_repo.verificar_membros_existentes():
            time_repo.criar_membro(
                nome="Vendedor Teste",
                email="teste@exemplo.com",
                telefone="(11) 99999-9999"
            )

        leads_recentes = lead_repo.listar_leads_recentes(5)
        membros_time = time_repo.listar_membros()
        
        # Somar leads e vendas de todos os membros do time
        total_leads = sum(membro.leads for membro in membros_time)
        total_vendas = sum(membro.vendas for membro in membros_time)
        
        leads_por_estagio = lead_repo.agrupar_leads_por_status()
        
        # Debug: Log detalhado de leads por estágio
        print("\n--- DASHBOARD - LEADS POR ESTÁGIO ---")
        for estagio, quantidade in leads_por_estagio.items():
            print(f"{estagio}: {quantidade}")
        print("--- FIM DO LOG ---\n")
        
        leads_nao_iniciados = leads_por_estagio.get('Não Iniciado', 0)
        leads_em_andamento = sum([
            leads_por_estagio.get('Enviado Email', 0),
            leads_por_estagio.get('Sem retorno Email', 0),
            leads_por_estagio.get('Retorno Agendado', 0),
            leads_por_estagio.get('Linkedin', 0),
            leads_por_estagio.get('Sem Retorno Linkedin', 0),
            leads_por_estagio.get('WhatsApp', 0),
            leads_por_estagio.get('Sem Retorno WhatsApp', 0)
        ])
        leads_fechados = leads_por_estagio.get('Email Despedida', 0)
        
        total_times = time_repo.contar_total_times()

        return render_template(
            'index.html', 
            total_leads=total_leads,
            total_vendas=total_vendas,
            leads_nao_iniciados=leads_nao_iniciados,
            leads_em_andamento=leads_em_andamento,
            leads_fechados=leads_fechados,
            total_times=total_times,
            leads_recentes=leads_recentes,
            membros_time=membros_time,
            leads_por_estagio=leads_por_estagio
        )
    except Exception as e:
        print(f"Erro na rota index: {e}")
        import traceback
        traceback.print_exc()
        flash('Erro ao carregar dados do dashboard.', 'danger')
        # Inicializa as variáveis com valores padrão em caso de erro
        return render_template('index.html', 
                             total_leads=0,
                             total_vendas=0,
                             leads_nao_iniciados=0,
                             leads_em_andamento=0,
                             leads_fechados=0,
                             total_times=0,
                             leads_recentes=[],
                             membros_time=[],
                             leads_por_estagio={})

@app.route('/kanban')
@login_required
def kanban():
    try:
        lead_repo = LeadRepositorio(get_sessao())
        leads = lead_repo.listar_leads()
        
        # Agrupar leads por estágio
        leads_por_estagio = {}
        for lead in leads:
            estagio = lead.estagio_atual or 'Não Iniciado'
            if estagio not in leads_por_estagio:
                leads_por_estagio[estagio] = []
            leads_por_estagio[estagio].append(lead)
        
        return render_template('kanban.html', leads_por_estagio=leads_por_estagio)
    except Exception as e:
        print(f"Erro na rota kanban: {e}")
        import traceback
        traceback.print_exc()
        flash('Erro ao carregar o kanban.', 'danger')
        return render_template('kanban.html', leads_por_estagio={})

@app.route('/leads')
@login_required
def leads():
    try:
        lead_repo = LeadRepositorio(get_sessao())
        leads = lead_repo.listar_leads()
        return render_template('leads.html', leads=leads)
    except Exception as e:
        print(f"Erro na rota leads: {e}")
        import traceback
        traceback.print_exc()
        flash('Erro ao carregar leads.', 'danger')
        return render_template('leads.html', leads=[])

@app.route('/leads/novo', methods=['GET', 'POST'])
@login_required
def novo_lead():
    if request.method == 'POST':
        try:
            dados_lead = {
                'nome': request.form.get('nome'),
                'email': request.form.get('email'),
                'telefone': request.form.get('telefone'),
                'empresa': request.form.get('empresa'),
                'cargo': request.form.get('cargo'),
                'estagio_atual': 'Não Iniciado',
                'vendedor_id': request.form.get('vendedor_id', type=int)
            }
            
            lead_repo = LeadRepositorio(get_sessao())
            lead_repo.criar_lead(dados_lead)
            
            flash('Lead criado com sucesso!', 'success')
            return redirect(url_for('leads'))
            
        except Exception as e:
            print(f"Erro ao criar lead: {e}")
            import traceback
            traceback.print_exc()
            flash('Erro ao criar lead.', 'danger')
            return redirect(url_for('leads'))
    
    # GET: Renderizar formulário
    time_repo = TimeRepositorio(get_sessao())
    vendedores = time_repo.listar_membros()
    return render_template('novo_lead.html', vendedores=vendedores)

@app.route('/leads/editar/<int:lead_id>', methods=['GET', 'POST'])
@login_required
def editar_lead(lead_id):
    lead_repo = LeadRepositorio(get_sessao())
    
    if request.method == 'POST':
        try:
            dados_lead = {
                'nome': request.form.get('nome'),
                'email': request.form.get('email'),
                'telefone': request.form.get('telefone'),
                'empresa': request.form.get('empresa'),
                'cargo': request.form.get('cargo'),
                'estagio_atual': request.form.get('estagio_atual'),
                'vendedor_id': request.form.get('vendedor_id', type=int)
            }
            
            lead_repo.editar_lead(lead_id, dados_lead)
            flash('Lead atualizado com sucesso!', 'success')
            return redirect(url_for('leads'))
            
        except Exception as e:
            print(f"Erro ao atualizar lead: {e}")
            import traceback
            traceback.print_exc()
            flash('Erro ao atualizar lead.', 'danger')
            return redirect(url_for('leads'))
    
    # GET: Buscar lead e renderizar formulário
    lead = lead_repo.buscar_lead_por_id(lead_id)
    if not lead:
        flash('Lead não encontrado.', 'danger')
        return redirect(url_for('leads'))
    
    time_repo = TimeRepositorio(get_sessao())
    vendedores = time_repo.listar_membros()
    return render_template('editar_lead.html', lead=lead, vendedores=vendedores)

@app.route('/leads/excluir/<int:lead_id>')
@login_required
def excluir_lead(lead_id):
    try:
        lead_repo = LeadRepositorio(get_sessao())
        if lead_repo.excluir_lead(lead_id):
            flash('Lead excluído com sucesso!', 'success')
        else:
            flash('Lead não encontrado.', 'danger')
    except Exception as e:
        print(f"Erro ao excluir lead: {e}")
        import traceback
        traceback.print_exc()
        flash('Erro ao excluir lead.', 'danger')
    
    return redirect(url_for('leads'))

@app.route('/leads/atualizar_estagio/<int:lead_id>', methods=['POST'])
@login_required
def atualizar_estagio_lead(lead_id):
    try:
        novo_estagio = request.form.get('estagio')
        if not novo_estagio:
            return jsonify({'success': False, 'message': 'Estágio não especificado'}), 400
        
        lead_repo = LeadRepositorio(get_sessao())
        lead_repo.atualizar_estagio(lead_id, novo_estagio)
        
        return jsonify({'success': True})
    except Exception as e:
        print(f"Erro ao atualizar estágio: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'message': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
