# models/categoria_tarefa.py
from uuid import uuid4

class CategoriaTarefa:
    CATEGORIAS_PREDEFINIDAS = ["Trabalho", "Treino", "Estudos", "Outros"]

    def __init__(self, nome: str, id: str = None):
        if not nome or not nome.strip():
            raise ValueError("O nome da categoria da tarefa não pode ser vazio.")
        
        self.id = id if id else str(uuid4())
        self.nome = nome.strip()

    def __repr__(self):
        return f"CategoriaTarefa(id='{self.id}', nome='{self.nome}')"

    @classmethod
    def obter_categorias_predefinidas(cls) -> list:
        # Esta função poderia criar instâncias de CategoriaTarefa se necessário,
        # mas por ora retorna apenas os nomes para referência nos serviços.
        return cls.CATEGORIAS_PREDEFINIDAS
