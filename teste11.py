import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime
import matplotlib.pyplot as plt
from fpdf import FPDF

# ============================================================
# 1. Banco de dados
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
# 2. Helpers de layout
# ============================================================
COR_FUNDO      = "#F5F5F5"
COR_PRIMARIA   = "#2563EB"
COR_BRANCO     = "#FFFFFF"
COR_BORDA      = "#D1D5DB"
COR_TEXTO      = "#1F2937"
COR_SECUNDARIA = "#6B7280"
PADDING        = 12

def frame_card(pai, titulo="", pady_top=0):
    """Cria um frame estilo card com título opcional."""
    outer = tk.Frame(pai, bg=COR_FUNDO)
    outer.pack(fill="x", padx=16, pady=(pady_top, 8))
    if titulo:
        tk.Label(outer, text=titulo, bg=COR_FUNDO, fg=COR_SECUNDARIA,
                 font=("Segoe UI", 9, "bold")).pack(anchor="w", pady=(4, 2))
    card = tk.Frame(outer, bg=COR_BRANCO, relief="flat",
                    highlightbackground=COR_BORDA, highlightthickness=1)
    card.pack(fill="x")
    return card

def label_entrada(pai, texto, linha, coluna, pady=6):
    tk.Label(pai, text=texto, bg=COR_BRANCO, fg=COR_TEXTO,
             font=("Segoe UI", 10)).grid(row=linha, column=coluna,
             sticky="e", padx=(12, 4), pady=pady)

def campo_entry(pai, linha, coluna, largura=26):
    e = tk.Entry(pai, width=largura, font=("Segoe UI", 10),
                 relief="flat", highlightbackground=COR_BORDA,
                 highlightthickness=1, bg=COR_BRANCO)
    e.grid(row=linha, column=coluna, sticky="w", padx=(0, 12), pady=6)
    return e

def botao_primario(pai, texto, comando, largura=20):
    return tk.Button(pai, text=texto, command=comando,
                     bg=COR_PRIMARIA, fg=COR_BRANCO, relief="flat",
                     font=("Segoe UI", 10, "bold"), cursor="hand2",
                     width=largura, pady=6,
                     activebackground="#1D4ED8", activeforeground=COR_BRANCO)

def botao_secundario(pai, texto, comando, largura=20):
    return tk.Button(pai, text=texto, command=comando,
                     bg=COR_BRANCO, fg=COR_PRIMARIA, relief="flat",
                     font=("Segoe UI", 10), cursor="hand2",
                     width=largura, pady=5,
                     highlightbackground=COR_BORDA, highlightthickness=1,
                     activebackground="#EFF6FF")

def texto_area(pai, altura=10, largura=80):
    frame = tk.Frame(pai, bg=COR_BRANCO,
                     highlightbackground=COR_BORDA, highlightthickness=1)
    frame.pack(fill="both", expand=True, padx=16, pady=(0, 12))
    texto = tk.Text(frame, height=altura, width=largura,
                    font=("Consolas", 10), bg=COR_BRANCO, fg=COR_TEXTO,
                    relief="flat", padx=8, pady=8, wrap="none")
    scroll_y = ttk.Scrollbar(frame, orient="vertical", command=texto.yview)
    scroll_x = ttk.Scrollbar(frame, orient="horizontal", command=texto.xview)
    texto.configure(yscrollcommand=scroll_y.set, xscrollcommand=scroll_x.set)
    scroll_y.pack(side="right", fill="y")
    scroll_x.pack(side="bottom", fill="x")
    texto.pack(side="left", fill="both", expand=True)
    return texto

def separador(pai):
    tk.Frame(pai, bg=COR_BORDA, height=1).pack(fill="x", padx=16, pady=4)

# ============================================================
# 3. Funções de Clientes (CRUD)
# ============================================================
def cadastrar_cliente():
    nome  = entrada_nome.get().strip()
    cpf   = entrada_cpf.get().strip()
    placa = entrada_placa.get().strip()
    if not all([nome, cpf, placa]):
        messagebox.showerror("Erro", "Todos os campos devem ser preenchidos.")
        return
    cursor.execute("INSERT INTO clientes (nome, cpf, placa) VALUES (?, ?, ?)",
                   (nome, cpf, placa))
    conexao.commit()
    messagebox.showinfo("Sucesso", "Cliente cadastrado com sucesso!")
    for e in (entrada_nome, entrada_cpf, entrada_placa):
        e.delete(0, tk.END)

def listar_clientes():
    cursor.execute("SELECT * FROM clientes")
    registros = cursor.fetchall()
    texto_clientes.delete("1.0", tk.END)
    for r in registros:
        texto_clientes.insert(tk.END,
            f"ID: {r[0]:<4} | Nome: {r[1]:<25} | CPF: {r[2]:<15} | Placa: {r[3]}\n")

def atualizar_cliente():
    id_cli = entrada_id_cliente.get().strip()
    nome   = entrada_nome_upd.get().strip()
    cpf    = entrada_cpf_upd.get().strip()
    placa  = entrada_placa_upd.get().strip()
    if not id_cli.isdigit():
        messagebox.showerror("Erro", "Informe um ID válido.")
        return
    cursor.execute("UPDATE clientes SET nome=?, cpf=?, placa=? WHERE id=?",
                   (nome, cpf, placa, id_cli))
    conexao.commit()
    messagebox.showinfo("Sucesso", "Cliente atualizado com sucesso!")

def excluir_cliente():
    id_cli = entrada_id_cliente.get().strip()
    if not id_cli.isdigit():
        messagebox.showerror("Erro", "Informe um ID válido.")
        return
    if messagebox.askyesno("Confirmar", "Deseja excluir este cliente?"):
        cursor.execute("DELETE FROM clientes WHERE id=?", (id_cli,))
        conexao.commit()
        messagebox.showinfo("Sucesso", "Cliente excluído com sucesso!")

# ============================================================
# 4. Funções de Movimentação
# ============================================================
def registrar_entrada():
    placa = entrada_placa_mov.get().strip()
    if not placa:
        messagebox.showerror("Erro", "Informe a placa.")
        return
    data         = datetime.now().strftime("%Y-%m-%d")
    hora_entrada = datetime.now().strftime("%H:%M:%S")
    cursor.execute(
        "INSERT INTO movimentacoes (placa, data, hora_entrada, hora_saida, valor, status) "
        "VALUES (?, ?, ?, '', 0, 'aberto')",
        (placa, data, hora_entrada)
    )
    conexao.commit()
    messagebox.showinfo("Entrada Registrada", f"Placa: {placa}\nHorário: {hora_entrada}")
    entrada_placa_mov.delete(0, tk.END)

def registrar_saida():
    id_mov = entrada_id_mov.get().strip()
    taxa   = entrada_taxa.get().strip()
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
    hora_saida   = datetime.now().strftime("%H:%M:%S")
    hora_entrada = r[0]
    fmt = "%H:%M:%S"
    try:
        delta = datetime.strptime(hora_saida, fmt) - datetime.strptime(hora_entrada, fmt)
        horas = delta.seconds / 3600
    except Exception:
        horas = 0
    valor = round(horas * taxa_hora, 2)
    cursor.execute("UPDATE movimentacoes SET hora_saida=?, valor=? WHERE id=?",
                   (hora_saida, valor, id_mov))
    conexao.commit()
    messagebox.showinfo("Saída Registrada",
        f"Hora de saída: {hora_saida}\nTempo: {horas:.2f}h\nValor: R$ {valor:.2f}")

def listar_movimentacoes():
    cursor.execute("SELECT * FROM movimentacoes")
    registros = cursor.fetchall()
    texto_mov.delete("1.0", tk.END)
    texto_mov.insert(tk.END,
        f"{'ID':<5} {'Placa':<10} {'Data':<12} {'Entrada':<10} {'Saída':<10} {'Valor':>8}  Status\n")
    texto_mov.insert(tk.END, "-" * 65 + "\n")
    for r in registros:
        texto_mov.insert(tk.END,
            f"{r[0]:<5} {r[1]:<10} {r[2]:<12} {r[3]:<10} {r[4] or '---':<10} R${r[5]:>6.2f}  {r[6]}\n")

# ============================================================
# 5. Funções de Cobrança
# ============================================================
def listar_abertos():
    cursor.execute("SELECT * FROM movimentacoes WHERE status='aberto'")
    registros = cursor.fetchall()
    texto_cobranca.delete("1.0", tk.END)
    texto_cobranca.insert(tk.END,
        f"{'ID':<5} {'Placa':<10} {'Data':<12} {'Entrada':<10} {'Saída':<10} {'Valor':>8}\n")
    texto_cobranca.insert(tk.END, "-" * 60 + "\n")
    for r in registros:
        texto_cobranca.insert(tk.END,
            f"{r[0]:<5} {r[1]:<10} {r[2]:<12} {r[3]:<10} {r[4] or '---':<10} R${r[5]:>6.2f}\n")

def baixar_pagamento():
    id_mov = entrada_id_baixa.get().strip()
    if not id_mov.isdigit():
        messagebox.showerror("Erro", "Informe um ID válido.")
        return
    cursor.execute("UPDATE movimentacoes SET status='pago' WHERE id=?", (id_mov,))
    conexao.commit()
    messagebox.showinfo("Sucesso", "Pagamento confirmado com sucesso!")
    entrada_id_baixa.delete(0, tk.END)

# ============================================================
# 6. Funções de Relatórios
# ============================================================
def relatorio_clientes():
    cursor.execute("SELECT * FROM clientes")
    registros = cursor.fetchall()
    texto_relatorio.delete("1.0", tk.END)
    texto_relatorio.insert(tk.END, "CLIENTES CADASTRADOS\n" + "=" * 60 + "\n")
    for r in registros:
        texto_relatorio.insert(tk.END,
            f"ID: {r[0]:<4} | Nome: {r[1]:<25} | CPF: {r[2]:<15} | Placa: {r[3]}\n")

def relatorio_em_aberto():
    cursor.execute("SELECT * FROM movimentacoes WHERE status='aberto'")
    registros = cursor.fetchall()
    texto_relatorio.delete("1.0", tk.END)
    texto_relatorio.insert(tk.END, "RECEBIMENTOS EM ABERTO\n" + "=" * 60 + "\n")
    for r in registros:
        texto_relatorio.insert(tk.END,
            f"ID:{r[0]:<4} Placa:{r[1]:<9} Data:{r[2]:<11} Entrada:{r[3]:<9} Saída:{r[4] or '---':<9} R${r[5]:.2f}\n")

def relatorio_recebimentos():
    cursor.execute("SELECT * FROM movimentacoes WHERE status='pago'")
    registros = cursor.fetchall()
    texto_relatorio.delete("1.0", tk.END)
    texto_relatorio.insert(tk.END, "RECEBIMENTOS PAGOS\n" + "=" * 60 + "\n")
    total = sum(r[5] for r in registros)
    for r in registros:
        texto_relatorio.insert(tk.END,
            f"ID:{r[0]:<4} Placa:{r[1]:<9} Data:{r[2]:<11} Entrada:{r[3]:<9} Saída:{r[4]:<9} R${r[5]:.2f}\n")
    texto_relatorio.insert(tk.END, f"\nTOTAL RECEBIDO: R$ {total:.2f}\n")

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
    texto_relatorio.insert(tk.END, "TOP 5 CLIENTES MAIS FREQUENTES\n" + "=" * 60 + "\n")
    for i, r in enumerate(registros, 1):
        barra = "█" * r[1]
        texto_relatorio.insert(tk.END, f"{i}. {r[0]:<25} {r[1]:>3} uso(s)  {barra}\n")
    if registros:
        nomes = [r[0] for r in registros]
        usos  = [r[1] for r in registros]
        fig, ax = plt.subplots(figsize=(7, 4))
        bars = ax.barh(nomes[::-1], usos[::-1], color="#2563EB")
        ax.set_xlabel("Número de usos")
        ax.set_title("Top 5 Clientes por Frequência")
        ax.bar_label(bars, padding=4)
        plt.tight_layout()
        plt.show()

# ============================================================
# 7. Função de PDF
# ============================================================
def gerar_pdf():
    caminho = filedialog.asksaveasfilename(
        defaultextension=".pdf",
        filetypes=[("PDF files", "*.pdf")],
        title="Salvar relatório como"
    )
    if not caminho:
        return
    try:
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", "B", 14)
        pdf.cell(0, 10, "Relatório de Estacionamento", ln=True, align="C")
        pdf.ln(4)
        pdf.set_font("Arial", size=10)
        pdf.cell(0, 8, f"Gerado em: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}", ln=True)
        pdf.ln(4)

        pdf.set_font("Arial", "B", 11)
        pdf.cell(0, 8, "Movimentações Pagas", ln=True)
        pdf.set_font("Arial", size=9)
        cursor.execute("SELECT * FROM movimentacoes WHERE status='pago'")
        registros = cursor.fetchall()
        total = 0
        for r in registros:
            linha = f"ID:{r[0]} | Placa:{r[1]} | Data:{r[2]} | Entrada:{r[3]} | Saída:{r[4]} | R${r[5]:.2f}"
            pdf.multi_cell(0, 7, linha)
            total += r[5]
        pdf.ln(2)
        pdf.set_font("Arial", "B", 10)
        pdf.cell(0, 8, f"Total recebido: R$ {total:.2f}", ln=True)

        pdf.output(caminho)
        messagebox.showinfo("Sucesso", f"PDF gerado com sucesso!\n{caminho}")
    except Exception as e:
        messagebox.showerror("Erro", f"Erro ao gerar PDF:\n{str(e)}")

# ============================================================
# 8. Janela principal
# ============================================================
janela = tk.Tk()
janela.title("Controle de Estacionamento")
janela.geometry("750x620")
janela.configure(bg=COR_FUNDO)
janela.resizable(True, True)

style = ttk.Style()
style.theme_use("clam")
style.configure("TNotebook",        background=COR_FUNDO, borderwidth=0)
style.configure("TNotebook.Tab",    background="#E5E7EB", foreground=COR_TEXTO,
                padding=[14, 6],    font=("Segoe UI", 10))
style.map("TNotebook.Tab",
          background=[("selected", COR_BRANCO)],
          foreground=[("selected", COR_PRIMARIA)])
style.configure("TFrame", background=COR_FUNDO)

abas = ttk.Notebook(janela)
abas.pack(expand=True, fill="both", padx=0, pady=0)

# ============================================================
# ABA 1 — CLIENTES
# ============================================================
aba_clientes = tk.Frame(abas, bg=COR_FUNDO)
abas.add(aba_clientes, text="  Clientes  ")

canvas_cli = tk.Canvas(aba_clientes, bg=COR_FUNDO, highlightthickness=0)
scroll_cli  = ttk.Scrollbar(aba_clientes, orient="vertical", command=canvas_cli.yview)
inner_cli   = tk.Frame(canvas_cli, bg=COR_FUNDO)
inner_cli.bind("<Configure>",
    lambda e: canvas_cli.configure(scrollregion=canvas_cli.bbox("all")))
canvas_cli.create_window((0, 0), window=inner_cli, anchor="nw")
canvas_cli.configure(yscrollcommand=scroll_cli.set)
canvas_cli.pack(side="left", fill="both", expand=True)
scroll_cli.pack(side="right", fill="y")

# -- Cadastro
card_cad = frame_card(inner_cli, "CADASTRAR CLIENTE", pady_top=12)
card_cad.columnconfigure(1, weight=1)

label_entrada(card_cad, "Nome:",  0, 0)
entrada_nome = campo_entry(card_cad, 0, 1)

label_entrada(card_cad, "CPF:",   1, 0)
entrada_cpf  = campo_entry(card_cad, 1, 1)

label_entrada(card_cad, "Placa:", 2, 0)
entrada_placa = campo_entry(card_cad, 2, 1)

botao_primario(card_cad, "Cadastrar Cliente", cadastrar_cliente)\
    .grid(row=3, column=0, columnspan=2, pady=10, padx=12, sticky="ew")

separador(inner_cli)

# -- Atualizar / Excluir
card_upd = frame_card(inner_cli, "EDITAR / EXCLUIR CLIENTE")
card_upd.columnconfigure(1, weight=1)

label_entrada(card_upd, "ID do cliente:", 0, 0)
entrada_id_cliente = campo_entry(card_upd, 0, 1, largura=8)

label_entrada(card_upd, "Novo nome:",  1, 0)
entrada_nome_upd = campo_entry(card_upd, 1, 1)

label_entrada(card_upd, "Novo CPF:",   2, 0)
entrada_cpf_upd  = campo_entry(card_upd, 2, 1)

label_entrada(card_upd, "Nova placa:", 3, 0)
entrada_placa_upd = campo_entry(card_upd, 3, 1)

frame_btns_upd = tk.Frame(card_upd, bg=COR_BRANCO)
frame_btns_upd.grid(row=4, column=0, columnspan=2, pady=10, padx=12, sticky="ew")
botao_primario(frame_btns_upd, "Salvar alterações", atualizar_cliente, largura=22)\
    .pack(side="left", padx=(0, 8))
botao_secundario(frame_btns_upd, "Excluir cliente", excluir_cliente, largura=18)\
    .pack(side="left")

separador(inner_cli)

# -- Listar
frame_listar = tk.Frame(inner_cli, bg=COR_FUNDO)
frame_listar.pack(fill="x", padx=16, pady=(4, 4))
botao_secundario(frame_listar, "Listar todos os clientes", listar_clientes, largura=30)\
    .pack(side="left")

texto_clientes = texto_area(inner_cli, altura=8)

# ============================================================
# ABA 2 — MOVIMENTAÇÃO
# ============================================================
aba_mov = tk.Frame(abas, bg=COR_FUNDO)
abas.add(aba_mov, text="  Movimentação  ")

# -- Entrada
card_entrada = frame_card(aba_mov, "REGISTRAR ENTRADA", pady_top=12)
card_entrada.columnconfigure(1, weight=1)

label_entrada(card_entrada, "Placa do veículo:", 0, 0)
entrada_placa_mov = campo_entry(card_entrada, 0, 1)

botao_primario(card_entrada, "Registrar Entrada", registrar_entrada)\
    .grid(row=1, column=0, columnspan=2, pady=10, padx=12, sticky="ew")

separador(aba_mov)

# -- Saída
card_saida = frame_card(aba_mov, "REGISTRAR SAÍDA")
card_saida.columnconfigure(1, weight=1)

label_entrada(card_saida, "ID da movimentação:", 0, 0)
entrada_id_mov = campo_entry(card_saida, 0, 1, largura=8)

label_entrada(card_saida, "Taxa por hora (R$):", 1, 0)
entrada_taxa = campo_entry(card_saida, 1, 1, largura=10)

botao_primario(card_saida, "Registrar Saída", registrar_saida)\
    .grid(row=2, column=0, columnspan=2, pady=10, padx=12, sticky="ew")

separador(aba_mov)

frame_listar_mov = tk.Frame(aba_mov, bg=COR_FUNDO)
frame_listar_mov.pack(fill="x", padx=16, pady=(4, 4))
botao_secundario(frame_listar_mov, "Listar todas as movimentações", listar_movimentacoes, largura=32)\
    .pack(side="left")

texto_mov = texto_area(aba_mov, altura=10)

# ============================================================
# ABA 3 — COBRANÇA
# ============================================================
aba_cobranca = tk.Frame(abas, bg=COR_FUNDO)
abas.add(aba_cobranca, text="  Cobrança  ")

frame_btn_abertos = tk.Frame(aba_cobranca, bg=COR_FUNDO)
frame_btn_abertos.pack(fill="x", padx=16, pady=(12, 6))
botao_secundario(frame_btn_abertos, "Ver recebimentos em aberto", listar_abertos, largura=30)\
    .pack(side="left")

texto_cobranca = texto_area(aba_cobranca, altura=10)

separador(aba_cobranca)

card_baixa = frame_card(aba_cobranca, "CONFIRMAR PAGAMENTO")
card_baixa.columnconfigure(1, weight=1)

label_entrada(card_baixa, "ID da movimentação:", 0, 0)
entrada_id_baixa = campo_entry(card_baixa, 0, 1, largura=8)

botao_primario(card_baixa, "Confirmar Pagamento", baixar_pagamento)\
    .grid(row=1, column=0, columnspan=2, pady=10, padx=12, sticky="ew")

# ============================================================
# ABA 4 — RELATÓRIOS
# ============================================================
aba_relatorios = tk.Frame(abas, bg=COR_FUNDO)
abas.add(aba_relatorios, text="  Relatórios  ")

frame_btns_rel = frame_card(aba_relatorios, "GERAR RELATÓRIO", pady_top=12)

botoes_rel = [
    ("Clientes cadastrados",       relatorio_clientes),
    ("Recebimentos em aberto",     relatorio_em_aberto),
    ("Recebimentos pagos",         relatorio_recebimentos),
    ("Top 5 clientes (+ gráfico)", relatorio_top5),
]
for i, (txt, cmd) in enumerate(botoes_rel):
    botao_secundario(frame_btns_rel, txt, cmd, largura=28)\
        .grid(row=i // 2, column=i % 2, padx=8, pady=6, sticky="ew")
frame_btns_rel.columnconfigure(0, weight=1)
frame_btns_rel.columnconfigure(1, weight=1)

separador(aba_relatorios)
texto_relatorio = texto_area(aba_relatorios, altura=14)

# ============================================================
# ABA 5 — GERAR PDF
# ============================================================
aba_pdf = tk.Frame(abas, bg=COR_FUNDO)
abas.add(aba_pdf, text="  PDF  ")

card_pdf = frame_card(aba_pdf, "EXPORTAR RELATÓRIO EM PDF", pady_top=12)
tk.Label(card_pdf, text="Gera um PDF com todas as movimentações pagas e o total recebido.",
         bg=COR_BRANCO, fg=COR_SECUNDARIA, font=("Segoe UI", 10),
         wraplength=500, justify="left")\
    .grid(row=0, column=0, padx=12, pady=(10, 6), sticky="w")

botao_primario(card_pdf, "Salvar PDF…", gerar_pdf, largura=22)\
    .grid(row=1, column=0, padx=12, pady=(4, 12), sticky="w")

# ============================================================
# 9. Iniciar
# ============================================================
janela.mainloop()
conexao.close()