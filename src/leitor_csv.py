import csv
from pathlib import Path

from src.item import Item

class ErroValidacaoCSV(ValueError):
    def __init__(self, erros: list[str]) -> None:
        self.erros = erros
        super().__init__("\n".join(erros))

def ler_itens_csv(caminho: str | Path) -> list[Item]:
    itens: list[Item] = []
    erros: list[str] = []
    ids_encontrados: set[int] = set()

    with open(caminho, newline="", encoding="utf-8-sig") as arquivo:
        leitor = csv.reader(arquivo, strict=True)

        try:
            cabecalho = next(leitor)
        except StopIteration:
            raise ErroValidacaoCSV(["Linha 1: arquivo CSV vazio; cabeçalho ausente."])
        except csv.Error as erro:
            raise ErroValidacaoCSV([f"Linha {leitor.line_num}: CSV malformado ({erro})."])

        if [coluna.strip() for coluna in cabecalho] != ["id", "nome", "peso", "valor"]:
            raise ErroValidacaoCSV(
                ["Linha 1: cabeçalho deve conter id,nome,peso,valor, nessa ordem."]
            )

        while True:
            try:
                linha = next(leitor)
            except StopIteration:
                break
            except csv.Error as erro:
                erros.append(f"Linha {leitor.line_num}: CSV malformado ({erro}).")
                break

            if not linha:
                continue

            numero_linha = leitor.line_num
            if len(linha) != 4:
                erros.append(
                    f"Linha {numero_linha}: esperadas 4 colunas, encontradas {len(linha)}."
                )
                continue

            id_texto, nome_texto, peso_texto, valor_texto = (
                campo.strip() for campo in linha
            )
            erros_linha: list[str] = []

            try:
                identificador = int(id_texto)
            except ValueError:
                identificador = None
                erros_linha.append("id deve ser um inteiro")
            else:
                if identificador in ids_encontrados:
                    erros_linha.append(f"id {identificador} repetido")
                else:
                    ids_encontrados.add(identificador)

            if not nome_texto:
                erros_linha.append("nome não pode estar vazio")

            try:
                peso = int(peso_texto)
            except ValueError:
                peso = None
                erros_linha.append("peso deve ser um inteiro maior ou igual a 1")
            else:
                if peso < 1:
                    erros_linha.append("peso deve ser um inteiro maior ou igual a 1")

            try:
                valor = int(valor_texto)
            except ValueError:
                valor = None
                erros_linha.append("valor deve ser um inteiro maior ou igual a 1")
            else:
                if valor < 1:
                    erros_linha.append("valor deve ser um inteiro maior ou igual a 1")

            if erros_linha:
                erros.append(f"Linha {numero_linha}: {', '.join(erros_linha)}.")
                continue

            itens.append(
                Item(
                    id=identificador,
                    nome=nome_texto,
                    peso=peso,
                    valor=valor,
                )
            )

    if erros:
        raise ErroValidacaoCSV(erros)

    return itens
