# tests/models/test_cartao.py
import unittest
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

    def test_criar_cartao_limite_negativo(self):
        with self.assertRaises(ValueError, msg="O limite do cartão não pode ser negativo."):
            Cartao(nome_cartao="Cartão X", ultimos_4_digitos="5678", limite=-100.00, data_vencimento_fatura=5)

    def test_criar_cartao_dia_vencimento_invalido(self):
        with self.assertRaises(ValueError, msg="O dia de vencimento da fatura deve ser entre 1 e 31."):
            Cartao(nome_cartao="Cartão Y", ultimos_4_digitos="1111", limite=1000.00, data_vencimento_fatura=0)
        with self.assertRaises(ValueError, msg="O dia de vencimento da fatura deve ser entre 1 e 31."):
            Cartao(nome_cartao="Cartão Z", ultimos_4_digitos="2222", limite=2000.00, data_vencimento_fatura=32)

    def test_criar_cartao_nome_vazio(self):
        with self.assertRaises(ValueError, msg="O nome do cartão não pode ser vazio."):
            Cartao(nome_cartao="", ultimos_4_digitos="1234", limite=1000.00, data_vencimento_fatura=15)
    
    def test_criar_cartao_ultimos_digitos_invalidos(self):
        with self.assertRaises(ValueError, msg="Os últimos 4 dígitos do cartão devem ser informados e conter 4 números."):
            Cartao(nome_cartao="Cartão Inválido", ultimos_4_digitos="123", limite=1000.00, data_vencimento_fatura=15)
        with self.assertRaises(ValueError, msg="Os últimos 4 dígitos do cartão devem ser informados e conter 4 números."):
            Cartao(nome_cartao="Cartão Inválido", ultimos_4_digitos="abcd", limite=1000.00, data_vencimento_fatura=15)
        with self.assertRaises(ValueError, msg="Os últimos 4 dígitos do cartão devem ser informados e conter 4 números."):
            Cartao(nome_cartao="Cartão Inválido", ultimos_4_digitos="12345", limite=1000.00, data_vencimento_fatura=15)

    def test_representacao_cartao(self):
        cartao = Cartao(id="test_cart_id", nome_cartao="Platinum", ultimos_4_digitos="9876", limite=10000.00, data_vencimento_fatura=25)
        expected_repr = "Cartao(id='test_cart_id', nome='Platinum', final='9876', limite=10000.00)"
        self.assertEqual(repr(cartao), expected_repr)
        
if __name__ == '__main__':
    unittest.main()
