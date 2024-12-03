-- Insert a test admin user if it doesn't exist
INSERT INTO usuarios (email, senha, nome, is_admin)
VALUES (
    'guh.larocca@gmail.com',
    '', -- Empty password that will be set on first login
    'Gustavo',
    true
)
ON CONFLICT (email) 
DO UPDATE SET 
    senha = '', -- Reset password to empty to allow new password setup
    is_admin = true;

-- Create the config_empresa table if it doesn't exist
CREATE TABLE IF NOT EXISTS config_empresa (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    nome_empresa TEXT,
    logo_url TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc'::text, NOW()) NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc'::text, NOW()) NOT NULL
);

-- Insert default config if it doesn't exist
INSERT INTO config_empresa (nome_empresa)
VALUES ('Minha Empresa')
ON CONFLICT DO NOTHING;
