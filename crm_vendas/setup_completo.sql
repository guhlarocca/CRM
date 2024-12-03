-- Criar tabela de membros
CREATE TABLE IF NOT EXISTS membros (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    nome TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    cargo TEXT,
    telefone TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc'::text, NOW()) NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc'::text, NOW()) NOT NULL
);

-- Criar tabela de leads
CREATE TABLE IF NOT EXISTS leads (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    nome TEXT NOT NULL,
    email TEXT,
    telefone TEXT,
    empresa TEXT,
    cargo TEXT,
    estado TEXT,
    regiao TEXT,
    estagio TEXT DEFAULT 'Novo',
    vendedor_id UUID REFERENCES membros(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc'::text, NOW()) NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc'::text, NOW()) NOT NULL
);

-- Criar tabela de config_empresa (se ainda não existir)
CREATE TABLE IF NOT EXISTS config_empresa (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    nome_empresa TEXT,
    logo_url TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc'::text, NOW()) NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc'::text, NOW()) NOT NULL
);

-- Inserir configuração padrão da empresa
INSERT INTO config_empresa (nome_empresa)
VALUES ('Minha Empresa')
ON CONFLICT DO NOTHING;

-- Habilitar RLS (Row Level Security)
ALTER TABLE membros ENABLE ROW LEVEL SECURITY;
ALTER TABLE leads ENABLE ROW LEVEL SECURITY;
ALTER TABLE config_empresa ENABLE ROW LEVEL SECURITY;

-- Criar políticas de acesso
CREATE POLICY "Permitir leitura para usuários autenticados" ON membros
    FOR SELECT USING (auth.role() = 'authenticated');

CREATE POLICY "Permitir leitura para usuários autenticados" ON leads
    FOR SELECT USING (auth.role() = 'authenticated');

CREATE POLICY "Permitir leitura para todos" ON config_empresa
    FOR SELECT USING (true);
