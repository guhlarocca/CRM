import os
from dotenv import load_dotenv
import psycopg2
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s: %(message)s')

def testar_conexao():
    try:
        # Usar o novo arquivo .env.ansi
        load_dotenv('.env.ansi')
        
        # Configurações de conexão
        db_config = {
            'host': os.getenv('DB_HOST'),
            'port': os.getenv('DB_PORT', '5432'),
            'dbname': os.getenv('DB_NAME', 'postgres'),
            'user': os.getenv('DB_USER'),
            'password': os.getenv('DB_PASS'),
            'client_encoding': 'LATIN1',
            'sslmode': 'require'  # Adicionando sslmode de volta
        }
        
        logging.info("Tentando conectar ao banco...")
        logging.info(f"Host: {db_config['host']}")
        logging.info(f"Port: {db_config['port']}")
        logging.info(f"User: {db_config['user']}")
        
        conn = psycopg2.connect(**db_config)
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
