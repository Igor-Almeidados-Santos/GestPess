# models/metodo_pagamento.py
from uuid import uuid4

class MetodoPagamento:
    def __init__(self, nome: str, id: str = None): # Ex: Débito, Crédito, Dinheiro
        if not nome:
            raise ValueError("O nome do método de pagamento não pode ser vazio.")
        self.id = id if id else str(uuid4())
        self.nome = nome

    def __repr__(self):
        return f"MetodoPagamento(id='{self.id}', nome='{self.nome}')"
