# tests/models/test_tarefa.py
import unittest
from datetime import datetime
from models.tarefa import Tarefa, Subtarefa

class TestSubtarefa(unittest.TestCase):
    def test_criar_subtarefa_sucesso(self):
        sub = Subtarefa(descricao="Revisar documento")
        self.assertIsNotNone(sub.id)
        self.assertEqual(sub.descricao, "Revisar documento")
        self.assertFalse(sub.concluida)

    def test_criar_subtarefa_descricao_vazia(self):
        with self.assertRaisesRegex(ValueError, "A descrição da subtarefa não pode ser vazia."):
            Subtarefa(descricao="")
        with self.assertRaisesRegex(ValueError, "A descrição da subtarefa não pode ser vazia."):
            Subtarefa(descricao="   ")

    def test_marcar_subtarefa_concluida_pendente(self):
        sub = Subtarefa(descricao="Teste")
        self.assertFalse(sub.concluida)
        sub.marcar_como_concluida()
        self.assertTrue(sub.concluida)
        sub.marcar_como_pendente()
        self.assertFalse(sub.concluida)

    def test_representacao_subtarefa(self):
        sub = Subtarefa(id="sub1", descricao="Item 1", concluida=True)
        self.assertEqual(repr(sub), "Subtarefa(id='sub1', descricao='Item 1', concluida=True)")

class TestTarefa(unittest.TestCase):
    def test_criar_tarefa_simples_sucesso(self):
        tarefa = Tarefa(titulo="Comprar pão", categoria_id="cat_mercado")
        self.assertIsNotNone(tarefa.id)
        self.assertEqual(tarefa.titulo, "Comprar pão")
        self.assertEqual(tarefa.categoria_id, "cat_mercado")
        self.assertIsNone(tarefa.data_hora)
        self.assertEqual(tarefa.observacoes, "")
        self.assertFalse(tarefa.concluida)
        self.assertEqual(len(tarefa.subtarefas), 0)

    def test_criar_tarefa_com_detalhes_sucesso(self):
        data = datetime(2024, 8, 15, 10, 30)
        sub1 = Subtarefa(descricao="Pão integral")
        sub2 = Subtarefa(descricao="Pão de queijo")
        tarefa = Tarefa(
            titulo="Supermercado Mensal", 
            categoria_id="cat_compras", 
            data_hora=data, 
            observacoes="Não esquecer sacolas retornáveis",
            subtarefas=[sub1, sub2]
        )
        self.assertEqual(tarefa.titulo, "Supermercado Mensal")
        self.assertEqual(tarefa.categoria_id, "cat_compras")
        self.assertEqual(tarefa.data_hora, data)
        self.assertEqual(tarefa.observacoes, "Não esquecer sacolas retornáveis")
        self.assertEqual(len(tarefa.subtarefas), 2)
        self.assertIn(sub1, tarefa.subtarefas)
        self.assertIn(sub2, tarefa.subtarefas)

    def test_criar_tarefa_titulo_vazio(self):
        with self.assertRaisesRegex(ValueError, "O título da tarefa não pode ser vazio."):
            Tarefa(titulo="", categoria_id="cat1")
        with self.assertRaisesRegex(ValueError, "O título da tarefa não pode ser vazio."):
            Tarefa(titulo="   ", categoria_id="cat1")

    def test_criar_tarefa_categoria_id_vazio(self):
        with self.assertRaisesRegex(ValueError, "O ID da categoria da tarefa não pode ser vazio."):
            Tarefa(titulo="Tarefa sem categoria", categoria_id="")
        with self.assertRaisesRegex(ValueError, "O ID da categoria da tarefa não pode ser vazio."):
            Tarefa(titulo="Tarefa sem categoria", categoria_id="   ")

    def test_adicionar_remover_subtarefa(self):
        tarefa = Tarefa(titulo="Organizar mesa", categoria_id="cat_casa")
        sub_desc = "Limpar teclado"
        subtarefa_adicionada = tarefa.adicionar_subtarefa(sub_desc)
        self.assertEqual(len(tarefa.subtarefas), 1)
        self.assertEqual(tarefa.subtarefas[0].descricao, sub_desc)
        self.assertEqual(subtarefa_adicionada.descricao, sub_desc)

        tarefa.remover_subtarefa(subtarefa_adicionada.id)
        self.assertEqual(len(tarefa.subtarefas), 0)

        # Tentar remover ID inexistente não deve dar erro
        tarefa.remover_subtarefa("id_inexistente")
        self.assertEqual(len(tarefa.subtarefas), 0)

    def test_marcar_tarefa_concluida_pendente(self):
        sub1 = Subtarefa(descricao="Sub 1")
        sub2 = Subtarefa(descricao="Sub 2")
        tarefa = Tarefa(titulo="Teste Conclusão", categoria_id="cat_teste", subtarefas=[sub1, sub2])
        
        self.assertFalse(tarefa.concluida)
        self.assertFalse(sub1.concluida)
        self.assertFalse(sub2.concluida)

        tarefa.marcar_como_concluida()
        self.assertTrue(tarefa.concluida)
        # Verifica se as subtarefas também foram marcadas como concluídas (conforme a lógica implementada no modelo)
        self.assertTrue(sub1.concluida, "Subtarefa 1 deveria ser marcada como concluída")
        self.assertTrue(sub2.concluida, "Subtarefa 2 deveria ser marcada como concluída")

        tarefa.marcar_como_pendente()
        self.assertFalse(tarefa.concluida)
        # Verifica se as subtarefas permanecem concluídas ou se são marcadas como pendentes (depende da lógica no modelo)
        # No modelo atual, marcar tarefa como pendente NÃO altera o estado das subtarefas.
        self.assertTrue(sub1.concluida, "Subtarefa 1 deveria permanecer concluída") 
        self.assertTrue(sub2.concluida, "Subtarefa 2 deveria permanecer concluída")
        # Se a lógica fosse para reverter subtarefas, estes asserts seriam False.

    def test_representacao_tarefa(self):
        tarefa = Tarefa(id="task1", titulo="Minha Tarefa", categoria_id="cat_geral", subtarefas=[Subtarefa("s1")])
        tarefa.marcar_como_concluida()
        self.assertEqual(repr(tarefa), "Tarefa(id='task1', titulo='Minha Tarefa', categoria_id='cat_geral', concluida=True, subtarefas=1)")

if __name__ == '__main__':
    unittest.main()
