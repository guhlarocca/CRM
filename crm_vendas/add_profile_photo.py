from database.conexao import ConexaoBanco
from database.modelos import Base
from sqlalchemy import text

# Criar conexão com o banco
conexao = ConexaoBanco()
engine = conexao.criar_engine()

# Adicionar coluna profile_photo se não existir
with engine.connect() as conn:
    try:
        # Verificar se a coluna já existe
        result = conn.execute(text("SELECT * FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = 'time' AND COLUMN_NAME = 'profile_photo'"))
        if not result.fetchone():
            print("Adicionando coluna profile_photo à tabela time...")
            conn.execute(text("ALTER TABLE time ADD COLUMN profile_photo VARCHAR(255) DEFAULT 'default_profile.png'"))
            conn.commit()
            print("Coluna profile_photo adicionada com sucesso!")
        else:
            print("Coluna profile_photo já existe na tabela time.")
    except Exception as e:
        print(f"Erro ao adicionar coluna: {e}")
