import time
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

from src.guloso import resolver_guloso
from src.item import Item
from src.knapsack import ResultadoMochila, resolver_mochila
from src.leitor_csv import ErroValidacaoCSV, ler_itens_csv
from src.tabela_visual import AreaTabela, desenhar_tabela

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
        self.resultado: ResultadoMochila | None = None

        janela.title("Planejador de Bagagem — Knapsack 0/1")
        janela.geometry("1100x760")
        janela.minsize(820, 560)

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
        self.capacidade_input = ttk.Spinbox(
            controles,
            from_=1,
            to=50,
            textvariable=self.capacidade_var,
            width=5,
        )
        self.capacidade_input.grid(row=0, column=3, sticky="w")
        ttk.Label(controles, text="kg").grid(row=0, column=4, padx=(5, 12))

        self.resolver_botao = ttk.Button(
            controles,
            text="Resolver",
            command=self.resolver,
            state="disabled",
        )
        self.resolver_botao.grid(row=0, column=5)

        self.status_var = tk.StringVar(value="Selecione um arquivo CSV para começar.")
        ttk.Label(principal, textvariable=self.status_var).grid(
            row=3, column=0, sticky="w", pady=(0, 8)
        )

        paineis = ttk.Panedwindow(principal, orient="vertical")
        paineis.grid(row=4, column=0, sticky="nsew")

        painel_itens = ttk.Frame(paineis)
        painel_itens.rowconfigure(0, weight=1)
        painel_itens.columnconfigure(0, weight=1)
        self.lista_itens = ttk.Treeview(
            painel_itens,
            columns=("id", "nome", "peso", "valor", "pd", "guloso"),
            show="headings",
            height=8,
        )
        colunas = (
            ("id", "ID", 55),
            ("nome", "Item", 280),
            ("peso", "Peso (kg)", 95),
            ("valor", "Importância", 105),
            ("pd", "PD", 55),
            ("guloso", "Guloso", 75),
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
        paineis.add(painel_itens, weight=1)

        painel_tabela = ttk.Frame(paineis)
        painel_tabela.rowconfigure(1, weight=1)
        painel_tabela.columnconfigure(0, weight=1)
        ttk.Label(painel_tabela, text="Tabela da programação dinâmica").grid(
            row=0, column=0, sticky="w", pady=(8, 4)
        )
        self.area_tabela = AreaTabela(painel_tabela, altura=300)
        self.area_tabela.grid(row=1, column=0, sticky="nsew")
        paineis.add(painel_tabela, weight=2)

        self.resumo_var = tk.StringVar(value="")
        ttk.Label(
            principal,
            textvariable=self.resumo_var,
            justify="left",
            wraplength=1000,
        ).grid(row=5, column=0, sticky="ew", pady=(10, 0))

    def abrir_csv(self) -> None:
        caminho = filedialog.askopenfilename(
            parent=self.janela,
            title="Selecionar arquivo CSV",
            filetypes=(("Arquivos CSV", "*.csv"), ("Todos os arquivos", "*.*")),
        )
        if not caminho:
            return

        self._limpar_resultado(desabilitar_resolucao=True)
        self.caminho_csv = None
        self.itens = []

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
        self.resolver_botao.configure(state="normal")

    def resolver(self) -> None:
        if self.caminho_csv is None:
            messagebox.showerror(
                "CSV não selecionado",
                "Selecione um arquivo CSV antes de resolver.",
                parent=self.janela,
            )
            return

        try:
            capacidade = ler_capacidade(self.capacidade_var.get())
        except ValueError as erro:
            messagebox.showerror("Capacidade inválida", str(erro), parent=self.janela)
            self.capacidade_input.focus_set()
            return

        self._limpar_resultado()
        inicio = time.perf_counter()
        resultado = resolver_mochila(self.itens, capacidade)
        itens_gulosos = resolver_guloso(self.itens, capacidade)
        tempo_ms = (time.perf_counter() - inicio) * 1000

        self.resultado = resultado
        escolhidos_pd = {item.id for item in resultado.escolhidos}
        escolhidos_guloso = {item.id for item in itens_gulosos}

        for item in self.itens:
            self.lista_itens.insert(
                "",
                "end",
                values=(
                    item.id,
                    item.nome,
                    item.peso,
                    item.valor,
                    "✓" if item.id in escolhidos_pd else "–",
                    "✓" if item.id in escolhidos_guloso else "–",
                ),
            )

        desenhar_tabela(self.area_tabela.canvas, self.itens, resultado)
        nomes_pd = ", ".join(item.nome for item in resultado.escolhidos) or "nenhum"
        nomes_gulosos = ", ".join(item.nome for item in itens_gulosos) or "nenhum"
        valor_guloso = sum(item.valor for item in itens_gulosos)
        peso_guloso = sum(item.peso for item in itens_gulosos)
        self.resumo_var.set(
            f"PD: importância {resultado.valor_total} · "
            f"{resultado.peso_total} de {capacidade} kg · {nomes_pd}\n"
            f"Guloso: importância {valor_guloso} · "
            f"{peso_guloso} de {capacidade} kg · {nomes_gulosos}\n"
            f"Tempo de execução: {tempo_ms:.2f} ms"
        )

    def _limpar_resultado(self, *, desabilitar_resolucao: bool = False) -> None:
        self.resultado = None
        for item_id in self.lista_itens.get_children():
            self.lista_itens.delete(item_id)
        self.area_tabela.canvas.delete("all")
        self.resumo_var.set("")
        if desabilitar_resolucao:
            self.resolver_botao.configure(state="disabled")
