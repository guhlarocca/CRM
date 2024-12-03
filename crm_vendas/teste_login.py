import psycopg
import os
from dotenv import load_dotenv
import logging

# Configurar logging
logging.basicConfig(level=logging.DEBUG)

def testar_usuario():
    # Carregar variáveis de ambiente
    load_dotenv()
    
    # Configurações de conexão
    conninfo = (
        f"host={os.getenv('DB_HOST')} "
        f"port={os.getenv('DB_PORT', '5432')} "
        f"dbname={os.getenv('DB_NAME', 'postgres')} "
        f"user={os.getenv('DB_USER')} "
        f"password={os.getenv('DB_PASS')} "
        "sslmode=require"
    )
    
    try:
        # Conectar ao banco
        with psycopg.connect(conninfo) as conn:
            # Criar cursor
            with conn.cursor() as cur:
                # Verificar se a tabela existe
                cur.execute("""
                    SELECT EXISTS (
                        SELECT FROM information_schema.tables 
                        WHERE table_name = 'usuarios'
                    );
                """)
                tabela_existe = cur.fetchone()[0]
                print(f"\nTabela 'usuarios' existe? {tabela_existe}")
                
                if tabela_existe:
                    # Listar todos os usuários
                    cur.execute("SELECT id, email, nome FROM usuarios;")
                    usuarios = cur.fetchall()
                    print("\nUsuários cadastrados:")
                    for usuario in usuarios:
                        print(f"ID: {usuario[0]}, Email: {usuario[1]}, Nome: {usuario[2]}")
                    
                    # Verificar estrutura da tabela
                    cur.execute("""
                        SELECT column_name, data_type 
                        FROM information_schema.columns 
                        WHERE table_name = 'usuarios';
                    """)
                    colunas = cur.fetchall()
                    print("\nEstrutura da tabela:")
                    for coluna in colunas:
                        print(f"Coluna: {coluna[0]}, Tipo: {coluna[1]}")
                else:
                    print("\nA tabela 'usuarios' não existe!")
                    print("Criando tabela...")
                    
                    # Criar tabela de usuários
                    cur.execute("""
                        CREATE TABLE IF NOT EXISTS usuarios (
                            id SERIAL PRIMARY KEY,
                            email VARCHAR(255) UNIQUE NOT NULL,
                            senha VARCHAR(255) NOT NULL,
                            nome VARCHAR(255) NOT NULL,
                            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                        );
                    """)
                    conn.commit()
                    print("Tabela criada com sucesso!")
                    
                    # Criar usuário de teste
                    from werkzeug.security import generate_password_hash
                    senha_hash = generate_password_hash('admin123')
                    cur.execute("""
                        INSERT INTO usuarios (email, senha, nome)
                        VALUES (%s, %s, %s)
                        ON CONFLICT (email) DO NOTHING
                        RETURNING id;
                    """, ('admin@admin.com', senha_hash, 'Administrador'))
                    conn.commit()
                    print("Usuário de teste criado: admin@admin.com / admin123")

    except Exception as e:
        print(f"Erro: {str(e)}")
        print(f"Tipo do erro: {type(e)}")

if __name__ == "__main__":
    testar_usuario()
