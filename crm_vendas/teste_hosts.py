import socket

def test_host(host):
    print(f"\nTestando {host}:")
    try:
        ip = socket.gethostbyname(host)
        print(f"✓ Resolvido para: {ip}")
        return True
    except socket.gaierror as e:
        print(f"✗ Falhou: {e}")
        return False

# Lista de possíveis variações do host
project_id = "hixycllemctkfmxgltgu"
hosts_to_test = [
    f"db.{project_id}.supabase.co",
    f"{project_id}.supabase.co",
    f"database.{project_id}.supabase.co",
    f"postgres.{project_id}.supabase.co",
    f"postgresql.{project_id}.supabase.co"
]

print("Testando possíveis hosts do Supabase:")
for host in hosts_to_test:
    test_host(host)
