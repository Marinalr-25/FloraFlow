import os
from flask import Flask, render_template, request, redirect, url_for, flash
from werkzeug.utils import secure_filename
import db_sql as db
import re
import click
from datetime import date
from flask import abort

app = Flask(__name__)
app.secret_key = "floricultura-chave-secreta"   # necessária para flash()
app.config["UPLOAD_FOLDER"] = os.path.join("static", "uploads")

# ---------- COMANDO: flask init-db ----------
@app.cli.command("init-db")
@click.option("--dados", is_flag=True, help="Também carrega os dados de exemplo (inclusoes.sql).")
def init_db_comando(dados):
    """Cria as tabelas lendo o schema.sql."""
    db.inicializar_banco(com_dados=dados)
    click.echo("Banco criado com sucesso!" + (" Dados de exemplo carregados." if dados else ""))


def salvar_foto(arquivo):
    if arquivo and arquivo.filename:
        nome = secure_filename(arquivo.filename)
        arquivo.save(os.path.join(app.config["UPLOAD_FOLDER"], nome))
        return nome
    return None


def ddmm(valor):
    """Garante o formato dd/mm (descarta o ano, se vier)."""
    d = "".join(ch for ch in valor if ch.isdigit())[:4]
    return f"{d[:2]}/{d[2:]}" if len(d) == 4 else valor.strip()[:5]


def dados_flor():
    f = request.form
    return (f["nome"], f["categoria"], float(f["preco"].replace(",", ".") or 0),
            f.get("unidade", "Haste"), int(f["estoque"] or 0), f["descricao"], f.get("cor", ""))

def validar_cliente(f):
    telefone = re.sub(r"\D", "", f["telefone"])          # só os números
    if not re.fullmatch(r"\d{2}9\d{8}", telefone):       # DDD + 9 + 8 dígitos
        return "Telefone inválido: use DDD + 9 dígitos, ex.: (11) 91234-5678."
    if not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", f["email"]):
        return "E-mail inválido, ex.: nome@email.com."
    return None


# ---------- INÍCIO ----------
@app.route("/")
def index():
    return render_template("index.html", flores=db.listar_flores()[:8], ativo="inicio")


# ---------- CLIENTES ----------
@app.route("/clientes")
def clientes():
    busca = request.args.get("q", "")
    return render_template("clientes.html", clientes=db.listar_clientes(busca), ativo="clientes")


@app.route("/clientes/novo", methods=["GET", "POST"])
def cliente_novo():
    if request.method == "POST":
        erro = validar_cliente(request.form)
        if erro:
            flash(erro)
            return render_template("cliente_form.html", cliente=request.form, ativo="clientes")
        f = request.form
        db.inserir_cliente(f["nome"], f["telefone"], f["email"], f["endereco"], ddmm(f["aniversario"]), f["observacoes"])
        flash("Cliente salvo!")
        return redirect(url_for("clientes"))
    return render_template("cliente_form.html", cliente=None, ativo="clientes")

@app.route("/clientes/<int:id>/editar", methods=["GET", "POST"])
def cliente_editar(id):
    if request.method == "POST":
        erro = validar_cliente(request.form)
        if erro:
            flash(erro)
            return render_template("cliente_form.html", cliente=request.form, ativo="clientes")
        f = request.form
        db.atualizar_cliente(id, f["nome"], f["telefone"], f["email"], f["endereco"], ddmm(f["aniversario"]), f["observacoes"])
        return redirect(url_for("clientes"))
    return render_template("cliente_form.html", cliente=db.buscar_cliente(id), ativo="clientes")

@app.route("/clientes/<int:id>/excluir", methods=["POST"])
def cliente_excluir(id):
    db.excluir_cliente(id)
    return redirect(url_for("clientes"))


# ---------- FLORES ----------
@app.route("/flores")
def flores():
    cat = request.args.get("categoria")
    return render_template("flores.html", flores=db.listar_flores(cat),
                          categorias=db.listar_categorias(), categoria=cat, ativo="flores")

@app.route("/flores/nova", methods=["GET", "POST"])
def flor_nova():
    if request.method == "POST":
        db.inserir_flor(*dados_flor(), salvar_foto(request.files.get("foto")))
        flash("Flor cadastrada!")
        return redirect(url_for("flores"))
    return render_template("flor_form.html", flor=None, ativo="flores")

@app.route("/flores/<int:id>/editar", methods=["GET", "POST"])
def flor_editar(id):
    if request.method == "POST":
        db.atualizar_flor(id, *dados_flor(), salvar_foto(request.files.get("foto")))
        return redirect(url_for("flores"))
    return render_template("flor_form.html", flor=db.buscar_flor(id), ativo="flores")

@app.route("/flores/<int:id>/excluir", methods=["POST"])
def flor_excluir(id):
    db.excluir_flor(id)
    return redirect(url_for("flores"))


# ---------- PEDIDOS ----------
@app.route("/pedidos", methods=["GET", "POST"])
def pedidos():
    if request.method == "POST":
        flor_ids = request.form.getlist("flor_id")
        qtds = request.form.getlist("quantidade")
        itens = [(int(f), int(q)) for f, q in zip(flor_ids, qtds) if f and q]
        try:
            db.inserir_pedido(int(request.form["cliente_id"]), itens)
            flash("Pedido registrado!")
        except ValueError as erro:
            flash(str(erro))
        return redirect(url_for("pedidos"))
    return render_template("pedidos.html", pedidos=db.listar_pedidos(),
                          clientes=db.listar_clientes(), flores=db.listar_flores(), ativo="pedidos")


# ---------- RELATÓRIOS ----------
@app.route("/relatorios")
def relatorios():
    return render_template("relatorios.html", r=db.resumo(), ativo="relatorios")


STATUS_CLASSE = {"Pendente": "s-pendente", "Aceito / Pago": "s-aceito", "Em produção": "s-producao",
                "Saiu para entrega": "s-entrega", "Finalizado": "s-final"}


@app.template_filter("brl")
def brl(valor):
    texto = f"{(valor or 0):,.2f}"
    return "R$ " + texto.replace(",", "X").replace(".", ",").replace("X", ".")


@app.template_filter("rotulo_data")
def rotulo_data(data, horario=""):
    """'2026-11-17' -> Hoje / Ontem / Amanhã / Há 3 dias / 25/12 (+ horário)."""
    try:
        d = date.fromisoformat(data)
    except (TypeError, ValueError):
        return horario or ""
    dif = (date.today() - d).days
    if dif == 0:
        dia = "Hoje"
    elif dif == 1:
        dia = "Ontem"
    elif dif == -1:
        dia = "Amanhã"
    elif dif > 1:
        dia = f"Há {dif} dias"
    else:
        dia = d.strftime("%d/%m")
    return f"{dia}, {horario}" if horario else dia


@app.template_filter("dia_rel")
def dia_rel(data):
    return rotulo_data(data).lower()


@app.template_filter("hora_hist")
def hora_hist(criado_em):
    """'2026-11-17 16:00:00' -> '16:00' (com a data se não for hoje)."""
    try:
        dia, hora = criado_em.split(" ")
        if date.fromisoformat(dia) == date.today():
            return hora[:5]
        return f"{dia[8:10]}/{dia[5:7]} {hora[:5]}"
    except (AttributeError, ValueError):
        return criado_em or ""


@app.template_filter("digitos")
def digitos(texto):
    return re.sub(r"\D", "", texto or "")


def proximo_status(tipo, status):
    ordem = [s for s in db.STATUS_PEDIDO if not (tipo == "Retirada" and s == "Saiu para entrega")]
    i = ordem.index(status) if status in ordem else 0
    return ordem[i + 1] if i + 1 < len(ordem) else None


def etapas_pedido(tipo, status):
    if tipo == "Entrega":
        base = [("Pendente", "Pendente"), ("Aceito / Pago", "Aceito / Pago"), ("Em produção", "Preparo"),
                ("Saiu para entrega", "Entrega"), ("Finalizado", "Entregue")]
    else:
        base = [("Pendente", "Pendente"), ("Aceito / Pago", "Aceito / Pago"), ("Em produção", "Preparo"),
                ("Finalizado", "Retirado")]
    chaves = [s for s, _ in base]
    atual = chaves.index(status) if status in chaves else 0
    return [{"rotulo": rotulo, "estado": "feito" if i < atual else ("atual" if i == atual else "futuro")}
            for i, (_, rotulo) in enumerate(base)]


@app.route("/pedidos-online")
def pedidos_online():
    q = request.args.get("q", "").strip()
    periodo = request.args.get("periodo", "todos")
    lista = db.listar_pedidos_online(q, periodo)
    colunas = {s: [p for p in lista if p["status"] == s] for s in db.STATUS_PEDIDO}
    return render_template("pedidos_online.html", colunas=colunas, classes=STATUS_CLASSE,
                          q=q, periodo=periodo, ativo="pedidos_online")


@app.route("/pedidos-online/novo", methods=["GET", "POST"])
def pedido_online_novo():
    flores_lista = db.listar_flores()
    dados = {"cliente_id": "", "tipo": "Entrega", "data_entrega": date.today().isoformat(),
            "horario": "12:00", "mensagem_cartao": "", "pagamento": "Pix", "endereco_entrega": "",
            "status": request.args.get("status", "Pendente"), "qtds": {}}
    if request.method == "POST":
        f = request.form
        qtds = {fl["id"]: int(f.get(f"qtd_{fl['id']}") or 0) for fl in flores_lista}
        dados.update({k: f.get(k, dados[k]) for k in dados if k != "qtds"})
        dados["qtds"] = qtds
        try:
            novo_id = db.inserir_pedido_online(
                int(f.get("cliente_id") or 0), f.get("tipo"), f.get("data_entrega"), f.get("horario"),
                f.get("mensagem_cartao", "").strip(), f.get("pagamento"), f.get("endereco_entrega", "").strip(),
                [(fid, q) for fid, q in qtds.items()], f.get("status", "Pendente"))
            flash(f"Pedido #{novo_id} criado!")
            return redirect(url_for("pedidos_online"))
        except ValueError as erro:
            flash(str(erro))
    return render_template("pedido_online_form.html", clientes=db.listar_clientes(), flores=flores_lista,
                          dados=dados, ativo="pedidos_online")


@app.route("/pedidos-online/<int:id>")
def pedido_online_detalhe(id):
    p = db.buscar_pedido_online(id)
    if p is None:
        abort(404)
    historico = db.listar_historico(id)
    fim = next((h["criado_em"][11:16] for h in historico if h["titulo"] in ("Pedido entregue", "Pedido retirado")), None)
    return render_template("pedido_online_detalhe.html", p=p, itens=db.listar_itens_pedido(id),
                          historico=historico, etapas=etapas_pedido(p["tipo"], p["status"]),
                          proximo=proximo_status(p["tipo"], p["status"]), finalizado_em=fim,
                          classe=STATUS_CLASSE[p["status"]], ativo="pedidos_online")


@app.route("/pedidos-online/<int:id>/status", methods=["POST"])
def pedido_online_status(id):
    """Chamado pelo JavaScript quando um card é arrastado para outra coluna."""
    try:
        db.mudar_status_pedido(id, request.form.get("status"))
    except ValueError as erro:
        return {"ok": False, "erro": str(erro)}, 400
    return {"ok": True}


@app.route("/pedidos-online/<int:id>/avancar", methods=["POST"])
def pedido_online_avancar(id):
    p = db.buscar_pedido_online(id)
    if p is None:
        abort(404)
    proximo = proximo_status(p["tipo"], p["status"])
    if proximo:
        db.mudar_status_pedido(id, proximo)
    return redirect(url_for("pedido_online_detalhe", id=id))


@app.route("/pedidos-online/<int:id>/atualizar", methods=["POST"])
def pedido_online_atualizar(id):
    f = request.form
    foto = None
    arquivo = request.files.get("comprovante")
    if arquivo and arquivo.filename:
        foto = f"comprovante_{id}_{secure_filename(arquivo.filename)}"
        arquivo.save(os.path.join(app.config["UPLOAD_FOLDER"], foto))
    nota = int(f["nota"]) if f.get("nota") else None
    db.atualizar_detalhes_pedido(id, f.get("florista", "").strip(), f.get("entregador", "").strip(),
                                f.get("recebido_por", "").strip(), nota, f.get("comentario", "").strip(), foto)
    flash("Detalhes salvos!")
    return redirect(url_for("pedido_online_detalhe", id=id))


if __name__ == "__main__":
    app.run(debug=True)
