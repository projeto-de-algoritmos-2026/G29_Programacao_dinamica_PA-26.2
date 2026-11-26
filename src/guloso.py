from src.item import Item

def importancia_por_kg(item: Item) -> float:
    return item.valor / item.peso

def resolver_guloso(itens: list[Item], capacidade: int) -> list[Item]:
    if capacidade < 0:
        raise ValueError("A capacidade não pode ser negativa")

    # sorted nao mexe na lista original e e estavel: no empate vale a ordem do CSV
    ordenados = sorted(itens, key=importancia_por_kg, reverse=True)

    escolhidos = []
    espaco_livre = capacidade

    # pega o melhor importancia/kg que ainda cabe e nunca volta atras;
    # por isso pode perder para a PD (ex.: leva a camera e sobra espaco vazio)
    for item in ordenados:
        if item.peso <= espaco_livre:
            escolhidos.append(item)
            espaco_livre -= item.peso

    return escolhidos
