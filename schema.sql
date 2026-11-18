PRAGMA foreign_keys = ON;

DROP TABLE IF EXISTS itens_pedido;
DROP TABLE IF EXISTS pedidos;
DROP TABLE IF EXISTS flores;
DROP TABLE IF EXISTS clientes;
DROP TABLE IF EXISTS historico_pedido;

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
  
  origem     TEXT NOT NULL DEFAULT 'balcao' CHECK (origem IN ('balcao', 'online')),
  tipo       TEXT NOT NULL DEFAULT 'Retirada' CHECK (tipo IN ('Entrega', 'Retirada')),
  status     TEXT NOT NULL DEFAULT 'Finalizado'
  CHECK (status IN ('Pendente', 'Aceito / Pago', 'Em produção', 'Saiu para entrega', 'Finalizado')),
  pago       INTEGER NOT NULL DEFAULT 1 CHECK (pago IN (0, 1)),
  pagamento  TEXT NOT NULL DEFAULT 'Dinheiro' CHECK (pagamento IN ('Pix', 'Cartão', 'Dinheiro')),
  criado_em  TEXT NOT NULL DEFAULT (datetime('now', 'localtime')),
  data_entrega     TEXT,          
  horario          TEXT,          
  mensagem_cartao  TEXT,
  endereco_entrega TEXT,
  taxa_entrega     REAL NOT NULL DEFAULT 0 CHECK (taxa_entrega >= 0),
  florista         TEXT,
  entregador       TEXT,
  recebido_por     TEXT,
  comprovante      TEXT,         
  avaliacao_nota       INTEGER CHECK (avaliacao_nota BETWEEN 1 AND 5),
  avaliacao_comentario TEXT,
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


CREATE TABLE historico_pedido (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    pedido_id  INTEGER NOT NULL,
    titulo     TEXT NOT NULL,
    detalhe    TEXT,
    criado_em  TEXT NOT NULL DEFAULT (datetime('now', 'localtime')),
    FOREIGN KEY (pedido_id) REFERENCES pedidos(id) ON DELETE CASCADE
);
