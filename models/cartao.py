# models/cartao.py
from uuid import uuid4
from datetime import datetime
from typing import List, Dict, Any

class Cartao:
    def __init__(self, nome_cartao: str, ultimos_4_digitos: str, limite: float, data_vencimento_fatura: int, bandeira: str = "", id: str = None):
        if limite < 0:
            raise ValueError("O limite do cartão não pode ser negativo.")
        if not (1 <= data_vencimento_fatura <= 31):
            raise ValueError("O dia de vencimento da fatura deve ser entre 1 e 31.")
        if not nome_cartao or not nome_cartao.strip():
            raise ValueError("O nome do cartão não pode ser vazio.")
        if not (ultimos_4_digitos and len(ultimos_4_digitos) == 4 and ultimos_4_digitos.isdigit()):
            raise ValueError("Os últimos 4 dígitos do cartão devem ser informados e conter 4 números.")

        self.id = id if id else str(uuid4())
        self.nome_cartao = nome_cartao.strip()
        self.ultimos_4_digitos = ultimos_4_digitos
        self.limite = limite
        self.data_vencimento_fatura = data_vencimento_fatura
        self.bandeira = bandeira.strip()
        # Este atributo é populado pelo serviço obter_cartao_por_id quando load_despesas=True
        self.despesas_associadas: List[Dict[str, Any]] = [] 

    def adicionar_despesa_interna(self, id_despesa: str, valor_despesa: float, data_despesa: datetime):
        """Adiciona uma despesa à lista interna do objeto Cartao em memória.
           Usado principalmente se o objeto Cartao precisa refletir adições de despesas
           após seu carregamento inicial, sem uma nova consulta ao DB.
           A validação de limite deve ser feita ANTES pelo serviço.
        """
        if valor_despesa <= 0:
            raise ValueError("O valor da despesa no cartão deve ser positivo.")
        
        self.despesas_associadas.append({
            'id_despesa': id_despesa,
            'valor': valor_despesa,
            'data': data_despesa
        })
        # print(f"DEBUG Cartao Modelo: Despesa ID {id_despesa} (R${valor_despesa:.2f}) adicionada internamente ao cartão {self.nome_cartao}")

    def calcular_fatura_atual(self) -> float:
        """Calcula a fatura atual com base nas despesas carregadas em self.despesas_associadas."""
        # No futuro, poderia considerar ciclo de fatura baseado em self.data_vencimento_fatura e data da despesa
        return sum(d['valor'] for d in self.despesas_associadas)

    def calcular_limite_disponivel(self) -> float:
        """Calcula o limite disponível com base na fatura atual e no limite total."""
        return self.limite - self.calcular_fatura_atual()

    def __repr__(self):
        # O cálculo do limite disponível aqui usará as despesas_associadas carregadas.
        return f"Cartao(id='{self.id}', nome='{self.nome_cartao}', final='{self.ultimos_4_digitos}', limite={self.limite:.2f}, disponivel={self.calcular_limite_disponivel():.2f})"

```
