# models/tarefa.py
from datetime import datetime
from typing import List, Optional
from uuid import uuid4

class Subtarefa:
    def __init__(self, descricao: str, concluida: bool = False, id: str = None):
        if not descricao or not descricao.strip():
            raise ValueError("A descrição da subtarefa não pode ser vazia.")
        self.id = id if id else str(uuid4())
        self.descricao = descricao.strip()
        self.concluida = concluida

    def __repr__(self):
        return f"Subtarefa(id='{self.id}', descricao='{self.descricao}', concluida={self.concluida})"

    def marcar_como_concluida(self):
        self.concluida = True

    def marcar_como_pendente(self):
        self.concluida = False

class Tarefa:
    def __init__(self, titulo: str, categoria_id: str, data_hora: Optional[datetime] = None, observacoes: str = "", subtarefas: Optional[List[Subtarefa]] = None, id: str = None):
        if not titulo or not titulo.strip():
            raise ValueError("O título da tarefa não pode ser vazio.")
        if not categoria_id or not categoria_id.strip():
            raise ValueError("O ID da categoria da tarefa não pode ser vazio.")
        
        self.id = id if id else str(uuid4())
        self.titulo = titulo.strip()
        self.categoria_id = categoria_id.strip()
        self.data_hora = data_hora
        self.observacoes = observacoes.strip() if observacoes else ""
        self.subtarefas = subtarefas if subtarefas is not None else []
        self.concluida = False # Estado da tarefa principal

    def adicionar_subtarefa(self, descricao_subtarefa: str) -> Subtarefa:
        nova_subtarefa = Subtarefa(descricao=descricao_subtarefa)
        self.subtarefas.append(nova_subtarefa)
        return nova_subtarefa

    def remover_subtarefa(self, subtarefa_id: str):
        self.subtarefas = [st for st in self.subtarefas if st.id != subtarefa_id]

    def marcar_como_concluida(self):
        self.concluida = True
        for sub_task in self.subtarefas: # Opcional: marcar todas as subtarefas como concluídas também
             sub_task.marcar_como_concluida()

    def marcar_como_pendente(self):
        self.concluida = False
        # Opcional: marcar todas as subtarefas como pendentes também
        # for sub_task in self.subtarefas:
        #      sub_task.marcar_como_pendente()


    def __repr__(self):
        return f"Tarefa(id='{self.id}', titulo='{self.titulo}', categoria_id='{self.categoria_id}', concluida={self.concluida}, subtarefas={len(self.subtarefas)})"
