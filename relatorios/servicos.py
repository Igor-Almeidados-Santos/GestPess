# relatorios/servicos.py
from datetime import datetime
from typing import Optional

# RF003 - ... gerar relatórios por categoria (movido para cá por ser um tipo de relatório)
def gerar_relatorio_gastos_por_categoria(data_inicio: datetime, data_fim: datetime):
    # Lógica para agregar despesas por categoria em um período
    print(f"Serviço: Gerando relatório de gastos por categoria de {data_inicio.strftime('%Y-%m-%d')} a {data_fim.strftime('%Y-%m-%d')}")
    return {} # Ex: {'Alimentação': 500.00, 'Transporte': 150.00}

# RF008 - Relatórios Financeiros
def gerar_grafico_gastos_por_periodo(data_inicio: datetime, data_fim: datetime):
    # Lógica para gerar dados para um gráfico de gastos (ex: gastos diários ou semanais)
    # Pode retornar uma estrutura de dados que a UI possa usar para desenhar um gráfico
    print(f"Serviço: Gerando dados para gráfico de gastos de {data_inicio.strftime('%Y-%m-%d')} a {data_fim.strftime('%Y-%m-%d')}")
    return {'labels': [], 'valores': []}

def obter_estatisticas_ganhos(data_inicio: datetime, data_fim: datetime):
    # Lógica para calcular estatísticas de ganhos (total, média, etc.)
    print(f"Serviço: Obtendo estatísticas de ganhos de {data_inicio.strftime('%Y-%m-%d')} a {data_fim.strftime('%Y-%m-%d')}")
    return {'total_ganhos': 0.0, 'media_mensal': 0.0}

def calcular_totais_mensais_anuais(ano: int, mes: Optional[int] = None):
    # Lógica para calcular totais de receitas e despesas para um mês ou ano específico
    print(f"Serviço: Calculando totais para {mes}/{ano if mes else ano}")
    return {'receitas': 0.0, 'despesas': 0.0, 'saldo': 0.0}

# RF009 - Análise de Tendências
def analisar_evolucao_gastos_mensais(ano: int):
    # Lógica para mostrar a evolução dos gastos mês a mês durante um ano
    # Pode retornar uma lista de valores de gastos mensais
    print(f"Serviço: Analisando evolução de gastos mensais para o ano {ano}")
    return [0.0] * 12 # Exemplo: [Janeiro_gasto, Fevereiro_gasto, ...]

def identificar_padroes_consumo(data_inicio: datetime, data_fim: datetime):
    # Lógica mais complexa para identificar padrões (ex: maior categoria de gasto, dias de maior gasto)
    print(f"Serviço: Identificando padrões de consumo de {data_inicio.strftime('%Y-%m-%d')} a {data_fim.strftime('%Y-%m-%d')}")
    return {}
