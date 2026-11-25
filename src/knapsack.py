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

def montar_tabela(itens: list[Item], capacidade: int) -> list[list[int]]:
    # a linha 0 e "nenhum item": vale 0 para qualquer capacidade
    tabela = [[0] * (capacidade + 1) for _ in range(len(itens) + 1)]

    for i in range(1, len(itens) + 1):
        # a linha i usa itens[i - 1], porque a lista comeca em 0
        item = itens[i - 1]

        for c in range(capacidade + 1):
            sem_o_item = tabela[i - 1][c]
            tabela[i][c] = sem_o_item

            if item.peso <= c:
                com_o_item = item.valor + tabela[i - 1][c - item.peso]
                tabela[i][c] = max(sem_o_item, com_o_item)

    return tabela

def resolver_mochila(itens: list[Item], capacidade: int) -> ResultadoMochila:
    if capacidade < 0:
        raise ValueError("A capacidade não pode ser negativa")

    tabela = montar_tabela(itens, capacidade)

    # a reconstrucao dos itens escolhidos ainda nao foi feita
    return ResultadoMochila(
        escolhidos=[],
        peso_total=0,
        valor_total=tabela[len(itens)][capacidade],
        tabela=tabela,
        caminho=[],
    )
