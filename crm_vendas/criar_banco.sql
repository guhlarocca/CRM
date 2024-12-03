-- Criar o banco de dados
IF NOT EXISTS (SELECT * FROM sys.databases WHERE name = 'CRM_VENDAS')
BEGIN
    CREATE DATABASE CRM_VENDAS;
END
GO

USE CRM_VENDAS;
GO

-- Criar tabela de leads
IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'leads')
BEGIN
    CREATE TABLE leads (
        id INT IDENTITY(1,1) PRIMARY KEY,
        nome NVARCHAR(100) NOT NULL,
        email NVARCHAR(100) UNIQUE,
        telefone NVARCHAR(20),
        empresa NVARCHAR(100),
        cargo NVARCHAR(100),
        estagio_atual NVARCHAR(50) NOT NULL DEFAULT 'Enviado Email',
        data_criacao DATETIME DEFAULT GETDATE(),
        ultima_interacao DATETIME,
        observacoes NVARCHAR(500)
    );
END
GO
