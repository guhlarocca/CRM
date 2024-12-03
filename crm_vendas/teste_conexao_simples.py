import os
from dotenv import load_dotenv
import psycopg2
import logging
import urllib.parse

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s: %(message)s')

def testar_conexao():
    try:
        load_dotenv()
        
        # Codificar a senha para garantir que caracteres especiais sejam tratados corretamente
        password = urllib.parse.quote_plus(os.getenv('DB_PASS'))
        
        # Construir DSN com a senha codificada
        dsn = f"postgresql://{os.getenv('DB_USER')}:{password}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
        
        logging.info("Tentando conectar usando DSN...")
        conn = psycopg2.connect(dsn)
        
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

if __name__ == "__main__":
    testar_conexao()
