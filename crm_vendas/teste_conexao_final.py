import psycopg2
import logging
import sys
from urllib.parse import quote

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s: %(message)s')

def testar_conexao():
    try:
        # Dados de conexão
        password = quote('Larocca@1234')  # Codifica a senha para URL
        DATABASE_URL = f"postgresql://postgres:{password}@db.hixycllemctkfmxgltgu.supabase.co:5432/postgres?client_encoding=utf8"
        
        logging.info("Tentando conectar ao banco de dados...")
        conn = psycopg2.connect(DATABASE_URL)
        logging.info("Conexão estabelecida com sucesso!")
        
        # Verificar codificação atual
        cur = conn.cursor()
        cur.execute("SELECT current_setting('client_encoding') as encoding;")
        encoding = cur.fetchone()[0]
        logging.info(f"Codificação atual do cliente: {encoding}")
        
        # Testar versão
        cur.execute('SELECT version();')
        version = cur.fetchone()[0]
        logging.info(f"Versão do PostgreSQL: {version}")
        
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
