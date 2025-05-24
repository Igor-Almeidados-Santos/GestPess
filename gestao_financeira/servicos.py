# gestao_financeira/servicos.py
from datetime import datetime
# from models.receita import Receita # Supondo que os modelos estão acessíveis
# from models.despesa import Despesa
# from models.cartao import Cartao

# RF001 - Controle de Receitas e Despesas
def cadastrar_receita(descricao: str, valor: float, data: datetime, recorrente: bool = False):
    # Lógica para criar e armazenar uma nova receita
    # Deverá interagir com alguma forma de persistência de dados
    print(f"Serviço: Cadastrando receita '{descricao}', Valor: {valor}")
    pass

def cadastrar_despesa(descricao: str, valor: float, data: datetime, categoria_id: str, metodo_pagamento_id: str, cartao_id: str = None, observacoes: str = ""):
    # Lógica para criar e armazenar uma nova despesa
    # Deverá interagir com alguma forma de persistência de dados
    print(f"Serviço: Cadastrando despesa '{descricao}', Valor: {valor}, Categoria: {categoria_id}")
    pass

def obter_saldo_atual():
    # Lógica para calcular o saldo (Receitas Totais - Despesas Totais)
    # Deverá buscar dados de receitas e despesas
    saldo = 0.0 # Exemplo
    print(f"Serviço: Obtendo saldo atual. Saldo: {saldo}")
    return saldo

# RF002 - Gestão de Salário e Rendas
def configurar_salario_principal(valor: float):
    # Lógica para definir ou atualizar o salário principal
    # Pode ser uma forma específica de receita recorrente
    print(f"Serviço: Configurando salário principal. Valor: {valor}")
    pass

def adicionar_renda_adicional(descricao: str, valor: float, data: datetime):
    # Similar a cadastrar_receita, mas pode ter tratamento específico
    print(f"Serviço: Adicionando renda adicional '{descricao}', Valor: {valor}")
    pass

def editar_valor_salario(novo_valor: float):
    # Lógica para editar o valor do salário principal existente
    print(f"Serviço: Editando valor do salário para {novo_valor}")
    pass

# RF003 - Categorização de Despesas (Serviços relacionados à gestão de categorias)
def criar_categoria_despesa(nome: str):
    # Lógica para criar uma nova categoria de despesa
    print(f"Serviço: Criando categoria de despesa '{nome}'")
    pass

def listar_categorias_despesa():
    # Lógica para listar todas as categorias de despesa
    print(f"Serviço: Listando categorias de despesa")
    return []

# RF004 - Métodos de Pagamento (Serviços relacionados à gestão de métodos de pagamento)
def adicionar_metodo_pagamento(nome: str):
    # Lógica para adicionar um novo método de pagamento
    print(f"Serviço: Adicionando método de pagamento '{nome}'")
    pass

# RF005 - Gestão de Cartões
def cadastrar_cartao(nome_cartao: str, ultimos_4_digitos: str, limite: float, data_vencimento_fatura: int, bandeira: str = ""):
    # Lógica para cadastrar um novo cartão
    print(f"Serviço: Cadastrando cartão '{nome_cartao}'")
    pass

def remover_cartao(cartao_id: str):
    # Lógica para remover um cartão
    print(f"Serviço: Removendo cartão ID '{cartao_id}'")
    pass

def obter_fatura_cartao(cartao_id: str):
    # Lógica para calcular a fatura atual de um cartão
    # Deverá buscar despesas associadas ao cartão
    fatura = 0.0 # Exemplo
    print(f"Serviço: Obtendo fatura do cartão ID '{cartao_id}'. Fatura: {fatura}")
    return fatura
