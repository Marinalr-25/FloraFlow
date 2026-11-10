-- Cria as tabelas (rode com: python executar.py schema.sql)
-- AJUSTE aqui para as tabelas que o grupo já definiu.
DROP TABLE IF EXISTS itens_pedido;
DROP TABLE IF EXISTS pedidos;
DROP TABLE IF EXISTS flores;
DROP TABLE IF EXISTS clientes;

CREATE TABLE clientes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    telefone TEXT,
    email TEXT,
    endereco TEXT,
    aniversario TEXT,      -- formato dd/mm
    observacoes TEXT
);

CREATE TABLE flores (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    categoria TEXT,
    preco REAL NOT NULL DEFAULT 0,
    unidade TEXT DEFAULT 'Haste',   -- Haste, Vaso, Maço...
    estoque INTEGER NOT NULL DEFAULT 0,
    descricao TEXT,
    cor TEXT,
    foto TEXT                        -- nome do arquivo em static/uploads
);

CREATE TABLE pedidos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    cliente_id INTEGER NOT NULL,
    data TEXT NOT NULL DEFAULT (date('now')),
    total REAL NOT NULL DEFAULT 0,
    FOREIGN KEY (cliente_id) REFERENCES clientes(id)
);

CREATE TABLE itens_pedido (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    pedido_id INTEGER NOT NULL,
    flor_id INTEGER NOT NULL,
    quantidade INTEGER NOT NULL DEFAULT 1,
    preco_unitario REAL NOT NULL,
    FOREIGN KEY (pedido_id) REFERENCES pedidos(id),
    FOREIGN KEY (flor_id) REFERENCES flores(id)
);
