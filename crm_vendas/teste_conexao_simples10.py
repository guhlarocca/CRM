import psycopg2
import logging
from urllib.parse import quote_plus

# Configurar logging detalhado
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s: %(message)s'
)

def testar_conexao():
    try:
        # Configurações do banco de dados
        host = "db.hixycllemctkfmxgltgu.supabase.co"
        port = "5432"
        database = "postgres"
        user = "postgres"
        password = "Larocca@123"  # Substitua pela sua senha
        
        # Codificar a senha para URL
        encoded_password = quote_plus(password)
        
        # Construir URL de conexão com senha codificada
        DATABASE_URL = f"postgresql://{user}:{encoded_password}@{host}:{port}/{database}?sslmode=require"
        
        logging.info("Tentando conectar usando URL codificada...")
        logging.info(f"Host: {host}")
        logging.info(f"Port: {port}")
        logging.info(f"Database: {database}")
        logging.info(f"User: {user}")
        
        # Tentar conexão
        conn = psycopg2.connect(DATABASE_URL)
        
        logging.info("Conexão estabelecida com sucesso!")

        # Testar uma query simples
        with conn.cursor() as cur:
            # Verificar encoding
            cur.execute("SHOW client_encoding;")
            encoding = cur.fetchone()[0]
            logging.info(f"Encoding atual do cliente: {encoding}")
            
            # Testar conexão
            cur.execute('SELECT current_timestamp;')
            result = cur.fetchone()
            logging.info(f"Timestamp do banco: {result[0]}")

        conn.close()
        logging.info("Conexão fechada com sucesso")

    except psycopg2.Error as e:
        logging.error("Erro PostgreSQL:")
        logging.error(f"  Mensagem: {e.pgerror}")
        logging.error(f"  Código: {e.pgcode}")
        logging.error(f"  Detalhes: {str(e)}")
    except Exception as e:
        logging.error(f"Erro inesperado: {str(e)}")
        logging.error(f"Tipo do erro: {type(e)}")
        import traceback
        logging.error(f"Traceback completo:\n{traceback.format_exc()}")

if __name__ == "__main__":
    testar_conexao()
