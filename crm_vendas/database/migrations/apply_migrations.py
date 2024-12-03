from ..conexao_supabase import criar_cliente_supabase
import logging

def apply_migrations():
    try:
        supabase = criar_cliente_supabase()
        
        # Adicionar colunas de cores
        migrations = [
            """
            ALTER TABLE configuracoes_empresa 
            ADD COLUMN IF NOT EXISTS primary_color VARCHAR(7) DEFAULT '#1a1c20';
            """,
            """
            ALTER TABLE configuracoes_empresa 
            ADD COLUMN IF NOT EXISTS secondary_color VARCHAR(7) DEFAULT '#292d33';
            """,
            """
            ALTER TABLE configuracoes_empresa 
            ADD COLUMN IF NOT EXISTS accent_color VARCHAR(7) DEFAULT '#00d9ff';
            """
        ]
        
        for migration in migrations:
            try:
                supabase.execute_sql(migration)
                logging.info(f"Migration executada com sucesso: {migration}")
            except Exception as e:
                if "already exists" not in str(e):
                    logging.error(f"Erro ao executar migration: {str(e)}")
                    raise e
                
        logging.info("Todas as migrations foram aplicadas com sucesso!")
        return True
        
    except Exception as e:
        logging.error(f"Erro ao aplicar migrations: {str(e)}")
        return False

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    apply_migrations()
