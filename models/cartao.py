# models/cartao.py
from uuid import uuid4

class Cartao:
    def __init__(self, nome_cartao: str, ultimos_4_digitos: str, limite: float, data_vencimento_fatura: int, bandeira: str = "", id: str = None):
        if limite < 0: # Limite pode ser 0, mas não negativo
            raise ValueError("O limite do cartão não pode ser negativo.")
        if not (1 <= data_vencimento_fatura <= 31):
            raise ValueError("O dia de vencimento da fatura deve ser entre 1 e 31.")
        if not nome_cartao:
            raise ValueError("O nome do cartão não pode ser vazio.")
        if not (ultimos_4_digitos and len(ultimos_4_digitos) == 4 and ultimos_4_digitos.isdigit()):
            raise ValueError("Os últimos 4 dígitos do cartão devem ser informados e conter 4 números.")

        self.id = id if id else str(uuid4())
        self.nome_cartao = nome_cartao
        self.ultimos_4_digitos = ultimos_4_digitos
        self.limite = limite
        self.data_vencimento_fatura = data_vencimento_fatura
        self.bandeira = bandeira
        # self.despesas_fatura_atual = [] # Para calcular limite disponível e fatura

    # def adicionar_despesa_fatura(self, despesa_valor: float):
    #     if despesa_valor > self.limite_disponivel():
    #         raise ValueError("Despesa excede o limite disponível do cartão.")
    #     self.despesas_fatura_atual.append(despesa_valor)

    # def calcular_fatura_atual(self) -> float:
    #     return sum(self.despesas_fatura_atual)

    # def limite_disponivel(self) -> float:
    #     return self.limite - self.calcular_fatura_atual()

    def __repr__(self):
        return f"Cartao(id='{self.id}', nome='{self.nome_cartao}', final='{self.ultimos_4_digitos}', limite={self.limite:.2f})"
