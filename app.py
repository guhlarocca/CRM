from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, session
from sqlalchemy import func, desc, inspect, text
from database.conexao_supabase import ConexaoSupabase
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
from dotenv import load_dotenv
import psycopg2

# Carregar variáveis de ambiente
load_dotenv()

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

# Configurar logging
import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s: %(message)s')
app.logger.setLevel(logging.INFO)

def save_profile_photo(file):
    if file and file.filename:
        filename = secure_filename(file.filename)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_')
        unique_filename = timestamp + filename
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
        file.save(file_path)
        return unique_filename
    return 'default_profile.png'

# Conexão com o Supabase
conexao = ConexaoSupabase()

def get_conn():
    return conexao.get_connection()

def get_cur(conn):
    return conn.cursor()

def fechar_sessao(cur, conn):
    try:
        if cur:
            cur.close()
        if conn:
            conn.close()
    except Exception as e:
        app.logger.error(f"Erro ao fechar sessão: {e}")

@app.teardown_appcontext
def shutdown_session(exception=None):
    fechar_sessao(cur=None, conn=None)

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
        
        try:
            usuario_repo = UsuarioRepositorio()
            if usuario_repo.verificar_senha(email, senha):
                usuario = usuario_repo.buscar_por_email(email)
                # Definir informações na sessão
                session['user_id'] = usuario['id']
                session['user_name'] = usuario['nome']
                session['user_email'] = usuario['email']
                session['is_admin'] = usuario.get('is_admin', False)
                session['profile_photo'] = usuario.get('profile_photo', 'default_profile.png')

                logging.info(f"Login realizado: {usuario['nome']}")
                flash('Login realizado com sucesso!', 'success')
                return redirect(url_for('index'))
            else:
                flash('Email ou senha incorretos.', 'danger')
                return redirect(url_for('login'))
                
        except Exception as e:
            logging.error(f"Erro no login: {e}")
            flash('Ocorreu um erro ao fazer login.', 'danger')
            return redirect(url_for('login'))
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('Você foi desconectado com sucesso.', 'success')
    return redirect(url_for('login'))

@app.route('/')
def index():
    try:
        if 'user_id' not in session:
            return redirect(url_for('login'))

        time_repo = TimeRepositorio()
        lead_repo = LeadRepositorio()
        usuario_repo = UsuarioRepositorio()
        
        # Buscar dados do usuário
        usuario = usuario_repo.buscar_por_id(session['user_id'])
        if not usuario:
            return redirect(url_for('login'))
            
        # Buscar membros e leads
        membros = time_repo.listar_membros()
        leads = lead_repo.listar_leads()
        
        # Log para debug
        logging.info(f"Número de membros: {len(membros)}")
        logging.info(f"Número de leads: {len(leads)}")
        
        # Adicionar contagem de leads por vendedor
        for membro in membros:
            membro['leads'] = lead_repo.contar_leads_por_vendedor(membro['id'])
        
        # Buscar contagens por região e estado
        leads_por_regiao = lead_repo.contar_leads_por_regiao()
        leads_por_estado = lead_repo.contar_leads_por_estado()
        leads_por_estagio = lead_repo.contar_leads_por_estagio()
        
        # Buscar leads recentes
        leads_recentes = lead_repo.listar_leads_recentes(limite=10)
        
        # Se não houver membros, criar um membro padrão
        if not membros:
            time_repo.criar_membro(
                nome="Vendedor Padrão",
                email="vendedor_padrao@empresa.com",
                telefone="123456789"
            )
            # Recarregar membros após criação
            membros = time_repo.listar_membros()

        return render_template('index.html',
                            usuario=usuario,
                            membros=membros,
                            membros_time=membros,  # alias para manter compatibilidade
                            leads=leads,
                            leads_recentes=leads_recentes,
                            leads_por_regiao=leads_por_regiao,
                            leads_por_estado=leads_por_estado,
                            leads_por_estagio=leads_por_estagio,
                            total_times=len(membros) if membros else 0,
                            total_leads=len(leads),
                            total_vendas=sum(membro['vendas'] for membro in membros))
                            
    except Exception as e:
        logging.error(f"Erro na rota principal: {e}", exc_info=True)
        flash('Ocorreu um erro ao carregar a página', 'error')
        return redirect(url_for('login'))

@app.route('/time')
@login_required
def time():
    time_repo = TimeRepositorio()
    membros = time_repo.listar_membros()
    return render_template('time.html', membros=membros)

@app.route('/time/criar', methods=['POST'])
@login_required
def criar_membro():
    try:
        nome = request.form.get('nome')
        email = request.form.get('email')
        telefone = request.form.get('telefone')
        
        # Validar campos obrigatórios
        if not nome or not email or not telefone:
            flash('Por favor, preencha todos os campos obrigatórios.', 'danger')
            return redirect(url_for('time'))

        # Processar foto do perfil
        profile_photo = 'default_profile.png'
        if 'profile_photo' in request.files:
            file = request.files['profile_photo']
            if file and file.filename:
                profile_photo = save_profile_photo(file)

        # Criar membro
        time_repo = TimeRepositorio()
        novo_id = time_repo.criar_membro(nome, email, telefone, profile_photo)
        
        if novo_id:
            flash('Membro criado com sucesso!', 'success')
        else:
            flash('Email já cadastrado.', 'danger')
            
    except Exception as e:
        app.logger.error(f"Erro ao criar membro: {e}")
        flash('Erro ao criar membro. Por favor, tente novamente.', 'danger')
    
    return redirect(url_for('time'))

@app.route('/time/editar/<int:id>', methods=['GET', 'POST'])
@login_required
def editar_membro(id):
    try:
        time_repo = TimeRepositorio()
        
        # Log de depuração
        app.logger.info(f"\n--- INÍCIO EDITAR MEMBRO ---")
        app.logger.info(f"ID do Membro: {id}")
        
        if request.method == 'POST':
            # Capturar dados do formulário
            nome = request.form.get('nome')
            email = request.form.get('email')
            telefone = request.form.get('telefone')
            
            # Log de dados recebidos
            app.logger.info("Dados recebidos:")
            app.logger.info(f"Nome: {nome}")
            app.logger.info(f"Email: {email}")
            app.logger.info(f"Telefone: {telefone}")
            
            # Buscar membro atual para manter a foto existente
            membro_atual = time_repo.buscar_membro_por_id(id)
            
            # Processar foto de perfil
            profile_photo = membro_atual.profile_photo if membro_atual else 'default_profile.png'
            if 'profile_photo' in request.files:
                file = request.files['profile_photo']
                if file and file.filename:
                    profile_photo = save_profile_photo(file)
            
            # Log da foto
            app.logger.info(f"Foto de perfil a ser salva: {profile_photo}")
            
            # Atualizar membro
            resultado = time_repo.atualizar_membro(id, nome, email, telefone, profile_photo)
            
            # Log do resultado
            if resultado:
                app.logger.info("Membro atualizado com sucesso!")
                flash('Membro atualizado com sucesso!', 'success')
            else:
                app.logger.error("ERRO: Falha ao atualizar membro")
                flash('Erro ao atualizar membro.', 'danger')
            
            return redirect(url_for('time'))
        
        # Para método GET, buscar dados do membro
        membro = time_repo.buscar_membro_por_id(id)
        
        # Log de dados do membro
        app.logger.info("\nDados do Membro:")
        app.logger.info(f"Nome: {membro.nome if membro else 'Não encontrado'}")
        app.logger.info(f"Email: {membro.email if membro else 'Não encontrado'}")
        app.logger.info(f"Telefone: {membro.telefone if membro else 'Não encontrado'}")
        app.logger.info(f"Foto de Perfil: {membro.profile_photo if membro else 'Não encontrado'}")
        
        if not membro:
            flash('Membro não encontrado.', 'danger')
            return redirect(url_for('time'))
        
        return render_template('editar_membro.html', membro=membro)
    
    except Exception as e:
        app.logger.error(f"\n--- ERRO CRÍTICO em editar_membro ---")
        app.logger.error(f"Erro: {e}")
        import traceback
        traceback.print_exc()
        
        flash('Erro interno ao processar a solicitação.', 'danger')
        return redirect(url_for('time'))

@app.route('/time/excluir/<int:id>', methods=['POST'])
@login_required
def excluir_membro(id):
    try:
        time_repo = TimeRepositorio()
        
        # Tentar excluir o membro
        if time_repo.excluir_membro(id):
            return jsonify({'success': True, 'message': 'Membro excluído com sucesso!'})
        else:
            return jsonify({'success': False, 'message': 'Não foi possível excluir o membro. Verifique se existem leads associados.'})
    
    except Exception as e:
        app.logger.error(f"\n--- ERRO CRÍTICO em excluir_membro ---")
        app.logger.error(f"Erro: {e}")
        import traceback
        traceback.print_exc()
        
        return jsonify({'success': False, 'message': f'Erro ao excluir membro: {str(e)}'})

@app.route('/api/membros/<int:id>')
@login_required
def get_membro(id):
    try:
        time_repo = TimeRepositorio()
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
        lead_repo = LeadRepositorio()
        leads_por_estagio = {}
        
        estagios = [
            'Não Iniciado', 'Enviado Email', 'Sem retorno Email', 
            'Retorno Agendado', 'Linkedin', 'Sem Retorno Linkedin',
            'WhatsApp', 'Sem Retorno WhatsApp', 'Email Despedida'
        ]
        
        for estagio in estagios:
            leads = lead_repo.buscar_por_estagio(estagio)
            leads_por_estagio[estagio] = leads
        
        # Obter dados de leads por estado
        leads_por_estado = lead_repo.contar_leads_por_estado()
        
        # Agrupar estados por região
        regioes = {
            'Norte': ['AC', 'AP', 'AM', 'PA', 'RO', 'RR', 'TO'],
            'Nordeste': ['AL', 'BA', 'CE', 'MA', 'PB', 'PE', 'PI', 'RN', 'SE'],
            'Centro-Oeste': ['DF', 'GO', 'MT', 'MS'],
            'Sudeste': ['ES', 'MG', 'RJ', 'SP'],
            'Sul': ['PR', 'RS', 'SC']
        }
        
        leads_por_regiao = {regiao: 0 for regiao in regioes.keys()}
        for estado, quantidade in leads_por_estado.items():
            for regiao, estados in regioes.items():
                if estado in estados:
                    leads_por_regiao[regiao] += quantidade
                    break
        
        return render_template('kanban.html', 
                             leads_por_estagio=leads_por_estagio, 
                             stages=estagios,
                             leads_por_regiao=leads_por_regiao)
    except Exception as e:
        app.logger.error(f"Erro na rota kanban: {e}")
        flash('Erro ao carregar o quadro Kanban.', 'danger')
        return redirect(url_for('index'))

@app.route('/leads/<int:lead_id>/update_stage', methods=['POST'])
@login_required
def atualizar_estagio_lead(lead_id):
    try:
        novo_estagio = request.json.get('estagio')
        if not novo_estagio:
            return jsonify({'success': False, 'error': 'Estágio não informado'}), 400

        lead_repo = LeadRepositorio()
        if lead_repo.atualizar_estagio(lead_id, novo_estagio):
            return jsonify({'success': True})
        else:
            return jsonify({'success': False, 'error': 'Lead não encontrado'}), 404
            
    except Exception as e:
        app.logger.error(f"Erro ao atualizar estágio do lead: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/novo-lead', methods=['GET', 'POST'])
@login_required
def novo_lead():
    if request.method == 'POST':
        try:
            # Conversão segura do vendedor_id
            try:
                vendedor_id = int(request.form.get('vendedor_id', 0))
            except (ValueError, TypeError):
                vendedor_id = None
                app.logger.warning(f"ID do vendedor inválido: {request.form.get('vendedor_id')}")

            # Converter venda_fechada para booleano
            venda_fechada = request.form.get('venda_fechada') == 'on'
            app.logger.info(f"Venda fechada: {venda_fechada}")

            dados_lead = {
                'nome': request.form.get('nome'),
                'email': request.form.get('email'),
                'telefone': request.form.get('telefone'),
                'empresa': request.form.get('empresa'),
                'cargo': request.form.get('cargo'),
                'estagio_atual': request.form.get('estagio_atual', 'Novo'),
                'vendedor_id': vendedor_id,
                'venda_fechada': venda_fechada,
                
                # Campos adicionais
                'email_comercial': request.form.get('email_comercial'),
                'email_comercial_02': request.form.get('email_comercial_02'),
                'email_comercial_03': request.form.get('email_comercial_03'),
                'email_financeiro': request.form.get('email_financeiro'),
                'telefone_comercial': request.form.get('telefone_comercial'),
                'cidade': request.form.get('cidade'),
                'estado': request.form.get('estado')
            }
            
            # Log dos dados recebidos
            app.logger.info(f"Dados do lead recebidos: {dados_lead}")
            
            # Validação dos campos obrigatórios
            if not dados_lead['nome']:
                flash('Nome é obrigatório.', 'danger')
                return redirect(url_for('criar_lead'))
            
            if not dados_lead['email']:
                flash('Email é obrigatório.', 'danger')
                return redirect(url_for('criar_lead'))
            
            if not dados_lead['vendedor_id']:
                flash('Vendedor é um campo obrigatório. Por favor, selecione um vendedor.', 'danger')
                return redirect(url_for('criar_lead'))
            
            lead_repo = LeadRepositorio()
            lead_id = lead_repo.criar_lead(dados_lead)
            
            # Log do resultado da criação do lead
            app.logger.info(f"Lead criado com ID: {lead_id}")
            
            if lead_id:
                flash('Lead criado com sucesso!', 'success')
                return redirect(url_for('leads'))
            else:
                flash('Erro ao criar lead.', 'danger')
                return redirect(url_for('criar_lead'))
            
        except Exception as e:
            app.logger.error(f"Erro ao criar lead: {e}", exc_info=True)
            flash('Erro ao criar lead.', 'danger')
            return redirect(url_for('criar_lead'))
    
    # GET: Renderizar formulário
    time_repo = TimeRepositorio()
    vendedores = time_repo.listar_membros()
    return render_template('novo_lead.html', vendedores=vendedores)

@app.route('/leads')
@login_required
def leads():
    try:
        lead_repo = LeadRepositorio()
        
        # Verificar se há um termo de busca
        termo_busca = request.args.get('busca', '').strip()
        
        if termo_busca:
            # Se houver termo de busca, usar método de pesquisa
            leads = lead_repo.pesquisar_leads(termo_busca)
        else:
            # Caso contrário, listar todos os leads
            leads = lead_repo.listar_leads()
        
        # Contar total de leads
        total_leads = len(leads)
        
        # Calcular estatísticas
        leads_por_estagio = {}
        for lead in leads:
            estagio = lead['estagio_atual']
            if estagio not in leads_por_estagio:
                leads_por_estagio[estagio] = 0
            leads_por_estagio[estagio] += 1
        
        # Log de depuração
        app.logger.info(f"Total de leads: {total_leads}")
        app.logger.info(f"Leads por estágio: {leads_por_estagio}")
        
        return render_template('leads.html', 
                               leads=leads, 
                               total_leads=total_leads, 
                               leads_por_estagio=leads_por_estagio,
                               termo_busca=termo_busca)
    except Exception as e:
        logging.error(f"Erro na página de leads: {e}", exc_info=True)
        flash('Ocorreu um erro ao carregar os leads', 'error')
        return redirect(url_for('index'))

@app.route('/leads/novo', methods=['GET', 'POST'])
@login_required
def criar_lead():
    if request.method == 'POST':
        try:
            # Conversão segura do vendedor_id
            try:
                vendedor_id = int(request.form.get('vendedor_id', 0))
            except (ValueError, TypeError):
                vendedor_id = None
                app.logger.warning(f"ID do vendedor inválido: {request.form.get('vendedor_id')}")

            # Converter venda_fechada para booleano
            venda_fechada = request.form.get('venda_fechada') == 'on'
            app.logger.info(f"Venda fechada: {venda_fechada}")

            dados_lead = {
                'nome': request.form.get('nome'),
                'email': request.form.get('email'),
                'telefone': request.form.get('telefone'),
                'empresa': request.form.get('empresa'),
                'cargo': request.form.get('cargo'),
                'estagio_atual': request.form.get('estagio_atual', 'Novo'),
                'vendedor_id': vendedor_id,
                'venda_fechada': venda_fechada,
                
                # Campos adicionais
                'email_comercial': request.form.get('email_comercial'),
                'email_comercial_02': request.form.get('email_comercial_02'),
                'email_comercial_03': request.form.get('email_comercial_03'),
                'email_financeiro': request.form.get('email_financeiro'),
                'telefone_comercial': request.form.get('telefone_comercial'),
                'cidade': request.form.get('cidade'),
                'estado': request.form.get('estado')
            }
            
            # Log dos dados recebidos
            app.logger.info(f"Dados do lead recebidos: {dados_lead}")
            
            # Validação dos campos obrigatórios
            if not dados_lead['nome']:
                flash('Nome é obrigatório.', 'danger')
                return redirect(url_for('criar_lead'))
            
            if not dados_lead['email']:
                flash('Email é obrigatório.', 'danger')
                return redirect(url_for('criar_lead'))
            
            if not dados_lead['vendedor_id']:
                flash('Vendedor é um campo obrigatório. Por favor, selecione um vendedor.', 'danger')
                return redirect(url_for('criar_lead'))
            
            lead_repo = LeadRepositorio()
            lead_id = lead_repo.criar_lead(dados_lead)
            
            # Log do resultado da criação do lead
            app.logger.info(f"Lead criado com ID: {lead_id}")
            
            if lead_id:
                flash('Lead criado com sucesso!', 'success')
                return redirect(url_for('leads'))
            else:
                flash('Erro ao criar lead.', 'danger')
                return redirect(url_for('criar_lead'))
            
        except Exception as e:
            app.logger.error(f"Erro ao criar lead: {e}", exc_info=True)
            flash('Erro ao criar lead.', 'danger')
            return redirect(url_for('criar_lead'))
    
    # GET: Renderizar formulário
    time_repo = TimeRepositorio()
    vendedores = time_repo.listar_membros()
    return render_template('novo_lead.html', vendedores=vendedores)

@app.route('/leads/editar/<int:lead_id>', methods=['GET', 'POST'])
@login_required
def editar_lead(lead_id):
    lead_repo = LeadRepositorio()
    lead = lead_repo.buscar_lead_por_id(lead_id)
    
    if not lead:
        flash('Lead não encontrado.', 'danger')
        return redirect(url_for('leads'))
    
    if request.method == 'POST':
        try:
            # Conversão segura do vendedor_id
            try:
                vendedor_id = int(request.form.get('vendedor_id', 0))
            except (ValueError, TypeError):
                vendedor_id = None
                app.logger.warning(f"ID do vendedor inválido: {request.form.get('vendedor_id')}")

            # Converter venda_fechada para booleano
            venda_fechada = request.form.get('venda_fechada') == 'on'
            app.logger.info(f"Venda fechada: {venda_fechada}")

            dados_lead = {
                'nome': request.form.get('nome'),
                'email': request.form.get('email'),
                'telefone': request.form.get('telefone'),
                'empresa': request.form.get('empresa'),
                'cargo': request.form.get('cargo'),
                'estagio_atual': request.form.get('estagio_atual', 'Novo'),
                'vendedor_id': vendedor_id,
                'venda_fechada': venda_fechada,
                
                # Campos adicionais
                'email_comercial': request.form.get('email_comercial'),
                'email_comercial_02': request.form.get('email_comercial_02'),
                'email_comercial_03': request.form.get('email_comercial_03'),
                'email_financeiro': request.form.get('email_financeiro'),
                'telefone_comercial': request.form.get('telefone_comercial'),
                'cidade': request.form.get('cidade'),
                'estado': request.form.get('estado')
            }
            
            # Log dos dados recebidos
            app.logger.info(f"Dados do lead recebidos para edição: {dados_lead}")
            
            # Validação dos campos obrigatórios
            if not dados_lead['nome']:
                flash('Nome é obrigatório.', 'danger')
                return redirect(url_for('editar_lead', lead_id=lead_id))
            
            if not dados_lead['email']:
                flash('Email é obrigatório.', 'danger')
                return redirect(url_for('editar_lead', lead_id=lead_id))
            
            if not dados_lead['vendedor_id']:
                flash('Vendedor é um campo obrigatório. Por favor, selecione um vendedor.', 'danger')
                return redirect(url_for('editar_lead', lead_id=lead_id))
            
            # Atualizar lead
            resultado = lead_repo.atualizar_lead(lead_id, dados_lead)
            
            # Log do resultado da atualização do lead
            app.logger.info(f"Lead atualizado: {resultado}")
            
            if resultado:
                flash('Lead atualizado com sucesso!', 'success')
                return redirect(url_for('leads'))
            else:
                flash('Erro ao atualizar lead.', 'danger')
                return redirect(url_for('editar_lead', lead_id=lead_id))
            
        except Exception as e:
            app.logger.error(f"Erro ao atualizar lead: {e}", exc_info=True)
            flash('Erro ao atualizar lead.', 'danger')
            return redirect(url_for('editar_lead', lead_id=lead_id))
    
    # GET: Renderizar formulário de edição
    time_repo = TimeRepositorio()
    vendedores = time_repo.listar_membros()
    return render_template('editar_lead.html', lead=lead, vendedores=vendedores)

@app.route('/leads/excluir/<int:lead_id>')
@login_required
def excluir_lead(lead_id):
    try:
        lead_repo = LeadRepositorio()
        if lead_repo.excluir_lead(lead_id):
            flash('Lead excluído com sucesso!', 'success')
        else:
            flash('Lead não encontrado.', 'danger')
    except Exception as e:
        app.logger.error(f"Erro ao excluir lead: {e}")
        flash('Erro ao excluir lead.', 'danger')
    
    return redirect(url_for('leads'))

@app.route('/api/leads')
@login_required
def api_leads():
    try:
        lead_repo = LeadRepositorio()
        leads = lead_repo.listar_leads()
        return jsonify(leads)
    except Exception as e:
        app.logger.error(f"Erro ao buscar leads: {e}")
        return jsonify([]), 500

@app.route('/debug/usuarios')
def debug_usuarios():
    """Rota para listar todos os usuários (APENAS PARA DEBUG)"""
    if not app.debug:
        return "Debug mode is off", 403
    
    usuario_repo = UsuarioRepositorio()
    usuarios = usuario_repo.listar_usuarios()
    
    usuarios_info = []
    for usuario in usuarios:
        usuarios_info.append({
            'id': usuario.id,
            'nome': usuario.nome,
            'email': usuario.email,
            'is_admin': usuario.is_admin
        })
    
    return jsonify(usuarios_info)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
