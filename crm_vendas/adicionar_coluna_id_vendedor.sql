-- Adicionar coluna id_vendedor se não existir
DO $$ 
BEGIN 
    IF NOT EXISTS (
        SELECT 1 
        FROM information_schema.columns 
        WHERE table_name = 'tarefas' 
        AND column_name = 'id_vendedor'
    ) THEN
        ALTER TABLE public.tarefas 
        ADD COLUMN id_vendedor UUID REFERENCES public.usuarios(id);
        
        -- Criar índice para a nova coluna
        CREATE INDEX IF NOT EXISTS idx_tarefas_vendedor ON public.tarefas(id_vendedor);
    END IF;
END $$;
