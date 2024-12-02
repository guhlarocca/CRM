-- Verifica se a tabela já existe e remove
DROP TABLE IF EXISTS configuracoes_empresa;

-- Cria a tabela de configurações da empresa
CREATE TABLE configuracoes_empresa (
    id SERIAL PRIMARY KEY,
    nome_sistema VARCHAR(100) NOT NULL DEFAULT 'CRM Vendas',
    logo_url VARCHAR(255),
    primary_color VARCHAR(7) NOT NULL DEFAULT '#1a1c20',
    secondary_color VARCHAR(7) NOT NULL DEFAULT '#292d33',
    accent_color VARCHAR(7) NOT NULL DEFAULT '#00d9ff',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
