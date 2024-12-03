-- Atualiza registros existentes que têm NULL nos campos leads e vendas
UPDATE time 
SET leads = 0 
WHERE leads IS NULL;

UPDATE time 
SET vendas = 0 
WHERE vendas IS NULL;

-- Altera a coluna leads para não permitir NULL e definir valor padrão 0
ALTER TABLE time 
ALTER COLUMN leads SET NOT NULL,
ALTER COLUMN leads SET DEFAULT 0;

-- Altera a coluna vendas para não permitir NULL e definir valor padrão 0
ALTER TABLE time 
ALTER COLUMN vendas SET NOT NULL,
ALTER COLUMN vendas SET DEFAULT 0;
