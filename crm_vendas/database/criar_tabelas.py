from database.conexao import ConexaoBanco
from database.modelos import Base

def criar_tabelas():
    """Cria todas as tabelas definidas nos modelos"""
    # Inicializa a conexão
    conexao = ConexaoBanco()
    
    # Cria o engine
    engine = conexao.criar_engine()
    
    # Cria todas as tabelas definidas nos modelos
    Base.metadata.create_all(engine)
    
    print("Tabelas criadas com sucesso!")

if __name__ == "__main__":
    criar_tabelas()
