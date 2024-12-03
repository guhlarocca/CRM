import os
from dotenv import load_dotenv
import psycopg2
import logging
import urllib.parse

# Configurar logging básico
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s: %(message)s'
)

try:
    # Carregar variáveis de ambiente
    load_dotenv()
    
    # Configurações do banco
    db_config = {
        'host': os.getenv('DB_HOST', 'db.hixycllemctkfmxgltgu.supabase.co'),
        'port': os.getenv('DB_PORT', '5432'),
        'dbname': os.getenv('DB_NAME', 'postgres'),
        'user': os.getenv('DB_USER', 'postgres'),
        'password': os.getenv('DB_PASS', 'Larocca@1234'),
        'sslmode': 'require'
    }
    
    logging.info("Tentando conectar...")
    logging.info(f"Host: {db_config['host']}")
    logging.info(f"Port: {db_config['port']}")
    logging.info(f"User: {db_config['user']}")
    
    # Conectar usando psycopg2
    conn = psycopg2.connect(**db_config)
    conn.set_client_encoding('UTF8')
    logging.info("Conectado com sucesso!")
    
    # Teste simples
    with conn.cursor() as cur:
        # Testar conexão
        cur.execute('SELECT version();')
        version = cur.fetchone()
        logging.info(f"Versão do PostgreSQL: {version[0]}")
        
        # Verificar codificação
        cur.execute("SHOW client_encoding;")
        encoding = cur.fetchone()
        logging.info(f"Codificação atual: {encoding[0]}")
    
    conn.close()
    
except Exception as e:
    logging.error(f"Erro: {str(e)}")
    logging.error(f"Tipo do erro: {type(e)}")
    if isinstance(e, psycopg2.Error):
        logging.error(f"Código do erro PostgreSQL: {e.pgcode}")
        logging.error(f"Mensagem do erro PostgreSQL: {e.pgerror}")
