from database.usuario_repositorio import UsuarioRepositorio
import logging

# Configurar logging
logging.basicConfig(level=logging.DEBUG)

def testar_login(email, senha):
    try:
        # Criar repositório de usuários
        usuario_repo = UsuarioRepositorio()
        
        # Tentar fazer login
        usuario = usuario_repo.login(email, senha)
        
        if usuario:
            print("\n✓ Login bem-sucedido!")
            print("\n📋 Informações do Usuário:")
            print(f"ID: {usuario.id}")
            print(f"Nome: {usuario.nome}")
            print(f"Email: {usuario.email}")
            print(f"Admin: {usuario.is_admin}")
            print(f"Foto de Perfil: {usuario.profile_photo}")
            return True
        else:
            print(f"\n✗ Falha no login para o email {email}")
            return False
    
    except Exception as e:
        print(f"\n❌ Erro durante o teste de login: {str(e)}")
        return False

if __name__ == "__main__":
    # Definir email e senhas para teste
    email = 'guh.larocca@gmail.com'
    senhas_para_testar = [
        'admin123',
        'Admin123',
        'Larocca@123',
        'larocca@123',
        'Gustavo123!',
        'gustavo123!'
    ]
    
    for senha in senhas_para_testar:
        print(f"\n🔐 Testando senha: {senha}")
        resultado = testar_login(email, senha)
        if resultado:
            break
