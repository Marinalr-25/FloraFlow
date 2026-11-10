"""Executa um arquivo .sql no banco.
Uso:  python executar.py schema.sql
      python executar.py inclusoes.sql
Se nenhum arquivo for informado, mostra a mensagem de uso.
"""
import sqlite3
import sys

BANCO = "floricultura.db"

if len(sys.argv) < 2:
    print("Uso: python executar.py arquivo.sql")
    sys.exit(1)

arquivo = sys.argv[1]
with open(arquivo, encoding="utf-8") as f:
    script = f.read()

conn = sqlite3.connect(BANCO)
conn.executescript(script)   # executa todos os comandos do arquivo
conn.commit()
conn.close()
print(f"'{arquivo}' executado em {BANCO}")
