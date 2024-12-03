-- Adicionar coluna venda_fechada
ALTER TABLE leads
ADD venda_fechada BIT NOT NULL DEFAULT 0;

-- Adicionar coluna data_venda
ALTER TABLE leads
ADD data_venda DATETIME NULL;
