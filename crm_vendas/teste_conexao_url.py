import psycopg2
import logging
from urllib.parse import quote_plus

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s: %(message)s')

def testar_conexao():
    try:
        # Parâmetros de conexão
        host = "db.hixycllemctkfmxgltgu.supabase.co"
        port = "5432"
        dbname = "postgres"
        user = "postgres"
        password = quote_plus("Larocca@1234")  # Codificar a senha para URL
        
        # String de conexão no formato URL
        conn_url = f"postgresql://{user}:{password}@{host}:{port}/{dbname}?sslmode=require&client_encoding=LATIN1"
        
        logging.info("Tentando conectar usando URL...")
        conn = psycopg2.connect(conn_url)
        logging.info("Conexão estabelecida com sucesso!")
        
        cur = conn.cursor()
        cur.execute('SELECT version();')
        version = cur.fetchone()
        logging.info(f"Versão do PostgreSQL: {version[0]}")
        
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
