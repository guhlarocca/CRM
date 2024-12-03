import psycopg2
import logging
import sys

# Configurar logging detalhado
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s: %(message)s'
)

def encode_param(value):
    """Força a codificação do parâmetro para ASCII, removendo caracteres especiais"""
    if value:
        return value.encode('ascii', 'ignore').decode('ascii')
    return value

def testar_conexao():
    try:
        # Configurações do banco de dados com encoding forçado
        params = {
            'host': encode_param("db.hixycllemctkfmxgltgu.supabase.co"),
            'port': encode_param("5432"),
            'dbname': encode_param("postgres"),
            'user': encode_param("postgres"),
            'password': encode_param("Larocca@123"),  # Substitua pela sua senha
            'sslmode': 'require'
        }
        
        logging.info("Parâmetros de conexão:")
        for key, value in params.items():
            if key != 'password':
                logging.info(f"{key}: {value}")
        
        logging.info("Tentando conectar usando parâmetros separados...")
        
        # Tentar conexão com parâmetros separados
        conn = psycopg2.connect(**params)
        
        logging.info("Conexão estabelecida com sucesso!")

        # Testar uma query simples
        with conn.cursor() as cur:
            # Verificar encoding
            cur.execute("SHOW client_encoding;")
            encoding = cur.fetchone()[0]
            logging.info(f"Encoding atual do cliente: {encoding}")
            
            # Testar conexão
            cur.execute('SELECT version();')
            version = cur.fetchone()[0]
            logging.info(f"Versão do PostgreSQL: {version}")

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
