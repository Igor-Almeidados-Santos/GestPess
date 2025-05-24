# tests/services/test_gestao_financeira_servicos.py
import unittest
from datetime import datetime, timedelta
from gestao_financeira import servicos as servicos_financeiros
from models.receita import Receita
from models.despesa import Despesa

class TestGestaoFinanceiraServicos(unittest.TestCase):

    def setUp(self):
        # Limpa os dados em memória antes de cada teste
        servicos_financeiros.limpar_dados_financeiros()

    def test_cadastrar_receita(self):
        data_receita = datetime.now()
        receita = servicos_financeiros.cadastrar_receita(
            descricao="Salário Mensal",
            valor=3000.50,
            data=data_receita,
            recorrente=True
        )
        self.assertIsInstance(receita, Receita)
        self.assertEqual(receita.descricao, "Salário Mensal")
        self.assertEqual(receita.valor, 3000.50)
        # Verifica se a receita está na lista interna (acesso indireto via saldo)
        self.assertEqual(servicos_financeiros.obter_saldo_atual(), 3000.50)

    def test_cadastrar_despesa(self):
        data_despesa = datetime.now()
        # Adiciona uma receita para ter saldo
        servicos_financeiros.cadastrar_receita("Salário", 500.0, datetime.now())
        
        despesa = servicos_financeiros.cadastrar_despesa(
            descricao="Aluguel",
            valor=1200.75,
            data=data_despesa,
            categoria_id="cat004", # ID de exemplo existente em servicos
            metodo_pagamento_id="mp001" # ID de exemplo
        )
        self.assertIsInstance(despesa, Despesa)
        self.assertEqual(despesa.descricao, "Aluguel")
        self.assertEqual(despesa.valor, 1200.75)
        # Saldo = 500 (receita) - 1200.75 (despesa)
        self.assertAlmostEqual(servicos_financeiros.obter_saldo_atual(), 500.0 - 1200.75)

    def test_cadastrar_despesa_categoria_invalida(self):
        with self.assertRaisesRegex(ValueError, "Categoria com ID 'cat_invalida' não encontrada."):
            servicos_financeiros.cadastrar_despesa(
                descricao="Lanche",
                valor=25.00,
                data=datetime.now(),
                categoria_id="cat_invalida",
                metodo_pagamento_id="mp001"
            )

    def test_cadastrar_despesa_metodo_pagamento_invalido(self):
        with self.assertRaisesRegex(ValueError, "Método de pagamento com ID 'mp_invalido' não encontrado."):
            servicos_financeiros.cadastrar_despesa(
                descricao="Cinema",
                valor=50.00,
                data=datetime.now(),
                categoria_id="cat003",
                metodo_pagamento_id="mp_invalido"
            )

    def test_obter_saldo_atual_sem_transacoes(self):
        self.assertEqual(servicos_financeiros.obter_saldo_atual(), 0.0)

    def test_obter_saldo_atual_varias_transacoes(self):
        data_comum = datetime.now()
        servicos_financeiros.cadastrar_receita("Salário", 2500.00, data_comum)
        servicos_financeiros.cadastrar_despesa("Supermercado", 300.00, data_comum, "cat001", "mp001")
        servicos_financeiros.cadastrar_receita("Freelance", 500.00, data_comum + timedelta(days=1))
        servicos_financeiros.cadastrar_despesa("Transporte", 150.00, data_comum + timedelta(days=2), "cat002", "mp003")
        
        saldo_esperado = (2500.00 + 500.00) - (300.00 + 150.00)
        self.assertAlmostEqual(servicos_financeiros.obter_saldo_atual(), saldo_esperado)

    def test_limpar_dados_financeiros(self):
        servicos_financeiros.cadastrar_receita("Teste", 100.0, datetime.now())
        self.assertNotEqual(servicos_financeiros.obter_saldo_atual(), 0.0)
        servicos_financeiros.limpar_dados_financeiros()
        self.assertEqual(servicos_financeiros.obter_saldo_atual(), 0.0)
        # Verifica se as listas estão realmente vazias (não diretamente, mas o saldo 0 é um bom indicativo)

    def test_configurar_salario_principal_novo(self):
        servicos_financeiros.configurar_salario_principal(5000.0)
        # Verifica se uma receita recorrente "Salário Principal" foi criada
        encontrado = False
        for r in servicos_financeiros._receitas: # Acesso à lista interna para teste
            if r.descricao == "Salário Principal" and r.recorrente and r.valor == 5000.0:
                encontrado = True
                break
        self.assertTrue(encontrado, "Salário principal não foi configurado corretamente.")
        self.assertAlmostEqual(servicos_financeiros.obter_saldo_atual(), 5000.0)

    def test_configurar_salario_principal_atualizar_existente(self):
        servicos_financeiros.cadastrar_receita("Salário Principal", 4000.0, datetime.now(), recorrente=True)
        servicos_financeiros.configurar_salario_principal(5500.0)
        
        num_salarios = 0
        valor_salario_correto = False
        for r in servicos_financeiros._receitas: # Acesso à lista interna para teste
            if r.descricao == "Salário Principal" and r.recorrente:
                num_salarios +=1
                if r.valor == 5500.0:
                    valor_salario_correto = True
        
        self.assertEqual(num_salarios, 1, "Deveria haver apenas uma entrada de salário principal.")
        self.assertTrue(valor_salario_correto, "Valor do salário principal não foi atualizado corretamente.")
        self.assertAlmostEqual(servicos_financeiros.obter_saldo_atual(), 5500.0)

    def test_adicionar_renda_adicional(self):
        data_renda = datetime.now()
        renda = servicos_financeiros.adicionar_renda_adicional("Consultoria", 750.0, data_renda)
        self.assertIsInstance(renda, Receita)
        self.assertEqual(renda.descricao, "Consultoria")
        self.assertEqual(renda.valor, 750.0)
        self.assertFalse(renda.recorrente) # Renda adicional não é recorrente por padrão
        self.assertAlmostEqual(servicos_financeiros.obter_saldo_atual(), 750.0)

if __name__ == '__main__':
    unittest.main()
