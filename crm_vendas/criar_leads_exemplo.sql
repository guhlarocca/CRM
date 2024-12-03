-- Criar tabela de leads se não existir
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
    vendedor_id UUID,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc'::text, NOW()) NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc'::text, NOW()) NOT NULL
);

-- Inserir alguns leads de exemplo
INSERT INTO leads (nome, email, telefone, empresa, cargo, estado, regiao, estagio)
VALUES 
    ('João Silva', 'joao@empresa.com', '11999999999', 'Empresa A', 'Gerente', 'SP', 'Sudeste', 'Novo'),
    ('Maria Santos', 'maria@empresa.com', '11988888888', 'Empresa B', 'Diretora', 'RJ', 'Sudeste', 'Em Contato'),
    ('Pedro Oliveira', 'pedro@empresa.com', '11977777777', 'Empresa C', 'Coordenador', 'MG', 'Sudeste', 'Agendado'),
    ('Ana Costa', 'ana@empresa.com', '11966666666', 'Empresa D', 'Analista', 'RS', 'Sul', 'Fechado'),
    ('Carlos Souza', 'carlos@empresa.com', '11955555555', 'Empresa E', 'Supervisor', 'PR', 'Sul', 'Novo')
ON CONFLICT DO NOTHING;
