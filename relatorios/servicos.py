# relatorios/servicos.py
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional # Adicionado Optional
from collections import defaultdict

from gestao_financeira.servicos import _despesas, _receitas, listar_categorias_despesa
from models.despesa import Despesa
from models.receita import Receita
from models.categoria_despesa import CategoriaDespesa

# RF003 / RF008
def calcular_distribuicao_gastos_por_categoria(data_inicio: datetime, data_fim: datetime) -> Dict[str, float]:
    gastos_por_categoria: Dict[str, float] = defaultdict(float)
    categorias_existentes: List[CategoriaDespesa] = listar_categorias_despesa()
    map_id_para_nome_categoria: Dict[str, str] = {cat.id: cat.nome for cat in categorias_existentes}
    despesas_periodo: List[Despesa] = [d for d in _despesas if data_inicio <= d.data <= data_fim]
    for despesa in despesas_periodo:
        nome_categoria = map_id_para_nome_categoria.get(despesa.categoria_id, "Categoria Desconhecida")
        gastos_por_categoria[nome_categoria] += despesa.valor
    return dict(gastos_por_categoria)

def gerar_dados_grafico_gastos_por_periodo(data_inicio: datetime, data_fim: datetime, agregacao: str = 'dia') -> Dict[str, List[Any]]:
    despesas_periodo: List[Despesa] = [d for d in _despesas if data_inicio <= d.data <= data_fim]
    # Ordenar por data não é estritamente necessário para defaultdict, mas pode ser bom para consistência se a fonte de dados mudar.
    # A ordenação dos labels no final é o que garante a ordem correta no gráfico.
    # despesas_periodo.sort(key=lambda d: d.data) 
    
    dados_grafico: Dict[str, float] = defaultdict(float)
    formato_label = ""
    if agregacao == 'dia':
        formato_label = "%d/%m/%Y"
        current_date = data_inicio
        while current_date <= data_fim:
            dados_grafico[current_date.strftime(formato_label)] = 0.0
            current_date += timedelta(days=1)
        for despesa in despesas_periodo:
            label = despesa.data.strftime(formato_label)
            dados_grafico[label] += despesa.valor
    elif agregacao == 'mes':
        formato_label = "%m/%Y"
        current_month_date = datetime(data_inicio.year, data_inicio.month, 1)
        # O loop deve incluir o mês da data_fim
        while current_month_date <= datetime(data_fim.year, data_fim.month, 1):
            dados_grafico[current_month_date.strftime(formato_label)] = 0.0
            if current_month_date.month == 12:
                current_month_date = datetime(current_month_date.year + 1, 1, 1)
            else:
                current_month_date = datetime(current_month_date.year, current_month_date.month + 1, 1)
        for despesa in despesas_periodo:
            label = despesa.data.strftime(formato_label)
            dados_grafico[label] += despesa.valor
    else:
        raise ValueError("Agregação deve ser 'dia' ou 'mes'.")
    
    if agregacao == 'dia':
        labels_ordenados = sorted(dados_grafico.keys(), key=lambda x: datetime.strptime(x, formato_label))
    else: # Mês
        # Para ordenar meses corretamente (ex: "01/2023", "02/2023")
        labels_ordenados = sorted(dados_grafico.keys(), key=lambda x: datetime.strptime(f"01/{x}", "%d/%m/%Y"))
        
    valores_ordenados = [dados_grafico[label] for label in labels_ordenados]
    return {'labels': labels_ordenados, 'valores': valores_ordenados}

def calcular_totais_financeiros_periodo(data_inicio: datetime, data_fim: datetime) -> Dict[str, float]:
    receitas_periodo: List[Receita] = [r for r in _receitas if data_inicio <= r.data <= data_fim]
    despesas_periodo: List[Despesa] = [d for d in _despesas if data_inicio <= d.data <= data_fim]
    total_receitas = sum(r.valor for r in receitas_periodo)
    total_despesas = sum(d.valor for d in despesas_periodo)
    saldo_periodo = total_receitas - total_despesas
    return {'total_receitas': total_receitas, 'total_despesas': total_despesas, 'saldo_periodo': saldo_periodo}

# RF008 - Estatísticas de ganhos ao longo do tempo
def calcular_estatisticas_ganhos_periodo(data_inicio: datetime, data_fim: datetime) -> Dict[str, float]:
    """Calcula o total de ganhos (receitas) e a média diária de ganhos no período."""
    receitas_periodo: List[Receita] = [r for r in _receitas if data_inicio <= r.data <= data_fim]
    total_ganhos = sum(r.valor for r in receitas_periodo)
    
    if data_inicio > data_fim: # Período inválido
        num_dias_periodo = 0
    else:
        num_dias_periodo = (data_fim - data_inicio).days + 1
        
    media_ganhos_diaria = total_ganhos / num_dias_periodo if num_dias_periodo > 0 else 0.0
    
    print(f"Serviço Relatórios: Estatísticas de ganhos calculadas para o período de {data_inicio.strftime('%Y-%m-%d')} a {data_fim.strftime('%Y-%m-%d')}.")
    return {
        'total_ganhos': total_ganhos,
        'media_ganhos_diaria': media_ganhos_diaria
    }

# RF009 - Análise de Tendências
def analisar_evolucao_gastos_mensais(ano: int) -> Dict[int, float]:
    """Calcula o total de gastos para cada mês de um determinado ano."""
    gastos_mensais: Dict[int, float] = defaultdict(float)
    # Inicializa todos os meses do ano com 0.0
    for mes in range(1, 13):
        gastos_mensais[mes] = 0.0
        
    despesas_ano: List[Despesa] = [d for d in _despesas if d.data.year == ano]
    
    for despesa in despesas_ano:
        gastos_mensais[despesa.data.month] += despesa.valor
        
    print(f"Serviço Relatórios: Evolução de gastos mensais para o ano {ano} calculada.")
    return dict(gastos_mensais) # Converte de volta para dict normal se necessário

# Esboços mantidos para completude do arquivo original
def calcular_totais_mensais_anuais(ano: int, mes: Optional[int] = None): # Renomeado no plano, mas mantendo assinatura original por enquanto
    if mes:
        if not (1 <= mes <= 12):
            raise ValueError("Mês inválido. Deve ser entre 1 e 12.")
        data_inicio = datetime(ano, mes, 1)
        if mes == 12:
            data_fim = datetime(ano, mes, 31) # Corrigido
        else:
            # Para outros meses, ir para o primeiro dia do próximo mês e subtrair um dia
            data_fim = datetime(ano, mes + 1, 1) - timedelta(days=1)
    else: # Ano inteiro
        data_inicio = datetime(ano, 1, 1)
        data_fim = datetime(ano, 12, 31)
    
    print(f"Serviço Relatórios: Calculando totais para {f'{mes:02d}/' if mes else ''}{ano} usando calcular_totais_financeiros_periodo.")
    return calcular_totais_financeiros_periodo(data_inicio, data_fim)

def identificar_padroes_consumo(data_inicio: datetime, data_fim: datetime):
    print(f"Serviço Relatórios: Identificando padrões de consumo de {data_inicio.strftime('%Y-%m-%d')} a {data_fim.strftime('%Y-%m-%d')} (não implementado)")
    return {}

```
