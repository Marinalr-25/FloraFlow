import os
from flask import Flask, render_template, request, redirect, url_for, flash
from werkzeug.utils import secure_filename
import db_sql as db
import re
import click

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


if __name__ == "__main__":
    app.run(debug=True)
