-- Adicionar coluna foto_url se não existir
DO $$ 
BEGIN 
    IF NOT EXISTS (
        SELECT 1 
        FROM information_schema.columns 
        WHERE table_name = 'usuarios' 
        AND column_name = 'foto_url'
    ) THEN
        ALTER TABLE usuarios 
        ADD COLUMN foto_url TEXT;
    END IF;
END $$;
