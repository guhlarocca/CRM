import sys
sys.path.append('.')  # Adiciona o diretório atual ao path

from database.conexao import ConexaoBanco
from database.modelos import Base

def criar_tabelas():
    """Cria todas as tabelas definidas nos modelos"""
    try:
        # Inicializa a conexão
        conexao = ConexaoBanco()
        
        # Cria o engine
        engine = conexao.criar_engine()
        
        # Cria todas as tabelas definidas nos modelos
        print("🛠️ Criando tabelas no banco de dados...")
        Base.metadata.create_all(engine)
        
        print("✅ Tabelas criadas com sucesso!")
    except Exception as e:
        print(f"❌ Erro ao criar tabelas: {e}")

if __name__ == "__main__":
    criar_tabelas()
