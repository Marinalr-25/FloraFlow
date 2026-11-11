"""Funções de acesso ao banco (CRUD)."""
import os
import sqlite3

PASTA = os.path.dirname(os.path.abspath(__file__))
BANCO = os.path.join(PASTA, "floricultura.db")

# o app.py usa este nome para tratar erros de regra do banco (UNIQUE, CHECK...)
ErroIntegridade = sqlite3.IntegrityError


def conectar():
    conn = sqlite3.connect(BANCO)
    conn.row_factory = sqlite3.Row   # permite usar linha['nome']
    conn.execute("PRAGMA foreign_keys = ON")   # sem isso o SQLite NÃO confere chaves estrangeiras
    return conn


def inicializar_banco(com_dados=False):
    """Lê o schema.sql (e, se pedido, o inclusoes.sql) e executa no banco."""
    arquivos = ["schema.sql"] + (["inclusoes.sql"] if com_dados else [])
    conn = conectar()
    for nome in arquivos:
        with open(os.path.join(PASTA, nome), encoding="utf-8") as f:
            conn.executescript(f.read())
    conn.commit()
    conn.close()


def consultar(sql, params=()):
    conn = conectar()
    try:
        return conn.execute(sql, params).fetchall()
    finally:
        conn.close()


def executar(sql, params=()):
    conn = conectar()
    try:
        cur = conn.execute(sql, params)
        conn.commit()
        return cur.lastrowid
    except Exception:
        conn.rollback()   # desfaz se o banco recusar (UNIQUE, CHECK...)
        raise
    finally:
        conn.close()      # sempre fecha a conexão, mesmo com erro


# ---------- FLORES ----------
def listar_flores(categoria=None):
    if categoria:
        return consultar("SELECT * FROM flores WHERE categoria = ? ORDER BY nome", (categoria,))
    return consultar("SELECT * FROM flores ORDER BY nome")

def listar_categorias():
    return consultar("SELECT DISTINCT categoria FROM flores WHERE categoria <> '' ORDER BY categoria")

def buscar_flor(id):
    r = consultar("SELECT * FROM flores WHERE id = ?", (id,))
    return r[0] if r else None

def inserir_flor(nome, categoria, preco, unidade, estoque, descricao, cor, foto):
    return executar(
        "INSERT INTO flores (nome, categoria, preco, unidade, estoque, descricao, cor, foto) "
        "VALUES (?,?,?,?,?,?,?,?)",
        (nome, categoria, preco, unidade, estoque, descricao, cor, foto))

def atualizar_flor(id, nome, categoria, preco, unidade, estoque, descricao, cor, foto):
    executar(
        "UPDATE flores SET nome=?, categoria=?, preco=?, unidade=?, estoque=?, descricao=?, cor=?, "
        "foto=COALESCE(?, foto) WHERE id=?",
        (nome, categoria, preco, unidade, estoque, descricao, cor, foto, id))

def excluir_flor(id):
    executar("DELETE FROM flores WHERE id = ?", (id,))


# ---------- CLIENTES ----------
def listar_clientes(busca=""):
    return consultar("SELECT * FROM clientes WHERE nome LIKE ? ORDER BY nome", (f"%{busca}%",))

def buscar_cliente(id):
    r = consultar("SELECT * FROM clientes WHERE id = ?", (id,))
    return r[0] if r else None

def inserir_cliente(nome, telefone, email, endereco, aniversario, observacoes):
    return executar(
        "INSERT INTO clientes (nome, telefone, email, endereco, aniversario, observacoes) "
        "VALUES (?,?,?,?,?,?)",
        (nome, telefone, email, endereco, aniversario, observacoes))

def atualizar_cliente(id, nome, telefone, email, endereco, aniversario, observacoes):
    executar(
        "UPDATE clientes SET nome=?, telefone=?, email=?, endereco=?, aniversario=?, observacoes=? WHERE id=?",
        (nome, telefone, email, endereco, aniversario, observacoes, id))

def excluir_cliente(id):
    executar("DELETE FROM clientes WHERE id = ?", (id,))


def email_em_uso(email, ignorar_id=0):
    return bool(consultar("SELECT 1 FROM clientes WHERE email = ? AND id <> ?", (email, ignorar_id)))


# ---------- PEDIDOS ----------
def listar_pedidos():
    # LEFT JOIN: o pedido aparece mesmo que o cliente ou a flor tenham sido apagados
    return consultar(
        "SELECT p.id, COALESCE(c.nome, 'Cliente removido') AS cliente, p.data, p.total, "
        "GROUP_CONCAT(i.quantidade || 'x ' || COALESCE(f.nome, 'flor removida'), ', ') AS itens "
        "FROM pedidos p "
        "LEFT JOIN clientes c ON c.id = p.cliente_id "
        "LEFT JOIN itens_pedido i ON i.pedido_id = p.id "
        "LEFT JOIN flores f ON f.id = i.flor_id "
        "GROUP BY p.id ORDER BY p.id DESC")

def inserir_pedido(cliente_id, itens):
    """itens = lista de (flor_id, quantidade). Cria UM pedido com todas as flores."""
    # junta flores repetidas na mesma linha
    juntos = {}
    for flor_id, qtd in itens:
        if qtd > 0:
            juntos[flor_id] = juntos.get(flor_id, 0) + qtd
    if not juntos:
        raise ValueError("Adicione pelo menos uma flor ao pedido.")

    conn = conectar()
    try:
        linhas, total = [], 0
        for flor_id, qtd in juntos.items():
            flor = conn.execute("SELECT * FROM flores WHERE id = ?", (flor_id,)).fetchone()
            if flor is None:
                raise ValueError("Flor não encontrada.")
            if flor["estoque"] < qtd:
                raise ValueError(f"Estoque insuficiente de {flor['nome']} (restam {flor['estoque']}).")
            linhas.append((flor_id, qtd, flor["preco"]))
            total += flor["preco"] * qtd

        cur = conn.execute("INSERT INTO pedidos (cliente_id, total) VALUES (?, ?)", (cliente_id, total))
        pedido_id = cur.lastrowid
        for flor_id, qtd, preco in linhas:
            conn.execute(
                "INSERT INTO itens_pedido (pedido_id, flor_id, quantidade, preco_unitario) VALUES (?,?,?,?)",
                (pedido_id, flor_id, qtd, preco))
            conn.execute("UPDATE flores SET estoque = estoque - ? WHERE id = ?", (qtd, flor_id))
        conn.commit()          # só grava se tudo deu certo
        return pedido_id
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


# ---------- RELATÓRIOS ----------
def resumo():
    return {
        "clientes": consultar("SELECT COUNT(*) AS n FROM clientes")[0]["n"],
        "flores": consultar("SELECT COUNT(*) AS n FROM flores")[0]["n"],
        "pedidos": consultar("SELECT COUNT(*) AS n FROM pedidos")[0]["n"],
        "faturamento": consultar("SELECT COALESCE(SUM(total),0) AS t FROM pedidos")[0]["t"],
        "baixo_estoque": consultar("SELECT nome, estoque FROM flores WHERE estoque < 20 ORDER BY estoque"),
    }