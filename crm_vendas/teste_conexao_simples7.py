import os
from dotenv import load_dotenv
import psycopg2
import logging
import sys

# Configurar logging detalhado
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s: %(message)s'
)

def testar_conexao():
    try:
        # Forçar encoding do sistema
        if sys.platform.startswith('win'):
            import locale
            sys.stdout.reconfigure(encoding=locale.getpreferredencoding())

        # Carregar variáveis de ambiente
        load_dotenv()
        logging.info("Variáveis de ambiente carregadas")

        # Obter credenciais e converter para bytes se necessário
        host = os.getenv('DB_HOST', '').encode('ascii', 'ignore').decode('ascii')
        port = os.getenv('DB_PORT', '5432').encode('ascii', 'ignore').decode('ascii')
        dbname = os.getenv('DB_NAME', 'postgres').encode('ascii', 'ignore').decode('ascii')
        user = os.getenv('DB_USER', '').encode('ascii', 'ignore').decode('ascii')
        password = os.getenv('DB_PASS', '').encode('ascii', 'ignore').decode('ascii')

        # Log das credenciais (sem a senha)
        logging.info(f"Host: {host}")
        logging.info(f"Port: {port}")
        logging.info(f"Database: {dbname}")
        logging.info(f"User: {user}")

        # Tentar conexão usando psycopg2.connect diretamente com parâmetros
        conn = psycopg2.connect(
            host=host,
            port=port,
            dbname=dbname,
            user=user,
            password=password,
            sslmode='require'
        )
        
        logging.info("Conexão estabelecida com sucesso!")

        # Configurar encoding após conexão
        conn.set_client_encoding('UTF8')
        
        # Testar uma query simples
        with conn.cursor() as cur:
            # Verificar encoding
            cur.execute("SHOW client_encoding;")
            encoding = cur.fetchone()[0]
            logging.info(f"Encoding atual do cliente: {encoding}")
            
            # Testar timestamp
            cur.execute('SELECT current_timestamp;')
            result = cur.fetchone()
            logging.info(f"Timestamp do banco: {result[0]}")

        conn.close()
        logging.info("Conexão fechada com sucesso")

    except psycopg2.Error as e:
        logging.error(f"Erro PostgreSQL: {e.pgerror}")
        logging.error(f"Código do erro: {e.pgcode}")
        logging.error(f"Detalhes completos: {str(e)}")
    except Exception as e:
        logging.error(f"Erro inesperado: {str(e)}")
        logging.error(f"Tipo do erro: {type(e)}")
        import traceback
        logging.error(f"Traceback completo:\n{traceback.format_exc()}")

if __name__ == "__main__":
    testar_conexao()
