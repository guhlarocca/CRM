import psycopg

# Configurações corretas do Supabase
conninfo = (
    "host=aws-0-sa-east-1.pooler.supabase.com "
    "port=5432 "
    "dbname=postgres "
    "user=postgres "
    "password=Larocca@123 "  # Substitua pela sua senha
    "sslmode=require"
)

# Conectar
print("Tentando conectar...")
with psycopg.connect(conninfo) as conn:
    print("Conectado com sucesso!")
    
    # Testar query
    with conn.cursor() as cur:
        cur.execute("SELECT current_timestamp")
        result = cur.fetchone()
        print(f"Timestamp do banco: {result[0]}")
        
        # Verificar encoding
        cur.execute("SHOW client_encoding")
        encoding = cur.fetchone()
        print(f"Encoding do cliente: {encoding[0]}")
        
        # Verificar versão
        cur.execute("SELECT version()")
        version = cur.fetchone()
        print(f"Versão do PostgreSQL: {version[0]}")
