import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import matplotlib.pyplot as plt

# ============================================================
# 1. Conexão com o banco de dados
# ============================================================
conexao = sqlite3.connect("estacionamento.db")
cursor = conexao.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS clientes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT,
    cpf TEXT,
    placa TEXT
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS movimentacoes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    placa TEXT,
    data TEXT,
    hora_entrada TEXT,
    hora_saida TEXT,
    valor REAL,
    status TEXT
)
""")
conexao.commit()

# ============================================================
# 2. Funções de Clientes (CRUD)
# ============================================================
def cadastrar_cliente():
    nome = entrada_nome.get().strip()
    cpf = entrada_cpf.get().strip()
    placa = entrada_placa.get().strip()

    if nome == "" or cpf == "" or placa == "":
        messagebox.showerror("Erro", "Todos os campos devem ser preenchidos.")
        return

    cursor.execute("INSERT INTO clientes (nome, cpf, placa) VALUES (?, ?, ?)", (nome, cpf, placa))
    conexao.commit()
    messagebox.showinfo("Sucesso", "Cliente cadastrado com sucesso!")
    entrada_nome.delete(0, tk.END)
    entrada_cpf.delete(0, tk.END)
    entrada_placa.delete(0, tk.END)

def listar_clientes():
    cursor.execute("SELECT * FROM clientes")
    registros = cursor.fetchall()
    texto_clientes.delete("1.0", tk.END)
    for r in registros:
        texto_clientes.insert(tk.END, f"ID: {r[0]} | Nome: {r[1]} | CPF: {r[2]} | Placa: {r[3]}\n")

def atualizar_cliente():
    id_cli = entrada_id_cliente.get().strip()
    nome = entrada_nome_upd.get().strip()
    cpf = entrada_cpf_upd.get().strip()
    placa = entrada_placa_upd.get().strip()

    if not id_cli.isdigit():
        messagebox.showerror("Erro", "Informe um ID válido.")
        return

    cursor.execute("UPDATE clientes SET nome=?, cpf=?, placa=? WHERE id=?", (nome, cpf, placa, id_cli))
    conexao.commit()
    messagebox.showinfo("Sucesso", "Cliente atualizado com sucesso!")

def excluir_cliente():
    id_cli = entrada_id_cliente.get().strip()
    if not id_cli.isdigit():
        messagebox.showerror("Erro", "Informe um ID válido.")
        return
    cursor.execute("DELETE FROM clientes WHERE id=?", (id_cli,))
    conexao.commit()
    messagebox.showinfo("Sucesso", "Cliente excluído com sucesso!")

# ============================================================
# 3. Funções de Movimentação
# ============================================================
def registrar_entrada():
    placa = entrada_placa_mov.get().strip()
    if placa == "":
        messagebox.showerror("Erro", "Informe a placa.")
        return
    agora = datetime.now()
    data = agora.strftime("%Y-%m-%d")
    hora = agora.strftime("%H:%M:%S")
    cursor.execute("""
        INSERT INTO movimentacoes (placa, data, hora_entrada, hora_saida, valor, status)
        VALUES (?, ?, ?, '', 0, 'aberto')
    """, (placa, data, hora))
    conexao.commit()
    messagebox.showinfo("Sucesso", f"Entrada registrada: {placa} às {hora}")
    entrada_placa_mov.delete(0, tk.END)

def registrar_saida():
    id_mov = entrada_id_mov.get().strip()
    taxa = entrada_taxa.get().strip()

    if not id_mov.isdigit():
        messagebox.showerror("Erro", "Informe um ID de movimentação válido.")
        return
    try:
        taxa_hora = float(taxa)
    except ValueError:
        messagebox.showerror("Erro", "Taxa por hora deve ser numérica.")
        return

    cursor.execute("SELECT hora_entrada FROM movimentacoes WHERE id=?", (id_mov,))
    r = cursor.fetchone()
    if not r:
        messagebox.showerror("Erro", "Movimentação não encontrada.")
        return

    hora_saida = datetime.now().strftime("%H:%M:%S")
    hora_entrada = r[0]
    fmt = "%H:%M:%S"
    try:
        delta = datetime.strptime(hora_saida, fmt) - datetime.strptime(hora_entrada, fmt)
        horas = delta.seconds / 3600
    except:
        horas = 0

    valor = round(horas * taxa_hora, 2)
    cursor.execute("UPDATE movimentacoes SET hora_saida=?, valor=? WHERE id=?", (hora_saida, valor, id_mov))
    conexao.commit()
    messagebox.showinfo("Saída", f"Saída registrada. Valor: R$ {valor:.2f}")

def listar_movimentacoes():
    cursor.execute("SELECT * FROM movimentacoes")
    registros = cursor.fetchall()
    texto_mov.delete("1.0", tk.END)
    for r in registros:
        texto_mov.insert(tk.END, f"ID:{r[0]} | Placa:{r[1]} | Data:{r[2]} | Entrada:{r[3]} | Saída:{r[4]} | R${r[5]:.2f} | {r[6]}\n")

# ============================================================
# 4. Funções de Cobrança
# ============================================================
def listar_abertos():
    cursor.execute("SELECT * FROM movimentacoes WHERE status='aberto'")
    registros = cursor.fetchall()
    texto_cobranca.delete("1.0", tk.END)
    texto_cobranca.insert(tk.END, "--- Recebimentos em Aberto ---\n")
    for r in registros:
        texto_cobranca.insert(tk.END, f"ID:{r[0]} | Placa:{r[1]} | Data:{r[2]} | Entrada:{r[3]} | Saída:{r[4]} | R${r[5]:.2f}\n")

def baixar_pagamento():
    id_mov = entrada_id_baixa.get().strip()
    if not id_mov.isdigit():
        messagebox.showerror("Erro", "Informe um ID válido.")
        return
    cursor.execute("UPDATE movimentacoes SET status='pago' WHERE id=?", (id_mov,))
    conexao.commit()
    messagebox.showinfo("Sucesso", "Pagamento baixado com sucesso!")

# ============================================================
# 5. Funções de Relatórios
# ============================================================
def relatorio_clientes():
    cursor.execute("SELECT * FROM clientes")
    registros = cursor.fetchall()
    texto_relatorio.delete("1.0", tk.END)
    texto_relatorio.insert(tk.END, "--- Clientes ---\n")
    for r in registros:
        texto_relatorio.insert(tk.END, f"ID:{r[0]} | Nome:{r[1]} | CPF:{r[2]} | Placa:{r[3]}\n")

def relatorio_em_aberto():
    cursor.execute("SELECT * FROM movimentacoes WHERE status='aberto'")
    registros = cursor.fetchall()
    texto_relatorio.delete("1.0", tk.END)
    texto_relatorio.insert(tk.END, "--- Recebimentos em Aberto ---\n")
    for r in registros:
        texto_relatorio.insert(tk.END, f"ID:{r[0]} | Placa:{r[1]} | Data:{r[2]} | Entrada:{r[3]} | Saída:{r[4]} | R${r[5]:.2f}\n")

def relatorio_recebimentos():
    cursor.execute("SELECT * FROM movimentacoes WHERE status='pago'")
    registros = cursor.fetchall()
    texto_relatorio.delete("1.0", tk.END)
    texto_relatorio.insert(tk.END, "--- Recebimentos Pagos ---\n")
    for r in registros:
        texto_relatorio.insert(tk.END, f"ID:{r[0]} | Placa:{r[1]} | Data:{r[2]} | Entrada:{r[3]} | Saída:{r[4]} | R${r[5]:.2f}\n")

def relatorio_top5():
    cursor.execute("""
        SELECT c.nome, COUNT(m.id) as usos
        FROM movimentacoes m
        JOIN clientes c ON c.placa = m.placa
        GROUP BY m.placa
        ORDER BY usos DESC
        LIMIT 5
    """)
    registros = cursor.fetchall()
    texto_relatorio.delete("1.0", tk.END)
    texto_relatorio.insert(tk.END, "--- Top 5 Clientes que mais usaram ---\n")
    for i, r in enumerate(registros, 1):
        texto_relatorio.insert(tk.END, f"{i}. {r[0]} - {r[1]} uso(s)\n")

    if registros:
        nomes = [r[0] for r in registros]
        usos = [r[1] for r in registros]
        plt.bar(nomes, usos, color="steelblue")
        plt.title("Top 5 Clientes")
        plt.xlabel("Cliente")
        plt.ylabel("Usos")
        plt.tight_layout()
        plt.show()

# ============================================================
# 6. Interface - Janela principal e abas
# ============================================================
janela = tk.Tk()
janela.title("Controle de Estacionamento")

abas = ttk.Notebook(janela)
abas.pack(expand=True, fill="both")

# ----------------------------
# Aba Clientes (CRUD)
# ----------------------------
aba_clientes = tk.Frame(abas)
abas.add(aba_clientes, text="Clientes")

tk.Label(aba_clientes, text="--- Cadastrar ---").grid(row=0, column=0, columnspan=2)

tk.Label(aba_clientes, text="Nome:").grid(row=1, column=0, sticky="e")
entrada_nome = tk.Entry(aba_clientes)
entrada_nome.grid(row=1, column=1)

tk.Label(aba_clientes, text="CPF:").grid(row=2, column=0, sticky="e")
entrada_cpf = tk.Entry(aba_clientes)
entrada_cpf.grid(row=2, column=1)

tk.Label(aba_clientes, text="Placa:").grid(row=3, column=0, sticky="e")
entrada_placa = tk.Entry(aba_clientes)
entrada_placa.grid(row=3, column=1)

tk.Button(aba_clientes, text="Cadastrar", command=cadastrar_cliente).grid(row=4, column=0, columnspan=2, pady=4)

tk.Label(aba_clientes, text="--- Atualizar / Excluir ---").grid(row=5, column=0, columnspan=2)

tk.Label(aba_clientes, text="ID:").grid(row=6, column=0, sticky="e")
entrada_id_cliente = tk.Entry(aba_clientes)
entrada_id_cliente.grid(row=6, column=1)

tk.Label(aba_clientes, text="Nome:").grid(row=7, column=0, sticky="e")
entrada_nome_upd = tk.Entry(aba_clientes)
entrada_nome_upd.grid(row=7, column=1)

tk.Label(aba_clientes, text="CPF:").grid(row=8, column=0, sticky="e")
entrada_cpf_upd = tk.Entry(aba_clientes)
entrada_cpf_upd.grid(row=8, column=1)

tk.Label(aba_clientes, text="Placa:").grid(row=9, column=0, sticky="e")
entrada_placa_upd = tk.Entry(aba_clientes)
entrada_placa_upd.grid(row=9, column=1)

tk.Button(aba_clientes, text="Atualizar", command=atualizar_cliente).grid(row=10, column=0)
tk.Button(aba_clientes, text="Excluir", command=excluir_cliente).grid(row=10, column=1)

tk.Button(aba_clientes, text="Listar Clientes", command=listar_clientes).grid(row=11, column=0, columnspan=2, pady=4)
texto_clientes = tk.Text(aba_clientes, height=8, width=70)
texto_clientes.grid(row=12, column=0, columnspan=2)

# ----------------------------
# Aba Movimentação
# ----------------------------
aba_mov = tk.Frame(abas)
abas.add(aba_mov, text="Movimentação")

tk.Label(aba_mov, text="--- Registrar Entrada ---").grid(row=0, column=0, columnspan=2)
tk.Label(aba_mov, text="Placa:").grid(row=1, column=0, sticky="e")
entrada_placa_mov = tk.Entry(aba_mov)
entrada_placa_mov.grid(row=1, column=1)
tk.Button(aba_mov, text="Registrar Entrada", command=registrar_entrada).grid(row=2, column=0, columnspan=2, pady=4)

tk.Label(aba_mov, text="--- Registrar Saída ---").grid(row=3, column=0, columnspan=2)
tk.Label(aba_mov, text="ID Movimentação:").grid(row=4, column=0, sticky="e")
entrada_id_mov = tk.Entry(aba_mov)
entrada_id_mov.grid(row=4, column=1)
tk.Label(aba_mov, text="Taxa por hora (R$):").grid(row=5, column=0, sticky="e")
entrada_taxa = tk.Entry(aba_mov)
entrada_taxa.grid(row=5, column=1)
tk.Button(aba_mov, text="Registrar Saída", command=registrar_saida).grid(row=6, column=0, columnspan=2, pady=4)

tk.Button(aba_mov, text="Listar Movimentações", command=listar_movimentacoes).grid(row=7, column=0, columnspan=2, pady=4)
texto_mov = tk.Text(aba_mov, height=10, width=80)
texto_mov.grid(row=8, column=0, columnspan=2)

# ----------------------------
# Aba Cobrança
# ----------------------------
aba_cobranca = tk.Frame(abas)
abas.add(aba_cobranca, text="Cobrança")

tk.Button(aba_cobranca, text="Ver em Aberto", command=listar_abertos).pack(pady=4)
texto_cobranca = tk.Text(aba_cobranca, height=10, width=80)
texto_cobranca.pack()

tk.Label(aba_cobranca, text="ID para baixar pagamento:").pack()
entrada_id_baixa = tk.Entry(aba_cobranca)
entrada_id_baixa.pack()
tk.Button(aba_cobranca, text="Baixar Pagamento", command=baixar_pagamento).pack(pady=4)

# ----------------------------
# Aba Relatórios
# ----------------------------
aba_relatorios = tk.Frame(abas)
abas.add(aba_relatorios, text="Relatórios")

tk.Button(aba_relatorios, text="Clientes", command=relatorio_clientes).pack()
tk.Button(aba_relatorios, text="Recebimentos em Aberto", command=relatorio_em_aberto).pack()
tk.Button(aba_relatorios, text="Recebimentos Pagos", command=relatorio_recebimentos).pack()
tk.Button(aba_relatorios, text="Top 5 Clientes", command=relatorio_top5).pack()
texto_relatorio = tk.Text(aba_relatorios, height=15, width=70)
texto_relatorio.pack()

# ============================================================
# 7. Iniciar programa
# ============================================================
janela.mainloop()
conexao.close()
