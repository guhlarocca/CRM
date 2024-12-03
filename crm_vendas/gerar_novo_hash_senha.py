import bcrypt
import psycopg
import os
from dotenv import load_dotenv

def gerar_novo_hash(senha_original):
    # Gerar novo salt e hash
    salt = bcrypt.gensalt()
    senha_bytes = senha_original.encode('utf-8')
    novo_hash = bcrypt.hashpw(senha_bytes, salt)
    
    return novo_hash.decode('utf-8')

def atualizar_senha_no_banco(email, nova_senha):
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
                # Gerar novo hash
                novo_hash = gerar_novo_hash(nova_senha)
                
                # Atualizar senha no banco
                cur.execute(
                    "UPDATE usuarios SET senha = %s WHERE email = %s", 
                    (novo_hash, email)
                )
                
                # Confirmar a transação
                conn.commit()
                
                print(f"\n✓ Senha atualizada com sucesso para {email}")
                print(f"Novo hash: {novo_hash}")
                
                return novo_hash
    
    except Exception as e:
        print(f"Erro: {str(e)}")
        print(f"Tipo do erro: {type(e)}")
        return None

if __name__ == "__main__":
    # Definir email e nova senha
    email = 'guh.larocca@gmail.com'
    nova_senha = 'Larocca@2024!'  # SUBSTITUA PELA NOVA SENHA
    
    # Gerar e atualizar hash
    atualizar_senha_no_banco(email, nova_senha)
