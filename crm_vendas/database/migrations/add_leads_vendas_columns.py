from sqlalchemy import create_engine, text
from database.conexao import ConexaoBanco

def migrate():
    # Criar conexão com o banco
    conexao = ConexaoBanco()
    engine = conexao.criar_engine()
    
    # SQL para adicionar as colunas
    sql_commands = [
        "ALTER TABLE time ADD COLUMN IF NOT EXISTS leads INTEGER DEFAULT 0",
        "ALTER TABLE time ADD COLUMN IF NOT EXISTS vendas INTEGER DEFAULT 0",
        
        # Atualizar contadores existentes
        """
        UPDATE time t 
        SET leads = (
            SELECT COUNT(*) 
            FROM leads l 
            WHERE l.vendedor_id = t.id
        )
        """,
        
        """
        UPDATE time t 
        SET vendas = (
            SELECT COUNT(*) 
            FROM leads l 
            WHERE l.vendedor_id = t.id 
            AND l.venda_fechada = TRUE
        )
        """
    ]
    
    # Executar os comandos
    with engine.connect() as conn:
        for sql in sql_commands:
            conn.execute(text(sql))
            conn.commit()

if __name__ == '__main__':
    migrate()
