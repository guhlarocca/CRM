import psycopg
import os
from dotenv import load_dotenv
import logging
from werkzeug.security import check_password_hash

# Configurar logging
logging.basicConfig(level=logging.DEBUG)

def testar_login(email, senha):
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
                
                if usuario:
                    id_usuario, nome, email_bd, senha_hash = usuario
                    
                    # Verificar senha
                    if check_password_hash(senha_hash, senha):
                        print(f"\n✓ Login bem-sucedido!")
                        print(f"ID: {id_usuario}")
                        print(f"Nome: {nome}")
                        print(f"Email: {email_bd}")
                        return True
                    else:
                        print("\n✗ Senha incorreta!")
                        return False
                else:
                    print(f"\n✗ Usuário com email {email} não encontrado!")
                    return False

    except Exception as e:
        print(f"Erro: {str(e)}")
        print(f"Tipo do erro: {type(e)}")
        return False

if __name__ == "__main__":
    # Testar login
    testar_login('guh.larocca@gmail.com', 'admin123')
