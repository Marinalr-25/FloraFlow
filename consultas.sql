-- Consultas para testar no VS Code (extensão SQLite)
SELECT * FROM flores;
SELECT * FROM clientes;
SELECT p.id, c.nome, p.data, p.total FROM pedidos p JOIN clientes c ON c.id = p.cliente_id;
SELECT categoria, COUNT(*) AS tipos, SUM(estoque) AS total_estoque FROM flores GROUP BY categoria;
