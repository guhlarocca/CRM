from database.conexao import ConexaoBanco
from database.modelos import Base, Time
import sqlalchemy as sa
from sqlalchemy.orm import sessionmaker

def recreate_time_table():
    # Criar conexão com o banco
    conexao = ConexaoBanco()
    engine = sa.create_engine(conexao.get_sqlalchemy_url())
    
    # Dropar a tabela time se ela existir
    Time.__table__.drop(engine, checkfirst=True)
    
    # Recriar a tabela time com a nova estrutura
    Time.__table__.create(engine)
    
    print("Tabela 'time' recriada com sucesso!")

if __name__ == '__main__':
    recreate_time_table()
