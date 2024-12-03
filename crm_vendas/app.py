from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, session, send_from_directory
from sqlalchemy import func, desc, inspect, text
from database.conexao_supabase import ConexaoSupabase
from database.repositorio import LeadRepositorio, TimeRepositorio
from database.usuario_repositorio import UsuarioRepositorio
from database.config_empresa_repositorio import ConfigEmpresaRepositorio
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
import os
import bcrypt
from datetime import datetime, timezone, timedelta
import logging
import traceback
from werkzeug.utils import secure_filename
from functools import wraps
import psycopg2
import psycopg2.extras
from database.modelos import Lead, Time, Base, Usuario
from dotenv import load_dotenv
import uuid
import jwt
from supabase import create_client, Client
import secrets

# Carregar variáveis de ambiente
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'sua_chave_secreta_aqui')
app.config['SESSION_TYPE'] = 'filesystem'
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=30)
app.config['SESSION_PERMANENT'] = True

# Configurações de segurança
app.config['SESSION_COOKIE_SECURE'] = False
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'

# Configurações de upload
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static', 'profile_photos')
TEAM_PHOTOS_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static', 'team_photos')
IMG_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static', 'img')

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
if not os.path.exists(TEAM_PHOTOS_FOLDER):
    os.makedirs(TEAM_PHOTOS_FOLDER, exist_ok=True)
if not os.path.exists(IMG_FOLDER):
    os.makedirs(IMG_FOLDER, exist_ok=True)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['TEAM_PHOTOS_FOLDER'] = TEAM_PHOTOS_FOLDER
app.config['IMG_FOLDER'] = IMG_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s: %(message)s')
app.logger.setLevel(logging.INFO)

# Configurações de e-mail
app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER', 'smtp.gmail.com')
app.config['MAIL_PORT'] = int(os.getenv('MAIL_PORT', 587))
app.config['MAIL_USE_TLS'] = os.getenv('MAIL_USE_TLS', 'True').lower() == 'true'
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
app.config['MAIL_DEFAULT_SENDER'] = os.getenv('MAIL_DEFAULT_SENDER')

def allowed_file(filename):
    """Verifica se a extensão do arquivo é permitida"""
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def save_uploaded_file(file, prefix='', folder=None):
    """Função auxiliar para salvar arquivos enviados"""
    if file and allowed_file(file.filename):
        # Gerar nome único para o arquivo
        timestamp = datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')
        filename = secure_filename(f"{prefix}_{timestamp}_{file.filename}" if prefix else f"{timestamp}_{file.filename}")
        
        # Se não especificado, usar UPLOAD_FOLDER como padrão
        if folder is None:
            folder = app.config['UPLOAD_FOLDER']
        
        # Garantir que o diretório existe
        if not os.path.exists(folder):
            os.makedirs(folder, exist_ok=True)
        
        # Salvar arquivo
        filepath = os.path.join(folder, filename)
        file.save(filepath)
        app.logger.info(f"Arquivo salvo em: {filepath}")
        
        return filename
    return None

def save_profile_photo(file, is_team_member=False):
    """Função para salvar fotos de perfil"""
    if is_team_member:
        return save_uploaded_file(file, prefix='team', folder=app.config['TEAM_PHOTOS_FOLDER'])
    return save_uploaded_file(file, prefix='perfil', folder=app.config['UPLOAD_FOLDER'])

def enviar_email_convite(email_destino, link_convite):
    try:
        import smtplib
        from email.mime.text import MIMEText
        from email.mime.multipart import MIMEMultipart

        msg = MIMEMultipart()
        msg['From'] = app.config['MAIL_DEFAULT_SENDER']
        msg['To'] = email_destino
        msg['Subject'] = 'Convite para o CRM Vendas'

        # Corpo do e-mail em HTML
        corpo_html = f"""
        <html>
            <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                    <h2 style="color: #2c3e50;">Convite para o CRM Vendas</h2>
                    <p>Olá!</p>
                    <p>Você foi convidado para participar do CRM Vendas.</p>
                    <p>Para completar seu cadastro, clique no botão abaixo:</p>
                    <p style="text-align: center;">
                        <a href="{link_convite}" 
                           style="display: inline-block; 
                                  background-color: #3498db; 
                                  color: white; 
                                  padding: 12px 24px; 
                                  text-decoration: none; 
                                  border-radius: 4px;
                                  margin: 20px 0;">
                            Completar Cadastro
                        </a>
                    </p>
                    <p>Se o botão não funcionar, copie e cole o link abaixo no seu navegador:</p>
                    <p style="background-color: #f8f9fa; 
                              padding: 10px; 
                              border-radius: 4px; 
                              word-break: break-all;">
                        {link_convite}
                    </p>
                    <p>Este link é válido por 7 dias.</p>
                    <hr style="border: none; border-top: 1px solid #eee; margin: 20px 0;">
                    <p style="color: #7f8c8d; font-size: 12px;">
                        Este é um e-mail automático. Por favor, não responda.
                    </p>
                </div>
            </body>
        </html>
        """

        msg.attach(MIMEText(corpo_html, 'html'))

        with smtplib.SMTP(app.config['MAIL_SERVER'], app.config['MAIL_PORT']) as server:
            if app.config['MAIL_USE_TLS']:
                server.starttls()
            
            if app.config['MAIL_USERNAME'] and app.config['MAIL_PASSWORD']:
                server.login(app.config['MAIL_USERNAME'], app.config['MAIL_PASSWORD'])
            
            server.send_message(msg)
            
        return True
    except Exception as e:
        logging.error(f"Erro ao enviar e-mail: {str(e)}")
        return False

# Conexão com o Supabase
class ConexaoSupabase:
    def __init__(self):
        self.supabase_url = os.getenv('SUPABASE_URL')
        self.supabase_key = os.getenv('SUPABASE_KEY')
        self.client = create_client(self.supabase_url, self.supabase_key)

    def buscar_usuario_por_email(self, email):
        try:
            result = self.client.table('usuarios').select('*').eq('email', email).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            logging.error(f"Erro ao buscar usuário: {str(e)}")
            return None

    def buscar_convite_ativo(self, email):
        try:
            agora = datetime.now(timezone.utc)
            result = self.client.table('convites').select('*')\
                .eq('email', email)\
                .eq('usado', False)\
                .gte('expiracao', agora.isoformat())\
                .execute()
            return result.data[0] if result.data else None
        except Exception as e:
            logging.error(f"Erro ao buscar convite: {str(e)}")
            return None

    def criar_convite(self, email, token, expiracao, criado_por):
        try:
            dados = {
                'email': email,
                'token': token,
                'expiracao': expiracao.isoformat(),
                'criado_por': criado_por,
                'usado': False,
                'data_criacao': datetime.now(timezone.utc).isoformat()
            }
            result = self.client.table('convites').insert(dados).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            logging.error(f"Erro ao criar convite: {str(e)}")
            return None

    def marcar_convite_como_usado(self, token):
        try:
            dados = {
                'usado': True,
                'data_uso': datetime.now(timezone.utc).isoformat()
            }
            result = self.client.table('convites').update(dados).eq('token', token).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            logging.error(f"Erro ao marcar convite como usado: {str(e)}")
            return None

conexao = ConexaoSupabase()
usuario_repo = UsuarioRepositorio()
config_empresa_repo = ConfigEmpresaRepositorio()

def get_conn():
    return conexao.client

def get_cur(conn):
    return conn.cursor()

def fechar_sessao(cur, conn):
    if cur:
        cur.close()
    if conn:
        conn.close()

@app.teardown_appcontext
def shutdown_session(exception=None):
    fechar_sessao(cur=None, conn=None)

# Configuração do Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    try:
        usuario_repo = UsuarioRepositorio()
        return usuario_repo.obter_por_id(user_id)
    except Exception as e:
        app.logger.error(f"Erro ao carregar usuário: {str(e)}")
        return None

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    if request.method == 'POST':
        email = request.form.get('email')
        senha = request.form.get('senha')
        
        try:
            usuario_repo = UsuarioRepositorio()
            usuario = usuario_repo.login(email, senha)
            if usuario:
                login_user(usuario)
                next_page = request.args.get('next')
                if not next_page or urlparse(next_page).netloc != '':
                    next_page = url_for('index')
                return redirect(next_page)
            else:
                flash('Email ou senha inválidos', 'error')
        except Exception as e:
            app.logger.error(f"Erro no login: {str(e)}")
            flash('Erro ao fazer login. Tente novamente.', 'error')
    
    return render_template('login.html')

@app.route('/')
@login_required
def index():
    try:
        time_repo = TimeRepositorio()
        lead_repo = LeadRepositorio()
        
        # Buscar membros e leads
        membros = time_repo.listar_membros()
        leads = lead_repo.listar_leads()
        
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
                            membros=membros,
                            membros_time=membros,  # alias para manter compatibilidade
                            leads=leads,
                            leads_recentes=leads_recentes,
                            leads_por_regiao=leads_por_regiao,
                            leads_por_estado=leads_por_estado,
                            leads_por_estagio=leads_por_estagio,
                            total_times=len(membros) if membros else 0,
                            total_leads=len(leads) if leads else 0,
                            total_vendas=sum(membro.get('vendas', 0) for membro in membros))
                            
    except Exception as e:
        app.logger.error(f"Erro ao renderizar index: {str(e)}")
        return redirect(url_for('login'))

@app.route('/logout')
@login_required
def logout():
    logout_user()
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
                profile_photo = save_profile_photo(file, is_team_member=True)

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
        
        if request.method == 'POST':
            # Capturar dados do formulário
            nome = request.form.get('nome')
            email = request.form.get('email')
            telefone = request.form.get('telefone')
            
            app.logger.info(f"Editando membro {id}")
            app.logger.info(f"Nome: {nome}")
            app.logger.info(f"Email: {email}")
            app.logger.info(f"Telefone: {telefone}")
            
            # Buscar membro atual para manter a foto existente se não for enviada nova
            membro_atual = time_repo.buscar_membro_por_id(id)
            app.logger.info(f"Membro atual: {membro_atual}")
            
            if not membro_atual:
                app.logger.error("Membro não encontrado")
                flash('Membro não encontrado.', 'danger')
                return redirect(url_for('time'))
            
            # Processar foto de perfil
            profile_photo = membro_atual['profile_photo']
            if 'profile_photo' in request.files:
                file = request.files['profile_photo']
                if file and file.filename:
                    try:
                        profile_photo = save_profile_photo(file, is_team_member=True)
                        app.logger.info(f"Nova foto salva: {profile_photo}")
                    except Exception as e:
                        app.logger.error(f"Erro ao salvar foto: {e}")
                        flash('Erro ao salvar a foto.', 'danger')
                        return redirect(url_for('time'))
            
            # Atualizar membro
            try:
                resultado = time_repo.atualizar_membro(id, nome, email, telefone, profile_photo)
                if resultado:
                    app.logger.info("Membro atualizado com sucesso")
                    flash('Membro atualizado com sucesso!', 'success')
                else:
                    app.logger.error("Falha ao atualizar membro")
                    flash('Erro ao atualizar membro.', 'danger')
            except Exception as e:
                app.logger.error(f"Erro ao atualizar membro no banco: {e}")
                flash('Erro ao atualizar membro no banco de dados.', 'danger')
            
            return redirect(url_for('time'))
        
        # Para método GET, buscar dados do membro
        membro = time_repo.buscar_membro_por_id(id)
        if not membro:
            flash('Membro não encontrado.', 'danger')
            return redirect(url_for('time'))
        
        return render_template('editar_membro.html', membro=membro)
    
    except Exception as e:
        app.logger.error(f"Erro em editar_membro: {str(e)}")
        import traceback
        app.logger.error(traceback.format_exc())
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
                'id': membro['id'],
                'nome': membro['nome'],
                'email': membro['email'],
                'telefone': membro['telefone'],
                'profile_photo': membro['profile_photo']
            })
        else:
            return jsonify({'error': 'Membro não encontrado'}), 404
            
    except Exception as e:
        app.logger.error(f"Erro ao buscar membro: {e}")
        return jsonify({'error': 'Erro interno do servidor'}), 500

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
                'id_vendedor': vendedor_id,
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
            
            if not dados_lead['id_vendedor']:
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
                'id_vendedor': vendedor_id,
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
            
            if not dados_lead['id_vendedor']:
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
                'id_vendedor': vendedor_id,
                'venda_fechada': venda_fechada,
                
                # Campos adicionais
                'email_comercial': request.form.get('email_comercial'),
                'email_comercial_02': request.form.get('email_comercial_02'),
                'email_comercial_03': request.form.get('email_comercial_03'),
                'email_financeiro': request.form.get('email_financeiro'),
                'telefone_comercial': request.form.get('telefone_comercial'),
                'cidade': request.form.get('cidade'),
                'estado': request.form.get('estado'),
                'contato_01': request.form.get('contato_01'),
                'contato_02': request.form.get('contato_02'),
                'observacoes': request.form.get('observacoes')
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
            
            if not dados_lead['id_vendedor']:
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

@app.context_processor
def inject_config():
    """Injeta configurações da empresa em todos os templates"""
    config = config_empresa_repo.obter_configuracao()
    timestamp = datetime.now(timezone.utc).timestamp()
    return dict(config=config, timestamp=timestamp)

@app.route('/atualizar_logo', methods=['POST'])
@login_required
def atualizar_logo():
    """Atualiza o logo da empresa"""
    try:
        app.logger.info("Iniciando atualização do logo")
        # Verificar se há arquivo na requisição
        if 'logo' not in request.files:
            flash('Nenhum arquivo selecionado', 'error')
            return redirect(url_for('config_empresa'))
        
        file = request.files['logo']
        if file.filename == '':
            flash('Nenhum arquivo selecionado', 'error')
            return redirect(url_for('config_empresa'))

        # Criar diretório para logos se não existir
        logos_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static', 'img')
        if not os.path.exists(logos_folder):
            os.makedirs(logos_folder, exist_ok=True)

        # Salvar arquivo no diretório img
        filename = save_uploaded_file(file, prefix='logo', folder=logos_folder)
        if not filename:
            flash('Tipo de arquivo não permitido', 'error')
            return redirect(url_for('config_empresa'))

        # Atualizar banco de dados
        updated_config = config_empresa_repo.atualizar_logo(filename)
        
        if updated_config:
            app.logger.info(f"Logo atualizada com sucesso: {updated_config['logo_url']}")
            flash('Logo atualizada com sucesso!', 'success')
        else:
            app.logger.error("Falha ao atualizar logo no banco de dados")
            flash('Erro ao atualizar logo no banco de dados', 'error')
            # Remove o arquivo se falhou ao atualizar o banco
            filepath = os.path.join(logos_folder, filename)
            if os.path.exists(filepath):
                os.remove(filepath)
        
        return redirect(url_for('config_empresa'))

    except Exception as e:
        app.logger.error(f'Erro ao atualizar logo: {str(e)}')
        flash('Erro ao atualizar logo. Por favor, tente novamente.', 'error')
        return redirect(url_for('config_empresa'))

@app.route('/alterar_senha', methods=['POST'])
@login_required
def alterar_senha():
    """Altera a senha do usuário logado"""
    try:
        app.logger.info("Iniciando alteração de senha")
        senha_atual = request.form.get('senha_atual')
        nova_senha = request.form.get('nova_senha')
        confirmar_senha = request.form.get('confirmar_senha')

        if not all([senha_atual, nova_senha, confirmar_senha]):
            app.logger.error("Campos obrigatórios não preenchidos")
            flash('Todos os campos são obrigatórios', 'error')
            return jsonify({'success': False, 'message': 'Todos os campos são obrigatórios'}), 400

        # Verifica se a senha atual está correta
        if not usuario_repo.verificar_senha(current_user.email, senha_atual):
            app.logger.error("Senha atual incorreta")
            flash('Senha atual incorreta', 'error')
            return jsonify({'success': False, 'message': 'Senha atual incorreta'}), 400

        # Verifica se as senhas novas coincidem
        if nova_senha != confirmar_senha:
            app.logger.error("As novas senhas não coincidem")
            flash('As novas senhas não coincidem', 'error')
            return jsonify({'success': False, 'message': 'As novas senhas não coincidem'}), 400

        # Verifica se a nova senha tem pelo menos 6 caracteres
        if len(nova_senha) < 6:
            app.logger.error("Nova senha muito curta")
            flash('A nova senha deve ter pelo menos 6 caracteres', 'error')
            return jsonify({'success': False, 'message': 'A nova senha deve ter pelo menos 6 caracteres'}), 400

        # Atualiza a senha usando o método corrigido do repositório
        if usuario_repo.atualizar_senha(current_user.email, nova_senha):
            app.logger.info("Senha atualizada com sucesso")
            flash('Senha alterada com sucesso!', 'success')
            return jsonify({'success': True, 'message': 'Senha alterada com sucesso!'})
        else:
            app.logger.error("Falha ao atualizar senha no banco de dados")
            flash('Erro ao atualizar senha no banco de dados', 'error')
            return jsonify({'success': False, 'message': 'Erro ao atualizar senha no banco de dados'}), 500

    except Exception as e:
        app.logger.error(f'Erro ao alterar senha: {str(e)}')
        flash('Erro ao alterar senha. Por favor, tente novamente.', 'error')
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/enviar_convite', methods=['POST'])
@login_required
def enviar_convite():
    try:
        data = request.get_json()
        email = data.get('email')

        if not email:
            return jsonify({'success': False, 'message': 'E-mail não fornecido'}), 400

        # Verifica se o e-mail já está cadastrado como usuário
        usuario_existente = conexao.buscar_usuario_por_email(email)
        if usuario_existente:
            return jsonify({'success': False, 'message': 'Este e-mail já está cadastrado no sistema'}), 400

        # Verifica se já existe um convite ativo para este e-mail
        convite_existente = conexao.buscar_convite_ativo(email)
        if convite_existente:
            return jsonify({'success': False, 'message': 'Já existe um convite ativo para este e-mail'}), 400

        # Gera um token único para o convite
        token = str(uuid.uuid4())
        expiracao = datetime.now(timezone.utc) + timedelta(days=7)  # Token válido por 7 dias

        # Salva o convite no banco de dados
        novo_convite = conexao.criar_convite(email, token, expiracao, str(current_user.id))
        if not novo_convite:
            return jsonify({'success': False, 'message': 'Erro ao criar convite'}), 500

        # Gera o link de convite e envia o e-mail
        link_convite = f"{request.host_url}registro_convite/{token}"
        email_enviado = enviar_email_convite(email, link_convite)
        
        if not email_enviado:
            return jsonify({
                'success': True,
                'message': 'Convite criado, mas houve um erro ao enviar o e-mail. Link do convite:',
                'link': link_convite
            })
        
        return jsonify({
            'success': True,
            'message': 'Convite enviado com sucesso',
            'link': link_convite
        })

    except Exception as e:
        logging.error(f"Erro ao enviar convite: {str(e)}")
        logging.error(traceback.format_exc())
        return jsonify({'success': False, 'message': 'Erro ao enviar convite'}), 500

@app.route('/registro_convite/<token>')
def registro_convite(token):
    try:
        # Busca o convite
        result = conexao.client.table('convites').select('*').eq('token', token).execute()
        
        if not result.data:
            flash('Link de convite inválido.', 'error')
            return redirect(url_for('login'))
            
        convite = result.data[0]
        
        # Verifica se o convite já foi usado
        if convite['usado']:
            flash('Este convite já foi utilizado.', 'error')
            return redirect(url_for('login'))
            
        # Verifica se o convite expirou
        expiracao = datetime.fromisoformat(convite['expiracao'].replace('Z', '+00:00'))
        if expiracao < datetime.now(timezone.utc):
            flash('Este convite expirou.', 'error')
            return redirect(url_for('login'))
            
        return render_template('registro_convite.html', token=token, email=convite['email'])
        
    except Exception as e:
        logging.error(f"Erro ao verificar convite: {str(e)}")
        flash('Erro ao verificar convite.', 'error')
        return redirect(url_for('login'))

@app.route('/completar_registro_convite/<token>', methods=['POST'])
def completar_registro_convite(token):
    try:
        # Obter dados do formulário
        nome = request.form.get('username')  # mantemos o nome do campo no form como username
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        profile_photo = request.files.get('profile_photo')

        # Validações básicas
        if not all([nome, email, password, confirm_password]):
            flash('Todos os campos são obrigatórios.', 'error')
            return redirect(url_for('registro_convite', token=token))

        if password != confirm_password:
            flash('As senhas não coincidem.', 'error')
            return redirect(url_for('registro_convite', token=token))

        if len(password) < 6:
            flash('A senha deve ter pelo menos 6 caracteres.', 'error')
            return redirect(url_for('registro_convite', token=token))

        # Verificar o convite novamente
        result = conexao.client.table('convites').select('*').eq('token', token).eq('email', email).execute()
        
        if not result.data:
            flash('Link de convite inválido.', 'error')
            return redirect(url_for('login'))
            
        convite = result.data[0]
        
        if convite['usado']:
            flash('Este convite já foi utilizado.', 'error')
            return redirect(url_for('login'))
            
        expiracao = datetime.fromisoformat(convite['expiracao'].replace('Z', '+00:00'))
        if expiracao < datetime.now(timezone.utc):
            flash('Este convite expirou.', 'error')
            return redirect(url_for('login'))

        # Verificar se o nome de usuário já existe
        result = conexao.client.table('usuarios').select('id').eq('nome', nome).execute()
        if result.data:
            flash('Este nome de usuário já está em uso.', 'error')
            return redirect(url_for('registro_convite', token=token))

        # Salvar a foto de perfil se fornecida
        profile_photo_filename = None
        if profile_photo:
            profile_photo_filename = save_profile_photo(profile_photo)
            if not profile_photo_filename:
                flash('Erro ao salvar foto de perfil.', 'error')
                return redirect(url_for('registro_convite', token=token))

        # Criar o usuário
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        
        novo_usuario = {
            'id': str(uuid.uuid4()),  # Gerar UUID manualmente
            'nome': nome,
            'email': email,
            'senha': hashed_password.decode('utf-8'),
            'profile_photo': profile_photo_filename,
            'is_admin': False
        }
        
        result = conexao.client.table('usuarios').insert(novo_usuario).execute()
        if not result.data:
            flash('Erro ao criar usuário.', 'error')
            return redirect(url_for('registro_convite', token=token))
        
        # Marcar o convite como usado
        conexao.client.table('convites').update({
            'usado': True,
            'data_uso': datetime.now(timezone.utc).isoformat()
        }).eq('token', token).execute()

        flash('Registro concluído com sucesso! Você já pode fazer login.', 'success')
        return redirect(url_for('login'))
        
    except Exception as e:
        logging.error(f"Erro ao completar registro: {str(e)}")
        flash('Erro ao completar registro.', 'error')
        return redirect(url_for('registro_convite', token=token))

@app.route('/config_empresa')
@login_required
def config_empresa():
    """Página de configurações da empresa"""
    timestamp = datetime.now(timezone.utc).timestamp()
    config = config_empresa_repo.obter_configuracao()
    return render_template('config_empresa.html', timestamp=timestamp, config=config)

@app.route('/atualizar_perfil', methods=['POST'])
@login_required
def atualizar_perfil():
    try:
        app.logger.info("Iniciando atualização de foto de perfil")
        # Verificar se há arquivo na requisição
        if 'profile_photo' not in request.files:
            flash('Nenhum arquivo selecionado', 'error')
            return redirect(url_for('config_empresa'))
        
        file = request.files['profile_photo']
        if file.filename == '':
            flash('Nenhum arquivo selecionado', 'error')
            return redirect(url_for('config_empresa'))

        # Salvar arquivo no diretório profile_photos
        filename = save_uploaded_file(file, prefix=f"perfil_{current_user.id}", folder=app.config['UPLOAD_FOLDER'])
        if not filename:
            flash('Tipo de arquivo não permitido', 'error')
            return redirect(url_for('config_empresa'))

        # Atualizar banco de dados
        updated_user = usuario_repo.atualizar_foto_perfil(current_user.id, filename)
        
        if updated_user:
            app.logger.info(f"Usuário atualizado com sucesso: {updated_user.profile_photo}")
            # Atualizar a sessão do usuário
            current_user.profile_photo = updated_user.profile_photo
            flash('Foto de perfil atualizada com sucesso!', 'success')
        else:
            app.logger.error("Falha ao atualizar usuário no banco de dados")
            flash('Erro ao atualizar foto no banco de dados', 'error')
            # Remove o arquivo se falhou ao atualizar o banco
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            if os.path.exists(filepath):
                os.remove(filepath)
        
        return redirect(url_for('config_empresa'))

    except Exception as e:
        app.logger.error(f'Erro ao atualizar foto de perfil: {str(e)}')
        flash('Erro ao atualizar foto de perfil. Por favor, tente novamente.', 'error')
        return redirect(url_for('config_empresa'))

@app.route('/atualizar_config_empresa', methods=['POST'])
@login_required
def atualizar_config_empresa():
    """Atualiza as configurações da empresa"""
    try:
        app.logger.info("Iniciando atualização de configurações da empresa")
        # Obtém a configuração atual
        config_atual = config_empresa_repo.obter_configuracao()
        
        # Processa a logo se foi enviada
        logo_url = config_atual.get('logo_url') if config_atual else None
        new_logo = None
        
        if 'logo' in request.files:
            file = request.files['logo']
            if file and file.filename != '':
                # Salvar nova logo no diretório img
                new_logo = save_uploaded_file(file, prefix='logo', folder=app.config['IMG_FOLDER'])
                if new_logo:
                    logo_url = new_logo
                else:
                    flash('Tipo de arquivo não permitido para o logo', 'error')

        # Coleta as configurações do formulário
        config_data = {
            'nome_sistema': request.form.get('nome_sistema', 'CRM Vendas'),
            'logo_url': logo_url
        }
        
        # Atualiza as configurações
        updated_config = config_empresa_repo.atualizar_configuracao(config_data)
        if updated_config:
            app.logger.info("Configurações atualizadas com sucesso")
            flash('Configurações atualizadas com sucesso!', 'success')
        else:
            app.logger.error("Falha ao atualizar configurações")
            flash('Erro ao atualizar configurações no banco de dados', 'error')
            # Remove o arquivo de logo se foi feito upload mas falhou ao atualizar
            if new_logo:
                filepath = os.path.join(app.config['IMG_FOLDER'], new_logo)
                if os.path.exists(filepath):
                    os.remove(filepath)
        
    except Exception as e:
        app.logger.error(f'Erro ao atualizar configurações: {str(e)}')
        flash('Erro ao atualizar configurações. Por favor, tente novamente.', 'error')
    
    # Força o recarregamento da página com um novo timestamp
    return redirect(url_for('config_empresa', _t=datetime.now(timezone.utc).timestamp()))

@app.after_request
def add_header(response):
    """Add headers to prevent caching"""
    if 'Cache-Control' not in response.headers:
        response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '-1'
    return response

@app.after_request
def add_header_static(response):
    """Add headers to prevent caching for static files"""
    if 'Cache-Control' not in response.headers and response.status_code == 200:
        if 'static' in response.headers['Content-Type']:
            response.headers['Cache-Control'] = 'max-age=31536000'
            response.headers['Pragma'] = 'public'
            response.headers['Expires'] = 'Fri, 01 Jan 2038 00:00:00 GMT'
    return response

@app.route('/tarefas')
@login_required
def tarefas():
    try:
        # Buscar todas as tarefas com join na tabela time
        result = conexao.client.from_('tarefas')\
            .select('*, time!inner(nome)')\
            .execute()
            
        tarefas = []
        if result.data:
            for tarefa in result.data:
                # Extrair o nome do vendedor
                time_data = tarefa.get('time', {})
                nome_vendedor = time_data.get('nome') if time_data else None
                
                tarefa_obj = {
                    'id': tarefa.get('id'),
                    'descricao': tarefa.get('descricao'),
                    'status': tarefa.get('status'),
                    'prioridade': tarefa.get('prioridade'),
                    'data_criacao': tarefa.get('data_criacao'),
                    'data_conclusao': tarefa.get('data_conclusao'),
                    'id_vendedor': tarefa.get('id_vendedor'),
                    'nome_vendedor': nome_vendedor
                }
                tarefas.append(tarefa_obj)
        
        # Buscar vendedores para o dropdown
        vendedores_result = conexao.client.from_('time')\
            .select('id, nome')\
            .execute()
        vendedores = vendedores_result.data if vendedores_result.data else []
        
        return render_template(
            'tarefas.html',
            tarefas=tarefas,
            vendedores=vendedores,
            current_user=current_user
        )
        
    except Exception as e:
        logging.error(f"Erro ao carregar tarefas: {str(e)}")
        flash('Erro ao carregar tarefas.', 'error')
        return redirect(url_for('tarefas'))

@app.route('/criar_tarefa', methods=['POST'])
@login_required
def criar_tarefa():
    try:
        descricao = request.form.get('descricao')
        id_vendedor = request.form.get('id_vendedor')
        status = request.form.get('status', 'pendente')  # default em minúsculo
        prioridade = request.form.get('prioridade')
        
        # Validar valores permitidos e limpar os dados
        prioridade = prioridade.strip().lower() if prioridade else None
        status = status.strip().lower() if status else 'pendente'
        descricao = descricao.strip() if descricao else None
        
        if prioridade not in ['baixa', 'media', 'alta']:
            flash('Prioridade inválida.', 'error')
            return redirect(url_for('tarefas'))
            
        if status not in ['pendente', 'concluída']:
            flash('Status inválido.', 'error')
            return redirect(url_for('tarefas'))
        
        if not all([descricao, id_vendedor, prioridade]):
            flash('Por favor, preencha todos os campos obrigatórios.', 'error')
            return redirect(url_for('tarefas'))

        # Criar nova tarefa
        nova_tarefa = {
            'id_vendedor': id_vendedor,
            'descricao': descricao,
            'status': status,
            'prioridade': prioridade,
            'data_criacao': datetime.now(timezone.utc).isoformat(),
            'data_conclusao': None
        }
        
        result = conexao.client.table('tarefas').insert(nova_tarefa).execute()
        
        if not result.data:
            flash('Erro ao criar tarefa.', 'error')
            return redirect(url_for('tarefas'))
        
        flash('Tarefa criada com sucesso!', 'success')
        return redirect(url_for('tarefas'))
        
    except Exception as e:
        logging.error(f"Erro ao criar tarefa: {str(e)}")
        flash('Erro ao criar tarefa.', 'error')
        return redirect(url_for('tarefas'))

@app.route('/atualizar_status_tarefa', methods=['POST'])
@login_required
def atualizar_status_tarefa():
    try:
        tarefa_id = request.form.get('tarefa_id')
        novo_status = 'concluida'  # Sem acento conforme constraint
        
        if not tarefa_id:
            return jsonify({'error': 'ID da tarefa não fornecido'}), 400
        
        # Atualizar status da tarefa
        result = conexao.client.from_('tarefas')\
            .update({
                'status': novo_status,
                'data_conclusao': datetime.now(timezone.utc).isoformat()
            })\
            .eq('id', tarefa_id)\
            .execute()
        
        if not result.data:
            return jsonify({'error': 'Erro ao atualizar tarefa'}), 500
        
        return jsonify({'message': 'Status atualizado com sucesso'}), 200
        
    except Exception as e:
        logging.error(f"Erro ao atualizar status da tarefa: {str(e)}")
        return jsonify({'error': 'Erro ao atualizar status'}), 500

@app.route('/excluir_tarefa', methods=['POST'])
@login_required
def excluir_tarefa():
    try:
        tarefa_id = request.form.get('tarefa_id')
        
        if not tarefa_id:
            return jsonify({'error': 'ID da tarefa não fornecido'}), 400
        
        # Excluir tarefa
        result = conexao.client.table('tarefas').delete().eq('id', tarefa_id).execute()
        
        if not result.data:
            return jsonify({'error': 'Erro ao excluir tarefa'}), 500
        
        return jsonify({'message': 'Tarefa excluída com sucesso'}), 200
        
    except Exception as e:
        logging.error(f"Erro ao excluir tarefa: {str(e)}")
        return jsonify({'error': 'Erro ao excluir tarefa'}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
