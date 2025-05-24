# tests/models/test_receita.py
import unittest
from datetime import datetime
from models.receita import Receita

class TestReceita(unittest.TestCase):

    def test_criar_receita_sucesso(self):
        data_atual = datetime.now()
        receita = Receita(descricao="Salário", valor=5000.00, data=data_atual, recorrente=True)
        self.assertIsNotNone(receita.id)
        self.assertEqual(receita.descricao, "Salário")
        self.assertEqual(receita.valor, 5000.00)
        self.assertEqual(receita.data, data_atual)
        self.assertTrue(receita.recorrente)

    def test_criar_receita_valor_negativo_ou_zero(self):
        with self.assertRaises(ValueError, msg="O valor da receita deve ser positivo."):
            Receita(descricao="Bico", valor=-100.00, data=datetime.now())
        with self.assertRaises(ValueError, msg="O valor da receita deve ser positivo."):
            Receita(descricao="Investimento", valor=0.00, data=datetime.now())

    def test_representacao_receita(self):
        data = datetime(2023, 1, 15)
        receita = Receita(id="test_id_rec", descricao="Aluguel Recebido", valor=1200.50, data=data)
        expected_repr = "Receita(id='test_id_rec', descricao='Aluguel Recebido', valor=1200.50, data='2023-01-15', recorrente=False)"
        self.assertEqual(repr(receita), expected_repr)

if __name__ == '__main__':
    unittest.main()
