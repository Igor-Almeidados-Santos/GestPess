# tests/models/test_cartao.py
import unittest
from datetime import datetime # Adicionado
from models.cartao import Cartao

class TestCartao(unittest.TestCase):

    def test_criar_cartao_sucesso(self):
        cartao = Cartao(
            nome_cartao="Meu Cartão Gold",
            ultimos_4_digitos="1234",
            limite=5000.00,
            data_vencimento_fatura=10,
            bandeira="Visa"
        )
        self.assertIsNotNone(cartao.id)
        self.assertEqual(cartao.nome_cartao, "Meu Cartão Gold")
        self.assertEqual(cartao.ultimos_4_digitos, "1234")
        self.assertEqual(cartao.limite, 5000.00)
        self.assertEqual(cartao.data_vencimento_fatura, 10)
        self.assertEqual(cartao.bandeira, "Visa")
        self.assertEqual(cartao.despesas_associadas, [])

    def test_criar_cartao_limite_negativo(self):
        with self.assertRaisesRegex(ValueError, "O limite do cartão não pode ser negativo."):
            Cartao(nome_cartao="Cartão X", ultimos_4_digitos="5678", limite=-100.00, data_vencimento_fatura=5)

    def test_criar_cartao_dia_vencimento_invalido(self):
        with self.assertRaisesRegex(ValueError, "O dia de vencimento da fatura deve ser entre 1 e 31."):
            Cartao(nome_cartao="Cartão Y", ultimos_4_digitos="1111", limite=1000.00, data_vencimento_fatura=0)
        with self.assertRaisesRegex(ValueError, "O dia de vencimento da fatura deve ser entre 1 e 31."):
            Cartao(nome_cartao="Cartão Z", ultimos_4_digitos="2222", limite=2000.00, data_vencimento_fatura=32)

    def test_criar_cartao_nome_vazio(self):
        with self.assertRaisesRegex(ValueError, "O nome do cartão não pode ser vazio."):
            Cartao(nome_cartao="", ultimos_4_digitos="1234", limite=1000.00, data_vencimento_fatura=15)
        with self.assertRaisesRegex(ValueError, "O nome do cartão não pode ser vazio."):
            Cartao(nome_cartao="   ", ultimos_4_digitos="1234", limite=1000.00, data_vencimento_fatura=15)
        
    def test_criar_cartao_ultimos_digitos_invalidos(self):
        with self.assertRaisesRegex(ValueError, "Os últimos 4 dígitos do cartão devem ser informados e conter 4 números."):
            Cartao(nome_cartao="Cartão Inválido", ultimos_4_digitos="123", limite=1000.00, data_vencimento_fatura=15)
        with self.assertRaisesRegex(ValueError, "Os últimos 4 dígitos do cartão devem ser informados e conter 4 números."):
            Cartao(nome_cartao="Cartão Inválido", ultimos_4_digitos="abcd", limite=1000.00, data_vencimento_fatura=15)
        with self.assertRaisesRegex(ValueError, "Os últimos 4 dígitos do cartão devem ser informados e conter 4 números."):
            Cartao(nome_cartao="Cartão Inválido", ultimos_4_digitos="12345", limite=1000.00, data_vencimento_fatura=15)

    def test_adicionar_despesa_ao_cartao_sucesso(self):
        cartao = Cartao(nome_cartao="Teste", ultimos_4_digitos="1111", limite=1000.00, data_vencimento_fatura=1)
        data_despesa = datetime.now()
        cartao.adicionar_despesa_ao_cartao(id_despesa="d1", valor_despesa=100.00, data_despesa=data_despesa)
        self.assertEqual(len(cartao.despesas_associadas), 1)
        self.assertEqual(cartao.despesas_associadas[0]['valor'], 100.00)
        self.assertEqual(cartao.calcular_fatura_atual(), 100.00)
        self.assertEqual(cartao.calcular_limite_disponivel(), 900.00)

    def test_adicionar_despesa_valor_negativo_ou_zero(self):
        cartao = Cartao(nome_cartao="Teste", ultimos_4_digitos="1111", limite=100.00, data_vencimento_fatura=1)
        with self.assertRaisesRegex(ValueError, "O valor da despesa no cartão deve ser positivo."):
            cartao.adicionar_despesa_ao_cartao("d1", 0, datetime.now())
        with self.assertRaisesRegex(ValueError, "O valor da despesa no cartão deve ser positivo."):
            cartao.adicionar_despesa_ao_cartao("d2", -50, datetime.now())

    def test_adicionar_despesa_excede_limite(self):
        cartao = Cartao(nome_cartao="Teste Limite", ultimos_4_digitos="2222", limite=50.00, data_vencimento_fatura=10)
        cartao.adicionar_despesa_ao_cartao(id_despesa="d1", valor_despesa=30.00, data_despesa=datetime.now())
        with self.assertRaisesRegex(ValueError, "Despesa de R\$25.00 excede o limite disponível de R\$20.00 do cartão 'Teste Limite'."):
            cartao.adicionar_despesa_ao_cartao(id_despesa="d2", valor_despesa=25.00, data_despesa=datetime.now())

    def test_calcular_fatura_e_limite_disponivel_multiplas_despesas(self):
        cartao = Cartao(nome_cartao="Multiplas", ultimos_4_digitos="3333", limite=1000.00, data_vencimento_fatura=15)
        cartao.adicionar_despesa_ao_cartao("d1", 100.00, datetime.now())
        cartao.adicionar_despesa_ao_cartao("d2", 250.50, datetime.now())
        cartao.adicionar_despesa_ao_cartao("d3", 50.25, datetime.now())
        fatura_esperada = 100.00 + 250.50 + 50.25
        self.assertAlmostEqual(cartao.calcular_fatura_atual(), fatura_esperada)
        self.assertAlmostEqual(cartao.calcular_limite_disponivel(), 1000.00 - fatura_esperada)

    def test_limite_disponivel_sem_despesas(self):
        cartao = Cartao(nome_cartao="Novo Cartão", ultimos_4_digitos="4444", limite=200.00, data_vencimento_fatura=20)
        self.assertEqual(cartao.calcular_limite_disponivel(), 200.00)
        self.assertEqual(cartao.calcular_fatura_atual(), 0.00)

    def test_representacao_cartao_com_limite_disponivel(self):
        cartao = Cartao(id="cart_repr_id", nome_cartao="Repres", ultimos_4_digitos="8888", limite=500.00, data_vencimento_fatura=5)
        cartao.adicionar_despesa_ao_cartao("d_repr", 100.00, datetime.now())
        expected_repr = "Cartao(id='cart_repr_id', nome='Repres', final='8888', limite=500.00, disponivel=400.00)"
        self.assertEqual(repr(cartao), expected_repr)
            
    if __name__ == '__main__':
        unittest.main()
