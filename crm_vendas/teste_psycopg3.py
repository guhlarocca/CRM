import psycopg
import sys

# Forçar encoding do sistema
if sys.platform.startswith('win'):
    import locale
    sys.stdout.reconfigure(encoding=locale.getpreferredencoding())

# Configurações
conninfo = "host=db.hixycllemctkfmxgltgu.supabase.co port=5432 dbname=postgres user=postgres password=Larocca@123 sslmode=require"

# Conectar
print("Tentando conectar...")
with psycopg.connect(conninfo) as conn:
    print("Conectado com sucesso!")
    
    # Testar query
    with conn.cursor() as cur:
        cur.execute("SELECT current_timestamp")
        result = cur.fetchone()
        print(f"Timestamp do banco: {result[0]}")
