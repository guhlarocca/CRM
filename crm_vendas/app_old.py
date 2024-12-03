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
app.secret_key = os.urandom(24)  # Chave secreta segura e aleatória
app.config['SESSION_TYPE'] = 'filesystem'
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=30)
app.config['SESSION_PERMANENT'] = True

# Configurações de segurança adicionais
app.config['SESSION_COOKIE_SECURE'] = False  # Defina como True em produção com HTTPS
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'

# Configuração para upload de arquivos
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static', 'profile_photos')
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def save_profile_photo(file):
    """Salva a foto de perfil e retorna o nome do arquivo"""
    if file and file.filename:
        # Gerar nome único para o arquivo
        filename = secure_filename(file.filename)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_')
        unique_filename = timestamp + filename
        
        # Salvar o arquivo
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
        file.save(file_path)
        
        return unique_filename
    return 'default_profile.png'

# Criar conexão com o banco
conexao = ConexaoBanco()
engine = conexao.criar_engine()
Session = sessionmaker(bind=engine)
sessao = Session()

# Função para obter uma nova sessão
def get_sessao():
    global sessao
    try:
        # Verificar se a sessão está fechada
        if not sessao or not sessao.is_active:
            sessao = Session()
        return sessao
    except Exception as e:
        print(f"Erro ao obter sessão: {e}")
        sessao = Session()
        return sessao

# Função para fechar a sessão
def fechar_sessao():
    global sessao
    try:
        if sessao and sessao.is_active:
            sessao.close()
    except Exception as e:
        print(f"Erro ao fechar sessão: {e}")

# Adicionar manipulador para fechar a sessão no final de cada requisição
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

# Rotas existentes...
[Suas rotas atuais aqui]

# Novas rotas para gerenciamento do time
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

        # Salvar foto do perfil
        photo_filename = save_profile_photo(profile_photo)

        # Criar membro
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

@app.route('/time/editar/<int:id>', methods=['POST'])
@login_required
def editar_membro(id):
    try:
        nome = request.form.get('nome')
        email = request.form.get('email')
        telefone = request.form.get('telefone')
        profile_photo = request.files.get('profile_photo')

        if not nome or not email:
            flash('Nome e email são obrigatórios.', 'danger')
            return redirect(url_for('time'))

        time_repo = TimeRepositorio(get_sessao())
        membro = time_repo.buscar_por_id(id)

        if not membro:
            flash('Membro não encontrado.', 'danger')
            return redirect(url_for('time'))

        # Atualizar foto do perfil se fornecida
        photo_filename = save_profile_photo(profile_photo) if profile_photo else membro.profile_photo

        # Atualizar membro
        time_repo.atualizar_membro(
            id=id,
            nome=nome,
            email=email,
            telefone=telefone,
            profile_photo=photo_filename
        )

        flash('Membro atualizado com sucesso!', 'success')
        return redirect(url_for('time'))
    except Exception as e:
        flash(f'Erro ao atualizar membro: {str(e)}', 'danger')
        return redirect(url_for('time'))

@app.route('/time/excluir/<int:id>', methods=['POST'])
@login_required
def excluir_membro(id):
    try:
        time_repo = TimeRepositorio(get_sessao())
        time_repo.excluir_membro(id)
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/api/membros/<int:id>')
@login_required
def get_membro(id):
    try:
        time_repo = TimeRepositorio(get_sessao())
        membro = time_repo.buscar_por_id(id)
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

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
