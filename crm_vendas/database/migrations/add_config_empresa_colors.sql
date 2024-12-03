-- Adicionar colunas de cores à tabela configuracoes_empresa
ALTER TABLE configuracoes_empresa 
ADD COLUMN IF NOT EXISTS primary_color VARCHAR(7) DEFAULT '#1a1c20',
    COLUMN IF NOT EXISTS secondary_color VARCHAR(7) DEFAULT '#292d33',
    COLUMN IF NOT EXISTS accent_color VARCHAR(7) DEFAULT '#00d9ff';
