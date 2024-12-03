from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

def migrar_campos_leads():
    try:
        # Configurações de conexão do banco de dados
        connection_string = (
            f'mssql+pyodbc://{os.getenv("DB_USER")}:{os.getenv("DB_PASSWORD")}@'
            f'{os.getenv("DB_SERVER")}/{os.getenv("DB_NAME")}?driver={os.getenv("DB_DRIVER")}'
        )
        
        # Criar engine de conexão
        engine = create_engine(connection_string)
        
        # Lista de campos a serem adicionados
        campos = [
            ('email_comercial', 'NVARCHAR(100)'),
            ('email_comercial_02', 'NVARCHAR(100)'),
            ('email_comercial_03', 'NVARCHAR(100)'),
            ('email_financeiro', 'NVARCHAR(100)'),
            ('telefone_comercial', 'NVARCHAR(20)'),
            ('cidade', 'NVARCHAR(100)'),
            ('estado', 'NVARCHAR(50)'),
            ('contato_01', 'NVARCHAR(100)'),
            ('contato_02', 'NVARCHAR(100)'),
        ]

        # Executar as alterações
        with engine.connect() as connection:
            for campo, tipo in campos:
                # Verificar se o campo já existe
                verificar_campo = f"""
                IF NOT EXISTS (
                    SELECT * 
                    FROM sys.columns 
                    WHERE object_id = OBJECT_ID('leads') AND name = '{campo}'
                )
                BEGIN
                    ALTER TABLE leads ADD {campo} {tipo} NULL
                END
                """
                
                print(f"Verificando e adicionando campo: {campo}")
                connection.execute(text(verificar_campo))
            
            connection.commit()

        print("Migração de campos de leads concluída com sucesso!")
    
    except Exception as e:
        print(f"Erro durante a migração: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    migrar_campos_leads()
