from database.migrations.apply_migrations import apply_migrations
import logging

if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s: %(message)s'
    )
    
    if apply_migrations():
        logging.info("Migrations aplicadas com sucesso!")
    else:
        logging.error("Erro ao aplicar migrations.")
