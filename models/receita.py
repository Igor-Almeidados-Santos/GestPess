# models/receita.py
from datetime import datetime

class Receita:
    def __init__(self, id: str, descricao: str, valor: float, data: datetime, recorrente: bool = False):
        self.id = id
        self.descricao = descricao
        self.valor = valor
        self.data = data
        self.recorrente = recorrente # Ex: salário mensal

# Exemplo de uso (opcional, apenas para teste)
# if __name__ == '__main__':
#     receita_salario = Receita(id="r001", descricao="Salário Mensal", valor=5000.00, data=datetime.now(), recorrente=True)
#     print(f"Receita: {receita_salario.descricao}, Valor: R${receita_salario.valor:.2f}")
