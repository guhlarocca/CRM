import psycopg
import os
import bcrypt
from dotenv import load_dotenv
import logging

# Configurar logging
logging.basicConfig(level=logging.DEBUG)

def redefinir_senha(email, nova_senha):
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
                # Gerar hash da nova senha
                nova_senha_bytes = nova_senha.encode('utf-8')
                senha_hash = bcrypt.hashpw(nova_senha_bytes, bcrypt.gensalt())
                
                # Converter hash para string
                senha_hash_str = senha_hash.decode('utf-8')
                
                # Atualizar senha no banco
                cur.execute(
                    "UPDATE usuarios SET senha = %s WHERE email = %s", 
                    (senha_hash_str, email)
                )
                
                # Confirmar a transação
                conn.commit()
                
                print(f"\n✓ Senha atualizada com sucesso para {email}")
                print(f"Novo hash: {senha_hash_str}")

    except Exception as e:
        print(f"Erro: {str(e)}")
        print(f"Tipo do erro: {type(e)}")

if __name__ == "__main__":
    # Definir nova senha
    email = 'guh.larocca@gmail.com'
    nova_senha = 'NovaSenha123!'  # SUBSTITUA PELA SENHA DESEJADA
    
    redefinir_senha(email, nova_senha)
