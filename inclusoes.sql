
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

UPDATE flores SET foto = 'rosa_vermelha.jpeg'    WHERE nome = 'Rosa vermelha';
UPDATE flores SET foto = 'orquidea_branca.jpeg'  WHERE nome = 'Orquídea branca';
UPDATE flores SET foto = 'lirio.jpeg'            WHERE nome = 'Lírio';
UPDATE flores SET foto = 'girassol.jpeg'         WHERE nome = 'Girassol';
UPDATE flores SET foto = 'lavanda.jpeg'          WHERE nome = 'Lavanda';
UPDATE flores SET foto = 'peonia.jpeg'           WHERE nome = 'Peônia';
UPDATE flores SET foto = 'tulipas.jpeg'          WHERE nome = 'Tulipas';
UPDATE flores SET foto = 'astromelia.jpeg'       WHERE nome = 'Astromélia';


INSERT INTO flores (nome, categoria, preco, unidade, estoque, descricao, cor, foto) VALUES
('Margarida','Margarida',25.90,'Haste',35,'transmite leveza e inocência','branco','margarida.jpeg');

INSERT INTO clientes (nome, telefone, email, endereco, aniversario, observacoes) VALUES
('Marina','(11) 99999-9999','marina@email.com','','15/02','Prefere Lirio'),
('Maria Rosa','(11) 98111-0001','maria.rosa@email.com','Rua das Palmeiras, 45','','' ),
('João Feijão','(11) 98111-0002','joao.feijao@email.com','Av. Paulista, 900','','' ),
('Juliana Mendes','(11) 98111-0003','juliana.mendes@email.com','Rua Augusta, 321','','' ),
('Beatriz Ferrari','(11) 98111-0004','beatriz.ferrari@email.com','Rua dos Pinheiros, 77','','' ),
('Rafael Mendes','(11) 98111-0005','rafael.mendes@email.com','Rua Oscar Freire, 15','','' ),
('Maiara Maraisa','(11) 98111-0006','maiara.maraisa@email.com','Rua Haddock Lobo, 210','','' ),
('Mariana Souza','(11) 91111-2222','mariana.souza@email.com','Rua das Acácias, 120 - Centro','','' );


INSERT INTO pedidos (cliente_id, data, total) VALUES (3, '2026-11-12', 179.30);
INSERT INTO itens_pedido (pedido_id, flor_id, quantidade, preco_unitario) VALUES (2, 3, 2, 14.90), (2, 6, 5, 29.90);


INSERT INTO pedidos (cliente_id, data, total, origem, tipo, status, pago, pagamento, criado_em,
                    data_entrega, horario, mensagem_cartao, endereco_entrega, florista, entregador,
                    recebido_por, avaliacao_nota, avaliacao_comentario) VALUES
(4, date('now','localtime'), 89.40,  'online','Retirada','Pendente',0,'Pix',     datetime('now','localtime','-2 hours'),  date('now','localtime'),'19:12','', '', NULL, NULL, NULL, NULL, NULL),
(5, date('now','localtime'), 79.80,  'online','Entrega', 'Pendente',0,'Cartão',  datetime('now','localtime','-90 minutes'),date('now','localtime'),'17:30','Parabéns!', 'Av. Paulista, 900', NULL, NULL, NULL, NULL, NULL),
(6, date('now','localtime'), 123.70, 'online','Entrega', 'Aceito / Pago',1,'Pix', datetime('now','localtime','-3 hours'),  date('now','localtime'),'16:45','Com carinho', 'Rua Augusta, 321', NULL, NULL, NULL, NULL, NULL),
(7, date('now','localtime'), 139.50, 'online','Entrega', 'Aceito / Pago',1,'Pix', datetime('now','localtime','-4 hours'),  date('now','localtime'),'15:03','', 'Rua dos Pinheiros, 77', NULL, NULL, NULL, NULL, NULL),
(8, date('now','localtime'), 22.90,  'online','Retirada','Em produção',1,'Dinheiro',datetime('now','localtime','-5 hours'), date('now','localtime'),'12:56','', '', 'Lucas Ferreira', NULL, NULL, NULL, NULL),
(9, date('now','localtime'), 39.90,  'online','Entrega', 'Saiu para entrega',1,'Pix',datetime('now','localtime','-6 hours'),date('now','localtime'),'11:45','Boa sorte!', 'Rua Haddock Lobo, 210', 'Lucas Ferreira', 'Pedro Nogueira', NULL, NULL, NULL),
(10, date('now','localtime','-1 day'), 106.80,'online','Entrega','Finalizado',1,'Pix', datetime('now','localtime','start of day','-1 day','+10 hours','+5 minutes'),
    date('now','localtime','-1 day'),'16:00','Feliz Dia das Mães!' || char(10) || 'Com amor, Mariana.','Rua das Acácias, 120 - Centro','Lucas Ferreira','Pedro Nogueira','Mariana Souza',5,'Flores lindas e chegaram no horário!');

INSERT INTO itens_pedido (pedido_id, flor_id, quantidade, preco_unitario) VALUES
(3, 3, 6, 14.90),
(4, 7, 1, 39.90), (4, 2, 1, 39.90),
(5, 4, 8, 9.90),  (5, 1, 5, 8.90),
(6, 6, 3, 29.90), (6, 5, 2, 24.90),
(7, 8, 1, 22.90),
(8, 2, 1, 39.90),
(9, 1, 12, 8.90);

INSERT INTO historico_pedido (pedido_id, titulo, detalhe, criado_em) VALUES
(3, 'Pedido recebido', 'Registrado na loja', datetime('now','localtime','-2 hours')),
(4, 'Pedido recebido', 'Registrado na loja', datetime('now','localtime','-90 minutes')),
(5, 'Pedido recebido', 'Registrado na loja', datetime('now','localtime','-3 hours')),
(5, 'Pagamento confirmado', 'Pix · R$ 123,70', datetime('now','localtime','-170 minutes')),
(6, 'Pedido recebido', 'Registrado na loja', datetime('now','localtime','-4 hours')),
(6, 'Pagamento confirmado', 'Pix · R$ 139,50', datetime('now','localtime','-230 minutes')),
(7, 'Pedido recebido', 'Registrado na loja', datetime('now','localtime','-5 hours')),
(7, 'Pagamento confirmado', 'Dinheiro · R$ 22,90', datetime('now','localtime','-290 minutes')),
(7, 'Em produção', 'Florista: Lucas Ferreira', datetime('now','localtime','-3 hours')),
(8, 'Pedido recebido', 'Registrado na loja', datetime('now','localtime','-6 hours')),
(8, 'Pagamento confirmado', 'Pix · R$ 39,90', datetime('now','localtime','-350 minutes')),
(8, 'Em produção', 'Florista: Lucas Ferreira', datetime('now','localtime','-5 hours')),
(8, 'Saiu para entrega', 'Entregador: Pedro Nogueira', datetime('now','localtime','-1 hours')),
(9, 'Pedido recebido', 'Registrado na loja', datetime('now','localtime','start of day','-1 day','+10 hours','+5 minutes')),
(9, 'Pagamento confirmado', 'Pix · R$ 106,80', datetime('now','localtime','start of day','-1 day','+10 hours','+10 minutes')),
(9, 'Em produção', 'Florista: Lucas Ferreira', datetime('now','localtime','start of day','-1 day','+14 hours')),
(9, 'Saiu para entrega', 'Entregador: Pedro Nogueira', datetime('now','localtime','start of day','-1 day','+15 hours','+40 minutes')),
(9, 'Pedido entregue', 'Recebido por Mariana Souza', datetime('now','localtime','start of day','-1 day','+16 hours'));
