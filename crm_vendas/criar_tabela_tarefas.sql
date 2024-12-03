-- Criar tabela de tarefas
CREATE TABLE IF NOT EXISTS public.tarefas (
    id UUID PRIMARY KEY,
    titulo TEXT NOT NULL,
    descricao TEXT,
    data_vencimento TIMESTAMP WITH TIME ZONE NOT NULL,
    prioridade TEXT NOT NULL CHECK (prioridade IN ('Alta', 'Média', 'Baixa')),
    status TEXT NOT NULL DEFAULT 'Pendente' CHECK (status IN ('Pendente', 'Em Andamento', 'Concluída', 'Cancelada')),
    usuario_id UUID REFERENCES public.usuarios(id),
    lead_id UUID REFERENCES public.leads(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc'::text, NOW()) NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc'::text, NOW()) NOT NULL
);

-- Criar índices para melhor performance
CREATE INDEX IF NOT EXISTS idx_tarefas_usuario ON public.tarefas(usuario_id);
CREATE INDEX IF NOT EXISTS idx_tarefas_lead ON public.tarefas(lead_id);
CREATE INDEX IF NOT EXISTS idx_tarefas_status ON public.tarefas(status);
CREATE INDEX IF NOT EXISTS idx_tarefas_data_vencimento ON public.tarefas(data_vencimento);

-- Desabilitar RLS temporariamente para debug
ALTER TABLE public.tarefas DISABLE ROW LEVEL SECURITY;

-- Criar trigger para atualizar o updated_at
CREATE TRIGGER update_tarefas_updated_at
    BEFORE UPDATE ON public.tarefas
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();
