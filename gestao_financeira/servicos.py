# gestao_financeira/servicos.py
from datetime import datetime
from typing import List, Optional
from models.receita import Receita
from models.despesa import Despesa
from models.categoria_despesa import CategoriaDespesa
from models.metodo_pagamento import MetodoPagamento
from models.cartao import Cartao # Importado!

# "Banco de dados" em memória
_receitas: List[Receita] = []
_despesas: List[Despesa] = []
_lista_categorias_despesa: List[CategoriaDespesa] = []
_lista_metodos_pagamento: List[MetodoPagamento] = []
_lista_cartoes: List[Cartao] = [] # Adicionado!

CATEGORIAS_DESPESA_PREDEFINIDAS = ["Alimentação", "Transporte", "Lazer", "Contas", "Outros"]
METODOS_PAGAMENTO_PREDEFINIDOS = ["Débito", "Crédito", "Dinheiro"]

def inicializar_categorias_despesa_predefinidas():
    nomes_existentes = [cat.nome for cat in _lista_categorias_despesa]
    for nome_cat in CATEGORIAS_DESPESA_PREDEFINIDAS:
        if nome_cat not in nomes_existentes:
            _lista_categorias_despesa.append(CategoriaDespesa(nome=nome_cat, predefinida=True))
    # print(f"Serviço: Categorias de despesa predefinidas inicializadas/verificadas.")

def inicializar_metodos_pagamento_predefinidos():
    nomes_existentes = [mp.nome for mp in _lista_metodos_pagamento]
    for nome_mp in METODOS_PAGAMENTO_PREDEFINIDOS:
        if nome_mp not in nomes_existentes:
            _lista_metodos_pagamento.append(MetodoPagamento(nome=nome_mp))
    # print(f"Serviço: Métodos de pagamento predefinidos inicializados/verificados.")

inicializar_categorias_despesa_predefinidas()
inicializar_metodos_pagamento_predefinidos()

def limpar_dados_financeiros():
    global _receitas, _despesas, _lista_categorias_despesa, _lista_metodos_pagamento, _lista_cartoes
    _receitas = []
    _despesas = []
    _lista_categorias_despesa = []
    _lista_metodos_pagamento = []
    _lista_cartoes = [] # Limpar cartões
    inicializar_categorias_despesa_predefinidas()
    inicializar_metodos_pagamento_predefinidos()
    print("Serviço: Todos os dados financeiros em memória foram limpos.")

# --- Gestão de Categorias de Despesa (sem alteração do passo anterior) ---
def criar_categoria_despesa(nome: str) -> CategoriaDespesa:
    if obter_categoria_despesa_por_nome(nome):
        raise ValueError(f"Categoria de despesa com nome '{nome}' já existe.")
    nova_categoria = CategoriaDespesa(nome=nome, predefinida=False)
    _lista_categorias_despesa.append(nova_categoria)
    return nova_categoria

def listar_categorias_despesa() -> List[CategoriaDespesa]:
    return list(_lista_categorias_despesa)

def obter_categoria_despesa_por_id(id_cat: str) -> Optional[CategoriaDespesa]:
    return next((cat for cat in _lista_categorias_despesa if cat.id == id_cat), None)

def obter_categoria_despesa_por_nome(nome_cat: str) -> Optional[CategoriaDespesa]:
    return next((cat for cat in _lista_categorias_despesa if cat.nome.lower() == nome_cat.lower()), None)

# --- Gestão de Métodos de Pagamento (sem alteração do passo anterior) ---
def criar_metodo_pagamento(nome: str) -> MetodoPagamento:
    if obter_metodo_pagamento_por_nome(nome):
        raise ValueError(f"Método de pagamento com nome '{nome}' já existe.")
    novo_metodo = MetodoPagamento(nome=nome)
    _lista_metodos_pagamento.append(novo_metodo)
    return novo_metodo

def listar_metodos_pagamento() -> List[MetodoPagamento]:
    return list(_lista_metodos_pagamento)

def obter_metodo_pagamento_por_id(id_mp: str) -> Optional[MetodoPagamento]:
    return next((mp for mp in _lista_metodos_pagamento if mp.id == id_mp), None)

def obter_metodo_pagamento_por_nome(nome_mp: str) -> Optional[MetodoPagamento]:
    return next((mp for mp in _lista_metodos_pagamento if mp.nome.lower() == nome_mp.lower()), None)

# --- Gestão de Cartões ---
def cadastrar_cartao(nome_cartao: str, ultimos_4_digitos: str, limite: float, data_vencimento_fatura: int, bandeira: str = "") -> Cartao:
    # Validação para evitar cartões duplicados (ex: mesmo nome e últimos 4 dígitos)
    for cartao_existente in _lista_cartoes:
        if cartao_existente.nome_cartao.lower() == nome_cartao.lower() and cartao_existente.ultimos_4_digitos == ultimos_4_digitos:
            raise ValueError(f"Cartão '{nome_cartao}' com final '{ultimos_4_digitos}' já cadastrado.")
    novo_cartao = Cartao(
        nome_cartao=nome_cartao,
        ultimos_4_digitos=ultimos_4_digitos,
        limite=limite,
        data_vencimento_fatura=data_vencimento_fatura,
        bandeira=bandeira
    )
    _lista_cartoes.append(novo_cartao)
    print(f"Serviço: Cartão '{novo_cartao.nome_cartao}' (ID: {novo_cartao.id}) cadastrado.")
    return novo_cartao

def listar_cartoes() -> List[Cartao]:
    print(f"Serviço: Listando {len(_lista_cartoes)} cartões.")
    return list(_lista_cartoes)

def obter_cartao_por_id(id_cartao: str) -> Optional[Cartao]:
    return next((cartao for cartao in _lista_cartoes if cartao.id == id_cartao), None)

# --- Gestão Financeira Principal ---
def cadastrar_receita(descricao: str, valor: float, data: datetime, recorrente: bool = False) -> Receita:
    nova_receita = Receita(descricao=descricao, valor=valor, data=data, recorrente=recorrente)
    _receitas.append(nova_receita)
    return nova_receita

def cadastrar_despesa(descricao: str, valor: float, data: datetime, categoria_id: str, metodo_pagamento_id: str, cartao_id: str = None, observacoes: str = "") -> Despesa:
    categoria_obj = obter_categoria_despesa_por_id(categoria_id) or obter_categoria_despesa_por_nome(categoria_id)
    if not categoria_obj:
        raise ValueError(f"Categoria de despesa com ID ou nome '{categoria_id}' não encontrada.")
    
    metodo_pag_obj = obter_metodo_pagamento_por_id(metodo_pagamento_id) or obter_metodo_pagamento_por_nome(metodo_pagamento_id)
    if not metodo_pag_obj:
        raise ValueError(f"Método de pagamento com ID ou nome '{metodo_pagamento_id}' não encontrado.")

    # Lógica para associar despesa ao cartão, se aplicável
    cartao_associado = None
    if cartao_id:
        cartao_associado = obter_cartao_por_id(cartao_id)
        if not cartao_associado:
            raise ValueError(f"Cartão com ID '{cartao_id}' não encontrado.")
        # Verifica se o método de pagamento é 'Crédito' se um cartão for usado (regra implícita)
        if metodo_pag_obj.nome.lower() != 'crédito':
            raise ValueError(f"Despesas com cartão devem usar o método de pagamento 'Crédito'. Método usado: '{metodo_pag_obj.nome}'.")
    
    nova_despesa = Despesa(
        descricao=descricao, 
        valor=valor, 
        data=data, 
        categoria_id=categoria_obj.id, 
        metodo_pagamento_id=metodo_pag_obj.id, 
        cartao_id=cartao_id, # Armazena o ID do cartão na despesa
        observacoes=observacoes
    )

    # Adiciona a despesa ao cartão APÓS a criação bem-sucedida da Despesa e ANTES de salvar a despesa na lista geral
    # Isso garante que, se o cartão rejeitar a despesa (ex: limite), a despesa não seja registrada.
    if cartao_associado:
        cartao_associado.adicionar_despesa_ao_cartao(id_despesa=nova_despesa.id, valor_despesa=nova_despesa.valor, data_despesa=nova_despesa.data)

    _despesas.append(nova_despesa)
    msg_cartao = f", Cartão: {cartao_associado.nome_cartao}" if cartao_associado else ""
    print(f"Serviço: Despesa '{nova_despesa.descricao}' cadastrada. Categoria: {categoria_obj.nome}, Método Pg: {metodo_pag_obj.nome}{msg_cartao}")
    return nova_despesa

def obter_saldo_atual() -> float:
    total_receitas = sum(r.valor for r in _receitas)
    # Saldo não deve considerar despesas de cartão diretamente se elas já estão na fatura do cartão?
    # Por enquanto, todas as despesas (incluindo as de cartão) abatem do saldo geral.
    # A fatura do cartão é uma dívida que será paga, o que seria outra despesa (pagamento da fatura).
    total_despesas = sum(d.valor for d in _despesas) 
    return total_receitas - total_despesas

# RF002 - Gestão de Salário e Rendas (sem alteração)
def configurar_salario_principal(valor: float):
    try:
        salario_existente = next(r for r in _receitas if r.descricao == "Salário Principal" and r.recorrente)
        salario_existente.valor = valor
    except StopIteration:
        cadastrar_receita(descricao="Salário Principal", valor=valor, data=datetime.now(), recorrente=True)

def adicionar_renda_adicional(descricao: str, valor: float, data: datetime):
    return cadastrar_receita(descricao=descricao, valor=valor, data=data, recorrente=False)

def editar_valor_salario(novo_valor: float):
    configurar_salario_principal(novo_valor)

# RF005 - Funções de Cartão que interagem com a lista de cartões
def obter_fatura_cartao(cartao_id: str) -> float:
    cartao = obter_cartao_por_id(cartao_id)
    if not cartao:
        raise ValueError(f"Cartão com ID '{cartao_id}' não encontrado.")
    fatura = cartao.calcular_fatura_atual()
    print(f"Serviço: Fatura atual do cartão '{cartao.nome_cartao}': R${fatura:.2f}")
    return fatura

def obter_limite_disponivel_cartao(cartao_id: str) -> float:
    cartao = obter_cartao_por_id(cartao_id)
    if not cartao:
        raise ValueError(f"Cartão com ID '{cartao_id}' não encontrado.")
    disponivel = cartao.calcular_limite_disponivel()
    print(f"Serviço: Limite disponível do cartão '{cartao.nome_cartao}': R${disponivel:.2f}")
    return disponivel

# Função remover_cartao não foi solicitada para implementação completa ainda.
# def remover_cartao(cartao_id: str):
#     global _lista_cartoes
#     cartao_para_remover = obter_cartao_por_id(cartao_id)
#     if not cartao_para_remover:
#         raise ValueError(f"Cartão com ID '{cartao_id}' não encontrado para remoção.")
#     # Adicionar lógica para verificar se o cartão tem despesas pendentes ou se deve ser apenas desativado
#     _lista_cartoes = [c for c in _lista_cartoes if c.id != cartao_id]
#     print(f"Serviço: Cartão '{cartao_para_remover.nome_cartao}' removido.")

```
