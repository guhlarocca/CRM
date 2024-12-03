from sqlalchemy import create_engine
from sqlalchemy.sql import text
from conexao import ConexaoBanco

def adicionar_coluna_profile_photo():
    # Criar conexão com o banco
    conexao = ConexaoBanco()
    engine = conexao.criar_engine()
    
    # Adicionar a coluna profile_photo se ela não existir
    with engine.connect() as conn:
        try:
            # Verificar se a coluna já existe
            conn.execute(text("SELECT profile_photo FROM usuarios LIMIT 1"))
            print("A coluna profile_photo já existe na tabela usuarios")
        except Exception:
            # Adicionar a coluna se ela não existir
            conn.execute(text("ALTER TABLE usuarios ADD COLUMN profile_photo VARCHAR(255) DEFAULT 'default_profile.png'"))
            conn.commit()
            print("Coluna profile_photo adicionada com sucesso!")

if __name__ == '__main__':
    adicionar_coluna_profile_photo()
