# gestao_pessoal/servicos.py
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from uuid import uuid4
from collections import defaultdict

from models.tarefa import Tarefa, Subtarefa
from models.categoria_tarefa import CategoriaTarefa
from core.database import get_db_connection #, populate_initial_data # Para limpar e repopular

# --- Funções Auxiliares de Conversão ---
def _row_to_categoria_tarefa(row) -> Optional[CategoriaTarefa]:
    if not row: return None
    return CategoriaTarefa(id=row['id'], nome=row['nome'])

def _load_subtarefas_para_tarefa(tarefa_id: str, conn: Optional[Any] = None) -> List[Subtarefa]:
    """Carrega subtarefas para um dado ID de tarefa.
       Reutiliza a conexão existente se fornecida, senão cria uma nova.
    """
    close_conn_after = False
    if conn is None:
        conn = get_db_connection()
        close_conn_after = True
    
    subtarefas = []
    try:
        rows = conn.execute("SELECT id, descricao, concluida FROM subtarefas WHERE tarefa_id = ? ORDER BY id", (tarefa_id,)).fetchall()
        subtarefas = [Subtarefa(id=r['id'], descricao=r['descricao'], concluida=bool(r['concluida'])) for r in rows]
    finally:
        if close_conn_after:
            conn.close()
    return subtarefas

def _row_to_tarefa(row, conn: Optional[Any] = None) -> Optional[Tarefa]: 
    """Converte uma linha do banco para um objeto Tarefa, incluindo suas subtarefas.
       Reutiliza a conexão existente para carregar subtarefas, se fornecida.
    """
    if not row: return None
    tarefa_id = row['id']
    # Passa a conexão para _load_subtarefas_para_tarefa para evitar abrir nova conexão desnecessariamente
    subtarefas = _load_subtarefas_para_tarefa(tarefa_id, conn) 
    data_hora_obj = datetime.fromisoformat(row['data_hora']) if row['data_hora'] else None
    return Tarefa(id=tarefa_id, titulo=row['titulo'], categoria_id=row['categoria_id'], 
                  data_hora=data_hora_obj, observacoes=row['observacoes'], 
                  concluida=bool(row['concluida']), subtarefas=subtarefas)

# --- Gestão de Categorias de Tarefa (DB) ---
# A inicialização de categorias predefinidas é feita por core/database.py:init_db()

def criar_categoria_tarefa(nome: str) -> CategoriaTarefa:
    if obter_categoria_tarefa_por_nome(nome):
        raise ValueError(f"Categoria de tarefa com nome '{nome}' já existe.")
    nova_id = str(uuid4())
    conn = get_db_connection()
    try:
        conn.execute("INSERT INTO categorias_tarefa (id, nome) VALUES (?, ?)", (nova_id, nome))
        conn.commit()
    finally: conn.close()
    print(f"DB: Categoria de tarefa '{nome}' (ID: {nova_id}) criada.")
    return CategoriaTarefa(id=nova_id, nome=nome)

def listar_categorias_tarefa() -> List[CategoriaTarefa]:
    conn = get_db_connection()
    try: rows = conn.execute("SELECT id, nome FROM categorias_tarefa ORDER BY nome").fetchall()
    finally: conn.close()
    return [_row_to_categoria_tarefa(row) for row in rows]

def obter_categoria_tarefa_por_id(id_categoria: str) -> Optional[CategoriaTarefa]:
    conn = get_db_connection()
    try: row = conn.execute("SELECT id, nome FROM categorias_tarefa WHERE id = ?", (id_categoria,)).fetchone()
    finally: conn.close()
    return _row_to_categoria_tarefa(row)

def obter_categoria_tarefa_por_nome(nome: str) -> Optional[CategoriaTarefa]:
    conn = get_db_connection()
    try: row = conn.execute("SELECT id, nome FROM categorias_tarefa WHERE lower(nome) = lower(?)", (nome,)).fetchone()
    finally: conn.close()
    return _row_to_categoria_tarefa(row)

# --- Gestão de Tarefas (DB) ---
def criar_tarefa(titulo: str, categoria_nome_ou_id: str, data_hora: Optional[datetime] = None, observacoes: str = "", descricoes_subtarefas: Optional[List[str]] = None) -> Tarefa:
    categoria = obter_categoria_tarefa_por_id(categoria_nome_ou_id) or obter_categoria_tarefa_por_nome(categoria_nome_ou_id)
    if not categoria:
        eh_uuid_potencial = len(categoria_nome_ou_id) == 36 and '-' in categoria_nome_ou_id # Simple check
        if eh_uuid_potencial: raise ValueError(f"Categoria de tarefa com ID '{categoria_nome_ou_id}' não encontrada.")
        else: categoria = criar_categoria_tarefa(categoria_nome_ou_id) # Cria se não for UUID e não existir por nome

    # Cria o objeto Tarefa primeiro (para ter o ID e outras validações do modelo)
    nova_tarefa_obj = Tarefa(titulo=titulo, categoria_id=categoria.id, data_hora=data_hora, observacoes=observacoes)
    
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO tarefas (id, titulo, categoria_id, data_hora, observacoes, concluida) "
                       "VALUES (?, ?, ?, ?, ?, ?)", 
                       (nova_tarefa_obj.id, nova_tarefa_obj.titulo, nova_tarefa_obj.categoria_id, 
                        nova_tarefa_obj.data_hora.isoformat() if nova_tarefa_obj.data_hora else None, 
                        nova_tarefa_obj.observacoes, 1 if nova_tarefa_obj.concluida else 0))
        
        if descricoes_subtarefas:
            for desc_sub in descricoes_subtarefas:
                nova_subtarefa_obj = Subtarefa(descricao=desc_sub) # Cria objeto Subtarefa
                nova_tarefa_obj.subtarefas.append(nova_subtarefa_obj) # Adiciona ao objeto Tarefa em memória
                cursor.execute("INSERT INTO subtarefas (id, tarefa_id, descricao, concluida) VALUES (?, ?, ?, ?)",
                               (nova_subtarefa_obj.id, nova_tarefa_obj.id, nova_subtarefa_obj.descricao, 
                                1 if nova_subtarefa_obj.concluida else 0))
        conn.commit()
    finally: conn.close()
    print(f"DB: Tarefa '{nova_tarefa_obj.titulo}' e {len(nova_tarefa_obj.subtarefas)} subtarefa(s) criadas.")
    return nova_tarefa_obj # Retorna o objeto com subtarefas (se criadas)

def obter_tarefa_por_id(tarefa_id: str) -> Optional[Tarefa]:
    conn = get_db_connection()
    tarefa = None
    try: 
        row = conn.execute("SELECT * FROM tarefas WHERE id = ?", (tarefa_id,)).fetchone()
        # Passa a conexão para _row_to_tarefa para que ela possa ser reutilizada por _load_subtarefas_para_tarefa
        tarefa = _row_to_tarefa(row, conn) 
    finally: 
        conn.close()
    if not tarefa: print(f"DB: Tarefa com ID '{tarefa_id}' não encontrada.")
    return tarefa

def adicionar_subtarefa_a_tarefa_existente(tarefa_id: str, descricao_subtarefa: str) -> Optional[Subtarefa]:
    # Primeiro, verifica se a tarefa principal existe. Não precisa carregar subtarefas aqui.
    conn_check = get_db_connection()
    try:
        tarefa_existe_row = conn_check.execute("SELECT id FROM tarefas WHERE id = ?", (tarefa_id,)).fetchone()
        if not tarefa_existe_row:
            raise ValueError(f"Tarefa com ID '{tarefa_id}' não encontrada.")
    finally:
        conn_check.close()
        
    nova_subtarefa_obj = Subtarefa(descricao=descricao_subtarefa)
    conn_insert = get_db_connection()
    try:
        conn_insert.execute("INSERT INTO subtarefas (id, tarefa_id, descricao, concluida) VALUES (?, ?, ?, ?)",
                       (nova_subtarefa_obj.id, tarefa_id, nova_subtarefa_obj.descricao, 
                        1 if nova_subtarefa_obj.concluida else 0))
        conn_insert.commit()
    finally: 
        conn_insert.close()
    print(f"DB: Subtarefa '{nova_subtarefa_obj.descricao}' adicionada à tarefa ID '{tarefa_id}'.")
    return nova_subtarefa_obj

def listar_tarefas_por_categoria(categoria_id_ou_nome: str) -> List[Tarefa]:
    categoria = obter_categoria_tarefa_por_id(categoria_id_ou_nome) or obter_categoria_tarefa_por_nome(categoria_id_ou_nome)
    if not categoria: 
        print(f"DB: Categoria '{categoria_id_ou_nome}' não encontrada. Nenhuma tarefa para listar.")
        return []
    
    conn = get_db_connection()
    tarefas = []
    try: 
        rows = conn.execute("SELECT * FROM tarefas WHERE categoria_id = ? ORDER BY data_hora DESC, titulo ASC", (categoria.id,)).fetchall()
        for row in rows:
            tarefa = _row_to_tarefa(row, conn) # Passa a conexão para reutilização
            if tarefa: tarefas.append(tarefa)
    finally: 
        conn.close()
    print(f"DB: Listando {len(tarefas)} tarefas da categoria '{categoria.nome}'.")
    return tarefas

def listar_todas_tarefas() -> List[Tarefa]:
    conn = get_db_connection()
    tarefas = []
    try: 
        rows = conn.execute("SELECT * FROM tarefas ORDER BY data_hora DESC, titulo ASC").fetchall()
        for row in rows:
            tarefa = _row_to_tarefa(row, conn) # Passa a conexão para reutilização
            if tarefa: tarefas.append(tarefa)
    finally: 
        conn.close()
    print(f"DB: Listando todas as {len(tarefas)} tarefas.")
    return tarefas

def _atualizar_campo_tarefa(tarefa_id: str, campo: str, valor: Any) -> bool:
    """Atualiza um campo específico de uma tarefa no banco."""
    valor_db = valor
    if isinstance(valor, bool): valor_db = 1 if valor else 0
    elif isinstance(valor, datetime): valor_db = valor.isoformat()
    elif valor is None: valor_db = None # Explicitamente para data_hora
    
    sql = f"UPDATE tarefas SET {campo} = ? WHERE id = ?"
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(sql, (valor_db, tarefa_id))
        conn.commit()
        return cursor.rowcount > 0
    finally: conn.close()

def definir_data_hora_tarefa(tarefa_id: str, data_hora: Optional[datetime]) -> Optional[Tarefa]:
    if not obter_tarefa_por_id(tarefa_id): # Verifica existência e carrega para confirmação
        raise ValueError(f"Tarefa com ID '{tarefa_id}' não encontrada.")
    if _atualizar_campo_tarefa(tarefa_id, 'data_hora', data_hora):
        print(f"DB: Data/hora da tarefa ID '{tarefa_id}' atualizada.")
        return obter_tarefa_por_id(tarefa_id) 
    return None # Caso a atualização falhe por algum motivo não previsto (ex: DB error)

def marcar_tarefa_como_concluida(tarefa_id: str) -> Optional[Tarefa]:
    if not obter_tarefa_por_id(tarefa_id): # Verifica existência
        raise ValueError(f"Tarefa com ID '{tarefa_id}' não encontrada.")
    
    conn = get_db_connection()
    try:
        # Marcar subtarefas como concluídas também
        conn.execute("UPDATE subtarefas SET concluida = 1 WHERE tarefa_id = ?", (tarefa_id,))
        conn.execute("UPDATE tarefas SET concluida = 1 WHERE id = ?", (tarefa_id,))
        conn.commit()
    finally: conn.close()
    print(f"DB: Tarefa ID '{tarefa_id}' e suas subtarefas marcadas como concluídas.")
    return obter_tarefa_por_id(tarefa_id) # Retorna a tarefa atualizada com subtarefas atualizadas

def marcar_tarefa_como_pendente(tarefa_id: str) -> Optional[Tarefa]:
    if not obter_tarefa_por_id(tarefa_id): # Verifica existência
        raise ValueError(f"Tarefa com ID '{tarefa_id}' não encontrada.")
    
    # A lógica de reverter subtarefas para pendente é opcional. 
    # Para manter o comportamento do modelo anterior, não mexemos nas subtarefas aqui.
    if _atualizar_campo_tarefa(tarefa_id, 'concluida', False):
        print(f"DB: Tarefa ID '{tarefa_id}' marcada como pendente.")
        return obter_tarefa_por_id(tarefa_id)
    return None

# RF007 - Calendário Integrado
def obter_tarefas_para_calendario(mes: int, ano: int) -> Dict[str, List[Tarefa]]:
    if not (1 <= mes <= 12): raise ValueError("Mês inválido.")
    data_inicio_mes = datetime(ano, mes, 1)
    if mes == 12: data_fim_mes = datetime(ano, 12, 31, 23, 59, 59)
    else: data_fim_mes = datetime(ano, mes + 1, 1) - timedelta(seconds=1)
    
    tarefas_do_mes_dict: Dict[str, List[Tarefa]] = defaultdict(list)
    conn = get_db_connection()
    try:
        sql = "SELECT * FROM tarefas WHERE data_hora IS NOT NULL AND data_hora >= ? AND data_hora <= ? ORDER BY data_hora"
        rows = conn.execute(sql, (data_inicio_mes.isoformat(), data_fim_mes.isoformat())).fetchall()
        for row in rows:
            tarefa = _row_to_tarefa(row, conn) # Passa a conexão
            if tarefa and tarefa.data_hora: 
                data_str = tarefa.data_hora.strftime('%Y-%m-%d')
                tarefas_do_mes_dict[data_str].append(tarefa)
    finally: conn.close()
    print(f"DB: Obtendo {sum(len(t_list) for t_list in tarefas_do_mes_dict.values())} tarefas para o calendário de {mes:02d}/{ano}.")
    return dict(tarefas_do_mes_dict)

# Função para limpar dados (para testes)
def limpar_tabelas_pessoais():
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM subtarefas;")
        cursor.execute("DELETE FROM tarefas;")
        cursor.execute("DELETE FROM categorias_tarefa;")
        conn.commit()
        from core.database import populate_initial_data # Importação tardia para evitar ciclo
        # populate_initial_data só lida com categorias de despesa e métodos de pagamento.
        # Precisamos de uma forma de repopular categorias de tarefa se quisermos aqui.
        # Por ora, vamos assumir que o init_db do core.database já cuidou disso na configuração inicial.
        # Se não, uma função específica em core.database para repopular SÓ categorias de tarefa seria necessária.
        # Para este contexto, vamos garantir que as predefinidas do modelo sejam inseridas se não existirem.
        for nome_cat_tarefa in CategoriaTarefa.CATEGORIAS_PREDEFINIDAS:
            if not obter_categoria_tarefa_por_nome(nome_cat_tarefa): # Usa as funções de serviço que acessam DB
                 criar_categoria_tarefa(nome_cat_tarefa) # Cria se não existir
        print("DB: Tabelas de gestão pessoal (subtarefas, tarefas, categorias_tarefa) limpas e categorias predefinidas verificadas/restauradas.")
    finally: conn.close()

```
