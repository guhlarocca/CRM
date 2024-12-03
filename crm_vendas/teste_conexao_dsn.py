import psycopg2
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s: %(message)s')

def testar_conexao():
    try:
        # String de conexão DSN direta
        dsn = "host=db.hixycllemctkfmxgltgu.supabase.co port=5432 dbname=postgres user=postgres password=Larocca@1234 sslmode=require client_encoding=LATIN1"
        
        logging.info("Tentando conectar usando DSN...")
        conn = psycopg2.connect(dsn)
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
