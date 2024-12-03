import os
from dotenv import load_dotenv
import psycopg2
import logging
import base64

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s: %(message)s')

def testar_conexao():
    try:
        # Carregar variáveis de ambiente
        load_dotenv()

        # Codificar a senha em base64
        password = base64.b64encode(os.getenv('DB_PASS', '').encode()).decode()

        # Configurações de conexão
        conn_params = {
            'host': os.getenv('DB_HOST'),
            'port': os.getenv('DB_PORT', '5432'),
            'dbname': os.getenv('DB_NAME', 'postgres'),
            'user': os.getenv('DB_USER'),
            'password': password,
            'sslmode': 'require'
        }

        logging.info("Tentando conectar ao banco...")
        conn = psycopg2.connect(**conn_params)
        conn.set_client_encoding('UTF8')
        logging.info("Conexão estabelecida com sucesso!")

        cur = conn.cursor()
        
        # Verificar se a tabela usuarios existe
        cur.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_name = 'usuarios'
            );
        """)
        tabela_existe = cur.fetchone()[0]
        
        if tabela_existe:
            logging.info("Tabela 'usuarios' existe!")
            
            # Contar número de usuários
            cur.execute("SELECT COUNT(*) FROM usuarios;")
            num_usuarios = cur.fetchone()[0]
            logging.info(f"Número de usuários cadastrados: {num_usuarios}")
            
            # Listar todos os usuários
            cur.execute("SELECT id, nome, email FROM usuarios;")
            usuarios = cur.fetchall()
            for usuario in usuarios:
                logging.info(f"ID: {usuario[0]}, Nome: {usuario[1]}, Email: {usuario[2]}")
        else:
            logging.error("Tabela 'usuarios' não existe!")
            
            # Criar a tabela
            logging.info("Criando tabela 'usuarios'...")
            cur.execute("""
                CREATE TABLE usuarios (
                    id SERIAL PRIMARY KEY,
                    nome VARCHAR(100) NOT NULL,
                    email VARCHAR(100) UNIQUE NOT NULL,
                    senha VARCHAR(255) NOT NULL,
                    is_admin BOOLEAN DEFAULT FALSE,
                    profile_photo VARCHAR(255)
                );
            """)
            conn.commit()
            logging.info("Tabela 'usuarios' criada com sucesso!")
            
            # Criar usuário admin padrão
            from werkzeug.security import generate_password_hash
            import bcrypt
            
            salt = bcrypt.gensalt()
            senha_hash = bcrypt.hashpw('admin123'.encode('utf-8'), salt)
            
            cur.execute("""
                INSERT INTO usuarios (nome, email, senha, is_admin)
                VALUES (%s, %s, %s, %s)
            """, ('Admin', 'admin@admin.com', senha_hash.decode('utf-8'), True))
            conn.commit()
            logging.info("Usuário admin criado com sucesso!")

        cur.close()
        conn.close()

    except Exception as e:
        logging.error(f"Erro: {str(e)}")
        logging.error(f"Tipo do erro: {type(e)}")
        if isinstance(e, psycopg2.Error):
            logging.error(f"Código do erro PostgreSQL: {e.pgcode}")
            logging.error(f"Mensagem do erro PostgreSQL: {e.pgerror}")

if __name__ == "__main__":
    testar_conexao()
