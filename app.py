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
        app.logger.error(f"Erro ao obter sessão: {e}")
        sessao = Session()
        return sessao

def fechar_sessao():
    global sessao
    try:
        if sessao and sessao.is_active:
            sessao.close()
    except Exception as e:
        app.logger.error(f"Erro ao fechar sessão: {e}")

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

        # Garantir que haja pelo menos um membro no time
        if not time_repo.verificar_membros_existentes():
            app.logger.info("Criando membro padrão...")
            novo_membro = time_repo.criar_membro(
                nome="Vendedor Padrão",
                email="vendedor_padrao@empresa.com",
                telefone="(11) 99999-9999"
            )
            if not novo_membro:
                app.logger.error("ERRO: Falha ao criar membro padrão")

        # Buscar dados para o dashboard
        total_leads = lead_repo.contar_total_leads()
        total_vendas = lead_repo.contar_vendas()
        
        # Buscar leads por estágio
        leads_por_estagio = lead_repo.agrupar_leads_por_status()
        leads_recentes = lead_repo.listar_leads_recentes(5)

        # Buscar dados de leads por estado e agrupar por região
        leads_por_estado = lead_repo.contar_leads_por_estado()
        
        # Definir regiões e seus estados
        regioes = {
            'Norte': ['AC', 'AP', 'AM', 'PA', 'RO', 'RR', 'TO'],
            'Nordeste': ['AL', 'BA', 'CE', 'MA', 'PB', 'PE', 'PI', 'RN', 'SE'],
            'Centro-Oeste': ['DF', 'GO', 'MT', 'MS'],
            'Sudeste': ['ES', 'MG', 'RJ', 'SP'],
            'Sul': ['PR', 'RS', 'SC']
        }
        
        # Calcular total de leads por região
        leads_por_regiao = {regiao: 0 for regiao in regioes.keys()}
        for estado, quantidade in leads_por_estado.items():
            if estado != 'Não Informado':
                for regiao, estados in regioes.items():
                    if estado in estados:
                        leads_por_regiao[regiao] += quantidade
                        break

        # Criar dicionário com nomes completos dos estados
        nomes_estados = {
            'AC': 'Acre', 'AL': 'Alagoas', 'AP': 'Amapá', 'AM': 'Amazonas', 'BA': 'Bahia',
            'CE': 'Ceará', 'DF': 'Distrito Federal', 'ES': 'Espírito Santo', 'GO': 'Goiás',
            'MA': 'Maranhão', 'MT': 'Mato Grosso', 'MS': 'Mato Grosso do Sul', 'MG': 'Minas Gerais',
            'PA': 'Pará', 'PB': 'Paraíba', 'PR': 'Paraná', 'PE': 'Pernambuco', 'PI': 'Piauí',
            'RJ': 'Rio de Janeiro', 'RN': 'Rio Grande do Norte', 'RS': 'Rio Grande do Sul',
            'RO': 'Rondônia', 'RR': 'Roraima', 'SC': 'Santa Catarina', 'SP': 'São Paulo',
            'SE': 'Sergipe', 'TO': 'Tocantins'
        }

        # Formatar dados de estado para o gráfico
        leads_por_estado_formatado = {
            nomes_estados.get(estado, estado): quantidade 
            for estado, quantidade in leads_por_estado.items() 
            if estado != 'Não Informado' and quantidade > 0
        }
        
        # Buscar membros do time
        membros_time = time_repo.listar_membros()
        
        # Contar times
        total_times = time_repo.contar_total_times()
        
        # Atualizar estatísticas de membros
        for membro in membros_time:
            membro['leads'] = lead_repo.contar_leads_por_vendedor(membro['id'])
            membro['vendas'] = lead_repo.contar_vendas_por_vendedor(membro['id'])

        return render_template(
            'index.html', 
            total_leads=total_leads,
            total_vendas=total_vendas,
            total_times=total_times,
            leads_recentes=leads_recentes,
            membros_time=membros_time,
            leads_por_estagio=leads_por_estagio,
            leads_por_regiao=leads_por_regiao,
            leads_por_estado=leads_por_estado_formatado
        )
    
    except Exception as e:
        app.logger.error(f"Erro no Dashboard: {e}")
        flash('Erro ao carregar o dashboard.', 'danger')
        return redirect(url_for('login'))

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
        time_repo = TimeRepositorio(get_sessao())
        
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
        app.logger.error(f"Erro ao atualizar estágio do lead: {e}")
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
            app.logger.error(f"Erro ao criar lead: {e}")
            flash('Erro ao criar lead.', 'danger')
            return redirect(url_for('novo_lead'))
    
    time_repo = TimeRepositorio(get_sessao())
    vendedores = time_repo.listar_membros()
    return render_template('novo_lead.html', vendedores=vendedores)

@app.route('/leads')
@login_required
def leads():
    try:
        # Get the current session
        sessao = get_sessao()
        
        # Create lead repository with the current session
        lead_repo = LeadRepositorio(sessao)
        
        # List leads
        leads = lead_repo.listar_leads()
        
        # Se for uma requisição AJAX, retornar JSON
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            leads_json = []
            for lead in leads:
                lead_dict = {
                    'id': lead.id,
                    'nome': lead.nome,
                    'email': lead.email,
                    'telefone': lead.telefone,
                    'empresa': lead.empresa,
                    'cargo': lead.cargo,
                    'vendedor': {
                        'nome': lead.vendedor.nome if lead.vendedor else None
                    } if lead.vendedor else None,
                    'estagio_atual': lead.estagio_atual,
                    'data_criacao': lead.data_criacao.isoformat() if lead.data_criacao else None,
                    'venda_fechada': lead.venda_fechada
                }
                leads_json.append(lead_dict)
            return jsonify(leads_json)
        
        # Render template with leads
        return render_template('leads.html', leads=leads)
    except Exception as e:
        app.logger.error(f"Erro na rota leads: {e}")
        import traceback
        traceback.print_exc()
        
        # Se for AJAX, retornar erro JSON
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'error': str(e)}), 500
        
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
            app.logger.error(f"Erro ao criar lead: {e}")
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
            
            # Coletar TODOS os campos do formulário
            dados_lead = {
                # Campos básicos
                'nome': request.form.get('nome'),
                'email': request.form.get('email'),
                'telefone': request.form.get('telefone'),
                'empresa': request.form.get('empresa'),
                'cargo': request.form.get('cargo'),
                'estagio_atual': request.form.get('estagio_atual'),
                'vendedor_id': request.form.get('vendedor_id', type=int),
                'venda_fechada': venda_fechada,
                'observacoes': request.form.get('observacoes', ''),
                
                # Campos de contato adicionais
                'contato_01': request.form.get('contato_01'),
                'contato_02': request.form.get('contato_02'),
                'cidade': request.form.get('cidade'),
                'estado': request.form.get('estado'),
                
                # Emails adicionais
                'email_comercial': request.form.get('email_comercial'),
                'email_comercial_02': request.form.get('email_comercial_02'),
                'email_comercial_03': request.form.get('email_comercial_03'),
                'email_financeiro': request.form.get('email_financeiro'),
                
                # Telefone comercial
                'telefone_comercial': request.form.get('telefone_comercial')
            }
            
            # Remover chaves com valor None
            dados_lead = {k: v for k, v in dados_lead.items() if v is not None and v != ''}
            
            # Log de depuração detalhado
            app.logger.info("\n--- DADOS RECEBIDOS PARA EDIÇÃO ---")
            for key, value in dados_lead.items():
                app.logger.info(f"{key}: {value}")
            
            lead_repo.editar_lead(lead_id, dados_lead)
            flash('Lead atualizado com sucesso!', 'success')
            return redirect(url_for('leads'))
            
        except Exception as e:
            app.logger.error(f"Erro ao atualizar lead: {e}")
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
        app.logger.error(f"Erro ao excluir lead: {e}")
        flash('Erro ao excluir lead.', 'danger')
    
    return redirect(url_for('leads'))

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
