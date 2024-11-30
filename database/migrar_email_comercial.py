from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

def migrar_email_comercial():
    try:
        # Configurações de conexão do banco de dados
        connection_string = (
            f'mssql+pyodbc://{os.getenv("DB_USER")}:{os.getenv("DB_PASSWORD")}@'
            f'{os.getenv("DB_SERVER")}/{os.getenv("DB_NAME")}?driver={os.getenv("DB_DRIVER")}'
        )
        
        # Criar engine de conexão
        engine = create_engine(connection_string)
        
        # Criar sessão
        Session = sessionmaker(bind=engine)
        session = Session()

        # Verificar e adicionar email_comercial_02
        verificar_email_comercial_02 = """
        IF NOT EXISTS (
            SELECT * 
            FROM sys.columns 
            WHERE object_id = OBJECT_ID('leads') AND name = 'email_comercial_02'
        )
        BEGIN
            ALTER TABLE leads ADD email_comercial_02 NVARCHAR(100) NULL
        END
        """

        # Verificar e adicionar email_comercial_03
        verificar_email_comercial_03 = """
        IF NOT EXISTS (
            SELECT * 
            FROM sys.columns 
            WHERE object_id = OBJECT_ID('leads') AND name = 'email_comercial_03'
        )
        BEGIN
            ALTER TABLE leads ADD email_comercial_03 NVARCHAR(100) NULL
        END
        """

        # Executar as alterações
        with engine.connect() as connection:
            connection.execute(text(verificar_email_comercial_02))
            connection.execute(text(verificar_email_comercial_03))
            connection.commit()

        print("Migração de campos de email comercial concluída com sucesso!")
    
    except Exception as e:
        print(f"Erro durante a migração: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    migrar_email_comercial()
