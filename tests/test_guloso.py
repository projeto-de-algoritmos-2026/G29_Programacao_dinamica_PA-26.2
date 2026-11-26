from random import Random

import pytest

from src.guloso import importancia_por_kg, resolver_guloso
from src.item import Item
from src.knapsack import resolver_mochila

def itens_do_exemplo() -> list[Item]:
    # mesmo exemplo do plano: o guloso leva 16, a PD leva 22
    return [
        Item(id=1, nome="Câmera", peso=1, valor=6),
        Item(id=2, nome="Notebook", peso=2, valor=10),
        Item(id=3, nome="Roupas", peso=3, valor=12),
    ]

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

def test_importancia_por_kg() -> None:
    assert importancia_por_kg(Item(id=1, nome="Roupas", peso=3, valor=12)) == 4

def test_exemplo_leva_camera_e_notebook() -> None:
    escolhidos = resolver_guloso(itens_do_exemplo(), 5)

    assert [item.nome for item in escolhidos] == ["Câmera", "Notebook"]
    assert sum(item.peso for item in escolhidos) == 3
    assert sum(item.valor for item in escolhidos) == 16

def test_exemplo_perde_para_a_pd() -> None:
    itens = itens_do_exemplo()

    valor_guloso = sum(item.valor for item in resolver_guloso(itens, 5))

    assert valor_guloso == 16
    assert resolver_mochila(itens, 5).valor_total == 22

def test_pega_primeiro_a_maior_importancia_por_kg() -> None:
    itens = [
        Item(id=1, nome="Livro", peso=4, valor=4),
        Item(id=2, nome="Remédios", peso=1, valor=9),
        Item(id=3, nome="Casaco", peso=2, valor=6),
    ]

    escolhidos = resolver_guloso(itens, 10)

    assert [item.nome for item in escolhidos] == ["Remédios", "Casaco", "Livro"]

def test_empate_mantem_a_ordem_da_entrada() -> None:
    itens = [
        Item(id=1, nome="A", peso=2, valor=4),
        Item(id=2, nome="B", peso=1, valor=2),
        Item(id=3, nome="C", peso=3, valor=6),
    ]

    escolhidos = resolver_guloso(itens, 10)

    assert [item.nome for item in escolhidos] == ["A", "B", "C"]

def test_pula_o_que_nao_cabe_e_continua() -> None:
    itens = [
        Item(id=1, nome="Câmera", peso=1, valor=6),
        Item(id=2, nome="Barraca", peso=8, valor=40),
        Item(id=3, nome="Lanterna", peso=2, valor=2),
    ]

    escolhidos = resolver_guloso(itens, 4)

    assert [item.nome for item in escolhidos] == ["Câmera", "Lanterna"]

def test_sem_itens_ou_capacidade_zero() -> None:
    assert resolver_guloso([], 5) == []
    assert resolver_guloso(itens_do_exemplo(), 0) == []

def test_nunca_passa_da_capacidade() -> None:
    gerador = Random(42)

    for _ in range(100):
        itens = gerar_itens(gerador, gerador.randint(0, 12))
        capacidade = gerador.randint(0, 40)

        escolhidos = resolver_guloso(itens, capacidade)

        assert sum(item.peso for item in escolhidos) <= capacidade
        # cada item entra no maximo uma vez
        assert len({item.id for item in escolhidos}) == len(escolhidos)

def test_nunca_supera_a_pd() -> None:
    gerador = Random(42)

    for _ in range(100):
        itens = gerar_itens(gerador, gerador.randint(0, 12))
        capacidade = gerador.randint(0, 40)

        valor_guloso = sum(item.valor for item in resolver_guloso(itens, capacidade))

        assert valor_guloso <= resolver_mochila(itens, capacidade).valor_total

def test_nao_altera_a_lista_original() -> None:
    itens = itens_do_exemplo()
    ordem_original = itens.copy()

    resolver_guloso(itens, 5)

    assert itens == ordem_original

def test_capacidade_negativa_gera_erro() -> None:
    with pytest.raises(ValueError, match="negativa"):
        resolver_guloso(itens_do_exemplo(), -1)
