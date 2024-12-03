from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from modelos import Base, Lead
import os

# Caminho do banco de dados
db_path = os.path.join(os.path.dirname(__file__), 'leads.db')
engine = create_engine(f'sqlite:///{db_path}')

# Criar sessão
Session = sessionmaker(bind=engine)
session = Session()

def migrar_banco():
    try:
        # Adicionar colunas com valores padrão
        print("Iniciando migração do banco de dados...")
        
        # Adicionar coluna 'origem'
        try:
            session.execute('ALTER TABLE leads ADD COLUMN origem VARCHAR(50) DEFAULT "Não especificado"')
            print("Coluna 'origem' adicionada com sucesso.")
        except Exception as e:
            print(f"Erro ao adicionar coluna 'origem': {e}")
        
        # Adicionar coluna 'data_conversao'
        try:
            session.execute('ALTER TABLE leads ADD COLUMN data_conversao DATETIME')
            print("Coluna 'data_conversao' adicionada com sucesso.")
        except Exception as e:
            print(f"Erro ao adicionar coluna 'data_conversao': {e}")
        
        # Commit das alterações
        session.commit()
        print("Migração concluída com sucesso!")
    
    except Exception as e:
        session.rollback()
        print(f"Erro durante a migração: {e}")
    
    finally:
        session.close()

if __name__ == '__main__':
    migrar_banco()
