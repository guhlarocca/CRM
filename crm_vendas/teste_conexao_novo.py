import psycopg2
import logging

# Configurar logging básico
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s: %(message)s'
)

try:
    logging.info("Tentando conectar...")
    
    # Parâmetros de conexão separados
    host = b'db.hixycllemctkfmxgltgu.supabase.co'.decode('ascii')
    dbname = b'postgres'.decode('ascii')
    user = b'postgres'.decode('ascii')
    password = b'Larocca@1234'.decode('ascii')
    port = b'5432'.decode('ascii')
    
    # Construir DSN
    dsn = f"host={host} dbname={dbname} user={user} password={password} port={port}"
    
    conn = psycopg2.connect(dsn)
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
