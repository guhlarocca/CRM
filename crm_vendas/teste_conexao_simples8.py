import os
import logging
from dotenv import dotenv_values
import psycopg2

# Configurar logging detalhado
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s: %(message)s'
)

def testar_conexao():
    try:
        # Carregar variáveis de ambiente usando dotenv_values
        config = dotenv_values(".env", encoding='latin1')
        logging.info("Arquivo .env carregado com encoding latin1")

        # Obter credenciais do config
        host = config.get('DB_HOST', '')
        port = config.get('DB_PORT', '5432')
        dbname = config.get('DB_NAME', 'postgres')
        user = config.get('DB_USER', '')
        password = config.get('DB_PASS', '')

        # Log das credenciais (sem a senha)
        logging.info("Credenciais carregadas:")
        logging.info(f"Host: {host}")
        logging.info(f"Port: {port}")
        logging.info(f"Database: {dbname}")
        logging.info(f"User: {user}")

        # Criar dicionário de parâmetros de conexão
        conn_params = {
            'host': host,
            'port': port,
            'dbname': dbname,
            'user': user,
            'password': password,
            'sslmode': 'require'
        }

        # Tentar conexão
        logging.info("Tentando conectar ao banco de dados...")
        conn = psycopg2.connect(**conn_params)
        
        logging.info("Conexão estabelecida com sucesso!")

        # Testar uma query simples
        with conn.cursor() as cur:
            # Verificar encoding
            cur.execute("SHOW client_encoding;")
            encoding = cur.fetchone()[0]
            logging.info(f"Encoding atual do cliente: {encoding}")
            
            # Testar conexão
            cur.execute('SELECT current_timestamp;')
            result = cur.fetchone()
            logging.info(f"Timestamp do banco: {result[0]}")

        conn.close()
        logging.info("Conexão fechada com sucesso")

    except psycopg2.Error as e:
        logging.error("Erro PostgreSQL:")
        logging.error(f"  Mensagem: {e.pgerror}")
        logging.error(f"  Código: {e.pgcode}")
        logging.error(f"  Detalhes: {str(e)}")
    except Exception as e:
        logging.error(f"Erro inesperado: {str(e)}")
        logging.error(f"Tipo do erro: {type(e)}")
        import traceback
        logging.error(f"Traceback completo:\n{traceback.format_exc()}")

if __name__ == "__main__":
    testar_conexao()
