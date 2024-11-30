import pyodbc

def criar_banco():
    try:
        # Conectar ao SQL Server usando autenticação do Windows
        conn_str = 'DRIVER={SQL Server};SERVER=localhost;DATABASE=master;Trusted_Connection=yes;autocommit=True'
        conn = pyodbc.connect(conn_str)
        cursor = conn.cursor()
        
        print("[OK] Conectado ao SQL Server com sucesso!")
        
        # Criar banco de dados
        try:
            print("\n[...] Criando banco de dados CRM_VENDAS...")
            cursor.execute("CREATE DATABASE CRM_VENDAS")
            print("[OK] Banco de dados criado com sucesso!")
        except pyodbc.Error as e:
            if 'já existe' in str(e) or 'already exists' in str(e):
                print("\n[INFO] Banco de dados CRM_VENDAS já existe")
            else:
                raise e

        # Fechar conexão com master e conectar ao CRM_VENDAS
        conn.close()
        
        # Conectar ao banco CRM_VENDAS
        conn_str = 'DRIVER={SQL Server};SERVER=localhost;DATABASE=CRM_VENDAS;Trusted_Connection=yes;'
        conn = pyodbc.connect(conn_str)
        cursor = conn.cursor()
        
        # Criar tabela
        print("\n[...] Criando tabela leads...")
        cursor.execute("""
            IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'leads')
            BEGIN
                CREATE TABLE leads (
                    id INT IDENTITY(1,1) PRIMARY KEY,
                    nome NVARCHAR(100) NOT NULL,
                    email NVARCHAR(100) UNIQUE,
                    telefone NVARCHAR(20),
                    empresa NVARCHAR(100),
                    cargo NVARCHAR(100),
                    estagio_atual NVARCHAR(50) NOT NULL DEFAULT 'Enviado Email',
                    data_criacao DATETIME DEFAULT GETDATE(),
                    ultima_interacao DATETIME,
                    observacoes NVARCHAR(500)
                )
            END
        """)
        conn.commit()
        print("[OK] Tabela leads criada com sucesso!")
        
    except Exception as e:
        print(f"[ERRO] Erro ao criar banco de dados: {str(e)}")
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    criar_banco()
