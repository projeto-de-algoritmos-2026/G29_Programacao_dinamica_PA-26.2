from dataclasses import dataclass

from src.item import Item

@dataclass
class ResultadoMochila:
    escolhidos: list[Item]
    peso_total: int
    valor_total: int
    # tabela[i][c] = OPT(i, c), com (n + 1) linhas e (capacidade + 1) colunas
    tabela: list[list[int]]
    # celulas (i, c) visitadas na reconstrucao, de (n, capacidade) ate a linha 0
    caminho: list[tuple[int, int]]

def resolver_mochila(itens: list[Item], capacidade: int) -> ResultadoMochila:
    if capacidade < 0:
        raise ValueError("A capacidade não pode ser negativa")

    # versao provisoria: tabela zerada no formato certo, para a interface ja poder desenhar
    tabela = [[0] * (capacidade + 1) for _ in range(len(itens) + 1)]

    return ResultadoMochila(
        escolhidos=[],
        peso_total=0,
        valor_total=0,
        tabela=tabela,
        caminho=[],
    )
