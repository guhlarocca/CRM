import psycopg
import os
from dotenv import load_dotenv
import logging

# Configurar logging
logging.basicConfig(level=logging.DEBUG)

def debug_usuario(email):
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
                # Buscar usuário pelo email com todos os detalhes
                cur.execute("SELECT * FROM usuarios WHERE email = %s", (email,))
                usuario = cur.fetchone()
                
                if usuario:
                    # Imprimir todos os campos do usuário
                    colunas = [desc.name for desc in cur.description]
                    for coluna, valor in zip(colunas, usuario):
                        print(f"{coluna}: {valor}")
                else:
                    print(f"\n✗ Usuário com email {email} não encontrado!")

    except Exception as e:
        print(f"Erro: {str(e)}")
        print(f"Tipo do erro: {type(e)}")

if __name__ == "__main__":
    # Debugar usuário
    debug_usuario('guh.larocca@gmail.com')
