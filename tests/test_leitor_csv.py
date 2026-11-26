from pathlib import Path

import pytest

from src.item import Item
from src.leitor_csv import ErroValidacaoCSV, ler_itens_csv

@pytest.mark.parametrize(
    ("nome_arquivo", "quantidade_esperada"),
    [
        ("bagagem_de_mao.csv", 10),
        ("guloso_falha.csv", 3),
        ("bagagem_despachada.csv", 15),
    ],
)
def test_le_csvs_de_exemplo_validos(
    nome_arquivo: str,
    quantidade_esperada: int,
) -> None:
    caminho = Path(__file__).resolve().parents[1] / "exemplos" / nome_arquivo

    itens = ler_itens_csv(caminho)

    assert len(itens) == quantidade_esperada
    assert len({item.id for item in itens}) == quantidade_esperada

def test_le_csv_valido_e_remove_espacos_e_bom(tmp_path) -> None:
    caminho = tmp_path / "itens.csv"
    caminho.write_text(
        "\ufeffid,nome,peso,valor\n1, Câmera ,1,6\n2,Notebook,2,10\n",
        encoding="utf-8",
    )

    assert ler_itens_csv(caminho) == [
        Item(id=1, nome="Câmera", peso=1, valor=6),
        Item(id=2, nome="Notebook", peso=2, valor=10),
    ]

@pytest.mark.parametrize(
    ("conteudo", "trecho_erro"),
    [
        ("", "Linha 1: arquivo CSV vazio"),
        ("id,nome,peso\n1,Câmera,1\n", "Linha 1: cabeçalho"),
        ("id,nome,peso,valor\nabc,Câmera,1,6\n", "id deve ser um inteiro"),
        ("id,nome,peso,valor\n1,Câmera,1.5,6\n", "Linha 2:"),
        ("id,nome,peso,valor\n1,Câmera,0,6\n", "peso deve ser um inteiro"),
        ("id,nome,peso,valor\n1,Câmera,-1,6\n", "peso deve ser um inteiro"),
        ("id,nome,peso,valor\n1,Câmera,1,0\n", "valor deve ser um inteiro"),
        ("id,nome,peso,valor\n1,Câmera,1,-1\n", "valor deve ser um inteiro"),
        ("id,nome,peso,valor\n1,,1,6\n", "nome não pode estar vazio"),
        ("id,nome,peso,valor\n1,Câmera,1\n", "esperadas 4 colunas"),
        ("id,nome,peso,valor\n1,Câmera,1,6,extra\n", "esperadas 4 colunas"),
        (
            'id,nome,peso,valor\n1,"Câmera,1,6\n',
            "CSV malformado",
        ),
        (
            "id,nome,peso,valor\n1,Câmera,1,6\n1,Notebook,2,10\n",
            "id 1 repetido",
        ),
    ],
)
def test_rejeita_csv_invalido(tmp_path, conteudo: str, trecho_erro: str) -> None:
    caminho = tmp_path / "itens.csv"
    caminho.write_text(conteudo, encoding="utf-8")

    with pytest.raises(ErroValidacaoCSV) as erro:
        ler_itens_csv(caminho)

    assert any(trecho_erro in mensagem for mensagem in erro.value.erros)
    assert str(erro.value) == "\n".join(erro.value.erros)

def test_reune_erros_com_numero_de_linha(tmp_path) -> None:
    caminho = tmp_path / "itens.csv"
    caminho.write_text(
        "id,nome,peso,valor\n"
        "1,,0,6\n"
        "2,Notebook,2,10\n"
        "2,Roupas,3,12\n",
        encoding="utf-8",
    )

    with pytest.raises(ErroValidacaoCSV) as erro:
        ler_itens_csv(caminho)

    assert erro.value.erros == [
        "Linha 2: nome não pode estar vazio, peso deve ser um inteiro maior ou igual a 1.",
        "Linha 4: id 2 repetido.",
    ]

def test_ignora_linhas_em_branco(tmp_path) -> None:
    caminho = tmp_path / "itens.csv"
    caminho.write_text(
        "id,nome,peso,valor\n\n1,Câmera,1,6\n",
        encoding="utf-8",
    )
    assert ler_itens_csv(caminho) == [Item(id=1, nome="Câmera", peso=1, valor=6)]

def test_csv_com_cabecalho_e_sem_itens_e_valido(tmp_path) -> None:
    caminho = tmp_path / "itens.csv"
    caminho.write_text("id,nome,peso,valor\n", encoding="utf-8")

    assert ler_itens_csv(caminho) == []
