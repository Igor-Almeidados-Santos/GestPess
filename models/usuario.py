# models/usuario.py
from uuid import uuid4
from typing import Optional

class Usuario:
    def __init__(self, nome: str, email: Optional[str] = None, id: Optional[str] = None):
        if not nome or not nome.strip():
            raise ValueError("O nome do usuário não pode ser vazio.")
        # Validação de email (formato básico) pode ser adicionada se necessário, mas não é crítica agora
        # if email and not ("@" in email and "." in email.split('@')[1]):
        #     raise ValueError("Formato de email inválido.")

        self.id = id if id else str(uuid4())
        self.nome = nome.strip()
        self.email = email.strip() if email else None

    def __repr__(self):
        return f"Usuario(id='{self.id}', nome='{self.nome}', email='{self.email}')"
