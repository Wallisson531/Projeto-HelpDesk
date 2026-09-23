import tkinter as tk
from tkinter import ttk, messagebox
import mysql.connector
from datetime import datetime


def conectar():
    try:
        return mysql.connector.connect(
            host="localhost",
            user="root",
            password="",        
            database="helpdesk"
        )
    except mysql.connector.Error as erro:
        messagebox.showerror(
            "Erro de conexão",
            f"Não foi possível conectar ao MySQL.\n"
            f"Verifique se o MySQL está iniciado no XAMPP.\n\n{erro}"
        )
        raise


def abrir_chamado():

    titulo = campo_titulo.get().upper().strip()
    descricao = campo_descricao.get("1.0", tk.END).strip()
    prioridade = combo_prioridade.get()

    if not titulo:
        messagebox.showwarning(
            "Aviso",
            "Digite o título do chamado."
        )
        return

    agora = datetime.now()

    data_abertura = agora.strftime("%d/%m/%Y")
    hora_abertura = agora.strftime("%H:%M:%S")

    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute("""
    INSERT INTO chamados(
        titulo,
        descricao,
        prioridade,
        data_abertura,
        hora_abertura
    )
    VALUES (%s, %s, %s, %s, %s)
    """, (
        titulo,
        descricao,
        prioridade,
        data_abertura,
        hora_abertura
    ))

    conexao.commit()
    cursor.close()
    conexao.close()

    campo_titulo.delete(0, tk.END)
    campo_descricao.delete("1.0", tk.END)

    carregar_chamados()

    messagebox.showinfo(
        "Sucesso",
        "Chamado aberto com sucesso!"
    )


def carregar_chamados():

    for item in tabela.get_children():
        tabela.delete(item)

    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute("""
    SELECT
        id,
        titulo,
        prioridade,
        status,
        data_abertura,
        hora_abertura
    FROM chamados
    ORDER BY id DESC
    """)

    registros = cursor.fetchall()

    cursor.close()
    conexao.close()

    for registro in registros:
        tabela.insert(
            "",
            tk.END,
            values=registro
        )


def buscar_chamado():

    termo = campo_busca.get().upper()

    for item in tabela.get_children():
        tabela.delete(item)

    conexao = conectar()
    cursor = conexao.cursor()

    # No MySQL o CAST para texto é CHAR (não TEXT como no SQLite)
    cursor.execute("""
    SELECT
        id,
        titulo,
        prioridade,
        status,
        data_abertura,
        hora_abertura
    FROM chamados
    WHERE titulo LIKE %s
       OR CAST(id AS CHAR) LIKE %s
    ORDER BY id DESC
    """, (
        f"%{termo}%",
        f"%{termo}%"
    ))

    registros = cursor.fetchall()

    cursor.close()
    conexao.close()

    for registro in registros:
        tabela.insert(
            "",
            tk.END,
            values=registro
        )


def resolver_por_id(id_chamado, janela_detalhes):

    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute("""
    UPDATE chamados
    SET status='Resolvido'
    WHERE id=%s
    """, (id_chamado,))

    conexao.commit()
    cursor.close()
    conexao.close()

    carregar_chamados()

    messagebox.showinfo(
        "Sucesso",
        "Chamado resolvido com sucesso!"
    )

    janela_detalhes.destroy()


def abrir_detalhes(event):

    selecionado = tabela.selection()

    if not selecionado:
        return

    item = tabela.item(selecionado)

    id_chamado = item["values"][0]

    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute("""
    SELECT
        titulo,
        descricao,
        prioridade,
        status,
        data_abertura,
        hora_abertura
    FROM chamados
    WHERE id=%s
    """, (id_chamado,))

    chamado = cursor.fetchone()

    cursor.close()
    conexao.close()

    janela = tk.Toplevel()

    janela.title(f"Chamado #{id_chamado}")
    janela.geometry("800x600")
    janela.resizable(False, False)

    tk.Label(
        janela,
        text=f"CHAMADO #{id_chamado}",
        font=("Segoe UI", 18, "bold")
    ).pack(pady=15)

    tk.Label(
        janela,
        text=f"TÍTULO: {chamado[0]}",
        font=("Segoe UI", 11, "bold")
    ).pack(anchor="w", padx=20)

    tk.Label(
        janela,
        text=f"PRIORIDADE: {chamado[2]}"
    ).pack(anchor="w", padx=20)

    tk.Label(
        janela,
        text=f"STATUS: {chamado[3]}"
    ).pack(anchor="w", padx=20)

    tk.Label(
        janela,
        text=f"DATA: {chamado[4]}"
    ).pack(anchor="w", padx=20)

    tk.Label(
        janela,
        text=f"HORA: {chamado[5]}"
    ).pack(anchor="w", padx=20)

    tk.Label(
        janela,
        text="DESCRIÇÃO",
        font=("Segoe UI", 11, "bold")
    ).pack(anchor="w", padx=20, pady=10)

    texto = tk.Text(
        janela,
        height=15,
        width=80
    )

    texto.pack(padx=20)

    texto.insert(
        "1.0",
        chamado[1]
    )

    texto.config(state="disabled")

    frame_botoes = tk.Frame(janela)

    frame_botoes.pack(pady=20)

    if chamado[3] != "Resolvido":

        tk.Button(
            frame_botoes,
            text="Resolver Chamado",
            bg="#16a34a",
            fg="white",
            font=("Segoe UI", 10, "bold"),
            command=lambda:
            resolver_por_id(
                id_chamado,
                janela
            )
        ).pack(side="left", padx=5)

    tk.Button(
        frame_botoes,
        text="Fechar",
        bg="#64748b",
        fg="white",
        command=janela.destroy
    ).pack(side="left", padx=5)


# JANELA PRINCIPAL

app = tk.Tk()

app.title("HELPDESK EMPRESARIAL")
app.geometry("1200x750")
app.configure(bg="#f4f6f9")

titulo = tk.Label(
    app,
    text="HELPDESK EMPRESARIAL",
    font=("Segoe UI", 24, "bold"),
    bg="#f4f6f9",
    fg="#0f172a"
)

titulo.pack(pady=20)

# FORMULÁRIO

frame = tk.Frame(
    app,
    bg="white",
    padx=20,
    pady=20,
    bd=1,
    relief="solid"
)

frame.pack(
    fill="x",
    padx=20,
    pady=10
)

tk.Label(frame, text="Título").pack(anchor="w")

campo_titulo = tk.Entry(
    frame,
    font=("Segoe UI", 11)
)

campo_titulo.pack(fill="x", pady=5)

tk.Label(frame, text="Descrição").pack(anchor="w")

campo_descricao = tk.Text(
    frame,
    height=5
)

campo_descricao.pack(fill="x", pady=5)

tk.Label(frame, text="Prioridade").pack(anchor="w")

combo_prioridade = ttk.Combobox(
    frame,
    values=[
        "Baixa",
        "Média",
        "Alta",
        "Crítica"
    ]
)

combo_prioridade.current(0)
combo_prioridade.pack(fill="x", pady=5)

tk.Button(
    frame,
    text="Abrir Chamado",
    bg="#2563eb",
    fg="white",
    command=abrir_chamado
).pack(pady=10)

# BUSCA

frame_busca = tk.Frame(
    app,
    bg="#f4f6f9"
)

frame_busca.pack(
    fill="x",
    padx=20,
    pady=10
)

tk.Label(
    frame_busca,
    text="Pesquisar:",
    bg="#f4f6f9"
).pack(side="left")

campo_busca = tk.Entry(
    frame_busca,
    width=40
)

campo_busca.pack(
    side="left",
    padx=10
)

tk.Button(
    frame_busca,
    text="Pesquisar",
    bg="#0284c7",
    fg="white",
    command=buscar_chamado
).pack(side="left")

tk.Button(
    frame_busca,
    text="Mostrar Todos",
    command=carregar_chamados
).pack(side="left", padx=5)

# TABELA

colunas = (
    "ID",
    "Título",
    "Prioridade",
    "Status",
    "Data",
    "Hora"
)

tabela = ttk.Treeview(
    app,
    columns=colunas,
    show="headings"
)

for coluna in colunas:
    tabela.heading(coluna, text=coluna)

tabela.column("ID", width=50, anchor="center")
tabela.column("Título", width=450)
tabela.column("Prioridade", width=120, anchor="center")
tabela.column("Status", width=120, anchor="center")
tabela.column("Data", width=120, anchor="center")
tabela.column("Hora", width=120, anchor="center")

tabela.pack(
    fill="both",
    expand=True,
    padx=20,
    pady=20
)

tabela.bind(
    "<Double-1>",
    abrir_detalhes
)

carregar_chamados()

app.mainloop()