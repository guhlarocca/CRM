import os
import sys
import logging
from dotenv import load_dotenv

# Adicionar o diretório do projeto ao path
projeto_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, projeto_dir)

# Configurar logging
logging.basicConfig(level=logging.DEBUG, 
                    format='%(asctime)s - %(levelname)s: %(message)s')

# Carregar variáveis de ambiente
load_dotenv()

# Importações após configuração do path
from database.usuario_repositorio import UsuarioRepositorio
import bcrypt

def testar_login_completo(email, senha):
    """
    Teste abrangente de login com múltiplas verificações
    """
    try:
        # Inicializar repositório de usuários
        usuario_repo = UsuarioRepositorio()
        
        # Etapa 1: Buscar usuário por email
        print("\n📋 Etapa 1: Buscar usuário")
        usuario_dict = usuario_repo.buscar_por_email(email)
        if not usuario_dict:
            print(f"✗ Usuário com email {email} não encontrado")
            return False
        
        print(f"✓ Usuário encontrado: {usuario_dict['nome']}")
        
        # Etapa 2: Verificar senha
        print("\n🔐 Etapa 2: Verificar Senha")
        senha_correta = usuario_repo.verificar_senha(email, senha)
        if not senha_correta:
            print("✗ Senha incorreta")
            return False
        
        print("✓ Senha verificada com sucesso")
        
        # Etapa 3: Tentar login
        print("\n🚪 Etapa 3: Login")
        usuario_login = usuario_repo.login(email, senha)
        if not usuario_login:
            print("✗ Falha no login")
            return False
        
        print("✓ Login realizado com sucesso!")
        print(f"Detalhes do Usuário:")
        print(f"ID: {usuario_login.id}")
        print(f"Nome: {usuario_login.nome}")
        print(f"Email: {usuario_login.email}")
        print(f"Admin: {usuario_login.is_admin}")
        
        return True
    
    except Exception as e:
        print(f"\n❌ Erro durante o teste de login: {str(e)}")
        logging.error(f"Erro no teste de login: {str(e)}", exc_info=True)
        return False

def main():
    # Email e senhas para teste
    email = 'guh.larocca@gmail.com'
    senhas_para_testar = [
        'Larocca@2024!',  # Nova senha definida anteriormente
        'admin123',
        'Admin123',
        'Larocca@123',
        'larocca@123'
    ]
    
    # Testar cada senha
    for senha in senhas_para_testar:
        print(f"\n🔐 Testando senha: {senha}")
        resultado = testar_login_completo(email, senha)
        
        if resultado:
            print("\n✅ Login bem-sucedido!")
            break
        else:
            print("\n❌ Falha no login")

if __name__ == "__main__":
    main()
