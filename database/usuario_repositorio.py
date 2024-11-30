from werkzeug.security import generate_password_hash, check_password_hash
from .modelos import Usuario

class UsuarioRepositorio:
    def __init__(self, sessao):
        self.sessao = sessao
    
    def criar_usuario(self, nome, email, senha, is_admin=False, profile_photo='default_profile.png'):
        senha_hash = generate_password_hash(senha)
        novo_usuario = Usuario(
            nome=nome,
            email=email,
            senha=senha_hash,
            is_admin=is_admin,
            profile_photo=profile_photo
        )
        self.sessao.add(novo_usuario)
        self.sessao.commit()
        return novo_usuario
    
    def buscar_por_email(self, email):
        return self.sessao.query(Usuario).filter_by(email=email).first()
    
    def verificar_senha(self, usuario, senha):
        if not usuario:
            return False
        return check_password_hash(usuario.senha, senha)
    
    def listar_usuarios(self):
        return self.sessao.query(Usuario).all()
    
    def buscar_por_id(self, id):
        return self.sessao.query(Usuario).filter_by(id=id).first()

    def atualizar_foto_perfil(self, usuario_id, nome_arquivo):
        """Atualiza a foto de perfil do usuário"""
        usuario = self.buscar_por_id(usuario_id)
        if usuario:
            usuario.profile_photo = nome_arquivo
            self.sessao.commit()
            return True
        return False

    def criar_usuario_admin_se_necessario(self):
        """
        Cria um usuário admin inicial se nenhum usuário existir.
        Garante que sempre haja pelo menos um usuário admin no sistema.
        """
        usuarios = self.listar_usuarios()
        if not usuarios:
            try:
                admin_usuario = self.criar_usuario(
                    nome='Administrador', 
                    email='admin@crm.com', 
                    senha='admin123', 
                    is_admin=True,
                    profile_photo='default_profile.png'
                )
                print(f"Usuário admin criado: {admin_usuario.email}")
                return admin_usuario
            except Exception as e:
                print(f"Erro ao criar usuário admin: {e}")
        return None
