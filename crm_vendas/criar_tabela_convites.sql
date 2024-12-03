-- Criar tabela de convites
DROP TABLE IF EXISTS public.convites;
CREATE TABLE public.convites (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) NOT NULL,
    token VARCHAR(255) NOT NULL UNIQUE,
    expiracao TIMESTAMP WITH TIME ZONE NOT NULL,
    criado_por INTEGER REFERENCES public.usuarios(id),
    usado BOOLEAN DEFAULT FALSE,
    data_criacao TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    data_uso TIMESTAMP WITH TIME ZONE
);

-- Criar índices para melhor performance
CREATE INDEX idx_convites_token ON public.convites(token);
CREATE INDEX idx_convites_email ON public.convites(email);

-- Garantir que apenas e-mails únicos possam ser convidados
CREATE UNIQUE INDEX idx_convites_email_not_used 
    ON public.convites(email) 
    WHERE NOT usado;

-- Desabilitar RLS temporariamente para debug
ALTER TABLE public.convites DISABLE ROW LEVEL SECURITY;
