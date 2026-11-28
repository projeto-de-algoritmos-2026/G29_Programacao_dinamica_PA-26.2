import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

from src.item import Item
from src.leitor_csv import ErroValidacaoCSV, ler_itens_csv

def ler_capacidade(texto: str) -> int:
    try:
        capacidade = int(texto)
    except ValueError as erro:
        raise ValueError("A capacidade deve ser um número inteiro.") from erro

    if not 1 <= capacidade <= 50:
        raise ValueError("A capacidade deve estar entre 1 e 50 kg.")

    return capacidade

class InterfaceBagagem:
    def __init__(self, janela: tk.Tk) -> None:
        self.janela = janela
        self.itens: list[Item] = []
        self.caminho_csv: Path | None = None

        janela.title("Planejador de Bagagem — Knapsack 0/1")
        janela.geometry("900x600")
        janela.minsize(700, 450)

        principal = ttk.Frame(janela, padding=16)
        principal.pack(fill="both", expand=True)
        principal.columnconfigure(0, weight=1)
        principal.rowconfigure(4, weight=1)

        ttk.Label(
            principal,
            text="Planejador de Bagagem",
            font=("TkDefaultFont", 18, "bold"),
        ).grid(row=0, column=0, sticky="w")
        ttk.Label(
            principal,
            text="Knapsack 0/1 — escolha os itens de maior importância sem exceder o peso.",
        ).grid(row=1, column=0, sticky="w", pady=(2, 14))

        controles = ttk.Frame(principal)
        controles.grid(row=2, column=0, sticky="ew", pady=(0, 10))
        controles.columnconfigure(1, weight=1)

        ttk.Button(controles, text="Abrir CSV", command=self.abrir_csv).grid(
            row=0, column=0, padx=(0, 8)
        )
        self.arquivo_var = tk.StringVar(value="Nenhum arquivo selecionado")
        ttk.Label(controles, textvariable=self.arquivo_var).grid(
            row=0, column=1, sticky="w"
        )

        ttk.Label(controles, text="Capacidade").grid(
            row=0, column=2, padx=(18, 6)
        )
        self.capacidade_var = tk.StringVar(value="10")
        ttk.Spinbox(
            controles,
            from_=1,
            to=50,
            textvariable=self.capacidade_var,
            width=5,
        ).grid(row=0, column=3, sticky="w")
        ttk.Label(controles, text="kg").grid(row=0, column=4, padx=(5, 12))

        self.status_var = tk.StringVar(value="Selecione um arquivo CSV para começar.")
        ttk.Label(principal, textvariable=self.status_var).grid(
            row=3, column=0, sticky="w", pady=(0, 8)
        )

        painel_itens = ttk.Frame(principal)
        painel_itens.grid(row=4, column=0, sticky="nsew")
        painel_itens.rowconfigure(0, weight=1)
        painel_itens.columnconfigure(0, weight=1)

        self.lista_itens = ttk.Treeview(
            painel_itens,
            columns=("id", "nome", "peso", "valor"),
            show="headings",
        )
        colunas = (
            ("id", "ID", 55),
            ("nome", "Item", 280),
            ("peso", "Peso (kg)", 95),
            ("valor", "Importância", 105),
        )
        for coluna, titulo, largura in colunas:
            self.lista_itens.heading(coluna, text=titulo)
            self.lista_itens.column(coluna, width=largura, anchor="w")

        rolagem_itens = ttk.Scrollbar(
            painel_itens, orient="vertical", command=self.lista_itens.yview
        )
        self.lista_itens.configure(yscrollcommand=rolagem_itens.set)
        self.lista_itens.grid(row=0, column=0, sticky="nsew")
        rolagem_itens.grid(row=0, column=1, sticky="ns")

    def abrir_csv(self) -> None:
        caminho = filedialog.askopenfilename(
            parent=self.janela,
            title="Selecionar arquivo CSV",
            filetypes=(("Arquivos CSV", "*.csv"), ("Todos os arquivos", "*.*")),
        )
        if not caminho:
            return

        self.caminho_csv = None
        self.itens = []
        self._limpar_lista()

        try:
            itens = ler_itens_csv(caminho)
        except ErroValidacaoCSV as erro:
            self.arquivo_var.set(Path(caminho).name)
            self.status_var.set("O CSV contém erros de validação.")
            messagebox.showerror(
                "CSV inválido",
                "\n".join(erro.erros),
                parent=self.janela,
            )
            return
        except (OSError, UnicodeDecodeError) as erro:
            self.arquivo_var.set(Path(caminho).name)
            self.status_var.set("Não foi possível ler o arquivo.")
            messagebox.showerror(
                "Erro ao abrir CSV",
                f"Não foi possível ler o arquivo:\n{erro}",
                parent=self.janela,
            )
            return

        self.caminho_csv = Path(caminho)
        self.itens = itens
        self.arquivo_var.set(self.caminho_csv.name)
        self.status_var.set(f"{len(itens)} itens carregados.")
        for item in self.itens:
            self.lista_itens.insert(
                "",
                "end",
                values=(item.id, item.nome, item.peso, item.valor),
            )

    def _limpar_lista(self) -> None:
        for item_id in self.lista_itens.get_children():
            self.lista_itens.delete(item_id)
