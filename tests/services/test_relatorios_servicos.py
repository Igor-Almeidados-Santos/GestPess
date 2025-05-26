# tests/services/test_relatorios_servicos.py
import unittest
from datetime import datetime, timedelta

# Configurar DB em memória ANTES de importar serviços e modelos
from core import database
database.DATABASE_NAME = ":memory:"

# Agora importar os serviços e modelos
from gestao_financeira import servicos as srv_fin # Para popular dados
from relatorios import servicos as srv_rel
# Não precisamos dos modelos diretamente aqui, pois os serviços de relatório devem retornar dicts ou primitivos.

class TestRelatoriosServicosDB(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # Cria o schema e popula dados iniciais uma vez para a classe de teste
        database.init_db(db_name=":memory:")

    def setUp(self):
        # Limpa as tabelas financeiras e repopula dados predefinidos
        # Isso garante um estado limpo para cada teste.
        srv_fin.limpar_tabelas_financeiras_core()
        
        # Popular com alguns dados de exemplo para os relatórios
        # Usar IDs de categorias e métodos predefinidos que são criados por populate_initial_data
        cat_alimentacao_db = srv_fin.obter_categoria_despesa_por_nome("Alimentação")
        cat_transporte_db = srv_fin.obter_categoria_despesa_por_nome("Transporte")
        cat_lazer_db = srv_fin.obter_categoria_despesa_por_nome("Lazer")
        cat_contas_db = srv_fin.obter_categoria_despesa_por_nome("Contas")

        mp_debito_db = srv_fin.obter_metodo_pagamento_por_nome("Débito")
        mp_credito_db = srv_fin.obter_metodo_pagamento_por_nome("Crédito")

        # Receitas
        srv_fin.cadastrar_receita("Salário Jan", 5000, datetime(2023, 1, 5))
        srv_fin.cadastrar_receita("Salário Fev", 5200, datetime(2023, 2, 5))
        srv_fin.cadastrar_receita("Freelance", 800, datetime(2023, 1, 15))
        srv_fin.cadastrar_receita("Salário Mar", 5300, datetime(2023, 3, 5))

        # Despesas
        # Janeiro 2023
        srv_fin.cadastrar_despesa("Supermercado Jan", 300, datetime(2023, 1, 10), cat_alimentacao_db.id, mp_debito_db.id)
        srv_fin.cadastrar_despesa("Restaurante", 150, datetime(2023, 1, 12), cat_alimentacao_db.id, mp_credito_db.id)
        srv_fin.cadastrar_despesa("Conta de Luz Jan", 120, datetime(2023, 1, 20), cat_contas_db.id, mp_debito_db.id)
        srv_fin.cadastrar_despesa("Cinema", 80, datetime(2023, 1, 25), cat_lazer_db.id, mp_credito_db.id)
        # Fevereiro 2023
        srv_fin.cadastrar_despesa("Supermercado Fev", 350, datetime(2023, 2, 10), cat_alimentacao_db.id, mp_debito_db.id)
        srv_fin.cadastrar_despesa("Transporte App", 70, datetime(2023, 2, 15), cat_transporte_db.id, mp_credito_db.id)
        srv_fin.cadastrar_despesa("Conta de Internet Fev", 100, datetime(2023, 2, 22), cat_contas_db.id, mp_debito_db.id)
        # Março 2023 (sem despesas para testar mês vazio em alguns relatórios)

    def test_calcular_distribuicao_gastos_por_categoria_db(self):
        data_inicio = datetime(2023, 1, 1)
        data_fim = datetime(2023, 1, 31)
        distribuicao = srv_rel.calcular_distribuicao_gastos_por_categoria(data_inicio, data_fim)
        
        self.assertAlmostEqual(distribuicao.get("Alimentação", 0), 300 + 150)
        self.assertAlmostEqual(distribuicao.get("Contas", 0), 120)
        self.assertAlmostEqual(distribuicao.get("Lazer", 0), 80)
        self.assertEqual(len(distribuicao), 3)

    def test_gerar_dados_grafico_gastos_por_periodo_diario_db(self):
        data_inicio = datetime(2023, 1, 10)
        data_fim = datetime(2023, 1, 12)
        dados = srv_rel.gerar_dados_grafico_gastos_por_periodo(data_inicio, data_fim, agregacao='dia')
        
        self.assertEqual(dados['labels'], ["10/01/2023", "11/01/2023", "12/01/2023"])
        self.assertListEqual(dados['valores'], [300.0, 0.0, 150.0])

    def test_gerar_dados_grafico_gastos_por_periodo_mensal_db(self):
        data_inicio = datetime(2023, 1, 1)
        data_fim = datetime(2023, 3, 31)
        dados = srv_rel.gerar_dados_grafico_gastos_por_periodo(data_inicio, data_fim, agregacao='mes')
        
        total_jan = 300 + 150 + 120 + 80
        total_fev = 350 + 70 + 100
        total_mar = 0
        self.assertEqual(dados['labels'], ["01/2023", "02/2023", "03/2023"])
        self.assertListEqual(dados['valores'], [float(total_jan), float(total_fev), float(total_mar)])

    def test_calcular_totais_financeiros_periodo_db(self):
        data_inicio_jan = datetime(2023, 1, 1)
        data_fim_jan = datetime(2023, 1, 31)
        totais_jan = srv_rel.calcular_totais_financeiros_periodo(data_inicio_jan, data_fim_jan)
        receitas_jan = 5000 + 800
        despesas_jan = 300 + 150 + 120 + 80
        self.assertAlmostEqual(totais_jan['total_receitas'], receitas_jan)
        self.assertAlmostEqual(totais_jan['total_despesas'], despesas_jan)
        self.assertAlmostEqual(totais_jan['saldo_periodo'], receitas_jan - despesas_jan)

    def test_calcular_estatisticas_ganhos_periodo_db(self):
        data_inicio = datetime(2023, 1, 1)
        data_fim = datetime(2023, 1, 31)
        stats_ganhos = srv_rel.calcular_estatisticas_ganhos_periodo(data_inicio, data_fim)
        total_ganhos_jan = 5000 + 800
        num_dias_jan = 31
        self.assertAlmostEqual(stats_ganhos['total_ganhos'], total_ganhos_jan)
        self.assertAlmostEqual(stats_ganhos['media_ganhos_diaria'], total_ganhos_jan / num_dias_jan)

    def test_analisar_evolucao_gastos_mensais_db(self):
        evolucao_2023 = srv_rel.analisar_evolucao_gastos_mensais(2023)
        despesas_jan_2023 = 300 + 150 + 120 + 80
        despesas_fev_2023 = 350 + 70 + 100
        self.assertAlmostEqual(evolucao_2023.get(1, 0), despesas_jan_2023)
        self.assertAlmostEqual(evolucao_2023.get(2, 0), despesas_fev_2023)
        self.assertAlmostEqual(evolucao_2023.get(3, 0), 0)
        self.assertEqual(len(evolucao_2023), 12)

    def test_calcular_totais_mensais_anuais_db(self):
        totais_jan = srv_rel.calcular_totais_mensais_anuais(ano=2023, mes=1)
        receitas_jan_calc = 5000 + 800
        despesas_jan_calc = 300 + 150 + 120 + 80
        self.assertAlmostEqual(totais_jan['total_receitas'], receitas_jan_calc)
        self.assertAlmostEqual(totais_jan['total_despesas'], despesas_jan_calc)

        totais_ano_2023 = srv_rel.calcular_totais_mensais_anuais(ano=2023)
        receitas_ano_2023 = 5000 + 800 + 5200 + 5300
        despesas_ano_2023 = (300 + 150 + 120 + 80) + (350 + 70 + 100)
        self.assertAlmostEqual(totais_ano_2023['total_receitas'], receitas_ano_2023)
        self.assertAlmostEqual(totais_ano_2023['total_despesas'], despesas_ano_2023)

    def test_identificar_padroes_consumo_db(self):
        data_inicio = datetime(2023, 1, 1)
        data_fim = datetime(2023, 1, 31) # Apenas Janeiro
        padroes = srv_rel.identificar_padroes_consumo(data_inicio, data_fim)
        self.assertEqual(padroes['maior_categoria'], "Alimentação")
        self.assertAlmostEqual(padroes['valor_maior_categoria'], 450.00)
        self.assertTrue("Alimentação" in padroes['distribuicao_completa'])
        
        # Teste período sem dados
        data_inicio_vazio = datetime(2024,1,1)
        data_fim_vazio = datetime(2024,1,31)
        padroes_vazio = srv_rel.identificar_padroes_consumo(data_inicio_vazio, data_fim_vazio)
        self.assertIsNone(padroes_vazio['maior_categoria'])
        self.assertEqual(padroes_vazio['valor_maior_categoria'], 0.0)
        self.assertEqual(padroes_vazio['outros_padroes'], 'Nenhum dado no período')


if __name__ == '__main__':
    unittest.main()

```
