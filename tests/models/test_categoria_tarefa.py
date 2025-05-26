# tests/models/test_categoria_tarefa.py
import unittest
from models.categoria_tarefa import CategoriaTarefa

class TestCategoriaTarefa(unittest.TestCase):

    def test_criar_categoria_tarefa_sucesso(self):
        cat = CategoriaTarefa(nome="Trabalho")
        self.assertIsNotNone(cat.id)
        self.assertEqual(cat.nome, "Trabalho")

    def test_criar_categoria_tarefa_nome_vazio(self):
        with self.assertRaisesRegex(ValueError, "O nome da categoria da tarefa não pode ser vazio."):
            CategoriaTarefa(nome="")
        with self.assertRaisesRegex(ValueError, "O nome da categoria da tarefa não pode ser vazio."):
            CategoriaTarefa(nome="   ")

    def test_obter_categorias_predefinidas(self):
        predefinidas = CategoriaTarefa.obter_categorias_predefinidas()
        self.assertIsInstance(predefinidas, list)
        self.assertIn("Trabalho", predefinidas)
        self.assertIn("Estudos", predefinidas)
        self.assertTrue(len(predefinidas) >= 4) # Pelo menos as 4 especificadas

    def test_representacao_categoria_tarefa(self):
        cat = CategoriaTarefa(id="cat_work_id", nome="Freelance")
        self.assertEqual(repr(cat), "CategoriaTarefa(id='cat_work_id', nome='Freelance')")

if __name__ == '__main__':
    unittest.main()
