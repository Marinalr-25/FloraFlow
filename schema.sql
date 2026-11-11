PRAGMA foreign_keys = ON;

DROP TABLE IF EXISTS itens_pedido;
DROP TABLE IF EXISTS pedidos;
DROP TABLE IF EXISTS flores;
DROP TABLE IF EXISTS clientes;

CREATE TABLE clientes (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    nome        TEXT NOT NULL,
    telefone    TEXT NOT NULL,
    email       TEXT NOT NULL UNIQUE, 
    endereco    TEXT,
    aniversario TEXT, 
    observacoes TEXT
);

CREATE TABLE flores (
    id        INTEGER PRIMARY KEY AUTOINCREMENT,
    nome      TEXT NOT NULL,
    categoria TEXT,
    preco     REAL NOT NULL CHECK (preco >= 0),
    unidade   TEXT NOT NULL DEFAULT 'Haste',   
    estoque   INTEGER NOT NULL DEFAULT 0 CHECK (estoque >= 0),
    descricao TEXT,
    cor       TEXT,
    foto      TEXT                                
);

CREATE TABLE pedidos (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    cliente_id INTEGER,                            
    data       TEXT NOT NULL DEFAULT (date('now')),
    total      REAL NOT NULL DEFAULT 0 CHECK (total >= 0),
    FOREIGN KEY (cliente_id) REFERENCES clientes(id) ON DELETE SET NULL
);

CREATE TABLE itens_pedido (
    id             INTEGER PRIMARY KEY AUTOINCREMENT,
    pedido_id      INTEGER NOT NULL,
    flor_id        INTEGER,                         
    quantidade     INTEGER NOT NULL CHECK (quantidade > 0),
    preco_unitario REAL NOT NULL CHECK (preco_unitario >= 0), 
    FOREIGN KEY (pedido_id) REFERENCES pedidos(id) ON DELETE CASCADE,
    FOREIGN KEY (flor_id) REFERENCES flores(id) ON DELETE SET NULL
);