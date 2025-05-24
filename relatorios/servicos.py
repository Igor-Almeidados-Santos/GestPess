# relatorios/servicos.py
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from collections import defaultdict

from core.database import get_db_connection
# Não mais importar _despesas, _receitas diretamente de gestao_financeira.servicos
# Importar o serviço de categorias de despesa para mapear IDs para nomes ainda é aceitável,
# ou fazer JOINs nas queries.
# from gestao_financeira.servicos import listar_categorias_despesa as obter_todas_categorias_despesa # Removido, JOIN será usado
# from models.categoria_despesa import CategoriaDespesa # Para type hinting se necessário

# --- Funções Auxiliares de Conversão (se necessário para dados brutos do DB) ---
# Exemplo: converter string de data do DB para datetime, se não for feito na query

# RF003 / RF008
def calcular_distribuicao_gastos_por_categoria(data_inicio: datetime, data_fim: datetime) -> Dict[str, float]:
    gastos_por_categoria: Dict[str, float] = defaultdict(float)
    conn = get_db_connection()
    try:
        # Opção 2 (Melhor): Fazer um JOIN para obter o nome da categoria diretamente
        sql = """
            SELECT cd.nome as categoria_nome, SUM(d.valor) as total_gasto
            FROM despesas d
            JOIN categorias_despesa cd ON d.categoria_id = cd.id
            WHERE date(d.data) >= date(?) AND date(d.data) <= date(?)
            GROUP BY cd.nome
        """
        # Usar .date().isoformat() para garantir que apenas a data seja comparada, ignorando a hora.
        rows = conn.execute(sql, (data_inicio.date().isoformat(), data_fim.date().isoformat())).fetchall()
        for row in rows:
            gastos_por_categoria[row['categoria_nome']] = row['total_gasto']
    finally:
        conn.close()
    print(f"DB Relatórios: Distribuição de gastos por categoria calculada.")
    return dict(gastos_por_categoria)

def gerar_dados_grafico_gastos_por_periodo(data_inicio: datetime, data_fim: datetime, agregacao: str = 'dia') -> Dict[str, List[Any]]:
    dados_grafico: Dict[str, float] = defaultdict(float)
    conn = get_db_connection()
    try:
        group_by_clause_sqlite = ''
        # date_format_py_parse = '' # Usado para parsear as chaves do dados_grafico
        # date_format_py_display = '' # Usado para formatar os labels finais

        if agregacao == 'dia':
            group_by_clause_sqlite = "strftime('%Y-%m-%d', data)"
            # date_format_py_parse = '%Y-%m-%d'
            # date_format_py_display = '%d/%m/%Y'
            
            current_date_loop = data_inicio
            while current_date_loop <= data_fim:
                dados_grafico[current_date_loop.strftime('%Y-%m-%d')] = 0.0 # Chave no formato YYYY-MM-DD
                current_date_loop += timedelta(days=1)

        elif agregacao == 'mes':
            group_by_clause_sqlite = "strftime('%Y-%m', data)"
            # date_format_py_parse = '%Y-%m'
            # date_format_py_display = '%m/%Y'

            current_month_date = datetime(data_inicio.year, data_inicio.month, 1)
            while current_month_date <= datetime(data_fim.year, data_fim.month, 1):
                dados_grafico[current_month_date.strftime('%Y-%m')] = 0.0 # Chave no formato YYYY-MM
                if current_month_date.month == 12:
                    current_month_date = datetime(current_month_date.year + 1, 1, 1)
                else:
                    current_month_date = datetime(current_month_date.year, current_month_date.month + 1, 1)
        else:
            conn.close() # Garante que a conexão seja fechada em caso de erro
            raise ValueError("Agregação deve ser 'dia' ou 'mes'.")

        sql = f"""
            SELECT {group_by_clause_sqlite} as periodo, SUM(valor) as total_gasto
            FROM despesas
            WHERE date(data) >= date(?) AND date(data) <= date(?)
            GROUP BY periodo
            ORDER BY periodo ASC
        """
        rows = conn.execute(sql, (data_inicio.date().isoformat(), data_fim.date().isoformat())).fetchall()
        for row in rows:
            dados_grafico[row['periodo']] = row['total_gasto'] # row['periodo'] já é YYYY-MM-DD ou YYYY-MM
    finally:
        conn.close()
    
    if agregacao == 'dia': 
        labels_ordenados = sorted(dados_grafico.keys(), key=lambda x: datetime.strptime(x, '%Y-%m-%d'))
        display_labels = [datetime.strptime(lbl, '%Y-%m-%d').strftime('%d/%m/%Y') for lbl in labels_ordenados]
    else: # mês
        labels_ordenados = sorted(dados_grafico.keys(), key=lambda x: datetime.strptime(x + '-01', '%Y-%m-%d'))
        display_labels = [datetime.strptime(lbl, '%Y-%m').strftime('%m/%Y') for lbl in labels_ordenados]

    valores_ordenados = [dados_grafico[label] for label in labels_ordenados]
    
    print(f"DB Relatórios: Dados para gráfico de gastos (agregação: {agregacao}) gerados.")
    return {'labels': display_labels, 'valores': valores_ordenados}

def calcular_totais_financeiros_periodo(data_inicio: datetime, data_fim: datetime) -> Dict[str, float]:
    total_receitas = 0.0
    total_despesas = 0.0
    conn = get_db_connection()
    try:
        row_r = conn.execute("SELECT SUM(valor) FROM receitas WHERE date(data) >= date(?) AND date(data) <= date(?)", 
                             (data_inicio.date().isoformat(), data_fim.date().isoformat())).fetchone()
        if row_r and row_r[0] is not None: total_receitas = row_r[0]
        
        row_d = conn.execute("SELECT SUM(valor) FROM despesas WHERE date(data) >= date(?) AND date(data) <= date(?)", 
                             (data_inicio.date().isoformat(), data_fim.date().isoformat())).fetchone()
        if row_d and row_d[0] is not None: total_despesas = row_d[0]
    finally:
        conn.close()
    saldo_periodo = total_receitas - total_despesas
    print(f"DB Relatórios: Totais financeiros calculados.")
    return {'total_receitas': total_receitas, 'total_despesas': total_despesas, 'saldo_periodo': saldo_periodo}

# RF008 - Estatísticas de ganhos
def calcular_estatisticas_ganhos_periodo(data_inicio: datetime, data_fim: datetime) -> Dict[str, float]:
    total_ganhos = 0.0
    conn = get_db_connection()
    try:
        row = conn.execute("SELECT SUM(valor) FROM receitas WHERE date(data) >= date(?) AND date(data) <= date(?)", 
                           (data_inicio.date().isoformat(), data_fim.date().isoformat())).fetchone()
        if row and row[0] is not None: total_ganhos = row[0]
    finally:
        conn.close()

    if data_inicio > data_fim: num_dias_periodo = 0
    else: num_dias_periodo = (data_fim - data_inicio).days + 1
        
    media_ganhos_diaria = total_ganhos / num_dias_periodo if num_dias_periodo > 0 else 0.0
    print(f"DB Relatórios: Estatísticas de ganhos calculadas.")
    return {'total_ganhos': total_ganhos, 'media_ganhos_diaria': media_ganhos_diaria}

# RF009 - Análise de Tendências
def analisar_evolucao_gastos_mensais(ano: int) -> Dict[int, float]:
    gastos_mensais: Dict[int, float] = {m: 0.0 for m in range(1, 13)}
    conn = get_db_connection()
    try:
        sql = """
            SELECT strftime('%m', data) as mes, SUM(valor) as total_gasto
            FROM despesas
            WHERE strftime('%Y', data) = ?
            GROUP BY mes
        """
        rows = conn.execute(sql, (str(ano),)).fetchall()
        for row in rows:
            gastos_mensais[int(row['mes'])] = row['total_gasto']
    finally:
        conn.close()
    print(f"DB Relatórios: Evolução de gastos mensais para o ano {ano} calculada.")
    return gastos_mensais

# Funções mantidas da versão anterior
def calcular_totais_mensais_anuais(ano: int, mes: Optional[int] = None) -> Dict[str, float]:
    if mes:
        if not (1 <= mes <= 12): raise ValueError("Mês inválido.")
        data_inicio = datetime(ano, mes, 1)
        if mes == 12:
            data_fim = datetime(ano, mes, 31)
        else:
            data_fim = datetime(ano, mes + 1, 1) - timedelta(days=1)
    else:
        data_inicio = datetime(ano, 1, 1)
        data_fim = datetime(ano, 12, 31)
    return calcular_totais_financeiros_periodo(data_inicio, data_fim)

def identificar_padroes_consumo(data_inicio: datetime, data_fim: datetime) -> Dict[str, Any]:
    distribuicao = calcular_distribuicao_gastos_por_categoria(data_inicio, data_fim)
    if not distribuicao:
        return {'maior_categoria': None, 'valor_maior_categoria': 0.0, 'outros_padroes': 'Nenhum dado no período'}
    
    maior_categoria = max(distribuicao, key=distribuicao.get)
    valor_maior_categoria = distribuicao[maior_categoria]
    
    print(f"DB Relatórios: Padrão de consumo (maior categoria) identificado.")
    return {
        'maior_categoria': maior_categoria,
        'valor_maior_categoria': valor_maior_categoria,
        'distribuicao_completa': distribuicao
    }

```
