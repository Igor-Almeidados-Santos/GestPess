# gestao_pessoal/servicos.py
from datetime import datetime
from typing import List, Optional
# from models.tarefa import Tarefa, Subtarefa

# RF006 - Sistema de Tarefas
def criar_tarefa(titulo: str, categoria_id: str, data_hora: Optional[datetime] = None, observacoes: str = "", subtarefas_desc: Optional[List[str]] = None):
    # Lógica para criar uma nova tarefa
    # Se subtarefas_desc for fornecido, criar objetos Subtarefa
    # Deverá interagir com alguma forma de persistência de dados
    print(f"Serviço: Criando tarefa '{titulo}', Categoria: {categoria_id}")
    if subtarefas_desc:
        for sub_desc in subtarefas_desc:
            print(f"  - Adicionando subtarefa: {sub_desc}")
    pass

def adicionar_subtarefa(tarefa_id: str, descricao_subtarefa: str):
    # Lógica para adicionar uma subtarefa a uma tarefa existente
    print(f"Serviço: Adicionando subtarefa '{descricao_subtarefa}' à tarefa ID '{tarefa_id}'")
    pass

def definir_data_hora_tarefa(tarefa_id: str, data_hora: datetime):
    # Lógica para definir ou atualizar data e hora de uma tarefa
    print(f"Serviço: Definindo data/hora para tarefa ID '{tarefa_id}' em {data_hora}")
    pass

def listar_tarefas_por_categoria(categoria_id: str):
    # Lógica para listar tarefas de uma categoria específica
    print(f"Serviço: Listando tarefas da categoria ID '{categoria_id}'")
    return []

def listar_tarefas_por_data(data: datetime):
    # Lógica para listar tarefas de uma data específica
    print(f"Serviço: Listando tarefas para a data {data.strftime('%Y-%m-%d')}")
    return []

# RF007 - Calendário Integrado (os serviços de tarefa já dão suporte parcial)
def obter_tarefas_para_calendario(mes: int, ano: int):
    # Lógica para buscar tarefas de um determinado mês/ano para exibição no calendário
    print(f"Serviço: Obtendo tarefas para o calendário de {mes}/{ano}")
    return {} # Ex: { '2024-12-25': [tarefa1, tarefa2] }
