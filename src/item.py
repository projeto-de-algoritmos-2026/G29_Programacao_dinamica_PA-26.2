from dataclasses import dataclass

@dataclass(frozen=True)
class Item:
    id: int
    nome: str
    peso: int
    valor: int

    def __post_init__(self) -> None:
        # a tabela da PD so tem capacidades inteiras, entao peso e valor tambem
        if not self.nome.strip():
            raise ValueError("O nome do item não pode estar vazio")
        if not isinstance(self.peso, int) or self.peso < 1:
            raise ValueError("O peso do item deve ser um inteiro maior ou igual a 1")
        if not isinstance(self.valor, int) or self.valor < 1:
            raise ValueError("O valor do item deve ser um inteiro maior ou igual a 1")
