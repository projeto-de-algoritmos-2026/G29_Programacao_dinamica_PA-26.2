from itertools import combinations
from random import Random

import pytest

from src.item import Item
from src.knapsack import resolver_mochila

def itens_do_exemplo() -> list[Item]:
    # mesmo exemplo do plano: o guloso leva 16, a PD leva 22
    return [
        Item(id=1, nome="Câmera", peso=1, valor=6),
        Item(id=2, nome="Notebook", peso=2, valor=10),
        Item(id=3, nome="Roupas", peso=3, valor=12),
    ]

def melhor_valor_por_forca_bruta(itens: list[Item], capacidade: int) -> int:
    # testa todos os subconjuntos: so serve para entradas pequenas
    melhor = 0

    for tamanho in range(len(itens) + 1):
        for subconjunto in combinations(itens, tamanho):
            if sum(item.peso for item in subconjunto) <= capacidade:
                melhor = max(melhor, sum(item.valor for item in subconjunto))

    return melhor

def gerar_itens(gerador: Random, quantidade: int) -> list[Item]:
    return [
        Item(
            id=identificador,
            nome=f"Item {identificador}",
            peso=gerador.randint(1, 10),
            valor=gerador.randint(1, 30),
        )
        for identificador in range(1, quantidade + 1)
    ]

def test_exemplo_escolhe_notebook_e_roupas() -> None:
    resultado = resolver_mochila(itens_do_exemplo(), 5)

    assert [item.nome for item in resultado.escolhidos] == ["Notebook", "Roupas"]
    assert resultado.peso_total == 5
    assert resultado.valor_total == 22

def test_exemplo_monta_a_tabela_do_plano() -> None:
    resultado = resolver_mochila(itens_do_exemplo(), 5)

    assert resultado.tabela == [
        [0, 0, 0, 0, 0, 0],
        [0, 6, 6, 6, 6, 6],
        [0, 6, 10, 16, 16, 16],
        [0, 6, 10, 16, 18, 22],
    ]

def test_exemplo_percorre_o_caminho_da_reconstrucao() -> None:
    resultado = resolver_mochila(itens_do_exemplo(), 5)

    assert resultado.caminho == [(3, 5), (2, 2), (1, 0), (0, 0)]

def test_resultado_equivale_a_forca_bruta() -> None:
    gerador = Random(42)

    for _ in range(100):
        itens = gerar_itens(gerador, gerador.randint(1, 12))
        capacidade = gerador.randint(0, 40)

        resultado = resolver_mochila(itens, capacidade)

        # so compara o valor: num empate, outro conjunto tambem seria otimo
        assert resultado.valor_total == melhor_valor_por_forca_bruta(itens, capacidade)

def test_solucao_e_valida_e_coerente_com_a_tabela() -> None:
    gerador = Random(42)

    for _ in range(100):
        itens = gerar_itens(gerador, gerador.randint(0, 12))
        capacidade = gerador.randint(0, 40)

        resultado = resolver_mochila(itens, capacidade)

        assert resultado.peso_total <= capacidade
        assert resultado.peso_total == sum(item.peso for item in resultado.escolhidos)
        assert resultado.valor_total == sum(item.valor for item in resultado.escolhidos)
        assert resultado.valor_total == resultado.tabela[len(itens)][capacidade]
        assert len(resultado.tabela) == len(itens) + 1
        assert all(len(linha) == capacidade + 1 for linha in resultado.tabela)
        assert resultado.caminho[0] == (len(itens), capacidade)
        assert len(resultado.caminho) == len(itens) + 1
        # os escolhidos saem na mesma ordem em que aparecem na entrada
        assert resultado.escolhidos == [
            item for item in itens if item in resultado.escolhidos
        ]

def test_sem_itens() -> None:
    resultado = resolver_mochila([], 4)

    assert resultado.escolhidos == []
    assert resultado.peso_total == 0
    assert resultado.valor_total == 0
    assert resultado.tabela == [[0, 0, 0, 0, 0]]
    assert resultado.caminho == [(0, 4)]

def test_capacidade_zero_nao_leva_nada() -> None:
    resultado = resolver_mochila(itens_do_exemplo(), 0)

    assert resultado.escolhidos == []
    assert resultado.valor_total == 0
    assert resultado.tabela == [[0], [0], [0], [0]]
    assert resultado.caminho == [(3, 0), (2, 0), (1, 0), (0, 0)]

def test_item_mais_pesado_que_a_capacidade_fica_de_fora() -> None:
    itens = [
        Item(id=1, nome="Barraca", peso=8, valor=50),
        Item(id=2, nome="Lanterna", peso=1, valor=3),
    ]

    resultado = resolver_mochila(itens, 5)

    assert [item.nome for item in resultado.escolhidos] == ["Lanterna"]
    assert resultado.valor_total == 3

def test_leva_todos_quando_cabem() -> None:
    itens = itens_do_exemplo()

    resultado = resolver_mochila(itens, 6)

    assert resultado.escolhidos == itens
    assert resultado.peso_total == 6
    assert resultado.valor_total == 28

def test_nao_altera_a_lista_original() -> None:
    itens = list(reversed(itens_do_exemplo()))
    ordem_original = itens.copy()

    resolver_mochila(itens, 5)

    assert itens == ordem_original

def test_capacidade_negativa_gera_erro() -> None:
    with pytest.raises(ValueError, match="negativa"):
        resolver_mochila(itens_do_exemplo(), -1)

@pytest.mark.parametrize(
    ("nome", "peso", "valor", "mensagem"),
    [
        ("   ", 1, 1, "nome"),
        ("Livro", 0, 1, "peso"),
        ("Livro", -2, 1, "peso"),
        ("Livro", 1.5, 1, "peso"),
        ("Livro", 1, 0, "valor"),
        ("Livro", 1, 2.5, "valor"),
    ],
)
def test_item_invalido_gera_erro(
    nome: str,
    peso: int,
    valor: int,
    mensagem: str,
) -> None:
    with pytest.raises(ValueError, match=mensagem):
        Item(id=1, nome=nome, peso=peso, valor=valor)
