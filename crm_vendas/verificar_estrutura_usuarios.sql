-- Verificar estrutura da tabela usuarios
SELECT 
    column_name, 
    data_type, 
    character_maximum_length,
    column_default,
    is_nullable
FROM 
    information_schema.columns
WHERE 
    table_name = 'usuarios'
ORDER BY 
    ordinal_position;
