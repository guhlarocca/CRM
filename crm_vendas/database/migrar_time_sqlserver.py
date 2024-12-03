import pyodbc
from datetime import datetime
from dotenv import load_dotenv
import os

# Carregar variáveis de ambiente
load_dotenv()

def criar_tabela_time():
    # Configuração da conexão usando as variáveis de ambiente
    conn = pyodbc.connect(
        f'DRIVER={os.getenv("DB_DRIVER")};'
        f'SERVER={os.getenv("DB_SERVER")};'
        f'DATABASE={os.getenv("DB_NAME")};'
        f'UID={os.getenv("DB_USER")};'
        f'PWD={os.getenv("DB_PASSWORD")};'
    )
    cursor = conn.cursor()

    try:
        # Verificar se a tabela já existe
        cursor.execute("""
            IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'time')
            BEGIN
                CREATE TABLE time (
                    id INT IDENTITY(1,1) PRIMARY KEY,
                    nome NVARCHAR(100) NOT NULL,
                    email NVARCHAR(100) NOT NULL UNIQUE,
                    telefone NVARCHAR(20),
                    leads INT DEFAULT 0,
                    vendas INT DEFAULT 0,
                    data_criacao DATETIME DEFAULT GETDATE()
                )
            END
        """)
        
        # Adicionar coluna vendedor_id na tabela leads se não existir
        cursor.execute("""
            IF NOT EXISTS (
                SELECT * FROM sys.columns 
                WHERE object_id = OBJECT_ID('leads') AND name = 'vendedor_id'
            )
            BEGIN
                ALTER TABLE leads
                ADD vendedor_id INT,
                CONSTRAINT FK_Lead_Vendedor FOREIGN KEY (vendedor_id)
                REFERENCES time(id)
            END
        """)

        conn.commit()
        print("Tabela 'time' e relacionamento com 'leads' criados com sucesso!")

    except Exception as e:
        print(f"Erro ao criar tabela: {str(e)}")
        conn.rollback()

    finally:
        cursor.close()
        conn.close()

if __name__ == '__main__':
    criar_tabela_time()
