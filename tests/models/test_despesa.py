# tests/models/test_despesa.py
import unittest
from datetime import datetime
from models.despesa import Despesa

class TestDespesa(unittest.TestCase):

    def test_criar_despesa_sucesso(self):
        data_atual = datetime.now()
        despesa = Despesa(
            descricao="Supermercado", 
            valor=150.75, 
            data=data_atual, 
            categoria_id="cat001", 
            metodo_pagamento_id="mp001"
        )
        self.assertIsNotNone(despesa.id)
        self.assertEqual(despesa.descricao, "Supermercado")
        self.assertEqual(despesa.valor, 150.75)
        self.assertEqual(despesa.data, data_atual)
        self.assertEqual(despesa.categoria_id, "cat001")
        self.assertEqual(despesa.metodo_pagamento_id, "mp001")

    def test_criar_despesa_valor_negativo_ou_zero(self):
        with self.assertRaises(ValueError, msg="O valor da despesa deve ser positivo."):
            Despesa(descricao="Conta de Luz", valor=-50.00, data=datetime.now(), categoria_id="cat004", metodo_pagamento_id="mp001")
        with self.assertRaises(ValueError, msg="O valor da despesa deve ser positivo."):
            Despesa(descricao="Cinema", valor=0.00, data=datetime.now(), categoria_id="cat003", metodo_pagamento_id="mp002")
    
    def test_representacao_despesa(self):
        data = datetime(2023, 1, 20)
        despesa = Despesa(id="test_id_desp", descricao="Restaurante", valor=75.00, data=data, categoria_id="cat001", metodo_pagamento_id="mp002")
        expected_repr = "Despesa(id='test_id_desp', descricao='Restaurante', valor=75.00, data='2023-01-20', categoria_id='cat001')"
        self.assertEqual(repr(despesa), expected_repr)

if __name__ == '__main__':
    unittest.main()
