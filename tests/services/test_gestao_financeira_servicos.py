# tests/services/test_gestao_financeira_servicos.py
import unittest
from datetime import datetime, timedelta
import sqlite3 # Para testar IntegrityError diretamente em alguns casos

# Configurar DB em memória ANTES de importar serviços e modelos que usam o DB
from core import database
database.DATABASE_NAME = ":memory:"

from gestao_financeira import servicos as srv_fin
from models.receita import Receita
from models.despesa import Despesa
from models.categoria_despesa import CategoriaDespesa
from models.metodo_pagamento import MetodoPagamento
from models.cartao import Cartao

class TestGestaoFinanceiraServicosDB(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # Cria o schema e popula dados iniciais uma vez para a classe de teste
        database.init_db(db_name=":memory:")

    def setUp(self):
        # Limpa as tabelas de dados transacionais e repopula dados predefinidos
        # Isso garante um estado limpo para cada teste, mas mantém as tabelas.
        srv_fin.limpar_tabelas_financeiras_core()
        
        # Poderia adicionar algumas receitas/despesas comuns aqui se muitos testes precisarem
        # self.receita_base = srv_fin.cadastrar_receita("Salário Base", 3000, datetime(2023,1,1))

    # --- Testes para CategoriaDespesa (DB) ---
    def test_criar_e_listar_categoria_despesa_db(self):
        # Verifica predefinidas
        cat_alimentacao_obj = srv_fin.obter_categoria_despesa_por_nome("Alimentação")
        self.assertIsNotNone(cat_alimentacao_obj)
        self.assertTrue(cat_alimentacao_obj.predefinida)

        nova_cat = srv_fin.criar_categoria_despesa("Educação DB")
        self.assertIsInstance(nova_cat, CategoriaDespesa)
        self.assertEqual(nova_cat.nome, "Educação DB")
        self.assertFalse(nova_cat.predefinida)
        
        categorias = srv_fin.listar_categorias_despesa()
        # O número exato depende de CATEGORIAS_DESPESA_PREDEFINIDAS_DATA em database.py
        self.assertTrue(len(categorias) >= 5) 
        
        # Verifica se a nova categoria está na lista (comparando atributos)
        cat_encontrada = next((c for c in categorias if c.id == nova_cat.id), None)
        self.assertIsNotNone(cat_encontrada)
        self.assertEqual(cat_encontrada.nome, "Educação DB")

    def test_criar_categoria_despesa_duplicada_db(self):
        srv_fin.criar_categoria_despesa("Saúde DB") # Cria uma vez
        with self.assertRaisesRegex(ValueError, "Categoria de despesa com nome 'Saúde DB' já existe."):
            srv_fin.criar_categoria_despesa("Saúde DB")
        
        # Teste com predefinida (deve falhar também)
        with self.assertRaisesRegex(ValueError, "Categoria de despesa com nome 'Alimentação' já existe."):
            srv_fin.criar_categoria_despesa("Alimentação")

    # --- Testes para MetodoPagamento (DB) ---
    def test_criar_e_listar_metodo_pagamento_db(self):
        mp_credito_obj = srv_fin.obter_metodo_pagamento_por_nome("Crédito")
        self.assertIsNotNone(mp_credito_obj)

        novo_mp = srv_fin.criar_metodo_pagamento("PIX DB")
        self.assertIsInstance(novo_mp, MetodoPagamento)
        self.assertEqual(novo_mp.nome, "PIX DB")
        
        metodos = srv_fin.listar_metodos_pagamento()
        self.assertTrue(len(metodos) >= 3) # Pelo menos 3 predefinidos
        mp_encontrado = next((mp for mp in metodos if mp.id == novo_mp.id), None)
        self.assertIsNotNone(mp_encontrado)
        self.assertEqual(mp_encontrado.nome, "PIX DB")

    def test_criar_metodo_pagamento_duplicado_db(self):
        srv_fin.criar_metodo_pagamento("Boleto DB")
        with self.assertRaisesRegex(ValueError, "Método de pagamento com nome 'Boleto DB' já existe."):
            srv_fin.criar_metodo_pagamento("Boleto DB")
        with self.assertRaisesRegex(ValueError, "Método de pagamento com nome 'Dinheiro' já existe."):
            srv_fin.criar_metodo_pagamento("Dinheiro")

    # --- Testes para Cartao (DB) ---
    def test_cadastrar_e_listar_cartao_db(self):
        cartao1 = srv_fin.cadastrar_cartao("Nubank DB", "1111", 5000, 10, "Mastercard")
        self.assertIsInstance(cartao1, Cartao)
        cartao2 = srv_fin.cadastrar_cartao("Inter DB", "2222", 10000, 15, "Visa")
        
        cartoes = srv_fin.listar_cartoes()
        self.assertEqual(len(cartoes), 2)
        # Verifica por atributos, não por instância direta
        c1_db = next((c for c in cartoes if c.id == cartao1.id), None)
        self.assertIsNotNone(c1_db)
        self.assertEqual(c1_db.nome_cartao, "Nubank DB")

    def test_cadastrar_cartao_duplicado_db(self):
        srv_fin.cadastrar_cartao("Meu Cartão DB", "1234", 1000, 1)
        with self.assertRaisesRegex(ValueError, "Cartão 'Meu Cartão DB' com final '1234' já cadastrado."):
            srv_fin.cadastrar_cartao("Meu Cartão DB", "1234", 2000, 5)

    def test_obter_cartao_por_id_db(self):
        cartao_cadastrado = srv_fin.cadastrar_cartao("Original DB", "3333", 3000, 20)
        cartao_obtido = srv_fin.obter_cartao_por_id(cartao_cadastrado.id) # load_despesas=True por padrão
        self.assertIsNotNone(cartao_obtido)
        self.assertEqual(cartao_cadastrado.id, cartao_obtido.id)
        self.assertEqual(cartao_obtido.nome_cartao, "Original DB")
        self.assertEqual(len(cartao_obtido.despesas_associadas), 0) # Nenhuma despesa ainda

    # --- Testes para Receita (DB) ---
    def test_cadastrar_e_obter_receita_db(self):
        data_receita = datetime(2023, 5, 10, 10, 30)
        receita_criada = srv_fin.cadastrar_receita("Salário Maio DB", 3500.75, data_receita, True)
        receita_obtida = srv_fin.obter_receita_por_id(receita_criada.id)
        
        self.assertIsNotNone(receita_obtida)
        self.assertEqual(receita_obtida.id, receita_criada.id)
        self.assertEqual(receita_obtida.descricao, "Salário Maio DB")
        self.assertAlmostEqual(receita_obtida.valor, 3500.75)
        self.assertEqual(receita_obtida.data, data_receita)
        self.assertTrue(receita_obtida.recorrente)

        receitas = srv_fin.listar_receitas()
        self.assertEqual(len(receitas), 1)

    def test_cadastrar_receita_valor_invalido_db(self):
        with self.assertRaises(ValueError): # Da validação do modelo
             srv_fin.cadastrar_receita("Salário Negativo", -100, datetime.now())
        # O SQLite check (valor > 0) também pegaria isso, resultando em IntegrityError se não fosse o modelo.
        # Mas como o modelo Pydantic/Python já valida, o erro do modelo é levantado primeiro.

    # --- Testes para Despesa (DB) ---
    def test_cadastrar_e_obter_despesa_db(self):
        cat_contas = srv_fin.obter_categoria_despesa_por_nome("Contas")
        mp_debito = srv_fin.obter_metodo_pagamento_por_nome("Débito")
        data_despesa = datetime(2023, 5, 12, 15, 0)

        despesa_criada = srv_fin.cadastrar_despesa("Aluguel Maio DB", 1200.00, data_despesa, cat_contas.id, mp_debito.id)
        despesa_obtida = srv_fin.obter_despesa_por_id(despesa_criada.id)

        self.assertIsNotNone(despesa_obtida)
        self.assertEqual(despesa_obtida.id, despesa_criada.id)
        self.assertEqual(despesa_obtida.descricao, "Aluguel Maio DB")
        self.assertAlmostEqual(despesa_obtida.valor, 1200.00)
        self.assertEqual(despesa_obtida.data, data_despesa)
        self.assertEqual(despesa_obtida.categoria_id, cat_contas.id)
        self.assertEqual(despesa_obtida.metodo_pagamento_id, mp_debito.id)
        self.assertIsNone(despesa_obtida.cartao_id)

        despesas = srv_fin.listar_despesas()
        self.assertEqual(len(despesas), 1)

    def test_cadastrar_despesa_com_cartao_db(self):
        cat_lazer = srv_fin.obter_categoria_despesa_por_nome("Lazer")
        mp_credito = srv_fin.obter_metodo_pagamento_por_nome("Crédito")
        cartao_teste = srv_fin.cadastrar_cartao("Cartão Lazer DB", "5555", 1000.00, 10)
        data_desp = datetime(2023, 5, 13)

        desp = srv_fin.cadastrar_despesa("Cinema DB", 75.00, data_desp, cat_lazer.id, mp_credito.id, cartao_teste.id)
        self.assertEqual(desp.cartao_id, cartao_teste.id)

        # Verifica se a despesa foi associada ao cartão (via DB)
        cartao_atualizado = srv_fin.obter_cartao_por_id(cartao_teste.id, load_despesas=True)
        self.assertEqual(len(cartao_atualizado.despesas_associadas), 1)
        self.assertEqual(cartao_atualizado.despesas_associadas[0]['id_despesa'], desp.id)
        self.assertAlmostEqual(cartao_atualizado.calcular_fatura_atual(), 75.00)
        self.assertAlmostEqual(cartao_atualizado.calcular_limite_disponivel(), 1000.00 - 75.00)

    def test_cadastrar_despesa_cartao_excede_limite_db(self):
        cat_outros = srv_fin.obter_categoria_despesa_por_nome("Outros")
        mp_credito = srv_fin.obter_metodo_pagamento_por_nome("Crédito")
        cartao_curto = srv_fin.cadastrar_cartao("Limite Baixo DB", "0011", 50.00, 1)
        
        with self.assertRaisesRegex(ValueError, "Despesa de R\$60.00 excede o limite disponível de R\$50.00 do cartão 'Limite Baixo DB'."):
            srv_fin.cadastrar_despesa("Compra Alta DB", 60.00, datetime.now(), cat_outros.id, mp_credito.id, cartao_curto.id)
        
        # Verifica que a despesa não foi salva no DB
        despesas_db = srv_fin.listar_despesas()
        self.assertEqual(len(despesas_db), 0, "Despesa que excede limite não deveria ser salva.")

    # --- Testes para Saldo (DB) ---
    def test_obter_saldo_atual_db(self):
        self.assertAlmostEqual(srv_fin.obter_saldo_atual(), 0.0)
        
        srv_fin.cadastrar_receita("R1", 1000, datetime.now())
        self.assertAlmostEqual(srv_fin.obter_saldo_atual(), 1000.0)

        cat = srv_fin.obter_categoria_despesa_por_nome("Outros")
        mp = srv_fin.obter_metodo_pagamento_por_nome("Dinheiro")
        srv_fin.cadastrar_despesa("D1", 200, datetime.now(), cat.id, mp.id)
        self.assertAlmostEqual(srv_fin.obter_saldo_atual(), 800.0)

        srv_fin.cadastrar_despesa("D2", 300, datetime.now(), cat.id, mp.id)
        self.assertAlmostEqual(srv_fin.obter_saldo_atual(), 500.0)

        srv_fin.cadastrar_receita("R2", 500, datetime.now())
        self.assertAlmostEqual(srv_fin.obter_saldo_atual(), 1000.0)

    # --- Testes para Salário (DB) ---
    def test_configurar_salario_principal_db(self):
        data_ini = datetime(2023, 1, 1)
        srv_fin.configurar_salario_principal(3000.00, data_config=data_ini)
        
        receitas = srv_fin.listar_receitas()
        self.assertEqual(len(receitas), 1)
        salario_db = receitas[0]
        self.assertEqual(salario_db.descricao, "Salário Principal")
        self.assertAlmostEqual(salario_db.valor, 3000.00)
        self.assertEqual(salario_db.data, data_ini)
        self.assertTrue(salario_db.recorrente)

        # Testa atualização
        data_att = datetime(2023, 2, 1)
        srv_fin.configurar_salario_principal(3200.00, data_config=data_att)
        receitas_att = srv_fin.listar_receitas()
        self.assertEqual(len(receitas_att), 1) # Ainda deve ser 1, não criar novo
        salario_att_db = receitas_att[0]
        self.assertEqual(salario_att_db.id, salario_db.id) # Mesmo ID
        self.assertAlmostEqual(salario_att_db.valor, 3200.00)
        self.assertEqual(salario_att_db.data, data_att)

    # --- Testes de Fatura e Limite de Cartão (DB) ---
    def test_obter_fatura_e_limite_disponivel_cartao_servico_db(self):
        cat = srv_fin.obter_categoria_despesa_por_nome("Outros")
        mp = srv_fin.obter_metodo_pagamento_por_nome("Crédito")
        cart = srv_fin.cadastrar_cartao("Cartão Fatura DB", "7890", 1000.00, 15)

        srv_fin.cadastrar_despesa("D1 Cartao", 150.00, datetime.now(), cat.id, mp.id, cart.id)
        srv_fin.cadastrar_despesa("D2 Cartao", 250.00, datetime.now(), cat.id, mp.id, cart.id)

        self.assertAlmostEqual(srv_fin.obter_fatura_cartao(cart.id), 400.00)
        self.assertAlmostEqual(srv_fin.obter_limite_disponivel_cartao(cart.id), 600.00)

if __name__ == '__main__':
    unittest.main()

```
