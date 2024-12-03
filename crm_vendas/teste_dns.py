import socket
import requests

def test_connection():
    host = "db.hixycllemctkfmxgltgu.supabase.co"
    
    print(f"\nTestando DNS para {host}:")
    try:
        ip = socket.gethostbyname(host)
        print(f"✓ DNS resolvido: {ip}")
    except socket.gaierror as e:
        print(f"✗ Erro DNS: {e}")
    
    print("\nTestando conexão HTTPS com Supabase:")
    try:
        response = requests.get("https://hixycllemctkfmxgltgu.supabase.co", timeout=5)
        print(f"✓ Supabase respondeu com status: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"✗ Erro ao conectar: {e}")
    
    print("\nTestando conexão com servidores DNS:")
    dns_servers = ["8.8.8.8", "1.1.1.1"]  # Google DNS e Cloudflare DNS
    for dns in dns_servers:
        try:
            socket.create_connection((dns, 53), timeout=5)
            print(f"✓ Conexão com DNS {dns} ok")
        except (socket.timeout, socket.error) as e:
            print(f"✗ Erro ao conectar com DNS {dns}: {e}")

if __name__ == "__main__":
    test_connection()
