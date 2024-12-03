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
        # 1. Carregar variáveis de ambiente
        load_dotenv()
        logging.info("Variáveis de ambiente carregadas")

        # 2. Obter credenciais
        host = os.getenv('DB_HOST')
        port = os.getenv('DB_PORT', '5432')
        dbname = os.getenv('DB_NAME', 'postgres')
        user = os.getenv('DB_USER')
        password = os.getenv('DB_PASS')

        # 3. Verificar se todas as credenciais necessárias estão presentes
        required_vars = {
            'DB_HOST': host,
            'DB_USER': user,
            'DB_PASS': password
        }

        for var_name, var_value in required_vars.items():
            if not var_value:
                logging.error(f"Variável de ambiente {var_name} não encontrada")
                return

        logging.info(f"Conectando ao banco de dados:")
        logging.info(f"Host: {host}")
        logging.info(f"Port: {port}")
        logging.info(f"Database: {dbname}")
        logging.info(f"User: {user}")

        # 4. Tentar conexão
        conn = psycopg2.connect(
            dbname=dbname,
            user=user,
            password=password,
            host=host,
            port=port,
            sslmode='require'
        )

        logging.info("Conexão estabelecida com sucesso!")

        # 5. Testar uma query simples
        with conn.cursor() as cur:
            cur.execute('SELECT current_timestamp;')
            result = cur.fetchone()
            logging.info(f"Timestamp do banco: {result[0]}")

        conn.close()
        logging.info("Conexão fechada com sucesso")

    except psycopg2.Error as e:
        logging.error(f"Erro PostgreSQL: {e.pgerror}")
        logging.error(f"Código do erro: {e.pgcode}")
    except Exception as e:
        logging.error(f"Erro inesperado: {str(e)}")
        logging.error(f"Tipo do erro: {type(e)}")

if __name__ == "__main__":
    testar_conexao()
