# models/tarefa.py
from datetime import datetime
from typing import List, Optional
from uuid import uuid4 # Garantir importação

class Subtarefa:
    def __init__(self, descricao: str, concluida: bool = False, id: str = None):
        if not descricao:
            raise ValueError("A descrição da subtarefa não pode ser vazia.")
        self.id = id if id else str(uuid4())
        self.descricao = descricao
        self.concluida = concluida

    def __repr__(self):
        return f"Subtarefa(id='{self.id}', descricao='{self.descricao}', concluida={self.concluida})"


class Tarefa:
    def __init__(self, titulo: str, categoria_id: str, data_hora: Optional[datetime] = None, observacoes: str = "", subtarefas: Optional[List[Subtarefa]] = None, id: str = None):
        if not titulo:
            raise ValueError("O título da tarefa não pode ser vazio.")
        # categoria_id será validado no nível de serviço ou com um enum/tabela no futuro
        
        self.id = id if id else str(uuid4())
        self.titulo = titulo
        self.categoria_id = categoria_id 
        self.data_hora = data_hora
        self.observacoes = observacoes
        self.subtarefas = subtarefas if subtarefas is not None else []
        self.concluida = False

    def adicionar_subtarefa(self, descricao_subtarefa: str):
        nova_subtarefa = Subtarefa(descricao=descricao_subtarefa)
        self.subtarefas.append(nova_subtarefa)
        return nova_subtarefa

    def __repr__(self):
        return f"Tarefa(id='{self.id}', titulo='{self.titulo}', categoria_id='{self.categoria_id}', concluida={self.concluida})"
