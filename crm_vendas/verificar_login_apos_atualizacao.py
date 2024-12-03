import psycopg
import os
import bcrypt
from dotenv import load_dotenv
import logging

# Configurar logging
logging.basicConfig(level=logging.DEBUG)

def verificar_login(email, senha):
    # Carregar variáveis de ambiente
    load_dotenv()
    
    # Configurações de conexão
    conninfo = (
        f"host={os.getenv('DB_HOST')} "
        f"port={os.getenv('DB_PORT', '5432')} "
        f"dbname={os.getenv('DB_NAME', 'postgres')} "
        f"user={os.getenv('DB_USER')} "
        f"password={os.getenv('DB_PASS')} "
        "sslmode=require"
    )
    
    try:
        # Conectar ao banco
        with psycopg.connect(conninfo) as conn:
            # Criar cursor
            with conn.cursor() as cur:
                # Buscar usuário pelo email
                cur.execute("SELECT id, nome, email, senha FROM usuarios WHERE email = %s", (email,))
                usuario = cur.fetchone()
                
                if not usuario:
                    print(f"\n✗ Nenhum usuário encontrado com o email {email}")
                    return False
                
                # Desempacotar informações do usuário
                user_id, nome, email_bd, senha_hash = usuario
                
                print("\n📋 Informações do Usuário:")
                print(f"ID: {user_id}")
                print(f"Nome: {nome}")
                print(f"Email: {email_bd}")
                print(f"Hash da Senha Armazenado: {senha_hash}")
                
                # Converter senha para bytes
                senha_bytes = senha.encode('utf-8')
                senha_hash_bytes = senha_hash.encode('utf-8')
                
                # Verificação da senha
                if bcrypt.checkpw(senha_bytes, senha_hash_bytes):
                    print("\n✓ Login AUTORIZADO!")
                    return True
                else:
                    print("\n✗ Login NEGADO!")
                    return False
    
    except Exception as e:
        print(f"\n❌ Erro durante o teste de login: {str(e)}")
        print(f"Tipo do erro: {type(e)}")
        return False

if __name__ == "__main__":
    # Definir email e senhas para teste
    email = 'guh.larocca@gmail.com'
    senhas_para_testar = [
        'Larocca@2024!',  # Nova senha definida no script anterior
        'Larocca@2024',
        'larocca@2024!'
    ]
    
    for senha in senhas_para_testar:
        print(f"\n🔐 Testando senha: {senha}")
        resultado = verificar_login(email, senha)
        if resultado:
            break
