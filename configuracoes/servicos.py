# configuracoes/servicos.py
from typing import Optional, List # Adicionado List
from uuid import uuid4
import sqlite3 # Adicionado para type hint em _criar_configuracoes_padrao_para_usuario

from models.usuario import Usuario
from models.configuracoes_usuario import ConfiguracoesUsuario, IDIOMAS_SUPORTADOS, TEMAS_SUPORTADOS
from core.database import get_db_connection, USUARIO_PADRAO_ID # Importa ID do usuário padrão
from typing import get_args # Para obter valores de Literal

# --- Funções Auxiliares de Conversão ---
def _row_to_usuario(row) -> Optional[Usuario]:
    if not row: return None
    return Usuario(id=row['id'], nome=row['nome'], email=row['email'])

def _row_to_configuracoes_usuario(row) -> Optional[ConfiguracoesUsuario]:
    if not row: return None
    return ConfiguracoesUsuario(id=row['id'], usuario_id=row['usuario_id'], 
                                idioma=row['idioma'], tema=row['tema'])

# --- Serviços de Usuário ---
def obter_usuario_por_id(usuario_id: str) -> Optional[Usuario]:
    """Obtém um usuário específico pelo seu ID."""
    conn = get_db_connection()
    try:
        row = conn.execute("SELECT * FROM usuarios WHERE id = ?", (usuario_id,)).fetchone()
    finally:
        conn.close()
    return _row_to_usuario(row)

def obter_usuario_padrao() -> Optional[Usuario]:
    """Obtém o usuário padrão definido no sistema."""
    return obter_usuario_por_id(USUARIO_PADRAO_ID)

def atualizar_perfil_usuario(usuario_id: str, nome: Optional[str] = None, email: Optional[str] = None) -> Optional[Usuario]:
    """Atualiza o nome e/ou email de um usuário existente.
       Campos não fornecidos (None) não são alterados.
    """
    if nome is None and email is None:
        # Nada a atualizar, retorna o usuário existente sem fazer query de update
        return obter_usuario_por_id(usuario_id)

    campos_para_atualizar = {}
    if nome is not None:
        if not nome.strip(): raise ValueError("O nome do usuário não pode ser vazio.")
        campos_para_atualizar['nome'] = nome.strip()
    if email is not None: # Permite email vazio para remover, ou valida formato se não vazio
        if email.strip() == "":
            campos_para_atualizar['email'] = None
        else:
            # Adicionar validação de formato de email se desejado aqui ou no modelo
            campos_para_atualizar['email'] = email.strip()
    
    if not campos_para_atualizar: # Caso email seja "" e nome seja None
        return obter_usuario_por_id(usuario_id)

    set_clauses = [f"{campo} = ?" for campo in campos_para_atualizar.keys()]
    valores = list(campos_para_atualizar.values()) + [usuario_id]

    sql = f"UPDATE usuarios SET {', '.join(set_clauses)} WHERE id = ?"
    
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(sql, valores)
        conn.commit()
        if cursor.rowcount == 0:
            print(f"DB Config: Usuário com ID '{usuario_id}' não encontrado para atualização.")
            return None
    finally:
        conn.close()
    print(f"DB Config: Perfil do usuário ID '{usuario_id}' atualizado.")
    return obter_usuario_por_id(usuario_id)

# --- Serviços de Configurações do Usuário ---
def obter_configuracoes_usuario(usuario_id: str) -> Optional[ConfiguracoesUsuario]:
    """Obtém as configurações de um usuário. 
       Se não existirem e o usuário existir, cria configurações padrão para ele.
    """
    conn = get_db_connection()
    config = None # Definir config como None inicialmente
    try:
        row = conn.execute("SELECT * FROM configuracoes_usuario WHERE usuario_id = ?", (usuario_id,)).fetchone()
        config = _row_to_configuracoes_usuario(row)
        
        if not config:
            # Verifica se o usuário ao menos existe antes de criar configs para ele
            # Não precisa fechar a conexão aqui, pois será fechada no finally do bloco externo
            usuario_check_conn_reused = conn 
            usuario_row = usuario_check_conn_reused.execute("SELECT * FROM usuarios WHERE id = ?", (usuario_id,)).fetchone()
            usuario = _row_to_usuario(usuario_row)
            
            if usuario:
                print(f"DB Config: Configurações não encontradas para usuário '{usuario_id}', criando padrão.")
                # Cria e retorna configurações padrão para este usuário
                config = _criar_configuracoes_padrao_para_usuario(usuario_id, conn) # Passa a conexão
            else:
                # Usuário não existe, não pode ter configurações
                pass # config continua None
    finally:
        conn.close()
    return config

def _criar_configuracoes_padrao_para_usuario(usuario_id: str, conn_externa: Optional[sqlite3.Connection] = None) -> ConfiguracoesUsuario:
    """Cria uma entrada de configuração padrão para um usuário. Usa a conexão fornecida ou cria uma nova."""
    nova_config_obj = ConfiguracoesUsuario(usuario_id=usuario_id) # Usa defaults do modelo
    
    conn_to_use = conn_externa if conn_externa else get_db_connection()
    try:
        conn_to_use.execute("INSERT INTO configuracoes_usuario (id, usuario_id, idioma, tema) VALUES (?, ?, ?, ?)",
                       (nova_config_obj.id, nova_config_obj.usuario_id, nova_config_obj.idioma, nova_config_obj.tema))
        if not conn_externa: conn_to_use.commit() # Commit apenas se não for uma conexão externa
    finally:
        if not conn_externa: conn_to_use.close() # Fecha apenas se não for uma conexão externa
    return nova_config_obj

def atualizar_configuracoes_usuario(usuario_id: str, idioma: Optional[IDIOMAS_SUPORTADOS] = None, tema: Optional[TEMAS_SUPORTADOS] = None) -> Optional[ConfiguracoesUsuario]:
    """Atualiza o idioma e/ou tema das configurações de um usuário.
       Valida contra os tipos Literal definidos no modelo.
    """
    if idioma is None and tema is None:
        # Se nada for fornecido para atualizar, apenas busca (e cria se necessário) as configs
        return obter_configuracoes_usuario(usuario_id)

    # Validação dos valores permitidos
    if idioma is not None and idioma not in get_args(IDIOMAS_SUPORTADOS):
        raise ValueError(f"Idioma '{idioma}' não é suportado. Suportados: {get_args(IDIOMAS_SUPORTADOS)}")
    if tema is not None and tema not in get_args(TEMAS_SUPORTADOS):
        raise ValueError(f"Tema '{tema}' não é suportado. Suportados: {get_args(TEMAS_SUPORTADOS)}")

    campos_para_atualizar = {}
    if idioma is not None: campos_para_atualizar['idioma'] = idioma
    if tema is not None: campos_para_atualizar['tema'] = tema

    # Se após validações, não houver campos válidos para atualizar (improvável com a lógica atual, mas seguro)
    if not campos_para_atualizar:
        return obter_configuracoes_usuario(usuario_id)
        
    set_clauses = [f"{campo} = ?" for campo in campos_para_atualizar.keys()]
    valores = list(campos_para_atualizar.values()) + [usuario_id]

    sql = f"UPDATE configuracoes_usuario SET {', '.join(set_clauses)} WHERE usuario_id = ?"

    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(sql, valores)
        conn.commit()
        if cursor.rowcount == 0:
            # Se não atualizou, pode ser que as configs não existiam. Tenta obter/criar.
            print(f"DB Config: Configurações para usuário ID '{usuario_id}' não encontradas para atualização ou já estavam com esses valores. Verificando/Criando...")
            # Tenta obter/criar para garantir que existam após a tentativa de update
            # obter_configuracoes_usuario já lida com a criação se necessário
            return obter_configuracoes_usuario(usuario_id) 
    finally:
        conn.close()
    print(f"DB Config: Configurações do usuário ID '{usuario_id}' atualizadas.")
    return obter_configuracoes_usuario(usuario_id) # Retorna o objeto atualizado
```
