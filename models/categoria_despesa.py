# models/categoria_despesa.py
from uuid import uuid4

class CategoriaDespesa:
    def __init__(self, nome: str, predefinida: bool = False, id: str = None):
        if not nome:
            raise ValueError("O nome da categoria não pode ser vazio.")
        self.id = id if id else str(uuid4())
        self.nome = nome
        self.predefinida = predefinida

    def __repr__(self):
        return f"CategoriaDespesa(id='{self.id}', nome='{self.nome}', predefinida={self.predefinida})"
