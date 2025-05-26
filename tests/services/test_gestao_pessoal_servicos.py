# tests/services/test_gestao_pessoal_servicos.py
import unittest
from datetime import datetime, timedelta

# Configurar DB em memória ANTES de importar serviços e modelos
from core import database
database.DATABASE_NAME = ":memory:"

from gestao_pessoal import servicos as srv_pess
from models.tarefa import Tarefa, Subtarefa
from models.categoria_tarefa import CategoriaTarefa

class TestGestaoPessoalServicosDB(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # Cria o schema e popula dados iniciais uma vez para a classe de teste
        # init_db também popula categorias de tarefa predefinidas.
        database.init_db(db_name=":memory:")

    def setUp(self):
        # Limpa as tabelas de tarefas, subtarefas e recria categorias de tarefa predefinidas
        # se a função limpar_tabelas_pessoais for robusta o suficiente.
        # A função limpar_tabelas_pessoais deve garantir que as categorias predefinidas sejam restauradas.
        srv_pess.limpar_tabelas_pessoais()

    def test_listar_categorias_tarefa_predefinidas_db(self):
        categorias = srv_pess.listar_categorias_tarefa()
        self.assertTrue(len(categorias) >= 4) # Trabalho, Treino, Estudos, Outros
        nomes_db = [cat.nome for cat in categorias]
        for nome_predefinido in CategoriaTarefa.CATEGORIAS_PREDEFINIDAS:
            self.assertIn(nome_predefinido, nomes_db)

    def test_criar_categoria_tarefa_nova_db(self):
        nova_cat_nome = "Finanças Pessoais DB"
        cat_criada = srv_pess.criar_categoria_tarefa(nova_cat_nome)
        self.assertIsInstance(cat_criada, CategoriaTarefa)
        self.assertEqual(cat_criada.nome, nova_cat_nome)
        
        cat_obtida = srv_pess.obter_categoria_tarefa_por_id(cat_criada.id)
        self.assertIsNotNone(cat_obtida)
        self.assertEqual(cat_obtida.nome, nova_cat_nome)

    def test_criar_categoria_tarefa_existente_db(self):
        with self.assertRaisesRegex(ValueError, "Categoria de tarefa com nome 'Trabalho' já existe."):
            srv_pess.criar_categoria_tarefa("Trabalho") # Predefinida

    def test_criar_tarefa_com_categoria_existente_por_nome_db(self):
        tarefa = srv_pess.criar_tarefa(titulo="Reunião de equipe DB", categoria_nome_ou_id="Trabalho")
        self.assertIsInstance(tarefa, Tarefa)
        
        tarefa_db = srv_pess.obter_tarefa_por_id(tarefa.id)
        self.assertIsNotNone(tarefa_db)
        self.assertEqual(tarefa_db.titulo, "Reunião de equipe DB")
        cat_trabalho_db = srv_pess.obter_categoria_tarefa_por_nome("Trabalho")
        self.assertEqual(tarefa_db.categoria_id, cat_trabalho_db.id)

    def test_criar_tarefa_com_nova_categoria_db(self):
        nova_cat_nome = "Projetos Voluntários DB"
        tarefa = srv_pess.criar_tarefa(titulo="Ação Comunitária", categoria_nome_ou_id=nova_cat_nome)
        
        tarefa_db = srv_pess.obter_tarefa_por_id(tarefa.id)
        cat_criada_db = srv_pess.obter_categoria_tarefa_por_nome(nova_cat_nome)
        self.assertIsNotNone(cat_criada_db, "Nova categoria não foi encontrada no DB.")
        self.assertEqual(tarefa_db.categoria_id, cat_criada_db.id)

    def test_criar_tarefa_com_subtarefas_db(self):
        desc_subs = ["Definir escopo", "Criar mockups", "Desenvolver MVP"]
        tarefa = srv_pess.criar_tarefa("App GestPess", "Estudos", descricoes_subtarefas=desc_subs)
        
        tarefa_db = srv_pess.obter_tarefa_por_id(tarefa.id) # obter_tarefa_por_id já carrega subtarefas
        self.assertIsNotNone(tarefa_db)
        self.assertEqual(len(tarefa_db.subtarefas), 3)
        desc_subs_db = sorted([st.descricao for st in tarefa_db.subtarefas])
        self.assertEqual(desc_subs_db, sorted(desc_subs))

    def test_adicionar_subtarefa_a_tarefa_existente_db(self):
        tarefa_mae = srv_pess.criar_tarefa("Limpar Escritório DB", "Outros")
        sub_criada = srv_pess.adicionar_subtarefa_a_tarefa_existente(tarefa_mae.id, "Organizar papéis")
        
        tarefa_atualizada_db = srv_pess.obter_tarefa_por_id(tarefa_mae.id)
        self.assertEqual(len(tarefa_atualizada_db.subtarefas), 1)
        self.assertEqual(tarefa_atualizada_db.subtarefas[0].id, sub_criada.id)
        self.assertEqual(tarefa_atualizada_db.subtarefas[0].descricao, "Organizar papéis")

    def test_listar_tarefas_por_categoria_db(self):
        cat_estudos = srv_pess.obter_categoria_tarefa_por_nome("Estudos")
        srv_pess.criar_tarefa("Estudar DB", cat_estudos.nome)
        srv_pess.criar_tarefa("Estudar Testes", cat_estudos.id) # Usando ID
        
        tarefas_estudos = srv_pess.listar_tarefas_por_categoria(cat_estudos.nome)
        self.assertEqual(len(tarefas_estudos), 2)

    def test_marcar_tarefa_como_concluida_e_pendente_db(self):
        tarefa_obj = srv_pess.criar_tarefa("Agendar Dentista DB", "Outros", descricoes_subtarefas=["Ligar consultório", "Confirmar horário"])
        self.assertFalse(tarefa_obj.concluida)
        
        srv_pess.marcar_tarefa_como_concluida(tarefa_obj.id)
        tarefa_concluida_db = srv_pess.obter_tarefa_por_id(tarefa_obj.id)
        self.assertTrue(tarefa_concluida_db.concluida)
        for sub in tarefa_concluida_db.subtarefas:
            self.assertTrue(sub.concluida, f"Subtarefa {sub.descricao} deveria estar concluída.")

        srv_pess.marcar_tarefa_como_pendente(tarefa_obj.id)
        tarefa_pendente_db = srv_pess.obter_tarefa_por_id(tarefa_obj.id)
        self.assertFalse(tarefa_pendente_db.concluida)
        # Subtarefas permanecem concluídas, conforme lógica do serviço
        for sub in tarefa_pendente_db.subtarefas:
            self.assertTrue(sub.concluida, f"Subtarefa {sub.descricao} deveria permanecer concluída após tarefa principal ser pendente.")

    def test_obter_tarefas_para_calendario_db(self):
        mes, ano = 7, 2024
        data1 = datetime(ano, mes, 10, 14, 0)
        data2 = datetime(ano, mes, 15, 9, 30)
        srv_pess.criar_tarefa("Evento 1 Cal DB", "Outros", data_hora=data1)
        srv_pess.criar_tarefa("Evento 2 Cal DB", "Outros", data_hora=data2)
        srv_pess.criar_tarefa("Evento Fora Mes", "Outros", data_hora=datetime(ano, mes + 1 if mes < 12 else 1, 1))

        tarefas_calendario = srv_pess.obter_tarefas_para_calendario(mes, ano)
        self.assertEqual(len(tarefas_calendario), 2) # Duas datas distintas
        self.assertIn(data1.strftime('%Y-%m-%d'), tarefas_calendario)
        self.assertIn(data2.strftime('%Y-%m-%d'), tarefas_calendario)
        self.assertEqual(len(tarefas_calendario[data1.strftime('%Y-%m-%d')]), 1)

if __name__ == '__main__':
    unittest.main()
```
