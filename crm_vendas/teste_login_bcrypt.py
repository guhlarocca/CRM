import psycopg
import os
import bcrypt
from dotenv import load_dotenv
import logging

# Configurar logging
logging.basicConfig(level=logging.DEBUG)

def testar_login(email, senha_tentativa):
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
                    
                    # Converter senha_tentativa para bytes
                    senha_tentativa_bytes = senha_tentativa.encode('utf-8')
                    
                    # Converter hash armazenado para bytes
                    senha_hash_bytes = senha_hash.encode('utf-8')
                    
                    # Verificar senha usando bcrypt
                    if bcrypt.checkpw(senha_tentativa_bytes, senha_hash_bytes):
                        print(f"\n✓ Login bem-sucedido!")
                        print(f"ID: {id_usuario}")
                        print(f"Nome: {nome}")
                        print(f"Email: {email_bd}")
                        return True
                    else:
                        print("\n✗ Senha incorreta!")
                        print(f"Hash tentativa: {bcrypt.hashpw(senha_tentativa_bytes, bcrypt.gensalt())}")
                        print(f"Hash armazenado: {senha_hash}")
                        return False
                else:
                    print(f"\n✗ Usuário com email {email} não encontrado!")
                    return False

    except Exception as e:
        print(f"Erro: {str(e)}")
        print(f"Tipo do erro: {type(e)}")
        return False

if __name__ == "__main__":
    # Testar login com diferentes senhas
    senhas_para_testar = [
        'admin123',
        'Admin123',
        'Larocca@123',
        'larocca@123'
    ]
    
    for senha in senhas_para_testar:
        print(f"\nTestando senha: {senha}")
        testar_login('guh.larocca@gmail.com', senha)
