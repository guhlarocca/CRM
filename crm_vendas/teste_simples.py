import os
from dotenv import load_dotenv
import psycopg2
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s: %(message)s')

def testar_conexao():
    try:
        # Carregar variáveis de ambiente do novo arquivo
        load_dotenv('.env.new')

        # Configurações de conexão
        conn_params = {
            'host': os.getenv('DB_HOST'),
            'port': os.getenv('DB_PORT', '5432'),
            'dbname': os.getenv('DB_NAME', 'postgres'),
            'user': os.getenv('DB_USER'),
            'password': os.getenv('DB_PASS'),
            'sslmode': 'require'
        }

        logging.info("Tentando conectar ao banco...")
        logging.info(f"Host: {conn_params['host']}")
        logging.info(f"Port: {conn_params['port']}")
        logging.info(f"User: {conn_params['user']}")
        
        conn = psycopg2.connect(**conn_params)
        conn.set_client_encoding('UTF8')
        logging.info("Conexão estabelecida com sucesso!")

        cur = conn.cursor()
        cur.execute('SELECT version();')
        version = cur.fetchone()
        logging.info(f"Versão do PostgreSQL: {version[0]}")

        cur.close()
        conn.close()

    except Exception as e:
        logging.error(f"Erro: {str(e)}")
        logging.error(f"Tipo do erro: {type(e)}")
        if isinstance(e, psycopg2.Error):
            logging.error(f"Código do erro PostgreSQL: {e.pgcode}")
            logging.error(f"Mensagem do erro PostgreSQL: {e.pgerror}")

if __name__ == "__main__":
    testar_conexao()
