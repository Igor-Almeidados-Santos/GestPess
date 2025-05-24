# tests/models/test_categoria_despesa.py
import unittest
from models.categoria_despesa import CategoriaDespesa

class TestCategoriaDespesa(unittest.TestCase):

    def test_criar_categoria_sucesso(self):
        cat = CategoriaDespesa(nome="Alimentação", predefinida=True)
        self.assertIsNotNone(cat.id)
        self.assertEqual(cat.nome, "Alimentação")
        self.assertTrue(cat.predefinida)

    def test_criar_categoria_nome_vazio(self):
        with self.assertRaises(ValueError, msg="O nome da categoria não pode ser vazio."):
            CategoriaDespesa(nome="")

    def test_representacao_categoria(self):
        cat = CategoriaDespesa(id="cat_test_id", nome="Saúde", predefinida=True)
        expected_repr = "CategoriaDespesa(id='cat_test_id', nome='Saúde', predefinida=True)"
        self.assertEqual(repr(cat), expected_repr)

if __name__ == '__main__':
    unittest.main()
