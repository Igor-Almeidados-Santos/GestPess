# tests/models/test_configuracoes_usuario.py
import unittest
from models.configuracoes_usuario import ConfiguracoesUsuario, IDIOMAS_SUPORTADOS, TEMAS_SUPORTADOS
from uuid import UUID
from typing import get_args # Para testar valores Literais

class TestConfiguracoesUsuario(unittest.TestCase):
    def test_criar_configuracoes_sucesso(self):
        cfg = ConfiguracoesUsuario(usuario_id="user123", idioma='en-US', tema='escuro')
        self.assertIsNotNone(cfg.id)
        self.assertTrue(isinstance(UUID(cfg.id), UUID))
        self.assertEqual(cfg.usuario_id, "user123")
        self.assertEqual(cfg.idioma, 'en-US')
        self.assertEqual(cfg.tema, 'escuro')

    def test_criar_configuracoes_valores_padrao(self):
        cfg = ConfiguracoesUsuario(usuario_id="user456")
        self.assertEqual(cfg.idioma, 'pt-BR') # Default
        self.assertEqual(cfg.tema, 'claro') # Default

    def test_criar_configuracoes_usuario_id_vazio(self):
        with self.assertRaisesRegex(ValueError, "O ID do usuário é obrigatório para as configurações."):
            ConfiguracoesUsuario(usuario_id="")

    # Testes de validação de Literal são mais efetivos nos serviços que recebem input externo.
    # O modelo em si confia que os tipos corretos são passados, ou usa type hints.
    # Mas podemos testar se ele armazena corretamente.
    def test_armazena_valores_corretos_literal(self):
        idiomas_validos = get_args(IDIOMAS_SUPORTADOS)
        temas_validos = get_args(TEMAS_SUPORTADOS)
        cfg = ConfiguracoesUsuario(usuario_id="test_uid", idioma=idiomas_validos[0], tema=temas_validos[0])
        self.assertEqual(cfg.idioma, idiomas_validos[0])
        self.assertEqual(cfg.tema, temas_validos[0])

    def test_representacao_configuracoes(self):
        cfg_id = "test-uuid-cfg"
        cfg = ConfiguracoesUsuario(id=cfg_id, usuario_id="uid1", idioma='en-US', tema='escuro')
        expected = f"ConfiguracoesUsuario(id='{cfg_id}', usuario_id='uid1', idioma='en-US', tema='escuro')"
        self.assertEqual(repr(cfg), expected)
