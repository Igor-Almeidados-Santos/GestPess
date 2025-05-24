# tests/services/test_gestao_financeira_servicos.py
import unittest
from datetime import datetime, timedelta
from gestao_financeira import servicos as srv_fin
from models.receita import Receita
from models.despesa import Despesa
from models.categoria_despesa import CategoriaDespesa
from models.metodo_pagamento import MetodoPagamento
from models.cartao import Cartao

class TestGestaoFinanceiraServicos(unittest.TestCase):

    def setUp(self):
        srv_fin.limpar_dados_financeiros()

    # Testes de Receita e Despesa (já existentes, podem precisar de pequenos ajustes se a lógica de ID mudou)
    def test_cadastrar_receita(self):
        data_receita = datetime.now()
        receita = srv_fin.cadastrar_receita("Salário Mensal", 3000.50, data_receita, True)
        self.assertIsInstance(receita, Receita)
        self.assertEqual(receita.descricao, "Salário Mensal")
        # ... (outros asserts existentes)
        self.assertEqual(srv_fin.obter_saldo_atual(), 3000.50)

    # --- Testes para CategoriaDespesa --- 
    def test_criar_e_listar_categoria_despesa(self):
        cat_alimentacao_obj = srv_fin.obter_categoria_despesa_por_nome("Alimentação")
        self.assertIsNotNone(cat_alimentacao_obj)
        self.assertTrue(cat_alimentacao_obj.predefinida)

        nova_cat = srv_fin.criar_categoria_despesa("Educação")
        self.assertIsInstance(nova_cat, CategoriaDespesa)
        self.assertEqual(nova_cat.nome, "Educação")
        self.assertFalse(nova_cat.predefinida)
        
        categorias = srv_fin.listar_categorias_despesa()
        self.assertTrue(len(categorias) >= 5) # 5 predefinidas + 1 nova (Alimentação, Transporte, Lazer, Contas, Outros)
        self.assertIn(nova_cat, categorias)
        self.assertTrue(any(c.nome == "Educação" for c in categorias))

    def test_criar_categoria_despesa_duplicada(self):
        # Criar uma não predefinida primeiro
        srv_fin.criar_categoria_despesa("Saúde")
        with self.assertRaisesRegex(ValueError, "Categoria de despesa com nome 'Saúde' já existe."):
            srv_fin.criar_categoria_despesa("Saúde") 
        
        with self.assertRaisesRegex(ValueError, "Categoria de despesa com nome 'Alimentação' já existe."):
            srv_fin.criar_categoria_despesa("Alimentação") # Predefinida

    def test_obter_categoria_despesa_por_id_e_nome(self):
        cat_lazer = srv_fin.obter_categoria_despesa_por_nome("Lazer")
        self.assertIsNotNone(cat_lazer)
        cat_obtida_por_id = srv_fin.obter_categoria_despesa_por_id(cat_lazer.id)
        self.assertEqual(cat_lazer, cat_obtida_por_id)
        self.assertIsNone(srv_fin.obter_categoria_despesa_por_id("id_inexistente"))
        self.assertIsNone(srv_fin.obter_categoria_despesa_por_nome("nome_inexistente"))

    # --- Testes para MetodoPagamento ---
    def test_criar_e_listar_metodo_pagamento(self):
        mp_credito_obj = srv_fin.obter_metodo_pagamento_por_nome("Crédito")
        self.assertIsNotNone(mp_credito_obj)

        novo_mp = srv_fin.criar_metodo_pagamento("PIX")
        self.assertIsInstance(novo_mp, MetodoPagamento)
        self.assertEqual(novo_mp.nome, "PIX")
        
        metodos = srv_fin.listar_metodos_pagamento()
        self.assertTrue(len(metodos) >= 3) # 3 predefinidos + 1 novo (Débito, Crédito, Dinheiro)
        self.assertIn(novo_mp, metodos)
        self.assertTrue(any(mp.nome == "PIX" for mp in metodos))

    def test_criar_metodo_pagamento_duplicado(self):
        # Criar um não predefinido primeiro
        srv_fin.criar_metodo_pagamento("Boleto")
        with self.assertRaisesRegex(ValueError, "Método de pagamento com nome 'Boleto' já existe."):
            srv_fin.criar_metodo_pagamento("Boleto")
            
        with self.assertRaisesRegex(ValueError, "Método de pagamento com nome 'Dinheiro' já existe."):
            srv_fin.criar_metodo_pagamento("Dinheiro") # Predefinido

    def test_obter_metodo_pagamento_por_id_e_nome(self):
        mp_debito = srv_fin.obter_metodo_pagamento_por_nome("Débito")
        self.assertIsNotNone(mp_debito)
        mp_obtido_por_id = srv_fin.obter_metodo_pagamento_por_id(mp_debito.id)
        self.assertEqual(mp_debito, mp_obtido_por_id)
        self.assertIsNone(srv_fin.obter_metodo_pagamento_por_id("id_inexistente"))
        self.assertIsNone(srv_fin.obter_metodo_pagamento_por_nome("nome_inexistente"))

    # --- Testes para Cartao ---
    def test_cadastrar_e_listar_cartao(self):
        cartao1 = srv_fin.cadastrar_cartao("Nubank", "1111", 5000, 10, "Mastercard")
        self.assertIsInstance(cartao1, Cartao)
        cartao2 = srv_fin.cadastrar_cartao("Inter", "2222", 10000, 15, "Visa")
        cartoes = srv_fin.listar_cartoes()
        self.assertEqual(len(cartoes), 2)
        self.assertIn(cartao1, cartoes)
        self.assertIn(cartao2, cartoes)

    def test_cadastrar_cartao_duplicado(self):
        srv_fin.cadastrar_cartao("Meu Cartão", "1234", 1000, 1)
        with self.assertRaisesRegex(ValueError, "Cartão 'Meu Cartão' com final '1234' já cadastrado."):
            srv_fin.cadastrar_cartao("Meu Cartão", "1234", 2000, 5)

    def test_obter_cartao_por_id(self):
        cartao_cadastrado = srv_fin.cadastrar_cartao("Original", "3333", 3000, 20)
        cartao_obtido = srv_fin.obter_cartao_por_id(cartao_cadastrado.id)
        self.assertEqual(cartao_cadastrado, cartao_obtido)
        self.assertIsNone(srv_fin.obter_cartao_por_id("id_cartao_fake"))

    # --- Testes de Despesa com Categorias, Métodos e Cartões Reais ---
    def test_cadastrar_despesa_com_objetos_reais(self):
        cat_lazer = srv_fin.obter_categoria_despesa_por_nome("Lazer")
        mp_dinheiro = srv_fin.obter_metodo_pagamento_por_nome("Dinheiro")
        despesa = srv_fin.cadastrar_despesa("Cinema", 50.00, datetime.now(), cat_lazer.id, mp_dinheiro.id)
        self.assertEqual(despesa.categoria_id, cat_lazer.id)
        self.assertEqual(despesa.metodo_pagamento_id, mp_dinheiro.id)

    def test_cadastrar_despesa_categoria_invalida_real(self):
        mp_dinheiro = srv_fin.obter_metodo_pagamento_por_nome("Dinheiro")
        with self.assertRaisesRegex(ValueError, "Categoria de despesa com ID ou nome 'cat_invalida' não encontrada."):
            srv_fin.cadastrar_despesa("Lanche", 25.00, datetime.now(), "cat_invalida", mp_dinheiro.id)

    def test_cadastrar_despesa_metodo_pagamento_invalido_real(self):
        cat_lazer = srv_fin.obter_categoria_despesa_por_nome("Lazer")
        with self.assertRaisesRegex(ValueError, "Método de pagamento com ID ou nome 'mp_invalido' não encontrado."):
            srv_fin.cadastrar_despesa("Show", 100.00, datetime.now(), cat_lazer.id, "mp_invalido")

    def test_cadastrar_despesa_com_cartao(self):
        cat_contas = srv_fin.obter_categoria_despesa_por_nome("Contas")
        mp_credito = srv_fin.obter_metodo_pagamento_por_nome("Crédito")
        meu_cartao = srv_fin.cadastrar_cartao("Meu Visa", "7777", 2000, 25)

        despesa_cartao = srv_fin.cadastrar_despesa("Netflix", 39.90, datetime.now(), cat_contas.id, mp_credito.id, meu_cartao.id)
        self.assertEqual(despesa_cartao.cartao_id, meu_cartao.id)
        self.assertAlmostEqual(meu_cartao.calcular_fatura_atual(), 39.90)
        self.assertAlmostEqual(meu_cartao.calcular_limite_disponivel(), 2000 - 39.90)
        # Verifica se o saldo geral também foi afetado (conforme regra atual)
        # srv_fin.cadastrar_receita("Salário Teste", 2000, datetime.now()) # Para ter saldo positivo
        # self.assertAlmostEqual(srv_fin.obter_saldo_atual(), 2000 - 39.90)

    def test_cadastrar_despesa_cartao_id_invalido(self):
        cat_contas = srv_fin.obter_categoria_despesa_por_nome("Contas")
        mp_credito = srv_fin.obter_metodo_pagamento_por_nome("Crédito")
        with self.assertRaisesRegex(ValueError, "Cartão com ID 'cartao_fantasma' não encontrado."):
            srv_fin.cadastrar_despesa("Spotify", 21.90, datetime.now(), cat_contas.id, mp_credito.id, "cartao_fantasma")

    def test_cadastrar_despesa_cartao_metodo_nao_credito(self):
        cat_contas = srv_fin.obter_categoria_despesa_por_nome("Contas")
        mp_debito = srv_fin.obter_metodo_pagamento_por_nome("Débito") # Usando Débito
        meu_cartao = srv_fin.cadastrar_cartao("Meu Master", "8888", 1500, 10)
        with self.assertRaisesRegex(ValueError, "Despesas com cartão devem usar o método de pagamento 'Crédito'. Método usado: 'Débito'."):
            srv_fin.cadastrar_despesa("iFood", 70.00, datetime.now(), cat_contas.id, mp_debito.id, meu_cartao.id)

    def test_cadastrar_despesa_cartao_excede_limite(self):
        cat_lazer = srv_fin.obter_categoria_despesa_por_nome("Lazer")
        mp_credito = srv_fin.obter_metodo_pagamento_por_nome("Crédito")
        cartao_curto = srv_fin.cadastrar_cartao("Pouco Limite", "0000", 100.00, 5)
        
        srv_fin.cadastrar_despesa("Ingresso Show", 80.00, datetime.now(), cat_lazer.id, mp_credito.id, cartao_curto.id)
        self.assertAlmostEqual(cartao_curto.calcular_limite_disponivel(), 20.00)

        with self.assertRaisesRegex(ValueError, "Despesa de R\$50.00 excede o limite disponível de R\$20.00 do cartão 'Pouco Limite'."):
            srv_fin.cadastrar_despesa("Jantar Show", 50.00, datetime.now(), cat_lazer.id, mp_credito.id, cartao_curto.id)
        # Garante que a despesa que excedeu não foi adicionada à lista geral de despesas
        despesas_registradas = [d for d in srv_fin._despesas if d.descricao == "Jantar Show"] # Acesso à lista interna para teste
        self.assertEqual(len(despesas_registradas), 0, "Despesa que excedeu o limite não deveria ser registrada.")

    def test_obter_fatura_e_limite_disponivel_cartao_servico(self):
        cat = srv_fin.obter_categoria_despesa_por_nome("Outros")
        mp = srv_fin.obter_metodo_pagamento_por_nome("Crédito")
        cart = srv_fin.cadastrar_cartao("Cartão Teste Fatura", "1212", 750.00, 12)

        srv_fin.cadastrar_despesa("D1", 100, datetime.now(), cat.id, mp.id, cart.id)
        srv_fin.cadastrar_despesa("D2", 200, datetime.now(), cat.id, mp.id, cart.id)

        self.assertAlmostEqual(srv_fin.obter_fatura_cartao(cart.id), 300.00)
        self.assertAlmostEqual(srv_fin.obter_limite_disponivel_cartao(cart.id), 450.00)

    def test_obter_fatura_cartao_inexistente(self):
        with self.assertRaisesRegex(ValueError, "Cartão com ID 'id_nao_existe' não encontrado."):
            srv_fin.obter_fatura_cartao("id_nao_existe")

    # Testes de Saldo (já existentes, podem precisar de revisão)
    def test_obter_saldo_atual_sem_transacoes(self):
        self.assertEqual(srv_fin.obter_saldo_atual(), 0.0)

    def test_obter_saldo_atual_varias_transacoes(self):
        data_comum = datetime.now()
        cat_outros = srv_fin.obter_categoria_despesa_por_nome("Outros") # Usar uma categoria predefinida
        mp_din = srv_fin.obter_metodo_pagamento_por_nome("Dinheiro") # Usar um método predefinido
        
        srv_fin.cadastrar_receita("Salário", 2500.00, data_comum)
        srv_fin.cadastrar_despesa("Supermercado", 300.00, data_comum, cat_outros.id, mp_din.id)
        srv_fin.cadastrar_receita("Freelance", 500.00, data_comum + timedelta(days=1))
        srv_fin.cadastrar_despesa("Transporte", 150.00, data_comum + timedelta(days=2), cat_outros.id, mp_din.id)
        
        saldo_esperado = (2500.00 + 500.00) - (300.00 + 150.00)
        self.assertAlmostEqual(srv_fin.obter_saldo_atual(), saldo_esperado)

    def test_limpar_dados_financeiros_completo(self):
        srv_fin.cadastrar_receita("Teste Rec", 100.0, datetime.now())
        srv_fin.criar_categoria_despesa("Teste Cat") # Cria uma não predefinida
        srv_fin.criar_metodo_pagamento("Teste MP")   # Cria um não predefinido
        srv_fin.cadastrar_cartao("Teste Cartao", "0000", 100, 1)
        
        srv_fin.limpar_dados_financeiros()
        
        self.assertEqual(srv_fin.obter_saldo_atual(), 0.0)
        self.assertEqual(len(srv_fin._receitas), 0) # Acesso à lista interna para teste
        self.assertEqual(len(srv_fin._despesas), 0) # Acesso à lista interna para teste
        self.assertEqual(len(srv_fin._lista_cartoes), 0) # Acesso à lista interna para teste
        
        # Verifica se as listas de categorias e metodos de pagamento voltam ao estado predefinido
        # e não contêm as que foram criadas no teste antes do 'limpar'
        categorias_depois_limpar = srv_fin.listar_categorias_despesa()
        metodos_depois_limpar = srv_fin.listar_metodos_pagamento()

        self.assertEqual(len(categorias_depois_limpar), len(srv_fin.CATEGORIAS_DESPESA_PREDEFINIDAS))
        self.assertFalse(any(c.nome == "Teste Cat" for c in categorias_depois_limpar))
        self.assertTrue(all(c.nome in srv_fin.CATEGORIAS_DESPESA_PREDEFINIDAS for c in categorias_depois_limpar))

        self.assertEqual(len(metodos_depois_limpar), len(srv_fin.METODOS_PAGAMENTO_PREDEFINIDOS))
        self.assertFalse(any(mp.nome == "Teste MP" for mp in metodos_depois_limpar))
        self.assertTrue(all(mp.nome in srv_fin.METODOS_PAGAMENTO_PREDEFINIDOS for mp in metodos_depois_limpar))

if __name__ == '__main__':
    unittest.main()

```
