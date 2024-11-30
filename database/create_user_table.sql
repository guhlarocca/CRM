USE CRM_VENDAS;

-- Verifica se a tabela já existe e remove
IF OBJECT_ID('usuarios', 'U') IS NOT NULL
    DROP TABLE usuarios;

-- Cria a tabela de usuários
CREATE TABLE usuarios (
    id INT IDENTITY(1,1) PRIMARY KEY,
    nome NVARCHAR(100) NOT NULL,
    email NVARCHAR(100) NOT NULL UNIQUE,
    senha NVARCHAR(255) NOT NULL,
    is_admin BIT DEFAULT 0
);

-- Insere o usuário admin
INSERT INTO usuarios (nome, email, senha, is_admin)
VALUES (
    'Gustavo Larocca',
    'guh.larocca@gmail.com',
    'scrypt:32768:8:1$5ndUQxPgtSCUCKWp$528417c1bff92cfcd7a438ad35d2e75173a8e00aa3956757ac078e16ecfb8b5c821ee41674f8903af16f71c9713b96edba4a9b5ce69f355a90cf15bd657b7237',
    1
);
