-- Adicionar coluna usuario_id se não existir
DO $$ 
BEGIN 
    IF NOT EXISTS (
        SELECT 1 
        FROM information_schema.columns 
        WHERE table_name = 'tarefas' 
        AND column_name = 'usuario_id'
    ) THEN
        ALTER TABLE public.tarefas 
        ADD COLUMN usuario_id UUID REFERENCES public.usuarios(id);
        
        -- Criar índice para a nova coluna
        CREATE INDEX IF NOT EXISTS idx_tarefas_usuario ON public.tarefas(usuario_id);
    END IF;
END $$;
