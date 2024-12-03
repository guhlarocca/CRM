-- Primeiro, remover a constraint de chave estrangeira se existir
DO $$ 
BEGIN
    IF EXISTS (
        SELECT 1 
        FROM information_schema.table_constraints 
        WHERE constraint_name = 'tarefas_id_vendedor_fkey'
        AND table_name = 'tarefas'
    ) THEN
        ALTER TABLE tarefas DROP CONSTRAINT tarefas_id_vendedor_fkey;
    END IF;
END $$;

-- Alterar o tipo da coluna id_vendedor para UUID
ALTER TABLE tarefas 
ALTER COLUMN id_vendedor TYPE uuid USING id_vendedor::text::uuid;

-- Adicionar a constraint de chave estrangeira para a tabela time
ALTER TABLE tarefas
ADD CONSTRAINT tarefas_id_vendedor_fkey
FOREIGN KEY (id_vendedor)
REFERENCES time (id);
