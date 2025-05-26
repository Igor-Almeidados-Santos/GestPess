# core/database.py
import sqlite3
import os
from typing import List
from uuid import uuid4 # Importado no topo agora

DATABASE_NAME = "gestpess.db"

# --- Funções de Conexão ---
def get_db_connection(db_name=DATABASE_NAME) -> sqlite3.Connection:
    conn = sqlite3.connect(db_name)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn

# --- Definição do Esquema (DDL) ---
SQL_CREATE_CATEGORIAS_DESPESA = """
CREATE TABLE IF NOT EXISTS categorias_despesa (
    id TEXT PRIMARY KEY,
    nome TEXT NOT NULL UNIQUE,
    predefinida INTEGER NOT NULL DEFAULT 0 CHECK(predefinida IN (0,1))
);
"""
SQL_CREATE_METODOS_PAGAMENTO = """
CREATE TABLE IF NOT EXISTS metodos_pagamento (
    id TEXT PRIMARY KEY,
    nome TEXT NOT NULL UNIQUE
);
"""
SQL_CREATE_CARTOES = """
CREATE TABLE IF NOT EXISTS cartoes (
    id TEXT PRIMARY KEY,
    nome_cartao TEXT NOT NULL,
    ultimos_4_digitos TEXT NOT NULL,
    limite REAL NOT NULL CHECK(limite >= 0),
    data_vencimento_fatura INTEGER NOT NULL CHECK(data_vencimento_fatura >= 1 AND data_vencimento_fatura <= 31),
    bandeira TEXT,
    UNIQUE(nome_cartao, ultimos_4_digitos)
);
"""
SQL_CREATE_RECEITAS = """
CREATE TABLE IF NOT EXISTS receitas (
    id TEXT PRIMARY KEY,
    descricao TEXT NOT NULL,
    valor REAL NOT NULL CHECK(valor > 0),
    data TEXT NOT NULL, -- ISO8601 string: YYYY-MM-DD HH:MM:SS
    recorrente INTEGER NOT NULL DEFAULT 0 CHECK(recorrente IN (0,1))
);
"""
SQL_CREATE_DESPESAS = """
CREATE TABLE IF NOT EXISTS despesas (
    id TEXT PRIMARY KEY,
    descricao TEXT NOT NULL,
    valor REAL NOT NULL CHECK(valor > 0),
    data TEXT NOT NULL, -- ISO8601 string: YYYY-MM-DD HH:MM:SS
    categoria_id TEXT NOT NULL,
    metodo_pagamento_id TEXT NOT NULL,
    cartao_id TEXT, 
    observacoes TEXT,
    FOREIGN KEY (categoria_id) REFERENCES categorias_despesa(id) ON DELETE RESTRICT,
    FOREIGN KEY (metodo_pagamento_id) REFERENCES metodos_pagamento(id) ON DELETE RESTRICT,
    FOREIGN KEY (cartao_id) REFERENCES cartoes(id) ON DELETE SET NULL
);
"""
SQL_CREATE_CATEGORIAS_TAREFA = """
CREATE TABLE IF NOT EXISTS categorias_tarefa (
    id TEXT PRIMARY KEY,
    nome TEXT NOT NULL UNIQUE
);
"""
SQL_CREATE_TAREFAS = """
CREATE TABLE IF NOT EXISTS tarefas (
    id TEXT PRIMARY KEY,
    titulo TEXT NOT NULL,
    categoria_id TEXT NOT NULL,
    data_hora TEXT, 
    observacoes TEXT,
    concluida INTEGER NOT NULL DEFAULT 0 CHECK(concluida IN (0,1)),
    FOREIGN KEY (categoria_id) REFERENCES categorias_tarefa(id) ON DELETE RESTRICT
);
"""
SQL_CREATE_SUBTAREFAS = """
CREATE TABLE IF NOT EXISTS subtarefas (
    id TEXT PRIMARY KEY,
    tarefa_id TEXT NOT NULL,
    descricao TEXT NOT NULL,
    concluida INTEGER NOT NULL DEFAULT 0 CHECK(concluida IN (0,1)),
    FOREIGN KEY (tarefa_id) REFERENCES tarefas(id) ON DELETE CASCADE
);
"""
SQL_CREATE_USUARIOS = """
CREATE TABLE IF NOT EXISTS usuarios (
    id TEXT PRIMARY KEY,
    nome TEXT NOT NULL,
    email TEXT UNIQUE
);
"""
SQL_CREATE_CONFIGURACOES_USUARIO = """
CREATE TABLE IF NOT EXISTS configuracoes_usuario (
    id TEXT PRIMARY KEY,
    usuario_id TEXT NOT NULL UNIQUE,
    idioma TEXT NOT NULL DEFAULT 'pt-BR',
    tema TEXT NOT NULL DEFAULT 'claro' CHECK(tema IN ('claro', 'escuro')),
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE
);
"""

ALL_TABLE_SCHEMAS = [
    SQL_CREATE_CATEGORIAS_DESPESA,
    SQL_CREATE_METODOS_PAGAMENTO,
    SQL_CREATE_CARTOES,
    SQL_CREATE_RECEITAS,
    SQL_CREATE_DESPESAS,
    SQL_CREATE_CATEGORIAS_TAREFA,
    SQL_CREATE_TAREFAS,
    SQL_CREATE_SUBTAREFAS,
    SQL_CREATE_USUARIOS, # Nova
    SQL_CREATE_CONFIGURACOES_USUARIO # Nova
]

def create_tables(conn: sqlite3.Connection):
    cursor = conn.cursor()
    for schema in ALL_TABLE_SCHEMAS:
        cursor.execute(schema)
    conn.commit()
    print("Database tables created/verified (incluindo usuarios e configuracoes_usuario).")

# --- População de Dados Iniciais ---
CATEGORIAS_DESPESA_PREDEFINIDAS_DATA = [
    ('Alimentação', True), ('Transporte', True), ('Lazer', True), 
    ('Contas', True), ('Outros', True)
]
METODOS_PAGAMENTO_PREDEFINIDOS_DATA = ['Débito', 'Crédito', 'Dinheiro']
CATEGORIAS_TAREFA_PREDEFINIDAS_DATA = ['Trabalho', 'Treino', 'Estudos', 'Outros']

# Dados para usuário padrão
USUARIO_PADRAO_NOME = "Usuário Padrão"
USUARIO_PADRAO_ID = "default_user_001" # ID Fixo para facilitar acesso

def populate_initial_data(conn: sqlite3.Connection):
    cursor = conn.cursor()
    
    # Categorias de Despesa
    for nome, predefinida_flag in CATEGORIAS_DESPESA_PREDEFINIDAS_DATA:
        cursor.execute("SELECT id FROM categorias_despesa WHERE nome = ?", (nome,))
        if not cursor.fetchone():
            cursor.execute("INSERT INTO categorias_despesa (id, nome, predefinida) VALUES (?, ?, ?)", 
                           (str(uuid4()), nome, 1 if predefinida_flag else 0))
    
    # Métodos de Pagamento
    for nome in METODOS_PAGAMENTO_PREDEFINIDOS_DATA:
        cursor.execute("SELECT id FROM metodos_pagamento WHERE nome = ?", (nome,))
        if not cursor.fetchone():
            cursor.execute("INSERT INTO metodos_pagamento (id, nome) VALUES (?, ?)", (str(uuid4()), nome))

    # Categorias de Tarefa
    for nome in CATEGORIAS_TAREFA_PREDEFINIDAS_DATA:
        cursor.execute("SELECT id FROM categorias_tarefa WHERE nome = ?", (nome,))
        if not cursor.fetchone():
            cursor.execute("INSERT INTO categorias_tarefa (id, nome) VALUES (?, ?)", (str(uuid4()), nome))

    # NOVO: Usuário Padrão e Configurações
    cursor.execute("SELECT id FROM usuarios WHERE id = ?", (USUARIO_PADRAO_ID,))
    if not cursor.fetchone():
        cursor.execute("INSERT INTO usuarios (id, nome, email) VALUES (?, ?, ?)", 
                       (USUARIO_PADRAO_ID, USUARIO_PADRAO_NOME, None)) # Email opcional
        print(f"Usuário padrão (ID: {USUARIO_PADRAO_ID}) inserido.")
        
        # Configurações para o usuário padrão
        cursor.execute("SELECT id FROM configuracoes_usuario WHERE usuario_id = ?", (USUARIO_PADRAO_ID,))
        if not cursor.fetchone():
            config_id = str(uuid4())
            cursor.execute("INSERT INTO configuracoes_usuario (id, usuario_id, idioma, tema) VALUES (?, ?, ?, ?)",
                           (config_id, USUARIO_PADRAO_ID, 'pt-BR', 'claro'))
            print(f"Configurações padrão para o usuário {USUARIO_PADRAO_ID} inseridas.")
            
    conn.commit()
    print("Initial data populated/verified (incluindo usuário padrão e configs).")

# --- Função de Inicialização Principal do DB ---
def init_db(db_name=DATABASE_NAME):
    conn = get_db_connection(db_name)
    create_tables(conn) 
    populate_initial_data(conn)
    conn.close()
    print(f"Database '{db_name}' initialized successfully.")

# --- Funções Utilitárias (Exemplo) ---
def _convert_row_to_dict(row: sqlite3.Row) -> dict:
    return dict(row) if row else None

def _convert_rows_to_dicts(rows: List[sqlite3.Row]) -> List[dict]:
    return [dict(row) for row in rows]

if __name__ == '__main__':
    print(f"Initializing database '{DATABASE_NAME}' from script...")
    init_db()
```
