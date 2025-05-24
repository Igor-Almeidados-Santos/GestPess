# models/despesa.py
from datetime import datetime
# Supondo que categoria_despesa e metodo_pagamento serão definidos em outros arquivos
# from .categoria_despesa import CategoriaDespesa
# from .metodo_pagamento import MetodoPagamento
# from .cartao import Cartao

class Despesa:
    def __init__(self, id: str, descricao: str, valor: float, data: datetime, categoria_id: str, metodo_pagamento_id: str, cartao_id: str = None, observacoes: str = ""):
        self.id = id
        self.descricao = descricao
        self.valor = valor
        self.data = data
        self.categoria_id = categoria_id # ID da categoria associada
        self.metodo_pagamento_id = metodo_pagamento_id # ID do método de pagamento
        self.cartao_id = cartao_id # ID do cartão, se aplicável
        self.observacoes = observacoes

# Exemplo de uso (opcional, apenas para teste)
# if __name__ == '__main__':
#     despesa_almoco = Despesa(id="d001", descricao="Almoço", valor=25.50, data=datetime.now(), categoria_id="cat001", metodo_pagamento_id="mp001", observacoes="Restaurante X")
#     print(f"Despesa: {despesa_almoco.descricao}, Valor: R${despesa_almoco.valor:.2f}")
