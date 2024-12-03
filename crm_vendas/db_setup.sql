-- Create config_empresa table
CREATE TABLE IF NOT EXISTS config_empresa (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    nome_empresa TEXT,
    logo_url TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc'::text, NOW()) NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc'::text, NOW()) NOT NULL
);

-- Create usuarios table if it doesn't exist
CREATE TABLE IF NOT EXISTS usuarios (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    email TEXT UNIQUE NOT NULL,
    senha TEXT NOT NULL,
    nome TEXT,
    foto_url TEXT,
    is_admin BOOLEAN DEFAULT false,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc'::text, NOW()) NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc'::text, NOW()) NOT NULL
);

-- Insert default config
INSERT INTO config_empresa (nome_empresa)
VALUES ('Minha Empresa')
ON CONFLICT DO NOTHING;

-- Enable Row Level Security (RLS)
ALTER TABLE config_empresa ENABLE ROW LEVEL SECURITY;
ALTER TABLE usuarios ENABLE ROW LEVEL SECURITY;

-- Create policies
CREATE POLICY "Enable read access for all users" ON config_empresa
    FOR SELECT USING (true);

CREATE POLICY "Enable read access for authenticated users" ON usuarios
    FOR SELECT USING (auth.role() = 'authenticated');
