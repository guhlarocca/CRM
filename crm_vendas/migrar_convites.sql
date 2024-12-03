-- Criar backup da tabela convites
CREATE TABLE convites_backup AS 
SELECT * FROM convites;

-- Recriar a tabela convites com UUID
DROP TABLE IF EXISTS public.convites CASCADE;

CREATE TABLE public.convites (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) NOT NULL,
    token VARCHAR(255) NOT NULL UNIQUE,
    expiracao TIMESTAMP WITH TIME ZONE NOT NULL,
    criado_por UUID REFERENCES public.usuarios(id),  -- Alterado para UUID
    usado BOOLEAN DEFAULT FALSE,
    data_criacao TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    data_uso TIMESTAMP WITH TIME ZONE
);

-- Criar índices
CREATE INDEX idx_convites_token ON public.convites(token);
CREATE INDEX idx_convites_email ON public.convites(email);
CREATE INDEX idx_convites_criado_por ON public.convites(criado_por);

-- Garantir que apenas e-mails únicos possam ser convidados
CREATE UNIQUE INDEX idx_convites_email_not_used 
    ON public.convites(email) 
    WHERE NOT usado;

-- Desabilitar RLS temporariamente para debug
ALTER TABLE public.convites DISABLE ROW LEVEL SECURITY;

-- Restaurar os dados dos convites
-- Primeiro, criar uma tabela temporária para mapear os IDs antigos para os novos UUIDs
CREATE TEMP TABLE id_mapping AS
SELECT 
    old.id as old_id,
    new.id as new_id
FROM 
    usuarios_backup old
    JOIN usuarios new ON old.email = new.email;

-- Agora inserir os dados usando o mapeamento
INSERT INTO convites (
    id,
    email,
    token,
    expiracao,
    criado_por,
    usado,
    data_criacao,
    data_uso
)
SELECT 
    COALESCE(c.id::uuid, gen_random_uuid()),
    c.email,
    c.token,
    c.expiracao,
    m.new_id,  -- Usar o novo UUID do usuário
    c.usado,
    c.data_criacao,
    c.data_uso
FROM 
    convites_backup c
    LEFT JOIN id_mapping m ON c.criado_por = m.old_id;

-- Remover tabelas temporárias após confirmar que tudo está ok
-- DROP TABLE convites_backup;
-- DROP TABLE id_mapping;
