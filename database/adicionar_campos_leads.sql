-- Script para adicionar novos campos na tabela leads

-- Verificar e adicionar email_comercial
IF NOT EXISTS (
    SELECT * 
    FROM sys.columns 
    WHERE object_id = OBJECT_ID('leads') AND name = 'email_comercial'
)
BEGIN
    ALTER TABLE leads ADD email_comercial NVARCHAR(100) NULL
END

-- Verificar e adicionar email_comercial_02
IF NOT EXISTS (
    SELECT * 
    FROM sys.columns 
    WHERE object_id = OBJECT_ID('leads') AND name = 'email_comercial_02'
)
BEGIN
    ALTER TABLE leads ADD email_comercial_02 NVARCHAR(100) NULL
END

-- Verificar e adicionar email_comercial_03
IF NOT EXISTS (
    SELECT * 
    FROM sys.columns 
    WHERE object_id = OBJECT_ID('leads') AND name = 'email_comercial_03'
)
BEGIN
    ALTER TABLE leads ADD email_comercial_03 NVARCHAR(100) NULL
END

-- Verificar e adicionar email_financeiro
IF NOT EXISTS (
    SELECT * 
    FROM sys.columns 
    WHERE object_id = OBJECT_ID('leads') AND name = 'email_financeiro'
)
BEGIN
    ALTER TABLE leads ADD email_financeiro NVARCHAR(100) NULL
END

-- Verificar e adicionar telefone_comercial
IF NOT EXISTS (
    SELECT * 
    FROM sys.columns 
    WHERE object_id = OBJECT_ID('leads') AND name = 'telefone_comercial'
)
BEGIN
    ALTER TABLE leads ADD telefone_comercial NVARCHAR(20) NULL
END

-- Verificar e adicionar cidade
IF NOT EXISTS (
    SELECT * 
    FROM sys.columns 
    WHERE object_id = OBJECT_ID('leads') AND name = 'cidade'
)
BEGIN
    ALTER TABLE leads ADD cidade NVARCHAR(100) NULL
END

-- Verificar e adicionar estado
IF NOT EXISTS (
    SELECT * 
    FROM sys.columns 
    WHERE object_id = OBJECT_ID('leads') AND name = 'estado'
)
BEGIN
    ALTER TABLE leads ADD estado NVARCHAR(50) NULL
END

-- Verificar e adicionar contato_01
IF NOT EXISTS (
    SELECT * 
    FROM sys.columns 
    WHERE object_id = OBJECT_ID('leads') AND name = 'contato_01'
)
BEGIN
    ALTER TABLE leads ADD contato_01 NVARCHAR(100) NULL
END

-- Verificar e adicionar contato_02
IF NOT EXISTS (
    SELECT * 
    FROM sys.columns 
    WHERE object_id = OBJECT_ID('leads') AND name = 'contato_02'
)
BEGIN
    ALTER TABLE leads ADD contato_02 NVARCHAR(100) NULL
END

PRINT 'Migração de campos de leads concluída com sucesso!'
