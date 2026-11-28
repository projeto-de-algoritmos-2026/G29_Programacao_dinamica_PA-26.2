import pytest

from src.interface import ler_capacidade

@pytest.mark.parametrize(("texto", "esperada"), [("1", 1), ("23", 23), ("50", 50)])
def test_aceita_capacidade_inteira_no_intervalo(texto: str, esperada: int) -> None:
    assert ler_capacidade(texto) == esperada


@pytest.mark.parametrize("texto", ["", "abc", "1.5"])
def test_rejeita_capacidade_que_nao_e_inteiro(texto: str) -> None:
    with pytest.raises(ValueError, match="número inteiro"):
        ler_capacidade(texto)


@pytest.mark.parametrize("texto", ["0", "-1", "51"])
def test_rejeita_capacidade_fora_do_intervalo(texto: str) -> None:
    with pytest.raises(ValueError, match="entre 1 e 50 kg"):
        ler_capacidade(texto)
