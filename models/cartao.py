# models/cartao.py
from datetime import date

class Cartao:
    def __init__(self, id: str, nome_cartao: str, ultimos_4_digitos: str, limite: float, data_vencimento_fatura: int, bandeira: str = ""):
        self.id = id
        self.nome_cartao = nome_cartao # Ex: "Meu Nubank", "Cartão Inter"
        self.ultimos_4_digitos = ultimos_4_digitos
        self.limite = limite
        self.data_vencimento_fatura = data_vencimento_fatura # Dia do mês
        self.bandeira = bandeira # Ex: Visa, Mastercard (opcional por enquanto)
        # Fatura atual e limite disponível seriam calculados dinamicamente

# Exemplo de uso (opcional, apenas para teste)
# if __name__ == '__main__':
#     cartao_nu = Cartao(id="c001", nome_cartao="Nubank Gold", ultimos_4_digitos="1234", limite=10000.00, data_vencimento_fatura=10)
#     print(f"Cartão: {cartao_nu.nome_cartao}, Limite: R${cartao_nu.limite:.2f}")
