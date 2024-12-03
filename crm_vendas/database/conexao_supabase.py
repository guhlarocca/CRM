import os
from dotenv import load_dotenv
import logging
import sys
import importlib.util

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Adicionar diretório do projeto ao path para importações
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

load_dotenv()

def import_psycopg2():
    """Importa o psycopg2 de forma segura"""
    try:
        # Tenta importar psycopg2 primeiro
        if importlib.util.find_spec("psycopg2") is not None:
            import psycopg2
            return psycopg2
        else:
            logger.warning("psycopg2 não encontrado, tentando psycopg2-binary")
            # Se não encontrar, tenta o psycopg2-binary
            if importlib.util.find_spec("psycopg2-binary") is not None:
                import psycopg2
                return psycopg2
            else:
                raise ImportError("Nem psycopg2 nem psycopg2-binary foram encontrados")
    except Exception as e:
        logger.error(f"Erro ao importar psycopg2: {str(e)}")
        return None

# Importar psycopg2
psycopg2 = import_psycopg2()
if psycopg2 is None:
    logger.error("Não foi possível importar psycopg2. Verifique a instalação.")
    sys.exit(1)

class ConexaoSupabase:
    def __init__(self):
        # Verificar variáveis de ambiente necessárias
        required_vars = ['DB_HOST', 'DB_USER', 'DB_PASS']
        missing_vars = [var for var in required_vars if not os.getenv(var)]
        if missing_vars:
            raise ValueError(f"As seguintes variáveis de ambiente são necessárias: {', '.join(missing_vars)}")

        # Configurações do Supabase
        self.db_config = {
            'host': os.getenv('DB_HOST'),
            'port': os.getenv('DB_PORT', '5432'),
            'dbname': os.getenv('DB_NAME', 'postgres'),
            'user': os.getenv('DB_USER'),
            'password': os.getenv('DB_PASS'),
            'client_encoding': 'UTF8'  # Mudando para UTF8
        }

    def get_connection(self):
        """Retorna uma conexão direta do psycopg2"""
        try:
            logger.info(f"Tentando conectar em: {self.db_config['host']}:{self.db_config['port']} como {self.db_config['user']}")
            conn = psycopg2.connect(
                dbname=self.db_config['dbname'],
                user=self.db_config['user'],
                password=self.db_config['password'],
                host=self.db_config['host'],
                port=self.db_config['port']
            )
            conn.set_client_encoding('UTF8')
            return conn
        except Exception as e:
            logger.error(f"Erro ao criar conexão: {str(e)}")
            return None

    def get_session(self):
        """Retorna uma sessão SQLAlchemy"""
        try:
            conn = self.get_connection()
            if conn:
                return conn
            else:
                raise Exception("Conexão não estabelecida")
        except Exception as e:
            logger.error(f"Erro ao criar sessão: {str(e)}")
            return None

def criar_cliente_supabase():
    """
    Cria e retorna um cliente Supabase para operações de banco de dados
    """
    try:
        supabase = ConexaoSupabase()
        return supabase
    except Exception as e:
        logger.error(f"Erro ao criar cliente Supabase: {str(e)}")
        return None
