# models/metodo_pagamento.py

class MetodoPagamento:
    def __init__(self, id: str, nome: str): # Ex: Débito, Crédito, Dinheiro
        self.id = id
        self.nome = nome

# Exemplo de uso (opcional, apenas para teste)
# if __name__ == '__main__':
#     mp_credito = MetodoPagamento(id="mp001", nome="Crédito")
#     mp_debito = MetodoPagamento(id="mp002", nome="Débito")
#     print(f"Método de Pagamento: {mp_credito.nome}")
