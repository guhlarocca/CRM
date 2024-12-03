import os
from dotenv import load_dotenv
import psycopg2
import logging

# Configurar logging detalhado
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s: %(message)s'
)

def testar_conexao():
    try:
        # Carregar variáveis de ambiente
        load_dotenv()
        logging.info("Variáveis de ambiente carregadas")

        # Obter credenciais
        host = os.getenv('DB_HOST')
        port = os.getenv('DB_PORT', '5432')
        dbname = os.getenv('DB_NAME', 'postgres')
        user = os.getenv('DB_USER')
        password = os.getenv('DB_PASS')

        # Criar string de conexão explícita
        conn_string = (
            f"host='{host}' "
            f"port='{port}' "
            f"dbname='{dbname}' "
            f"user='{user}' "
            f"password='{password}' "
            f"sslmode='require' "
            f"client_encoding='LATIN1'"  # Forçar encoding
        )

        logging.info("Tentando conectar com string de conexão explícita...")
        
        # Tentar conexão
        conn = psycopg2.connect(conn_string)
        
        logging.info("Conexão estabelecida com sucesso!")
        
        # Verificar encoding atual
        cur = conn.cursor()
        cur.execute("SHOW client_encoding;")
        encoding = cur.fetchone()[0]
        logging.info(f"Encoding atual do cliente: {encoding}")
        
        # Testar uma query simples
        cur.execute('SELECT current_timestamp;')
        result = cur.fetchone()
        logging.info(f"Timestamp do banco: {result[0]}")
        
        cur.close()
        conn.close()
        logging.info("Conexão fechada com sucesso")

    except psycopg2.Error as e:
        logging.error(f"Erro PostgreSQL: {e.pgerror}")
        logging.error(f"Código do erro: {e.pgcode}")
        logging.error(f"Detalhes do erro: {str(e)}")
    except Exception as e:
        logging.error(f"Erro inesperado: {str(e)}")
        logging.error(f"Tipo do erro: {type(e)}")

if __name__ == "__main__":
    testar_conexao()
