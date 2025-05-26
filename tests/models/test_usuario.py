# tests/models/test_usuario.py
import unittest
from models.usuario import Usuario
from uuid import UUID

class TestUsuario(unittest.TestCase):
    def test_criar_usuario_sucesso(self):
        usuario = Usuario(nome="Usuário Teste", email="teste@exemplo.com")
        self.assertIsNotNone(usuario.id)
        self.assertTrue(isinstance(UUID(usuario.id), UUID)) # Verifica se ID é UUID válido
        self.assertEqual(usuario.nome, "Usuário Teste")
        self.assertEqual(usuario.email, "teste@exemplo.com")

    def test_criar_usuario_sem_email(self):
        usuario = Usuario(nome="Outro Usuário")
        self.assertEqual(usuario.nome, "Outro Usuário")
        self.assertIsNone(usuario.email)

    def test_criar_usuario_nome_vazio(self):
        with self.assertRaisesRegex(ValueError, "O nome do usuário não pode ser vazio."):
            Usuario(nome="")
        with self.assertRaisesRegex(ValueError, "O nome do usuário não pode ser vazio."):
            Usuario(nome="   ")

    def test_representacao_usuario(self):
        uid = "test-uuid-user"
        usuario = Usuario(id=uid, nome="Rep Test", email="rep@ex.com")
        expected = f"Usuario(id='{uid}', nome='Rep Test', email='rep@ex.com')"
        self.assertEqual(repr(usuario), expected)
