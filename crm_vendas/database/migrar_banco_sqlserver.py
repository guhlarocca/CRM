from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import os

# Configurações de conexão
# Substitua com suas credenciais de conexão
connection_string = 'mssql+pyodbc://seu_usuario:sua_senha@localhost/seu_banco_de_dados?driver=ODBC+Driver+17+for+SQL+Server'

def migrar_banco():
    try:
        # Criar engine de conexão
        engine = create_engine(connection_string)
        
        # Criar sessão
        Session = sessionmaker(bind=engine)
        session = Session()

        # Verificar se a coluna origem já existe
        verificar_origem = """
        IF NOT EXISTS (
            SELECT * 
            FROM sys.columns 
            WHERE object_id = OBJECT_ID('leads') AND name = 'origem'
        )
        BEGIN
            ALTER TABLE leads ADD origem NVARCHAR(50) NULL DEFAULT 'Não especificado'
        END
        """

        # Verificar se a coluna data_conversao já existe
        verificar_data_conversao = """
        IF NOT EXISTS (
            SELECT * 
            FROM sys.columns 
            WHERE object_id = OBJECT_ID('leads') AND name = 'data_conversao'
        )
        BEGIN
            ALTER TABLE leads ADD data_conversao DATETIME NULL
        END
        """

        # Executar as alterações
        with engine.connect() as connection:
            connection.execute(text(verificar_origem))
            connection.execute(text(verificar_data_conversao))
            connection.commit()

        print("Migração concluída com sucesso!")
    
    except Exception as e:
        print(f"Erro durante a migração: {e}")

if __name__ == '__main__':
    migrar_banco()
