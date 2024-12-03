-- Adicionar coluna vendedor_id se não existir
DO $$ 
BEGIN 
    IF NOT EXISTS (
        SELECT 1 
        FROM information_schema.columns 
        WHERE table_name = 'tarefas' 
        AND column_name = 'vendedor_id'
    ) THEN
        ALTER TABLE public.tarefas 
        ADD COLUMN vendedor_id UUID REFERENCES public.usuarios(id);
        
        -- Criar índice para a nova coluna
        CREATE INDEX IF NOT EXISTS idx_tarefas_vendedor ON public.tarefas(vendedor_id);
    END IF;
END $$;
