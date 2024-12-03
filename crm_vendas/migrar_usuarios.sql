-- Criar tabela temporária para backup
CREATE TABLE usuarios_backup AS 
SELECT * FROM usuarios;

-- Recriar a tabela usuarios com a nova estrutura
DROP TABLE IF EXISTS public.usuarios CASCADE;

CREATE TABLE public.usuarios (
    id UUID NOT NULL PRIMARY KEY,
    nome TEXT,
    email TEXT UNIQUE NOT NULL,
    senha TEXT NOT NULL,
    profile_photo TEXT,
    is_admin BOOLEAN DEFAULT false,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc'::text, NOW()) NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc'::text, NOW()) NOT NULL
);

-- Restaurar os dados com novos UUIDs
INSERT INTO usuarios (
    id,
    nome,
    email,
    senha,
    profile_photo,
    is_admin
    -- created_at e updated_at serão preenchidos com o valor padrão
)
SELECT 
    gen_random_uuid(),  -- Gerar novo UUID para cada registro
    nome,
    email,
    senha,
    profile_photo,
    is_admin
FROM usuarios_backup;

-- Criar índices para melhor performance
CREATE INDEX IF NOT EXISTS idx_usuarios_email ON public.usuarios(email);
CREATE INDEX IF NOT EXISTS idx_usuarios_nome ON public.usuarios(nome);

-- Desabilitar RLS temporariamente para debug
ALTER TABLE public.usuarios DISABLE ROW LEVEL SECURITY;

-- Criar trigger para atualizar o updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_usuarios_updated_at
    BEFORE UPDATE ON public.usuarios
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Remover tabela de backup após confirmar que tudo está ok
-- DROP TABLE usuarios_backup;  -- Descomente esta linha após verificar que a migração funcionou
