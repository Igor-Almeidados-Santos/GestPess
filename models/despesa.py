# models/despesa.py
from datetime import datetime
from uuid import uuid4
# from .categoria_despesa import CategoriaDespesa # Futura importação para type hinting
# from .metodo_pagamento import MetodoPagamento # Futura importação para type hinting
# from .cartao import Cartao # Futura importação para type hinting

class Despesa:
    def __init__(self, descricao: str, valor: float, data: datetime, categoria_id: str, metodo_pagamento_id: str, cartao_id: str = None, observacoes: str = "", id: str = None):
        if valor <= 0:
            raise ValueError("O valor da despesa deve ser positivo.")
        
        self.id = id if id else str(uuid4())
        self.descricao = descricao
        self.valor = valor
        self.data = data
        self.categoria_id = categoria_id
        self.metodo_pagamento_id = metodo_pagamento_id
        self.cartao_id = cartao_id
        self.observacoes = observacoes

    def __repr__(self):
        return f"Despesa(id='{self.id}', descricao='{self.descricao}', valor={self.valor:.2f}, data='{self.data.strftime('%Y-%m-%d')}', categoria_id='{self.categoria_id}')"
