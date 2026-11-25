from src.item import Item

def resolver_guloso(itens: list[Item], capacidade: int) -> list[Item]:
    if capacidade < 0:
        raise ValueError("A capacidade não pode ser negativa")

    # versao provisoria: ainda nao escolhe nenhum item
    return []
