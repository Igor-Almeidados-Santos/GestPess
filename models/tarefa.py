# models/tarefa.py
from datetime import datetime
from typing import List, Optional

class Subtarefa:
    def __init__(self, id: str, descricao: str, concluida: bool = False):
        self.id = id
        self.descricao = descricao
        self.concluida = concluida

class Tarefa:
    def __init__(self, id: str, titulo: str, categoria_id: str, data_hora: Optional[datetime] = None, observacoes: str = "", subtarefas: Optional[List[Subtarefa]] = None):
        self.id = id
        self.titulo = titulo
        self.categoria_id = categoria_id # ID da categoria da tarefa (Trabalho, Treino, etc.)
        self.data_hora = data_hora
        self.observacoes = observacoes
        self.subtarefas = subtarefas if subtarefas is not None else []
        self.concluida = False # Estado da tarefa principal

# Exemplo de uso (opcional, apenas para teste)
# if __name__ == '__main__':
#     sub1 = Subtarefa(id="st001", descricao="Comprar passagens")
#     sub2 = Subtarefa(id="st002", descricao="Reservar hotel")
#     tarefa_viagem = Tarefa(id="t001", titulo="Planejar Viagem", categoria_id="cat_lazer", data_hora=datetime(2024, 12, 15, 10, 0, 0), subtarefas=[sub1, sub2])
#     print(f"Tarefa: {tarefa_viagem.titulo}, Data: {tarefa_viagem.data_hora}")
#     for sub in tarefa_viagem.subtarefas:
#         print(f"  Subtarefa: {sub.descricao}")
