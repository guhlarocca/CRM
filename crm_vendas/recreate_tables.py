from database.conexao import ConexaoBanco
from database.modelos import Base
import sqlalchemy as sa
from sqlalchemy.orm import sessionmaker

def recreate_tables():
    # Criar conexão com o banco
    conexao = ConexaoBanco()
    engine = sa.create_engine(conexao.get_sqlalchemy_url())
    
    # Remover todas as tabelas existentes
    Base.metadata.drop_all(engine)
    
    # Criar todas as tabelas novamente
    Base.metadata.create_all(engine)
    
    print("Tabelas recriadas com sucesso!")

if __name__ == '__main__':
    recreate_tables()
