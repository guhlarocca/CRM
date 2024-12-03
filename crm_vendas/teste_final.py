import psycopg2

# Credenciais simplificadas - apenas ASCII
params = {
    'host': 'db.hixycllemctkfmxgltgu.supabase.co',
    'port': '5432',
    'dbname': 'postgres',
    'user': 'postgres',
    'password': 'Test123!@#',  # MUDE PARA UMA SENHA TEMPORÁRIA SIMPLES NO SUPABASE
    'sslmode': 'require'
}

# Tentar conexão
conn = psycopg2.connect(**params)
print("Conectado com sucesso!")
conn.close()
