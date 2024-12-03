-- Verificar estrutura da tabela tarefas
SELECT 
    column_name, 
    data_type, 
    character_maximum_length,
    column_default,
    is_nullable
FROM 
    information_schema.columns
WHERE 
    table_name = 'tarefas'
ORDER BY 
    ordinal_position;