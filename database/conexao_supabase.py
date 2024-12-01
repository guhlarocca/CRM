import os
from dotenv import load_dotenv
import psycopg2
import logging

load_dotenv()

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
            logging.info(f"Tentando conectar em: {self.db_config['host']}:{self.db_config['port']} como {self.db_config['user']}")
            return psycopg2.connect(**self.db_config)
        except Exception as e:
            logging.error(f"Erro detalhado ao criar conexão: {e}")
            logging.error(f"Configurações de conexão: {self.db_config}")
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
            logging.error(f"Erro ao criar sessão: {e}")
            return None
