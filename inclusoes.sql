-- Dados iniciais (rode com: python executar.py inclusoes.sql)
INSERT INTO flores (nome, categoria, preco, unidade, estoque, descricao, cor) VALUES
('Rosa vermelha','Rosa',8.90,'Haste',120,'Clássica e perfumada','vermelho'),
('Orquídea branca','Orquídea',39.90,'Vaso',15,'Elegante, dura semanas','branco'),
('Lírio','Lírio',14.90,'Haste',60,'Flores grandes e perfumadas','rosa'),
('Girassol','Girassol',9.90,'Haste',80,'Alegria em amarelo','amarelo'),
('Lavanda','Lavanda',24.90,'Vaso',30,'Aroma calmante','lilás'),
('Peônia','Peônia',29.90,'Haste',25,'Pétalas volumosas','rosa'),
('Tulipas','Tulipa',39.90,'Maço com 5',40,'Cores variadas','amarelo'),
('Astromélia','Astromélia',22.90,'Maço',35,'Duram bastante','rosa');

INSERT INTO clientes (nome, telefone, email, endereco, aniversario, observacoes) VALUES
('Maria Souza','(11) 91234-5678','maria@email.com','Rua das Flores, 100','15/03','Prefere rosas'),
('João Lima','(11) 99876-5432','joao@email.com','Av. Brasil, 250','02/09','');

INSERT INTO pedidos (cliente_id, data, total) VALUES (1, date('now'), 26.70) ;
INSERT INTO itens_pedido (pedido_id, flor_id, quantidade, preco_unitario) VALUES (1, 1, 3, 8.90);
