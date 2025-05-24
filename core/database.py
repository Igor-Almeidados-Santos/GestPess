# core/database.py
import sqlite3
import os
from typing import List

DATABASE_NAME = "gestpess.db"
# Para testes, podemos querer um DB em memória ou um arquivo diferente
# Isso pode ser configurado por uma variável de ambiente no futuro

# --- Funções de Conexão ---
def get_db_connection(db_name=DATABASE_NAME) -> sqlite3.Connection:
    conn = sqlite3.connect(db_name)
    conn.row_factory = sqlite3.Row # Para acessar colunas por nome
    conn.execute("PRAGMA foreign_keys = ON;") # Habilita FK constraints
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
    cartao_id TEXT, -- Pode ser NULL
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
    data_hora TEXT, -- ISO8601 string: YYYY-MM-DD HH:MM:SS or NULL
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

ALL_TABLE_SCHEMAS = [
    SQL_CREATE_CATEGORIAS_DESPESA,
    SQL_CREATE_METODOS_PAGAMENTO,
    SQL_CREATE_CARTOES,
    SQL_CREATE_RECEITAS,
    SQL_CREATE_DESPESAS,
    SQL_CREATE_CATEGORIAS_TAREFA,
    SQL_CREATE_TAREFAS,
    SQL_CREATE_SUBTAREFAS
]

def create_tables(conn: sqlite3.Connection):
    cursor = conn.cursor()
    for schema in ALL_TABLE_SCHEMAS:
        cursor.execute(schema)
    conn.commit()
    print("Database tables created/verified.")

# --- População de Dados Iniciais ---
# (Importar modelos aqui pode criar dependência circular se database.py for importado por eles)
# Por isso, passamos os dados diretamente.
CATEGORIAS_DESPESA_PREDEFINIDAS_DATA = [
    ('Alimentação', True), ('Transporte', True), ('Lazer', True), 
    ('Contas', True), ('Outros', True)
]
METODOS_PAGAMENTO_PREDEFINIDOS_DATA = ['Débito', 'Crédito', 'Dinheiro']
CATEGORIAS_TAREFA_PREDEFINIDAS_DATA = ['Trabalho', 'Treino', 'Estudos', 'Outros']

def populate_initial_data(conn: sqlite3.Connection):
    cursor = conn.cursor()
    
    # Categorias de Despesa
    for nome, predefinida_flag in CATEGORIAS_DESPESA_PREDEFINIDAS_DATA:
        # Evita duplicatas se já existirem (considerando nome como unique)
        cursor.execute("SELECT id FROM categorias_despesa WHERE nome = ?", (nome,))
        if not cursor.fetchone():
            from uuid import uuid4 # Gerar ID aqui
            cursor.execute("INSERT INTO categorias_despesa (id, nome, predefinida) VALUES (?, ?, ?)", 
                           (str(uuid4()), nome, 1 if predefinida_flag else 0))
    
    # Métodos de Pagamento
    for nome in METODOS_PAGAMENTO_PREDEFINIDOS_DATA:
        cursor.execute("SELECT id FROM metodos_pagamento WHERE nome = ?", (nome,))
        if not cursor.fetchone():
            from uuid import uuid4
            cursor.execute("INSERT INTO metodos_pagamento (id, nome) VALUES (?, ?)", (str(uuid4()), nome))

    # Categorias de Tarefa
    for nome in CATEGORIAS_TAREFA_PREDEFINIDAS_DATA:
        cursor.execute("SELECT id FROM categorias_tarefa WHERE nome = ?", (nome,))
        if not cursor.fetchone():
            from uuid import uuid4
            cursor.execute("INSERT INTO categorias_tarefa (id, nome) VALUES (?, ?)", (str(uuid4()), nome))
            
    conn.commit()
    print("Initial data populated/verified.")

# --- Função de Inicialização Principal do DB ---
def init_db(db_name=DATABASE_NAME):
    # Remove o arquivo do banco de dados existente para um estado limpo durante o desenvolvimento/teste inicial
    # Em produção, isso NÃO deve ser feito.
    # if os.path.exists(db_name) and db_name != ':memory:':
    #    print(f"Removing existing database: {db_name}") # CUIDADO!
    #    os.remove(db_name)
        
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
    # Este bloco é executado se o script for chamado diretamente
    # Útil para criar o banco de dados manualmente pela primeira vez
    print(f"Initializing database '{DATABASE_NAME}' from script...")
    init_db() 
    # Exemplo de como verificar:
    # conn_check = get_db_connection()
    # print("Categorias de despesa:", conn_check.execute("SELECT * FROM categorias_despesa").fetchall())
    # print("Métodos de pagamento:", conn_check.execute("SELECT * FROM metodos_pagamento").fetchall())
    # print("Categorias de tarefa:", conn_check.execute("SELECT * FROM categorias_tarefa").fetchall())
    # conn_check.close()

```
