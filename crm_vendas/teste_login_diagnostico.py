import psycopg
import os
import bcrypt
from dotenv import load_dotenv
import logging

# Configurar logging
logging.basicConfig(level=logging.DEBUG)

def diagnosticar_login(email):
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
                    return
                
                # Desempacotar informações do usuário
                user_id, nome, email_bd, senha_hash = usuario
                
                print("\n📋 Informações do Usuário:")
                print(f"ID: {user_id}")
                print(f"Nome: {nome}")
                print(f"Email: {email_bd}")
                print(f"Hash da Senha: {senha_hash}")
                
                # Verificar se o hash está vazio ou None
                if not senha_hash:
                    print("\n❌ ERRO: Hash da senha está vazio!")
                    return
                
                # Verificar o formato do hash
                if not senha_hash.startswith('$2b$'):
                    print("\n❌ ERRO: Hash não parece ser um hash bcrypt válido!")
                    print("Formato esperado: $2b$[custo]$[salt+hash]")
                    return
                
                print("\n✓ Hash da senha parece estar no formato correto.")
                
    except Exception as e:
        print(f"\n❌ Erro durante o diagnóstico: {str(e)}")
        print(f"Tipo do erro: {type(e)}")

if __name__ == "__main__":
    # Definir email para diagnóstico
    email = 'guh.larocca@gmail.com'
    diagnosticar_login(email)
