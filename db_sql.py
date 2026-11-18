
import os
import sqlite3

PASTA = os.path.dirname(os.path.abspath(__file__))
BANCO = os.path.join(PASTA, "floricultura.db")

ErroIntegridade = sqlite3.IntegrityError


def conectar():
    conn = sqlite3.connect(BANCO)
    conn.row_factory = sqlite3.Row  
    conn.execute("PRAGMA foreign_keys = ON")  
    return conn


def inicializar_banco(com_dados=False):
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
        conn.rollback()  
        raise
    finally:
        conn.close()    


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


def listar_pedidos():
    return consultar(
        "SELECT p.id, COALESCE(c.nome, 'Cliente removido') AS cliente, p.data, p.total, "
        "GROUP_CONCAT(i.quantidade || 'x ' || COALESCE(f.nome, 'flor removida'), ', ') AS itens "
        "FROM pedidos p "
        "LEFT JOIN clientes c ON c.id = p.cliente_id "
        "LEFT JOIN itens_pedido i ON i.pedido_id = p.id "
        "LEFT JOIN flores f ON f.id = i.flor_id "
        "GROUP BY p.id ORDER BY p.id DESC")

def inserir_pedido(cliente_id, itens):
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
        conn.commit()         
        return pedido_id
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()

def resumo():
    return {
        "clientes": consultar("SELECT COUNT(*) AS n FROM clientes")[0]["n"],
        "flores": consultar("SELECT COUNT(*) AS n FROM flores")[0]["n"],
        "pedidos": consultar("SELECT COUNT(*) AS n FROM pedidos")[0]["n"],
        "faturamento": consultar("SELECT COALESCE(SUM(total),0) AS t FROM pedidos")[0]["t"],
        "baixo_estoque": consultar("SELECT nome, estoque FROM flores WHERE estoque < 20 ORDER BY estoque"),
    }

STATUS_PEDIDO = ["Pendente", "Aceito / Pago", "Em produção", "Saiu para entrega", "Finalizado"]
TIPOS_PEDIDO = ["Entrega", "Retirada"]
FORMAS_PAGAMENTO = ["Pix", "Cartão", "Dinheiro"]


def _evento(p, status):
    if status == "Pendente":
        return "Pedido recebido", "Registrado na loja"
    if status == "Aceito / Pago":
        valor = f"R$ {p['total']:.2f}".replace(".", ",")
        return "Pagamento confirmado", f"{p['pagamento']} · {valor}"
    if status == "Em produção":
        return "Em produção", f"Florista: {p['florista']}" if p["florista"] else ""
    if status == "Saiu para entrega":
        return "Saiu para entrega", f"Entregador: {p['entregador']}" if p["entregador"] else ""
    titulo = "Pedido entregue" if p["tipo"] == "Entrega" else "Pedido retirado"
    return titulo, f"Recebido por {p['recebido_por']}" if p["recebido_por"] else ""


def _registrar_evento(conn, pedido_id, titulo, detalhe=""):
    conn.execute("INSERT INTO historico_pedido (pedido_id, titulo, detalhe) VALUES (?,?,?)",
                (pedido_id, titulo, detalhe))


def inserir_pedido_online(cliente_id, tipo, data_entrega, horario, mensagem, pagamento,
                          endereco, itens, status="Pendente"):
    if tipo not in TIPOS_PEDIDO:
        raise ValueError("Escolha o tipo: Entrega ou Retirada.")
    if pagamento not in FORMAS_PAGAMENTO:
        raise ValueError("Escolha a forma de pagamento.")
    if status not in STATUS_PEDIDO or (tipo == "Retirada" and status == "Saiu para entrega"):
        status = "Pendente"
    if not data_entrega or not horario:
        raise ValueError("Informe a data e o horário.")

    juntos = {}
    for flor_id, qtd in itens:
        if qtd > 0:
            juntos[flor_id] = juntos.get(flor_id, 0) + qtd
    if not juntos:
        raise ValueError("Adicione pelo menos uma flor ao pedido.")

    conn = conectar()
    try:
        cliente = conn.execute("SELECT * FROM clientes WHERE id = ?", (cliente_id,)).fetchone()
        if cliente is None:
            raise ValueError("Selecione o cliente.")
        if tipo == "Entrega":
            endereco = endereco or cliente["endereco"] or ""
        else:
            endereco = ""

        linhas, total = [], 0
        for flor_id, qtd in juntos.items():
            flor = conn.execute("SELECT * FROM flores WHERE id = ?", (flor_id,)).fetchone()
            if flor is None:
                raise ValueError("Flor não encontrada.")
            if flor["estoque"] < qtd:
                raise ValueError(f"Estoque insuficiente de {flor['nome']} (restam {flor['estoque']}).")
            linhas.append((flor_id, qtd, flor["preco"]))
            total += flor["preco"] * qtd

        pago = 1 if STATUS_PEDIDO.index(status) >= 1 else 0
        cur = conn.execute(
            "INSERT INTO pedidos (cliente_id, total, origem, tipo, status, pago, pagamento, "
            "data_entrega, horario, mensagem_cartao, endereco_entrega) "
            "VALUES (?,?,'online',?,?,?,?,?,?,?,?)",
            (cliente_id, total, tipo, status, pago, pagamento, data_entrega, horario, mensagem, endereco))
        pedido_id = cur.lastrowid
        for flor_id, qtd, preco in linhas:
            conn.execute(
                "INSERT INTO itens_pedido (pedido_id, flor_id, quantidade, preco_unitario) VALUES (?,?,?,?)",
                (pedido_id, flor_id, qtd, preco))
            conn.execute("UPDATE flores SET estoque = estoque - ? WHERE id = ?", (qtd, flor_id))

        pedido = {"total": total, "pagamento": pagamento, "tipo": tipo,
                  "florista": "", "entregador": "", "recebido_por": ""}
        titulo, detalhe = _evento(pedido, status)
        _registrar_evento(conn, pedido_id, titulo, detalhe)
        conn.commit()
        return pedido_id
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def listar_pedidos_online(busca="", periodo="todos"):
    sql = ("SELECT p.id, p.status, p.tipo, p.pago, p.total, p.data_entrega, p.horario, "
          "COALESCE(c.nome, 'Cliente removido') AS cliente, "
          "GROUP_CONCAT(i.quantidade || 'x ' || COALESCE(f.nome, 'flor removida'), ' + ') AS itens "
          "FROM pedidos p "
          "LEFT JOIN clientes c ON c.id = p.cliente_id "
          "LEFT JOIN itens_pedido i ON i.pedido_id = p.id "
          "LEFT JOIN flores f ON f.id = i.flor_id "
          "WHERE p.origem = 'online' ")
    params = []
    if busca:
        sql += "AND (COALESCE(c.nome, '') LIKE ? OR CAST(p.id AS TEXT) LIKE ?) "
        params += [f"%{busca}%", f"%{busca.lstrip('#')}%"]
    if periodo == "hoje":
        sql += "AND p.data_entrega = date('now', 'localtime') "
    elif periodo == "semana":
        sql += "AND strftime('%Y-%W', p.data_entrega) = strftime('%Y-%W', 'now', 'localtime') "
    sql += "GROUP BY p.id ORDER BY p.data_entrega DESC, p.horario DESC"
    return consultar(sql, tuple(params))


def buscar_pedido_online(id):
    r = consultar(
        "SELECT p.*, COALESCE(c.nome, 'Cliente removido') AS cliente, c.telefone, c.email, "
        "c.endereco AS cliente_endereco "
        "FROM pedidos p LEFT JOIN clientes c ON c.id = p.cliente_id "
        "WHERE p.id = ? AND p.origem = 'online'", (id,))
    return r[0] if r else None


def listar_itens_pedido(pedido_id):
    return consultar(
        "SELECT i.quantidade, i.preco_unitario, i.quantidade * i.preco_unitario AS subtotal, "
        "COALESCE(f.nome, 'Flor removida') AS nome, f.foto "
        "FROM itens_pedido i LEFT JOIN flores f ON f.id = i.flor_id "
        "WHERE i.pedido_id = ? ORDER BY i.id", (pedido_id,))


def listar_historico(pedido_id):
    return consultar(
        "SELECT titulo, detalhe, criado_em FROM historico_pedido "
        "WHERE pedido_id = ? ORDER BY id DESC", (pedido_id,))


def mudar_status_pedido(id, novo):
    conn = conectar()
    try:
        p = conn.execute("SELECT * FROM pedidos WHERE id = ? AND origem = 'online'", (id,)).fetchone()
        if p is None:
            raise ValueError("Pedido não encontrado.")
        if novo not in STATUS_PEDIDO:
            raise ValueError("Status inválido.")
        if novo == p["status"]:
            return
        if novo == "Saiu para entrega" and p["tipo"] == "Retirada":
            raise ValueError("Pedidos para retirada não saem para entrega.")
        antigo_i, novo_i = STATUS_PEDIDO.index(p["status"]), STATUS_PEDIDO.index(novo)
        conn.execute("UPDATE pedidos SET status = ?, pago = ? WHERE id = ?",
                    (novo, 1 if novo_i >= 1 else 0, id))
        titulo, detalhe = _evento(p, novo)
        if novo_i < antigo_i:
            titulo, detalhe = f"Voltou para {novo}", ""
        _registrar_evento(conn, id, titulo, detalhe)
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def atualizar_detalhes_pedido(id, florista, entregador, recebido_por, nota, comentario, comprovante):
    executar(
        "UPDATE pedidos SET florista=?, entregador=?, recebido_por=?, avaliacao_nota=?, "
        "avaliacao_comentario=?, comprovante=COALESCE(?, comprovante) WHERE id=? AND origem='online'",
        (florista, entregador, recebido_por, nota, comentario, comprovante, id))
