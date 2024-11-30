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
    """Rota principal do dashboard"""
    # Inicializar variáveis padrão
    total_leads = 0
    total_vendas = 0
    leads_nao_iniciados = 0
    leads_em_andamento = 0
    leads_fechados = 0
    total_times = 0
    leads_recentes = []
    membros_time = []
    leads_por_estagio = {}

    try:
        # Inicializar repositórios
        lead_repo = LeadRepositorio(get_sessao())
        time_repo = TimeRepositorio(get_sessao())

        # Garantir que haja pelo menos um membro no time
        if not time_repo.verificar_membros_existentes():
            print("Criando membro padrão...")
            novo_membro = time_repo.criar_membro(
                nome="Vendedor Padrão",
                email="vendedor_padrao@empresa.com",
                telefone="(11) 99999-9999"
            )
            if not novo_membro:
                print("ERRO: Falha ao criar membro padrão")

        # Buscar dados para o dashboard
        total_leads = lead_repo.contar_total_leads()
        total_vendas = lead_repo.contar_vendas()
        
        # Buscar leads por estágio
        leads_por_estagio = lead_repo.agrupar_leads_por_status()
        
        # Calcular leads por estágio
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
        
        # Buscar membros do time
        membros_time = time_repo.listar_membros()
        
        # Contar times
        total_times = time_repo.contar_total_times()
        
        # Buscar leads recentes
        leads_recentes = lead_repo.listar_leads_recentes(5)
        
        # Atualizar estatísticas de membros
        for membro in membros_time:
            membro['leads'] = lead_repo.contar_leads_por_vendedor(membro['id'])
            membro['vendas'] = lead_repo.contar_vendas_por_vendedor(membro['id'])
        
        # Log de depuração
        print("\n--- DADOS DO DASHBOARD ---")
        print(f"Total de Leads: {total_leads}")
        print(f"Total de Vendas: {total_vendas}")
        print(f"Leads não iniciados: {leads_nao_iniciados}")
        print(f"Leads em andamento: {leads_em_andamento}")
        print(f"Leads fechados: {leads_fechados}")
        print(f"Total de Times: {total_times}")
        print(f"Membros do Time: {len(membros_time)}")
        
        # Renderizar template
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
        # Log de erro detalhado
        print("\n--- ERRO CRÍTICO NO DASHBOARD ---")
        print(f"Erro: {e}")
        import traceback
        traceback.print_exc()
        
        # Salvar log de erro
        try:
            with open('dashboard_error_log.txt', 'w') as log_file:
                log_file.write(f"Erro no Dashboard: {e}\n\n")
                log_file.write("Rastreamento de pilha completo:\n")
                log_file.write(traceback.format_exc())
        except Exception as log_error:
            print(f"Erro ao salvar log: {log_error}")
        
        # Renderizar template com dados padrão
        flash('Erro ao carregar dados do dashboard. Verifique o log de erros.', 'danger')
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

@app.route('/time')
@login_required
def time():
    time_repo = TimeRepositorio(get_sessao())
    membros = time_repo.listar_membros()
    return render_template('time.html', membros=membros)

@app.route('/time/criar', methods=['POST'])
@login_required
def criar_membro():
    try:
        nome = request.form.get('nome')
        email = request.form.get('email')
        telefone = request.form.get('telefone')
        profile_photo = request.files.get('profile_photo')

        if not nome or not email:
            flash('Nome e email são obrigatórios.', 'danger')
            return redirect(url_for('time'))

        photo_filename = save_profile_photo(profile_photo)

        time_repo = TimeRepositorio(get_sessao())
        time_repo.criar_membro(
            nome=nome,
            email=email,
            telefone=telefone,
            profile_photo=photo_filename
        )

        flash('Membro adicionado com sucesso!', 'success')
        return redirect(url_for('time'))
    except Exception as e:
        flash(f'Erro ao adicionar membro: {str(e)}', 'danger')
        return redirect(url_for('time'))

@app.route('/time/editar/<int:id>', methods=['GET', 'POST'])
@login_required
def editar_membro(id):
    try:
        time_repo = TimeRepositorio(get_sessao())
        
        # Log de depuração
        print(f"\n--- INÍCIO EDITAR MEMBRO ---")
        print(f"ID do Membro: {id}")
        
        if request.method == 'POST':
            # Capturar dados do formulário
            nome = request.form.get('nome')
            email = request.form.get('email')
            telefone = request.form.get('telefone')
            
            # Log de dados recebidos
            print("Dados recebidos:")
            print(f"Nome: {nome}")
            print(f"Email: {email}")
            print(f"Telefone: {telefone}")
            
            # Buscar membro atual para manter a foto existente
            membro_atual = time_repo.buscar_membro_por_id(id)
            
            # Processar foto de perfil
            profile_photo = membro_atual.profile_photo if membro_atual else 'default_profile.png'
            if 'profile_photo' in request.files:
                file = request.files['profile_photo']
                if file and file.filename:
                    profile_photo = save_profile_photo(file)
            
            # Log da foto
            print(f"Foto de perfil a ser salva: {profile_photo}")
            
            # Atualizar membro
            resultado = time_repo.atualizar_membro(id, nome, email, telefone, profile_photo)
            
            # Log do resultado
            if resultado:
                print("Membro atualizado com sucesso!")
                flash('Membro atualizado com sucesso!', 'success')
            else:
                print("ERRO: Falha ao atualizar membro")
                flash('Erro ao atualizar membro.', 'danger')
            
            return redirect(url_for('time'))
        
        # Para método GET, buscar dados do membro
        membro = time_repo.buscar_membro_por_id(id)
        
        # Log de dados do membro
        print("\nDados do Membro:")
        print(f"Nome: {membro.nome if membro else 'Não encontrado'}")
        print(f"Email: {membro.email if membro else 'Não encontrado'}")
        print(f"Telefone: {membro.telefone if membro else 'Não encontrado'}")
        print(f"Foto de Perfil: {membro.profile_photo if membro else 'Não encontrado'}")
        
        if not membro:
            flash('Membro não encontrado.', 'danger')
            return redirect(url_for('time'))
        
        return render_template('editar_membro.html', membro=membro)
    
    except Exception as e:
        print(f"\n--- ERRO CRÍTICO em editar_membro ---")
        print(f"Erro: {e}")
        import traceback
        traceback.print_exc()
        
        flash('Erro interno ao processar a solicitação.', 'danger')
        return redirect(url_for('time'))

@app.route('/time/excluir/<int:id>', methods=['POST'])
@login_required
def excluir_membro(id):
    try:
        time_repo = TimeRepositorio(get_sessao())
        
        # Tentar excluir o membro
        if time_repo.excluir_membro(id):
            return jsonify({'success': True, 'message': 'Membro excluído com sucesso!'})
        else:
            return jsonify({'success': False, 'message': 'Não foi possível excluir o membro. Verifique se existem leads associados.'})
    
    except Exception as e:
        print(f"\n--- ERRO CRÍTICO em excluir_membro ---")
        print(f"Erro: {e}")
        import traceback
        traceback.print_exc()
        
        return jsonify({'success': False, 'message': f'Erro ao excluir membro: {str(e)}'})

@app.route('/api/membros/<int:id>')
@login_required
def get_membro(id):
    try:
        time_repo = TimeRepositorio(get_sessao())
        membro = time_repo.buscar_membro_por_id(id)
        if membro:
            return jsonify({
                'id': membro.id,
                'nome': membro.nome,
                'email': membro.email,
                'telefone': membro.telefone,
                'profile_photo': membro.profile_photo
            })
        return jsonify({'error': 'Membro não encontrado'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/kanban')
@login_required
def kanban():
    try:
        lead_repo = LeadRepositorio(get_sessao())
        leads_por_estagio = {}
        
        estagios = [
            'Não Iniciado', 'Enviado Email', 'Sem retorno Email', 
            'Retorno Agendado', 'Linkedin', 'Sem Retorno Linkedin',
            'WhatsApp', 'Sem Retorno WhatsApp', 'Email Despedida'
        ]
        
        for estagio in estagios:
            leads = lead_repo.buscar_por_estagio(estagio)
            leads_por_estagio[estagio] = leads
        
        return render_template('kanban.html', leads_por_estagio=leads_por_estagio, stages=estagios)
    except Exception as e:
        print(f"Erro na rota kanban: {e}")
        flash('Erro ao carregar o quadro Kanban.', 'danger')
        return redirect(url_for('index'))

@app.route('/api/leads/<int:lead_id>/stage', methods=['PUT'])
@login_required
def atualizar_estagio_lead(lead_id):
    try:
        data = request.get_json()
        novo_estagio = data.get('stage')
        
        if not novo_estagio:
            return jsonify({'success': False, 'message': 'Novo estágio não fornecido'}), 400
        
        lead_repo = LeadRepositorio(get_sessao())
        lead_repo.atualizar_estagio(lead_id, novo_estagio)
        
        return jsonify({'success': True})
    except Exception as e:
        print(f"Erro ao atualizar estágio do lead: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/novo-lead', methods=['GET', 'POST'])
@login_required
def novo_lead():
    if request.method == 'POST':
        try:
            nome = request.form.get('nome')
            empresa = request.form.get('empresa')
            cargo = request.form.get('cargo')
            email = request.form.get('email')
            telefone = request.form.get('telefone')
            linkedin = request.form.get('linkedin')
            vendedor_id = request.form.get('vendedor_id')
            
            if not nome or not empresa or not vendedor_id:
                flash('Por favor, preencha todos os campos obrigatórios.', 'danger')
                return redirect(url_for('novo_lead'))
            
            lead_repo = LeadRepositorio(get_sessao())
            lead_repo.criar_lead(
                nome=nome,
                empresa=empresa,
                cargo=cargo,
                email=email,
                telefone=telefone,
                linkedin=linkedin,
                vendedor_id=vendedor_id
            )
            
            flash('Lead criado com sucesso!', 'success')
            return redirect(url_for('kanban'))
            
        except Exception as e:
            print(f"Erro ao criar lead: {e}")
            flash('Erro ao criar lead.', 'danger')
            return redirect(url_for('novo_lead'))
    
    time_repo = TimeRepositorio(get_sessao())
    vendedores = time_repo.listar_membros()
    return render_template('novo_lead.html', vendedores=vendedores)

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
def criar_lead():
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
            # Processar venda_fechada como booleano
            venda_fechada = 'venda_fechada' in request.form
            
            dados_lead = {
                'nome': request.form.get('nome'),
                'email': request.form.get('email'),
                'telefone': request.form.get('telefone'),
                'empresa': request.form.get('empresa'),
                'cargo': request.form.get('cargo'),
                'estagio_atual': request.form.get('estagio_atual'),
                'vendedor_id': request.form.get('vendedor_id', type=int),
                'venda_fechada': venda_fechada,
                'observacoes': request.form.get('observacoes', ''),
                'data_venda': request.form.get('data_venda') if venda_fechada else None
            }
            
            # Log de depuração
            print("\n--- DADOS RECEBIDOS PARA EDIÇÃO ---")
            for key, value in dados_lead.items():
                print(f"{key}: {value}")
            
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

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
