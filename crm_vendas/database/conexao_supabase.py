import os
from dotenv import load_dotenv
import logging

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
        self._psycopg2 = None

    @property
    def psycopg2(self):
        if self._psycopg2 is None:
            try:
                import psycopg2
                self._psycopg2 = psycopg2
            except ImportError:
                logger.error("Erro ao importar psycopg2")
                raise
        return self._psycopg2

    def get_connection(self):
        try:
            # Tentar importar e usar o psycopg2
            pg = self.psycopg2
            conn = pg.connect(**self.db_config)
            # Testar a conexão
            with conn.cursor() as cur:
                cur.execute('SELECT 1')
            return conn
        except Exception as e:
            logger.error(f"Erro na conexão: {str(e)}")
            return None

    def get_session(self):
        return self.get_connection()

def criar_cliente_supabase():
    try:
        return ConexaoSupabase()
    except Exception as e:
        logger.error(f"Erro ao criar cliente: {str(e)}")
        return None
