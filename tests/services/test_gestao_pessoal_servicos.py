# tests/services/test_gestao_pessoal_servicos.py
import unittest
from datetime import datetime, timedelta
from gestao_pessoal import servicos as servicos_pessoal
from models.tarefa import Tarefa, Subtarefa
from models.categoria_tarefa import CategoriaTarefa

class TestGestaoPessoalServicos(unittest.TestCase):

    def setUp(self):
        # Limpa os dados em memória antes de cada teste
        servicos_pessoal.limpar_dados_pessoais()
        # Garante que as categorias predefinidas sejam recriadas se limpar_dados_pessoais as remover
        # servicos_pessoal.inicializar_categorias_tarefa_predefinidas() # Chamado dentro de limpar_dados_pessoais

    def test_listar_categorias_tarefa_predefinidas(self):
        categorias = servicos_pessoal.listar_categorias_tarefa()
        self.assertTrue(len(categorias) >= 4) # Trabalho, Treino, Estudos, Outros
        nomes_categorias = [cat.nome for cat in categorias]
        for nome_predefinido in CategoriaTarefa.CATEGORIAS_PREDEFINIDAS:
            self.assertIn(nome_predefinido, nomes_categorias)

    def test_criar_categoria_tarefa_nova(self):
        nova_cat_nome = "Finanças"
        cat_criada = servicos_pessoal.criar_categoria_tarefa(nova_cat_nome)
        self.assertIsInstance(cat_criada, CategoriaTarefa)
        self.assertEqual(cat_criada.nome, nova_cat_nome)
        
        categorias = servicos_pessoal.listar_categorias_tarefa()
        self.assertIn(cat_criada, categorias)
        self.assertTrue(any(c.nome == nova_cat_nome for c in categorias))

    def test_criar_categoria_tarefa_existente(self):
        with self.assertRaisesRegex(ValueError, "Categoria de tarefa com nome 'Trabalho' já existe."):
            servicos_pessoal.criar_categoria_tarefa("Trabalho")

    def test_criar_tarefa_com_categoria_existente_por_nome(self):
        tarefa = servicos_pessoal.criar_tarefa(titulo="Reunião de equipe", categoria_nome_ou_id="Trabalho")
        self.assertIsInstance(tarefa, Tarefa)
        self.assertEqual(tarefa.titulo, "Reunião de equipe")
        cat_trabalho = servicos_pessoal.obter_categoria_tarefa_por_nome("Trabalho")
        self.assertEqual(tarefa.categoria_id, cat_trabalho.id)

    def test_criar_tarefa_com_categoria_existente_por_id(self):
        cat_estudos = servicos_pessoal.obter_categoria_tarefa_por_nome("Estudos")
        self.assertIsNotNone(cat_estudos, "Categoria 'Estudos' não encontrada para o teste")
        tarefa = servicos_pessoal.criar_tarefa(titulo="Estudar Python", categoria_nome_ou_id=cat_estudos.id)
        self.assertEqual(tarefa.categoria_id, cat_estudos.id)

    def test_criar_tarefa_com_nova_categoria(self):
        nova_categoria_nome = "Projetos Pessoais"
        tarefa = servicos_pessoal.criar_tarefa(titulo="Desenvolver app", categoria_nome_ou_id=nova_categoria_nome)
        self.assertIsInstance(tarefa, Tarefa)
        cat_criada = servicos_pessoal.obter_categoria_tarefa_por_nome(nova_categoria_nome)
        self.assertIsNotNone(cat_criada)
        self.assertEqual(tarefa.categoria_id, cat_criada.id)

    def test_criar_tarefa_com_id_categoria_invalido(self):
        id_invalido = "id-que-nao-existe-de-categoria"
        with self.assertRaisesRegex(ValueError, f"Categoria de tarefa com ID '{id_invalido}' não encontrada."):
            servicos_pessoal.criar_tarefa(titulo="Tarefa Teste", categoria_nome_ou_id=id_invalido)

    def test_criar_tarefa_com_subtarefas(self):
        desc_subtarefas = ["Comprar ingredientes", "Preparar massa", "Assar bolo"]
        tarefa = servicos_pessoal.criar_tarefa(
            titulo="Fazer bolo", 
            categoria_nome_ou_id="Outros", 
            descricoes_subtarefas=desc_subtarefas
        )
        self.assertEqual(len(tarefa.subtarefas), 3)
        self.assertEqual(tarefa.subtarefas[0].descricao, "Comprar ingredientes")
        self.assertEqual(tarefa.subtarefas[1].descricao, "Preparar massa")
        self.assertEqual(tarefa.subtarefas[2].descricao, "Assar bolo")

    def test_obter_tarefa_por_id(self):
        tarefa_criada = servicos_pessoal.criar_tarefa(titulo="Buscar encomenda", categoria_nome_ou_id="Outros")
        tarefa_obtida = servicos_pessoal.obter_tarefa_por_id(tarefa_criada.id)
        self.assertEqual(tarefa_criada, tarefa_obtida)

    def test_obter_tarefa_por_id_nao_existente(self):
        tarefa = servicos_pessoal.obter_tarefa_por_id("id_fantasma")
        self.assertIsNone(tarefa)

    def test_adicionar_subtarefa_a_tarefa_existente(self):
        tarefa_mae = servicos_pessoal.criar_tarefa(titulo="Limpar Casa", categoria_nome_ou_id="Outros")
        subtarefa = servicos_pessoal.adicionar_subtarefa_a_tarefa_existente(tarefa_mae.id, "Lavar louça")
        self.assertIsInstance(subtarefa, Subtarefa)
        self.assertEqual(subtarefa.descricao, "Lavar louça")
        self.assertIn(subtarefa, tarefa_mae.subtarefas)
        self.assertEqual(len(tarefa_mae.subtarefas), 1)

    def test_adicionar_subtarefa_tarefa_nao_existente(self):
        with self.assertRaisesRegex(ValueError, "Tarefa com ID 'id_inexistente' não encontrada para adicionar subtarefa."):
            servicos_pessoal.adicionar_subtarefa_a_tarefa_existente("id_inexistente", "Subtarefa fantasma")

    def test_listar_tarefas_por_categoria_nome(self):
        servicos_pessoal.criar_tarefa(titulo="Yoga Matinal", categoria_nome_ou_id="Treino")
        servicos_pessoal.criar_tarefa(titulo="Corrida no Parque", categoria_nome_ou_id="Treino")
        servicos_pessoal.criar_tarefa(titulo="Ler livro", categoria_nome_ou_id="Estudos")

        tarefas_treino = servicos_pessoal.listar_tarefas_por_categoria("Treino")
        self.assertEqual(len(tarefas_treino), 2)
        for tarefa in tarefas_treino:
            cat_obj = servicos_pessoal.obter_categoria_tarefa_por_id(tarefa.categoria_id)
            self.assertEqual(cat_obj.nome, "Treino")

    def test_listar_tarefas_por_categoria_id(self):
        cat_trabalho = servicos_pessoal.obter_categoria_tarefa_por_nome("Trabalho")
        servicos_pessoal.criar_tarefa(titulo="Relatório Semanal", categoria_nome_ou_id=cat_trabalho.id)
        tarefas_trabalho = servicos_pessoal.listar_tarefas_por_categoria(cat_trabalho.id)
        self.assertEqual(len(tarefas_trabalho), 1)

    def test_listar_tarefas_por_categoria_inexistente(self):
        tarefas = servicos_pessoal.listar_tarefas_por_categoria("Categoria Fantasma")
        self.assertEqual(len(tarefas), 0)

    def test_listar_todas_tarefas(self):
        servicos_pessoal.criar_tarefa(titulo="T1", categoria_nome_ou_id="Outros")
        servicos_pessoal.criar_tarefa(titulo="T2", categoria_nome_ou_id="Trabalho")
        todas = servicos_pessoal.listar_todas_tarefas()
        self.assertEqual(len(todas), 2)

    def test_definir_data_hora_tarefa(self):
        tarefa = servicos_pessoal.criar_tarefa(titulo="Médico", categoria_nome_ou_id="Outros")
        nova_data = datetime(2025, 1, 10, 14, 0)
        tarefa_atualizada = servicos_pessoal.definir_data_hora_tarefa(tarefa.id, nova_data)
        self.assertIsNotNone(tarefa_atualizada)
        self.assertEqual(tarefa_atualizada.data_hora, nova_data)

    def test_obter_tarefas_para_calendario(self):
        data_mes_atual_ano_atual = datetime.now()
        mes = data_mes_atual_ano_atual.month
        ano = data_mes_atual_ano_atual.year

        servicos_pessoal.criar_tarefa("T1 Cal", "Outros", data_hora=datetime(ano, mes, 10))
        servicos_pessoal.criar_tarefa("T2 Cal", "Outros", data_hora=datetime(ano, mes, 15, 10, 0))
        servicos_pessoal.criar_tarefa("T3 Cal Fora Mes", "Outros", data_hora=datetime(ano, mes % 12 + 1, 10) if mes < 12 else datetime(ano + 1, 1, 10))
        servicos_pessoal.criar_tarefa("T4 Cal Sem Data", "Outros")

        tarefas_calendario = servicos_pessoal.obter_tarefas_para_calendario(mes, ano)
        self.assertEqual(len(tarefas_calendario), 2) # Duas datas distintas com tarefas
        self.assertIn(datetime(ano, mes, 10).strftime('%Y-%m-%d'), tarefas_calendario)
        self.assertIn(datetime(ano, mes, 15).strftime('%Y-%m-%d'), tarefas_calendario)
        self.assertEqual(len(tarefas_calendario[datetime(ano, mes, 10).strftime('%Y-%m-%d')]), 1)
        self.assertEqual(len(tarefas_calendario[datetime(ano, mes, 15).strftime('%Y-%m-%d')]), 1)

if __name__ == '__main__':
    unittest.main()
