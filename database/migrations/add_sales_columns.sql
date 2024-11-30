-- Migração para adicionar colunas de venda à tabela leads

-- Verificar se a coluna venda_fechada já existe
IF NOT EXISTS (
    SELECT * 
    FROM sys.columns 
    WHERE object_id = OBJECT_ID('leads') AND name = 'venda_fechada'
)
BEGIN
    -- Adicionar coluna venda_fechada
    ALTER TABLE leads 
    ADD venda_fechada BIT DEFAULT 0 NOT NULL;
END

-- Verificar se a coluna data_venda já existe
IF NOT EXISTS (
    SELECT * 
    FROM sys.columns 
    WHERE object_id = OBJECT_ID('leads') AND name = 'data_venda'
)
BEGIN
    -- Adicionar coluna data_venda
    ALTER TABLE leads 
    ADD data_venda DATETIME NULL;
END
