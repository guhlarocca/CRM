SELECT 
    tc.constraint_name, 
    cc.check_clause
FROM 
    information_schema.table_constraints tc
    JOIN information_schema.check_constraints cc 
        ON tc.constraint_name = cc.constraint_name
WHERE 
    tc.table_name = 'tarefas' 
    AND tc.constraint_type = 'CHECK';
