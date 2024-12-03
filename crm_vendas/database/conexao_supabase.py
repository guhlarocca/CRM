import os
from dotenv import load_dotenv
import logging
from supabase import create_client, Client

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

class ConexaoSupabase:
    def __init__(self):
        self.supabase_url = os.getenv('SUPABASE_URL')
        self.supabase_key = os.getenv('SUPABASE_KEY')
        self.client = create_client(self.supabase_url, self.supabase_key)

    def table(self, nome_tabela):
        return self.client.table(nome_tabela)

def criar_cliente_supabase():
    try:
        return ConexaoSupabase()
    except Exception as e:
        logger.error(f"Erro ao criar cliente: {str(e)}")
        return None
