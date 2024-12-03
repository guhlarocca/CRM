import psycopg2
import logging
from urllib.parse import quote

# Configurar logging básico
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s: %(message)s'
)

try:
    logging.info("Tentando conectar...")
    
    # Codificar os componentes da URL individualmente
    password = quote('Larocca@1234', safe='')
    host = quote('db.hixycllemctkfmxgltgu.supabase.co', safe='')
    
    # Construir a URL de conexão
    DATABASE_URL = f"postgresql://postgres:{password}@{host}:5432/postgres"
    
    # Tentar conexão com a URL codificada
    conn = psycopg2.connect(DATABASE_URL.encode('ascii').decode('ascii'))
    
    logging.info("Conectado com sucesso!")
    
    # Teste simples
    cur = conn.cursor()
    cur.execute('SELECT 1;')
    result = cur.fetchone()
    logging.info(f"Teste de select: {result}")
    
    cur.close()
    conn.close()
    
except Exception as e:
    logging.error(f"Erro: {str(e)}")
    logging.error(f"Tipo do erro: {type(e)}")
    if isinstance(e, psycopg2.Error):
        logging.error(f"Código do erro PostgreSQL: {e.pgcode}")
        logging.error(f"Mensagem do erro PostgreSQL: {e.pgerror}")
