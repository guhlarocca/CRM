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
        # URL de conexão do Supabase (substitua com seus valores)
        DATABASE_URL = "postgresql://postgres:[SUA_SENHA]@db.hixycllemctkfmxgltgu.supabase.co:5432/postgres"
        
        logging.info("Tentando conectar usando URL direta...")
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
