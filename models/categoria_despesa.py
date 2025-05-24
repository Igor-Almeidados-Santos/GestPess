# models/categoria_despesa.py

class CategoriaDespesa:
    def __init__(self, id: str, nome: str, predefinida: bool = False):
        self.id = id
        self.nome = nome
        self.predefinida = predefinida # True para categorias como Alimentação, Transporte, etc.

# Exemplo de uso (opcional, apenas para teste)
# if __name__ == '__main__':
#     cat_alimentacao = CategoriaDespesa(id="cat001", nome="Alimentação", predefinida=True)
#     cat_personalizada = CategoriaDespesa(id="cat002", nome="Viagem Férias")
#     print(f"Categoria: {cat_alimentacao.nome}, Predefinida: {cat_alimentacao.predefinida}")
#     print(f"Categoria: {cat_personalizada.nome}, Predefinida: {cat_personalizada.predefinida}")
