import os
from dotenv import load_dotenv
import psycopg2
import logging
from urllib.parse import quote_plus

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s: %(message)s')

def testar_conexao():
    try:
        # Carregar variáveis de ambiente
        load_dotenv()
        
        # Criar URL de conexão direta
        password = quote_plus(os.getenv('DB_PASS', ''))
        host = os.getenv('DB_HOST', '')
        port = os.getenv('DB_PORT', '5432')
        dbname = os.getenv('DB_NAME', 'postgres')
        user = os.getenv('DB_USER', 'postgres')
        
        # Construir DSN
        dsn = f"postgresql://{user}:{password}@{host}:{port}/{dbname}?sslmode=require"
        
        logging.info("Tentando conectar...")
        logging.info(f"Host: {host}")
        logging.info(f"Port: {port}")
        logging.info(f"User: {user}")
        
        # Conectar
        conn = psycopg2.connect(dsn)
        conn.set_client_encoding('LATIN1')
        logging.info("Conexão estabelecida com sucesso!")
        
        # Testar uma query simples
        cur = conn.cursor()
        cur.execute('SELECT version();')
        version = cur.fetchone()
        logging.info(f"Versão do PostgreSQL: {version[0]}")
        
        cur.close()
        conn.close()
        
    except Exception as e:
        logging.error(f"Erro ao conectar: {str(e)}")
        logging.error(f"Tipo do erro: {type(e)}")
        if isinstance(e, psycopg2.Error):
            logging.error(f"Código do erro PostgreSQL: {e.pgcode}")
            logging.error(f"Mensagem do erro PostgreSQL: {e.pgerror}")

if __name__ == "__main__":
    testar_conexao()
