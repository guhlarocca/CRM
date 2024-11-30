from sqlalchemy import create_engine, text
from modelos import Base
from config import DATABASE_URL

def atualizar_banco():
    # Criar engine
    engine = create_engine(DATABASE_URL)
    
    # Adicionar colunas se não existirem
    with engine.connect() as conn:
        # Verificar se a coluna total_leads existe
        try:
            conn.execute(text("SELECT total_leads FROM time WHERE 1=0"))
        except:
            print("Adicionando coluna total_leads...")
            conn.execute(text("ALTER TABLE time ADD total_leads INT DEFAULT 0"))
            conn.commit()
        
        # Verificar se a coluna total_vendas existe
        try:
            conn.execute(text("SELECT total_vendas FROM time WHERE 1=0"))
        except:
            print("Adicionando coluna total_vendas...")
            conn.execute(text("ALTER TABLE time ADD total_vendas INT DEFAULT 0"))
            conn.commit()

if __name__ == '__main__':
    print("Iniciando atualização do banco de dados...")
    atualizar_banco()
    print("Atualização concluída!")
