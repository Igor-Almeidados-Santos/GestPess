# gestao_financeira/servicos.py
from datetime import datetime
from typing import List, Dict
from models.receita import Receita
from models.despesa import Despesa
# from models.cartao import Cartao # Futura utilização
# from models.categoria_despesa import CategoriaDespesa # Futura utilização
# from models.metodo_pagamento import MetodoPagamento # Futura utilização

# "Banco de dados" em memória
_receitas: List[Receita] = []
_despesas: List[Despesa] = []
_categorias_despesa: Dict[str, str] = { # Exemplo, idealmente viria de CategoriaDespesa
    "cat001": "Alimentação",
    "cat002": "Transporte",
    "cat003": "Lazer",
    "cat004": "Contas",
    "cat005": "Outros"
}
_metodos_pagamento: Dict[str, str] = { # Exemplo, idealmente viria de MetodoPagamento
    "mp001": "Débito",
    "mp002": "Crédito",
    "mp003": "Dinheiro"
}

# RF001 - Controle de Receitas e Despesas
def cadastrar_receita(descricao: str, valor: float, data: datetime, recorrente: bool = False) -> Receita:
    nova_receita = Receita(descricao=descricao, valor=valor, data=data, recorrente=recorrente)
    _receitas.append(nova_receita)
    print(f"Serviço: Receita '{nova_receita.descricao}' (ID: {nova_receita.id}) cadastrada. Valor: {nova_receita.valor:.2f}")
    return nova_receita

def cadastrar_despesa(descricao: str, valor: float, data: datetime, categoria_id: str, metodo_pagamento_id: str, cartao_id: str = None, observacoes: str = "") -> Despesa:
    # Validação básica de existência de categoria e método de pagamento (simulada)
    if categoria_id not in _categorias_despesa:
        raise ValueError(f"Categoria com ID '{categoria_id}' não encontrada.")
    if metodo_pagamento_id not in _metodos_pagamento:
        raise ValueError(f"Método de pagamento com ID '{metodo_pagamento_id}' não encontrado.")
    # No futuro, verificar cartao_id se fornecido

    nova_despesa = Despesa(
        descricao=descricao, 
        valor=valor, 
        data=data, 
        categoria_id=categoria_id, 
        metodo_pagamento_id=metodo_pagamento_id, 
        cartao_id=cartao_id, 
        observacoes=observacoes
    )
    _despesas.append(nova_despesa)
    print(f"Serviço: Despesa '{nova_despesa.descricao}' (ID: {nova_despesa.id}) cadastrada. Valor: {nova_despesa.valor:.2f}, Categoria: {_categorias_despesa.get(categoria_id)}")
    return nova_despesa

def obter_saldo_atual() -> float:
    total_receitas = sum(r.valor for r in _receitas)
    total_despesas = sum(d.valor for d in _despesas)
    saldo = total_receitas - total_despesas
    print(f"Serviço: Obtendo saldo atual. Receitas: {total_receitas:.2f}, Despesas: {total_despesas:.2f}, Saldo: {saldo:.2f}")
    return saldo

# Funções utilitárias para limpar dados em memória (útil para testes)
def limpar_dados_financeiros():
    global _receitas, _despesas
    _receitas = []
    _despesas = []
    print("Serviço: Dados financeiros (receitas e despesas) em memória foram limpos.")

# --- Esboços de funções futuras (mantendo a estrutura do plano anterior) ---

# RF002 - Gestão de Salário e Rendas
def configurar_salario_principal(valor: float):
    try:
        # Tenta encontrar um salário existente para atualizar ou cria um novo
        salario_existente = next(r for r in _receitas if r.descricao == "Salário Principal" and r.recorrente)
        salario_existente.valor = valor # Atualiza o valor
        # Considerar atualizar a data também se necessário, ou manter a original
        print(f"Serviço: Salário principal atualizado. Novo Valor: {valor:.2f}")
    except StopIteration:
        # Se não encontrar, cadastra um novo
        cadastrar_receita(descricao="Salário Principal", valor=valor, data=datetime.now(), recorrente=True)
        # A mensagem de cadastro já é impressa por cadastrar_receita
    pass # Manter o pass aqui não é estritamente necessário, mas não prejudica

def adicionar_renda_adicional(descricao: str, valor: float, data: datetime) -> Receita:
    # A função cadastrar_receita já imprime a mensagem e retorna o objeto
    return cadastrar_receita(descricao=descricao, valor=valor, data=data, recorrente=False)

def editar_valor_salario(novo_valor: float):
    configurar_salario_principal(novo_valor) # Reutiliza a lógica
    pass

# RF003 - Categorização de Despesas (Serviços relacionados à gestão de categorias)
def criar_categoria_despesa(nome: str):
    # Lógica para criar uma nova categoria de despesa
    # No futuro: criar objeto CategoriaDespesa e adicionar a uma lista _categorias_despesa_obj
    # e atualizar o dicionário _categorias_despesa
    print(f"Serviço: Criando categoria de despesa '{nome}' (não implementado completamente)")
    pass

def listar_categorias_despesa() -> Dict[str, str]:
    print(f"Serviço: Listando categorias de despesa (simulado)")
    return _categorias_despesa

# RF004 - Métodos de Pagamento
def adicionar_metodo_pagamento(nome: str):
    # Lógica para adicionar um novo método de pagamento
    # Similar à criação de categoria
    print(f"Serviço: Adicionando método de pagamento '{nome}' (não implementado completamente)")
    pass

def listar_metodos_pagamento() -> Dict[str, str]:
    print(f"Serviço: Listando métodos de pagamento (simulado)")
    return _metodos_pagamento

# RF005 - Gestão de Cartões
def cadastrar_cartao(nome_cartao: str, ultimos_4_digitos: str, limite: float, data_vencimento_fatura: int, bandeira: str = ""):
    # Lógica para cadastrar um novo cartão
    # No futuro: criar objeto Cartao e adicionar a uma lista _cartoes
    print(f"Serviço: Cadastrando cartão '{nome_cartao}' (não implementado)")
    pass

def remover_cartao(cartao_id: str):
    # Lógica para remover um cartão
    print(f"Serviço: Removendo cartão ID '{cartao_id}' (não implementado)")
    pass

def obter_fatura_cartao(cartao_id: str):
    # Lógica para calcular a fatura atual de um cartão
    # Deverá buscar despesas associadas ao cartão
    fatura = 0.0 # Exemplo
    print(f"Serviço: Obtendo fatura do cartão ID '{cartao_id}'. Fatura: {fatura} (não implementado)")
    return fatura
