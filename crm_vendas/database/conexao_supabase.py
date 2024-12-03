import os
from dotenv import load_dotenv
import logging
import sys

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Adicionar diretório do projeto ao path para importações
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

load_dotenv()

try:
    import psycopg2
    from psycopg2 import Error as PsycopgError
except Exception as e:
    logger.error(f"Erro ao importar psycopg2: {str(e)}")
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
            'client_encoding': 'LATIN1'
        }

    def get_connection(self):
        """Retorna uma conexão direta do psycopg2"""
        try:
            logger.info(f"Tentando conectar em: {self.db_config['host']}:{self.db_config['port']} como {self.db_config['user']}")
            return psycopg2.connect(**self.db_config)
        except PsycopgError as e:
            logger.error(f"Erro detalhado ao criar conexão: {e}")
            logger.error(f"Configurações de conexão: {self.db_config}")
            return None
        except Exception as e:
            logger.error(f"Erro inesperado ao criar conexão: {e}")
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
            logger.error(f"Erro ao criar sessão: {e}")
            return None

def criar_cliente_supabase():
    """
    Cria e retorna um cliente Supabase para operações de banco de dados
    """
    try:
        from supabase import create_client, Client
        
        # Carregar variáveis de ambiente
        url = os.getenv('SUPABASE_URL')
        key = os.getenv('SUPABASE_KEY')
        
        if not url or not key:
            raise ValueError("Variáveis SUPABASE_URL e SUPABASE_KEY são necessárias")
        
        supabase: Client = create_client(url, key)
        return supabase
    
    except ImportError:
        logger.error("Biblioteca supabase não instalada. Instale com: pip install supabase")
        return None
    except Exception as e:
        logger.error(f"Erro ao criar cliente Supabase: {e}")
        return None
