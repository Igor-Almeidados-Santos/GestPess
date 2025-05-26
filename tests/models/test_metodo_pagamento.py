# tests/models/test_metodo_pagamento.py
import unittest
from models.metodo_pagamento import MetodoPagamento

class TestMetodoPagamento(unittest.TestCase):

    def test_criar_metodo_pagamento_sucesso(self):
        mp = MetodoPagamento(nome="Crédito")
        self.assertIsNotNone(mp.id)
        self.assertEqual(mp.nome, "Crédito")

    def test_criar_metodo_pagamento_nome_vazio(self):
        with self.assertRaises(ValueError, msg="O nome do método de pagamento não pode ser vazio."):
            MetodoPagamento(nome="")

    def test_representacao_metodo_pagamento(self):
        mp = MetodoPagamento(id="mp_test_id", nome="PIX")
        expected_repr = "MetodoPagamento(id='mp_test_id', nome='PIX')"
        self.assertEqual(repr(mp), expected_repr)

if __name__ == '__main__':
    unittest.main()
