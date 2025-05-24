# gestao_pessoal/servicos.py
from datetime import datetime
from typing import List, Optional, Dict
from models.tarefa import Tarefa, Subtarefa
from models.categoria_tarefa import CategoriaTarefa

# "Banco de dados" em memória
_tarefas: List[Tarefa] = []
_categorias_tarefa: List[CategoriaTarefa] = []

def inicializar_categorias_tarefa_predefinidas():
    """Adiciona as categorias predefinidas se ainda não existirem."""
    nomes_categorias_existentes = [cat.nome for cat in _categorias_tarefa]
    categorias_adicionadas = False
    for nome_categoria in CategoriaTarefa.CATEGORIAS_PREDEFINIDAS:
        if nome_categoria not in nomes_categorias_existentes:
            nova_categoria = CategoriaTarefa(nome=nome_categoria)
            _categorias_tarefa.append(nova_categoria)
            categorias_adicionadas = True
    if categorias_adicionadas or not nomes_categorias_existentes:
        print(f"Serviço: Categorias de tarefa predefinidas inicializadas/verificadas: {[cat.nome for cat in _categorias_tarefa]}")

# Inicializar as categorias ao carregar o módulo de serviços
inicializar_categorias_tarefa_predefinidas()

def limpar_dados_pessoais():
    """Limpa as listas de tarefas e re-inicializa/verifica as categorias predefinidas em memória."""
    global _tarefas
    _tarefas = []
    # _categorias_tarefa não é limpa para manter IDs consistentes se desejado,
    # mas garantimos que as predefinidas existam.
    inicializar_categorias_tarefa_predefinidas() # Garante que as predefinidas estejam lá
    print("Serviço: Dados de tarefas em memória foram limpos. Categorias predefinidas verificadas.")

def obter_categoria_tarefa_por_nome(nome: str) -> Optional[CategoriaTarefa]:
    for cat in _categorias_tarefa:
        if cat.nome.lower() == nome.lower():
            return cat
    return None

def obter_categoria_tarefa_por_id(id_categoria: str) -> Optional[CategoriaTarefa]:
    for cat in _categorias_tarefa:
        if cat.id == id_categoria:
            return cat
    return None

def criar_categoria_tarefa(nome: str) -> CategoriaTarefa:
    if obter_categoria_tarefa_por_nome(nome):
        raise ValueError(f"Categoria de tarefa com nome '{nome}' já existe.")
    nova_categoria = CategoriaTarefa(nome=nome)
    _categorias_tarefa.append(nova_categoria)
    print(f"Serviço: Categoria de tarefa '{nova_categoria.nome}' (ID: {nova_categoria.id}) criada.")
    return nova_categoria

def listar_categorias_tarefa() -> List[CategoriaTarefa]:
    print(f"Serviço: Listando categorias de tarefa. Total: {len(_categorias_tarefa)}")
    return list(_categorias_tarefa)


# RF006 - Sistema de Tarefas
def criar_tarefa(titulo: str, categoria_nome_ou_id: str, data_hora: Optional[datetime] = None, observacoes: str = "", descricoes_subtarefas: Optional[List[str]] = None) -> Tarefa:
    categoria = obter_categoria_tarefa_por_id(categoria_nome_ou_id)
    if not categoria:
        categoria = obter_categoria_tarefa_por_nome(categoria_nome_ou_id)
        if not categoria:
            eh_uuid_potencial = len(categoria_nome_ou_id) == 36 and '-' in categoria_nome_ou_id
            if eh_uuid_potencial:
                 raise ValueError(f"Categoria de tarefa com ID '{categoria_nome_ou_id}' não encontrada.")
            else:
                print(f"Serviço: Categoria '{categoria_nome_ou_id}' não encontrada, criando nova...")
                categoria = criar_categoria_tarefa(categoria_nome_ou_id)

    subtarefas_objs = []
    if descricoes_subtarefas:
        for desc_sub in descricoes_subtarefas:
            subtarefas_objs.append(Subtarefa(descricao=desc_sub))
    
    nova_tarefa = Tarefa(
        titulo=titulo,
        categoria_id=categoria.id, 
        data_hora=data_hora,
        observacoes=observacoes,
        subtarefas=subtarefas_objs
    )
    _tarefas.append(nova_tarefa)
    print(f"Serviço: Tarefa '{nova_tarefa.titulo}' (ID: {nova_tarefa.id}) criada na categoria '{categoria.nome}'.")
    return nova_tarefa

def obter_tarefa_por_id(tarefa_id: str) -> Optional[Tarefa]:
    for tarefa in _tarefas:
        if tarefa.id == tarefa_id:
            return tarefa
    print(f"Serviço: Tarefa com ID '{tarefa_id}' não encontrada.")
    return None

def adicionar_subtarefa_a_tarefa_existente(tarefa_id: str, descricao_subtarefa: str) -> Subtarefa:
    tarefa = obter_tarefa_por_id(tarefa_id)
    if not tarefa:
        raise ValueError(f"Tarefa com ID '{tarefa_id}' não encontrada para adicionar subtarefa.")
    
    nova_subtarefa = tarefa.adicionar_subtarefa(descricao_subtarefa)
    print(f"Serviço: Subtarefa '{nova_subtarefa.descricao}' adicionada à tarefa '{tarefa.titulo}'.")
    return nova_subtarefa

def listar_tarefas_por_categoria(categoria_id_ou_nome: str) -> List[Tarefa]:
    categoria = obter_categoria_tarefa_por_id(categoria_id_ou_nome)
    if not categoria:
        categoria = obter_categoria_tarefa_por_nome(categoria_id_ou_nome)
    
    if not categoria:
        print(f"Serviço: Categoria '{categoria_id_ou_nome}' não encontrada. Nenhuma tarefa para listar.")
        return []
        
    tarefas_filtradas = [t for t in _tarefas if t.categoria_id == categoria.id]
    print(f"Serviço: Listando {len(tarefas_filtradas)} tarefas da categoria '{categoria.nome}'.")
    return tarefas_filtradas

def listar_todas_tarefas() -> List[Tarefa]:
    print(f"Serviço: Listando todas as {len(_tarefas)} tarefas.")
    return list(_tarefas)

def definir_data_hora_tarefa(tarefa_id: str, data_hora: datetime) -> Optional[Tarefa]:
    tarefa = obter_tarefa_por_id(tarefa_id)
    if not tarefa:
        return None 
    tarefa.data_hora = data_hora
    print(f"Serviço: Data/hora da tarefa '{tarefa.titulo}' definida para {data_hora}.")
    return tarefa

# RF007 - Calendário Integrado
def obter_tarefas_para_calendario(mes: int, ano: int) -> Dict[str, List[Tarefa]]:
    tarefas_do_mes: Dict[str, List[Tarefa]] = {}
    for tarefa in _tarefas:
        if tarefa.data_hora and tarefa.data_hora.year == ano and tarefa.data_hora.month == mes:
            data_str = tarefa.data_hora.strftime('%Y-%m-%d')
            if data_str not in tarefas_do_mes:
                tarefas_do_mes[data_str] = []
            tarefas_do_mes[data_str].append(tarefa)
    print(f"Serviço: Obtendo {sum(len(t) for t in tarefas_do_mes.values())} tarefas para o calendário de {mes:02d}/{ano}.")
    return tarefas_do_mes
