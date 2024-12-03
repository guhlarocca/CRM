import os
from dotenv import load_dotenv
import logging
import psycopg2

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

class ConexaoSupabase:
    def __init__(self):
        self.db_config = {
            'dbname': os.getenv('DB_NAME', 'postgres'),
            'user': os.getenv('DB_USER'),
            'password': os.getenv('DB_PASS'),
            'host': os.getenv('DB_HOST'),
            'port': os.getenv('DB_PORT', '5432')
        }

    def get_connection(self):
        try:
            return psycopg2.connect(**self.db_config)
        except Exception as e:
            logger.error(f"Erro na conexão: {e}")
            return None

    def get_session(self):
        return self.get_connection()

def criar_cliente_supabase():
    try:
        return ConexaoSupabase()
    except Exception as e:
        logger.error(f"Erro ao criar cliente: {e}")
        return None
