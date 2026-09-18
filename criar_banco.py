import sqlite3

conexao = sqlite3.connect("chamados.db")

cursor = conexao.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS chamados(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    titulo TEXT NOT NULL,
    descricao TEXT NOT NULL,
    prioridade TEXT NOT NULL,
    status TEXT DEFAULT 'Aberto',
    data_abertura TEXT NOT NULL,
    hora_abertura TEXT NOT NULL
)
""")

conexao.commit()
conexao.close()

print("Banco criado com sucesso!")