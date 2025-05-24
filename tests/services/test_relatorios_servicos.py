# tests/services/test_relatorios_servicos.py
import unittest
from datetime import datetime, timedelta
from gestao_financeira import servicos as srv_fin
from relatorios import servicos as srv_rel
from models.categoria_despesa import CategoriaDespesa
from models.metodo_pagamento import MetodoPagamento

class TestRelatoriosServicos(unittest.TestCase):

    def setUp(self):
        srv_fin.limpar_dados_financeiros()
        # Popular com alguns dados de exemplo
        self.cat_alimentacao = srv_fin.obter_categoria_despesa_por_nome("Alimentação")
        self.cat_transporte = srv_fin.obter_categoria_despesa_por_nome("Transporte")
        self.cat_lazer = srv_fin.obter_categoria_despesa_por_nome("Lazer")
        self.cat_contas = srv_fin.obter_categoria_despesa_por_nome("Contas")
        self.cat_outros = srv_fin.obter_categoria_despesa_por_nome("Outros")

        self.mp_debito = srv_fin.obter_metodo_pagamento_por_nome("Débito")
        self.mp_credito = srv_fin.obter_metodo_pagamento_por_nome("Crédito")
        self.mp_dinheiro = srv_fin.obter_metodo_pagamento_por_nome("Dinheiro")

        # Receitas
        srv_fin.cadastrar_receita("Salário Jan", 5000, datetime(2023, 1, 5))
        srv_fin.cadastrar_receita("Salário Fev", 5200, datetime(2023, 2, 5))
        srv_fin.cadastrar_receita("Freelance", 800, datetime(2023, 1, 15))
        srv_fin.cadastrar_receita("Salário Mar", 5300, datetime(2023, 3, 5))

        # Despesas
        # Janeiro 2023
        srv_fin.cadastrar_despesa("Supermercado Jan", 300, datetime(2023, 1, 10), self.cat_alimentacao.id, self.mp_debito.id)
        srv_fin.cadastrar_despesa("Restaurante", 150, datetime(2023, 1, 12), self.cat_alimentacao.id, self.mp_credito.id)
        srv_fin.cadastrar_despesa("Conta de Luz Jan", 120, datetime(2023, 1, 20), self.cat_contas.id, self.mp_debito.id)
        srv_fin.cadastrar_despesa("Cinema", 80, datetime(2023, 1, 25), self.cat_lazer.id, self.mp_credito.id)
        # Fevereiro 2023
        srv_fin.cadastrar_despesa("Supermercado Fev", 350, datetime(2023, 2, 10), self.cat_alimentacao.id, self.mp_debito.id)
        srv_fin.cadastrar_despesa("Transporte App", 70, datetime(2023, 2, 15), self.cat_transporte.id, self.mp_credito.id)
        srv_fin.cadastrar_despesa("Conta de Internet Fev", 100, datetime(2023, 2, 22), self.cat_contas.id, self.mp_debito.id)
        # Março 2023 (sem despesas para testar mês vazio em alguns relatórios)

    def test_calcular_distribuicao_gastos_por_categoria(self):
        data_inicio = datetime(2023, 1, 1)
        data_fim = datetime(2023, 1, 31)
        distribuicao = srv_rel.calcular_distribuicao_gastos_por_categoria(data_inicio, data_fim)
        
        self.assertAlmostEqual(distribuicao.get("Alimentação", 0), 300 + 150)
        self.assertAlmostEqual(distribuicao.get("Contas", 0), 120)
        self.assertAlmostEqual(distribuicao.get("Lazer", 0), 80)
        self.assertEqual(len(distribuicao), 3) # Apenas categorias com gastos no período

        data_inicio_total = datetime(2023, 1, 1)
        data_fim_total = datetime(2023, 2, 28)
        distribuicao_total = srv_rel.calcular_distribuicao_gastos_por_categoria(data_inicio_total, data_fim_total)
        self.assertAlmostEqual(distribuicao_total.get("Alimentação", 0), 300 + 150 + 350)
        self.assertAlmostEqual(distribuicao_total.get("Contas", 0), 120 + 100)
        self.assertAlmostEqual(distribuicao_total.get("Transporte", 0), 70)
        self.assertAlmostEqual(distribuicao_total.get("Lazer", 0), 80)

    def test_gerar_dados_grafico_gastos_por_periodo_diario(self):
        data_inicio = datetime(2023, 1, 10)
        data_fim = datetime(2023, 1, 12)
        dados = srv_rel.gerar_dados_grafico_gastos_por_periodo(data_inicio, data_fim, agregacao='dia')
        
        # Esperado: 10/01 (300), 11/01 (0), 12/01 (150)
        self.assertEqual(dados['labels'], ["10/01/2023", "11/01/2023", "12/01/2023"])
        self.assertListEqual(dados['valores'], [300.0, 0.0, 150.0])

    def test_gerar_dados_grafico_gastos_por_periodo_mensal(self):
        data_inicio = datetime(2023, 1, 1)
        data_fim = datetime(2023, 3, 31) # Inclui Março sem despesas
        dados = srv_rel.gerar_dados_grafico_gastos_por_periodo(data_inicio, data_fim, agregacao='mes')
        
        total_jan = 300 + 150 + 120 + 80
        total_fev = 350 + 70 + 100
        total_mar = 0

        self.assertEqual(dados['labels'], ["01/2023", "02/2023", "03/2023"])
        self.assertListEqual(dados['valores'], [float(total_jan), float(total_fev), float(total_mar)])

    def test_calcular_totais_financeiros_periodo(self):
        # Janeiro 2023
        data_inicio_jan = datetime(2023, 1, 1)
        data_fim_jan = datetime(2023, 1, 31)
        totais_jan = srv_rel.calcular_totais_financeiros_periodo(data_inicio_jan, data_fim_jan)
        receitas_jan = 5000 + 800
        despesas_jan = 300 + 150 + 120 + 80
        self.assertAlmostEqual(totais_jan['total_receitas'], receitas_jan)
        self.assertAlmostEqual(totais_jan['total_despesas'], despesas_jan)
        self.assertAlmostEqual(totais_jan['saldo_periodo'], receitas_jan - despesas_jan)

        # Fevereiro 2023
        data_inicio_fev = datetime(2023, 2, 1)
        data_fim_fev = datetime(2023, 2, 28)
        totais_fev = srv_rel.calcular_totais_financeiros_periodo(data_inicio_fev, data_fim_fev)
        receitas_fev = 5200
        despesas_fev = 350 + 70 + 100
        self.assertAlmostEqual(totais_fev['total_receitas'], receitas_fev)
        self.assertAlmostEqual(totais_fev['total_despesas'], despesas_fev)
        self.assertAlmostEqual(totais_fev['saldo_periodo'], receitas_fev - despesas_fev)

    def test_calcular_estatisticas_ganhos_periodo(self):
        data_inicio = datetime(2023, 1, 1)
        data_fim = datetime(2023, 1, 31)
        stats_ganhos = srv_rel.calcular_estatisticas_ganhos_periodo(data_inicio, data_fim)
        total_ganhos_jan = 5000 + 800
        num_dias_jan = 31
        self.assertAlmostEqual(stats_ganhos['total_ganhos'], total_ganhos_jan)
        self.assertAlmostEqual(stats_ganhos['media_ganhos_diaria'], total_ganhos_jan / num_dias_jan)

        data_inicio_fev = datetime(2023, 2, 1)
        data_fim_fev = datetime(2023, 2, 28)
        stats_ganhos_fev = srv_rel.calcular_estatisticas_ganhos_periodo(data_inicio_fev, data_fim_fev)
        total_ganhos_fev = 5200
        num_dias_fev = 28
        self.assertAlmostEqual(stats_ganhos_fev['total_ganhos'], total_ganhos_fev)
        self.assertAlmostEqual(stats_ganhos_fev['media_ganhos_diaria'], total_ganhos_fev / num_dias_fev)

    def test_analisar_evolucao_gastos_mensais(self):
        evolucao_2023 = srv_rel.analisar_evolucao_gastos_mensais(2023)
        despesas_jan_2023 = 300 + 150 + 120 + 80
        despesas_fev_2023 = 350 + 70 + 100
        self.assertAlmostEqual(evolucao_2023.get(1, 0), despesas_jan_2023) # Mês 1 (Janeiro)
        self.assertAlmostEqual(evolucao_2023.get(2, 0), despesas_fev_2023) # Mês 2 (Fevereiro)
        self.assertAlmostEqual(evolucao_2023.get(3, 0), 0) # Mês 3 (Março) - sem despesas
        self.assertEqual(len(evolucao_2023), 12) # Deve retornar para todos os 12 meses

    def test_calcular_totais_mensais_anuais(self):
        # Teste para um mês específico (Janeiro 2023)
        totais_jan = srv_rel.calcular_totais_mensais_anuais(ano=2023, mes=1)
        receitas_jan_calc = 5000 + 800
        despesas_jan_calc = 300 + 150 + 120 + 80
        self.assertAlmostEqual(totais_jan['total_receitas'], receitas_jan_calc)
        self.assertAlmostEqual(totais_jan['total_despesas'], despesas_jan_calc)

        # Teste para o ano todo (2023)
        totais_ano_2023 = srv_rel.calcular_totais_mensais_anuais(ano=2023)
        receitas_ano_2023 = 5000 + 800 + 5200 + 5300
        despesas_ano_2023 = (300 + 150 + 120 + 80) + (350 + 70 + 100)
        self.assertAlmostEqual(totais_ano_2023['total_receitas'], receitas_ano_2023)
        self.assertAlmostEqual(totais_ano_2023['total_despesas'], despesas_ano_2023)

if __name__ == '__main__':
    unittest.main()

```
