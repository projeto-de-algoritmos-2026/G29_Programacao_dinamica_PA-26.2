import tkinter as tk
from dataclasses import dataclass
from tkinter import font as tkfont

from src.item import Item
from src.knapsack import ResultadoMochila

MARGEM = 12
# espaco entre o texto e a borda da celula
FOLGA = 8
MAX_CARACTERES_NOME = 18
# o selo com o numero do passo fica no canto de cima, a esquerda da celula,
# e o valor anda um pouco para a direita para nao encostar nele
RECUO_SELO = 2
DESLOCAMENTO_VALOR = 3

FONTE = ("Arial", 10)
FONTE_NEGRITO = ("Arial", 10, "bold")
FONTE_SELO = ("Arial", 7, "bold")

COR_GRADE = "#cbd5e1"
COR_CABECALHO = "#f1f5f9"
COR_TEXTO = "#0f172a"
COR_TEXTO_FRACO = "#64748b"
# mesmas cores da figura do plano
COR_ENTRA = "#fde68a"
COR_FORA = "#e2e8f0"
COR_RESPOSTA = "#b45309"

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
    largura_selo: int
    altura_selo: int

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

    def centro_valor(self, i: int, c: int) -> tuple[float, float]:
        x1, y1, x2, y2 = self.celula(i, c)
        return (x1 + x2) / 2 + DESLOCAMENTO_VALOR, (y1 + y2) / 2

    def selo(self, i: int, c: int) -> tuple[int, int, int, int]:
        x1, y1, _, _ = self.celula(i, c)
        x, y = x1 + RECUO_SELO, y1 + RECUO_SELO
        return x, y, x + self.largura_selo, y + self.altura_selo

@dataclass
class Passo:
    numero: int
    entrou: bool

def passos_da_reconstrucao(
    caminho: list[tuple[int, int]],
) -> dict[tuple[int, int], Passo]:
    passos = {}

    # cada celula do caminho, menos a ultima (na linha 0), e um passo.
    # como o peso e pelo menos 1, o item i entrou quando a coluna muda na subida
    for numero, (celula, seguinte) in enumerate(zip(caminho, caminho[1:]), start=1):
        passos[celula] = Passo(numero, entrou=seguinte[1] != celula[1])

    return passos

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
    fonte_selo = tkfont.Font(root=canvas, font=FONTE_SELO)
    capacidade = len(tabela[0]) - 1
    maior_numero = max(capacidade, max(map(max, tabela)))
    # o ultimo passo recebe o numero de itens
    maior_passo = len(tabela) - 1

    altura_selo = fonte_selo.metrics("linespace")
    largura_selo = max(altura_selo, fonte_selo.measure(str(maior_passo)) + FOLGA // 2)

    altura_celula = fonte.metrics("linespace") + FOLGA
    largura_valor = fonte.measure(str(maior_numero))
    # o valor e centralizado e deslocado para a direita; a borda esquerda dele
    # (largura_celula / 2 + deslocamento - largura_valor / 2) fica depois do selo
    ocupado_pelo_selo = RECUO_SELO + largura_selo + RECUO_SELO
    largura_celula = largura_valor + 2 * (ocupado_pelo_selo - DESLOCAMENTO_VALOR)
    largura_rotulo = max(fonte.measure(texto) for texto in rotulos) + 2 * FOLGA

    return Geometria(
        largura_rotulo, largura_celula, altura_celula, largura_selo, altura_selo
    )

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
    passos = passos_da_reconstrucao(resultado.caminho)

    # titulo das colunas, alinhado com a coluna c = 0
    x1, y1, _, y2 = geometria.celula(-2, 0)
    canvas.create_text(
        x1, (y1 + y2) / 2, text="capacidade c (kg) →",
        anchor="w", font=FONTE, fill=COR_TEXTO_FRACO,
    )

    # linha i = -1: cabecalho dos rotulos e as capacidades 0..W
    desenhar_rotulo(canvas, geometria.rotulo(-1), cabecalho, COR_TEXTO_FRACO)
    for c in range(capacidade + 1):
        desenhar_celula(canvas, geometria, -1, c, str(c), COR_CABECALHO, FONTE_NEGRITO)

    for i, rotulo in enumerate(rotulos):
        desenhar_rotulo(canvas, geometria.rotulo(i), rotulo, COR_TEXTO)

        for c in range(capacidade + 1):
            valor = str(tabela[i][c])
            passo = passos.get((i, c))

            if passo is None:
                desenhar_celula(canvas, geometria, i, c, valor, "white", FONTE)
                continue

            # celula visitada na reconstrucao: ambar se o item entrou, cinza se nao
            fundo = COR_ENTRA if passo.entrou else COR_FORA
            cor_selo = COR_RESPOSTA if passo.entrou else COR_TEXTO_FRACO
            desenhar_celula(canvas, geometria, i, c, valor, fundo, FONTE_NEGRITO)
            desenhar_selo(canvas, geometria.selo(i, c), passo.numero, cor_selo)

    # a resposta OPT(n, W) ganha uma borda grossa, por cima da grade
    canvas.create_rectangle(
        *geometria.celula(len(itens), capacidade), outline=COR_RESPOSTA, width=2
    )

    desenhar_legenda(canvas, geometria, len(itens), capacidade)

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
    geometria: Geometria,
    i: int,
    c: int,
    texto: str,
    fundo: str,
    fonte: tuple,
) -> None:
    canvas.create_rectangle(*geometria.celula(i, c), fill=fundo, outline=COR_GRADE)
    canvas.create_text(
        *geometria.centro_valor(i, c), text=texto, font=fonte, fill=COR_TEXTO
    )

def desenhar_selo(
    canvas: tk.Canvas,
    retangulo: tuple[float, float, float, float],
    numero: int,
    cor: str,
) -> None:
    x1, y1, x2, y2 = retangulo
    canvas.create_oval(x1, y1, x2, y2, fill=cor, outline="")
    canvas.create_text(
        (x1 + x2) / 2, (y1 + y2) / 2, text=str(numero), font=FONTE_SELO, fill="white"
    )

def desenhar_legenda(
    canvas: tk.Canvas,
    geometria: Geometria,
    n: int,
    capacidade: int,
) -> None:
    fonte = tkfont.Font(root=canvas, font=FONTE)
    lado = geometria.altura_selo
    # o espaco entre o simbolo e o texto cresce junto com a fonte
    espaco = lado // 2
    altura_linha = geometria.altura_celula
    # comeca logo abaixo da tabela e quebra a linha para nao passar da largura dela
    _, _, x_limite, y_fim_tabela = geometria.celula(n, capacidade)
    x, y = MARGEM, y_fim_tabela + FOLGA

    entradas = [
        ("entra", "item entra"),
        ("fora", "item fica de fora"),
        ("resposta", "resposta OPT(n, W)"),
        ("passo", "ordem da reconstrução"),
    ]

    for tipo, texto in entradas:
        largura = lado + espaco + fonte.measure(texto)
        if x > MARGEM and x + largura > x_limite:
            x, y = MARGEM, y + altura_linha

        meio = y + altura_linha / 2
        amostra = (x, meio - lado / 2, x + lado, meio + lado / 2)

        if tipo == "passo":
            desenhar_selo(canvas, amostra, 1, COR_RESPOSTA)
        elif tipo == "resposta":
            canvas.create_rectangle(*amostra, fill="white", outline=COR_RESPOSTA, width=2)
        else:
            fundo = COR_ENTRA if tipo == "entra" else COR_FORA
            canvas.create_rectangle(*amostra, fill=fundo, outline=COR_GRADE)

        canvas.create_text(
            x + lado + espaco, meio, text=texto,
            anchor="w", font=FONTE, fill=COR_TEXTO_FRACO,
        )
        x += largura + 2 * FOLGA
