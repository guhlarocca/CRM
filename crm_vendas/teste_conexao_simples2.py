import os
from dotenv import load_dotenv
import psycopg2
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s: %(message)s')

def testar_conexao():
    try:
        # Carregar variáveis de ambiente
        load_dotenv()
        
        # Configurações
        db_params = {
            'host': os.getenv('DB_HOST'),
            'port': os.getenv('DB_PORT', '5432'),
            'dbname': os.getenv('DB_NAME', 'postgres'),
            'user': os.getenv('DB_USER'),
            'password': os.getenv('DB_PASS'),
            'sslmode': 'require'
        }
        
        # Criar string de conexão
        conn_str = " ".join([f"{key}={value}" for key, value in db_params.items()])
        
        logging.info("Tentando conectar...")
        logging.info(f"Host: {db_params['host']}")
        logging.info(f"Port: {db_params['port']}")
        logging.info(f"User: {db_params['user']}")
        
        # Conectar
        conn = psycopg2.connect(conn_str)
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

if __name__ == "__main__":
    testar_conexao()
