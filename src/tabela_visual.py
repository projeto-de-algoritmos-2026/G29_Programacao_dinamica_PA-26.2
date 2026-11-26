import tkinter as tk
from dataclasses import dataclass
from tkinter import font as tkfont

from src.item import Item
from src.knapsack import ResultadoMochila

MARGEM = 12
# espaco entre o texto e a borda da celula
FOLGA = 8
MAX_CARACTERES_NOME = 18

FONTE = ("Arial", 10)
FONTE_NEGRITO = ("Arial", 10, "bold")

COR_GRADE = "#cbd5e1"
COR_CABECALHO = "#f1f5f9"
COR_TEXTO = "#0f172a"
COR_TEXTO_FRACO = "#64748b"

class AreaTabela(tk.Frame):
    # a tabela tem capacidade + 1 colunas, entao pode nao caber na janela
    def __init__(self, mestre: tk.Misc, largura: int = 720, altura: int = 320) -> None:
        super().__init__(mestre)

        self.canvas = tk.Canvas(
            self, width=largura, height=altura, bg="white", highlightthickness=0
        )
        rolagem_vertical = tk.Scrollbar(
            self, orient="vertical", command=self.canvas.yview
        )
        rolagem_horizontal = tk.Scrollbar(
            self, orient="horizontal", command=self.canvas.xview
        )
        self.canvas.configure(
            yscrollcommand=rolagem_vertical.set,
            xscrollcommand=rolagem_horizontal.set,
        )

        self.canvas.grid(row=0, column=0, sticky="nsew")
        rolagem_vertical.grid(row=0, column=1, sticky="ns")
        rolagem_horizontal.grid(row=1, column=0, sticky="ew")
        # so o canvas cresce quando a janela muda de tamanho
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)

        # roda do mouse rola na vertical; com shift, na horizontal
        self.canvas.bind("<MouseWheel>", self.rolar_vertical)
        self.canvas.bind("<Shift-MouseWheel>", self.rolar_horizontal)

    def rolar_vertical(self, evento: tk.Event) -> None:
        self.canvas.yview_scroll(-1 if evento.delta > 0 else 1, "units")

    def rolar_horizontal(self, evento: tk.Event) -> None:
        self.canvas.xview_scroll(-1 if evento.delta > 0 else 1, "units")

@dataclass
class Geometria:
    largura_rotulo: int
    largura_celula: int
    altura_celula: int

    @property
    def x_tabela(self) -> int:
        # borda esquerda da coluna c = 0, logo depois dos rotulos das linhas
        return MARGEM + self.largura_rotulo

    @property
    def y_tabela(self) -> int:
        # borda de cima da linha i = 0; acima ficam o titulo (i = -2)
        # e a linha das capacidades (i = -1)
        return MARGEM + 2 * self.altura_celula

    def celula(self, i: int, c: int) -> tuple[int, int, int, int]:
        x1 = self.x_tabela + c * self.largura_celula
        y1 = self.y_tabela + i * self.altura_celula
        return x1, y1, x1 + self.largura_celula, y1 + self.altura_celula

    def rotulo(self, i: int) -> tuple[int, int, int, int]:
        _, y1, _, y2 = self.celula(i, 0)
        return MARGEM, y1, self.x_tabela, y2

def encurtar(nome: str) -> str:
    if len(nome) <= MAX_CARACTERES_NOME:
        return nome
    return nome[: MAX_CARACTERES_NOME - 1] + "…"

def rotulos_das_linhas(itens: list[Item]) -> list[str]:
    rotulos = ["0  nenhum item"]

    for i, item in enumerate(itens, start=1):
        rotulos.append(f"{i}  {encurtar(item.nome)} ({item.peso} kg, {item.valor})")

    return rotulos

def calcular_geometria(
    canvas: tk.Canvas,
    rotulos: list[str],
    tabela: list[list[int]],
) -> Geometria:
    # mede o texto com a fonte de verdade: com a escala do Windows em 125% ou 150%
    # um tamanho fixo em pixels deixaria os numeros saindo das celulas
    fonte = tkfont.Font(root=canvas, font=FONTE_NEGRITO)
    capacidade = len(tabela[0]) - 1
    maior_numero = max(capacidade, max(map(max, tabela)))

    altura_celula = fonte.metrics("linespace") + FOLGA
    largura_celula = max(fonte.measure(str(maior_numero)) + 2 * FOLGA, altura_celula)
    largura_rotulo = max(fonte.measure(texto) for texto in rotulos) + 2 * FOLGA

    return Geometria(largura_rotulo, largura_celula, altura_celula)

def desenhar_tabela(
    canvas: tk.Canvas,
    itens: list[Item],
    resultado: ResultadoMochila,
) -> None:
    canvas.delete("all")

    tabela = resultado.tabela
    capacidade = len(tabela[0]) - 1
    rotulos = rotulos_das_linhas(itens)
    cabecalho = "i  item (peso, importância)"
    geometria = calcular_geometria(canvas, [cabecalho, *rotulos], tabela)

    # titulo das colunas, alinhado com a coluna c = 0
    x1, y1, _, y2 = geometria.celula(-2, 0)
    canvas.create_text(
        x1, (y1 + y2) / 2, text="capacidade c (kg) →",
        anchor="w", font=FONTE, fill=COR_TEXTO_FRACO,
    )

    # linha i = -1: cabecalho dos rotulos e as capacidades 0..W
    desenhar_rotulo(canvas, geometria.rotulo(-1), cabecalho, COR_TEXTO_FRACO)
    for c in range(capacidade + 1):
        desenhar_celula(
            canvas, geometria.celula(-1, c), str(c), COR_CABECALHO, FONTE_NEGRITO
        )

    for i, rotulo in enumerate(rotulos):
        desenhar_rotulo(canvas, geometria.rotulo(i), rotulo, COR_TEXTO)

        for c in range(capacidade + 1):
            desenhar_celula(
                canvas, geometria.celula(i, c), str(tabela[i][c]), "white", FONTE
            )

    # a regiao de rolagem acompanha o tamanho da tabela desenhada
    _, _, x_fim, y_fim = canvas.bbox("all")
    canvas.configure(scrollregion=(0, 0, x_fim + MARGEM, y_fim + MARGEM))
    canvas.xview_moveto(0)
    canvas.yview_moveto(0)

def desenhar_rotulo(
    canvas: tk.Canvas,
    retangulo: tuple[int, int, int, int],
    texto: str,
    cor_texto: str,
) -> None:
    x1, y1, x2, y2 = retangulo
    canvas.create_rectangle(x1, y1, x2, y2, fill=COR_CABECALHO, outline=COR_GRADE)
    canvas.create_text(
        x1 + FOLGA, (y1 + y2) / 2, text=texto,
        anchor="w", font=FONTE, fill=cor_texto,
    )

def desenhar_celula(
    canvas: tk.Canvas,
    retangulo: tuple[int, int, int, int],
    texto: str,
    fundo: str,
    fonte: tuple,
) -> None:
    x1, y1, x2, y2 = retangulo
    canvas.create_rectangle(x1, y1, x2, y2, fill=fundo, outline=COR_GRADE)
    canvas.create_text(
        (x1 + x2) / 2, (y1 + y2) / 2, text=texto, font=fonte, fill=COR_TEXTO
    )
