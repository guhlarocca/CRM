-- Atualizar a senha para um hash bcrypt válido
-- A senha padrão será '123456'
UPDATE usuarios 
SET senha = '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LcdYJ1J.UNIJJx5Fm'
WHERE senha IS NOT NULL;
