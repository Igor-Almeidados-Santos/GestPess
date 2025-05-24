# models/receita.py
from datetime import datetime
from uuid import uuid4

class Receita:
    def __init__(self, descricao: str, valor: float, data: datetime, recorrente: bool = False, id: str = None):
        if valor <= 0:
            raise ValueError("O valor da receita deve ser positivo.")
        
        self.id = id if id else str(uuid4())
        self.descricao = descricao
        self.valor = valor
        self.data = data
        self.recorrente = recorrente

    def __repr__(self):
        return f"Receita(id='{self.id}', descricao='{self.descricao}', valor={self.valor:.2f}, data='{self.data.strftime('%Y-%m-%d')}', recorrente={self.recorrente})"
