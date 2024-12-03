from werkzeug.security import generate_password_hash

# Gerar hash da senha
senha = 'Larocca@1234'
hash_senha = generate_password_hash(senha)
print(f"Hash gerado: {hash_senha}")
