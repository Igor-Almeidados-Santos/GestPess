# models/configuracoes_usuario.py
from uuid import uuid4
from typing import Literal, Optional # Adicionado Optional

IDIOMAS_SUPORTADOS = Literal['pt-BR', 'en-US'] # Exemplo
TEMAS_SUPORTADOS = Literal['claro', 'escuro']

class ConfiguracoesUsuario:
    def __init__(self, usuario_id: str, 
                 idioma: IDIOMAS_SUPORTADOS = 'pt-BR', 
                 tema: TEMAS_SUPORTADOS = 'claro', 
                 id: Optional[str] = None): # id deve ser Optional
        
        if not usuario_id:
            raise ValueError("O ID do usuário é obrigatório para as configurações.")
        
        # Validação dos tipos literais (Python não força isso em runtime sem bibliotecas extras como Pydantic)
        # Para checagem manual, se necessário (ex: em um setter ou validação de serviço):
        # from typing import get_args # Mova esta importação para o topo do arquivo se usar os métodos de classe abaixo
        # if idioma not in get_args(IDIOMAS_SUPORTADOS):
        #     raise ValueError(f"Idioma '{idioma}' não suportado. Suportados: {get_args(IDIOMAS_SUPORTADOS)}")
        # if tema not in get_args(TEMAS_SUPORTADOS):
        #     raise ValueError(f"Tema '{tema}' não suportado. Suportados: {get_args(TEMAS_SUPORTADOS)}")

        self.id = id if id else str(uuid4())
        self.usuario_id = usuario_id
        self.idioma = idioma
        self.tema = tema

    def __repr__(self):
        return f"ConfiguracoesUsuario(id='{self.id}', usuario_id='{self.usuario_id}', idioma='{self.idioma}', tema='{self.tema}')"

    # Exemplo de como obter os valores literais em runtime (se get_args for importado no topo)
    # from typing import get_args
    # @classmethod
    # def get_idiomas_suportados(cls):
    #     return get_args(IDIOMAS_SUPORTADOS)
    # @classmethod
    # def get_temas_suportados(cls):
    #     return get_args(TEMAS_SUPORTADOS)
