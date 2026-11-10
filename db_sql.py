"""Funções de acesso ao banco (CRUD)."""
import sqlite3

BANCO = "floricultura.db"


def conectar():
    conn = sqlite3.connect(BANCO)
    conn.row_factory = sqlite3.Row   # permite usar linha['nome']
    return conn


def consultar(sql, params=()):
    conn = conectar()
    linhas = conn.execute(sql, params).fetchall()
    conn.close()
    return linhas


def executar(sql, params=()):
    conn = conectar()
    cur = conn.execute(sql, params)
    conn.commit()
    novo_id = cur.lastrowid
    conn.close()
    return novo_id


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


# ---------- PEDIDOS ----------
def listar_pedidos():
    return consultar(
        "SELECT p.id, c.nome AS cliente, p.data, p.total, "
        "GROUP_CONCAT(i.quantidade || 'x ' || f.nome, ', ') AS itens "
        "FROM pedidos p JOIN clientes c ON c.id = p.cliente_id "
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
