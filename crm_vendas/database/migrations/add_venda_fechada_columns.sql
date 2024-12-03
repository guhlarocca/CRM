-- Adicionar coluna venda_fechada
IF NOT EXISTS (SELECT * FROM sys.columns WHERE object_id = OBJECT_ID('leads') AND name = 'venda_fechada')
BEGIN
    ALTER TABLE leads
    ADD venda_fechada BIT NOT NULL DEFAULT 0
END

-- Adicionar coluna data_venda
IF NOT EXISTS (SELECT * FROM sys.columns WHERE object_id = OBJECT_ID('leads') AND name = 'data_venda')
BEGIN
    ALTER TABLE leads
    ADD data_venda DATETIME NULL
END
