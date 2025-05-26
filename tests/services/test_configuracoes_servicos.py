# tests/services/test_configuracoes_servicos.py
import unittest
from core import database
database.DATABASE_NAME = ":memory:" # Configura DB em memória ANTES de outros imports

from configuracoes import servicos as srv_cfg
from models.usuario import Usuario
from models.configuracoes_usuario import ConfiguracoesUsuario, IDIOMAS_SUPORTADOS, TEMAS_SUPORTADOS
from typing import get_args

class TestConfiguracoesServicos(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        database.init_db(db_name=":memory:") # Cria tabelas e dados predefinidos (usuário padrão)

    def setUp(self):
        # Limpa tabelas relevantes e repopula dados predefinidos antes de cada teste
        # para garantir isolamento.
        conn = database.get_db_connection(db_name=":memory:")
        try:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM configuracoes_usuario;")
            # Não deletar o usuário padrão da tabela usuarios, apenas outros que possam ter sido criados.
            # Se um teste deleta o usuário padrão, ele será recriado abaixo.
            cursor.execute("DELETE FROM usuarios WHERE id != ?;", (database.USUARIO_PADRAO_ID,))
            
            # Garante que o usuário padrão exista
            cursor.execute("SELECT id FROM usuarios WHERE id = ?", (database.USUARIO_PADRAO_ID,))
            if not cursor.fetchone():
                cursor.execute("INSERT INTO usuarios (id, nome, email) VALUES (?, ?, ?)", 
                               (database.USUARIO_PADRAO_ID, database.USUARIO_PADRAO_NOME, None))
            
            # Garante que as configurações do usuário padrão existam
            cursor.execute("SELECT id FROM configuracoes_usuario WHERE usuario_id = ?", (database.USUARIO_PADRAO_ID,))
            if not cursor.fetchone():
                 cfg_id_padrao = str(database.uuid4()) # Gerar UUID aqui
                 conn.execute("INSERT INTO configuracoes_usuario (id, usuario_id, idioma, tema) VALUES (?, ?, ?, ?)",
                               (cfg_id_padrao, database.USUARIO_PADRAO_ID, 'pt-BR', 'claro'))
            conn.commit()
        finally:
            conn.close()

    def test_obter_usuario_padrao(self):
        usuario = srv_cfg.obter_usuario_padrao()
        self.assertIsNotNone(usuario)
        self.assertEqual(usuario.id, database.USUARIO_PADRAO_ID)
        self.assertEqual(usuario.nome, database.USUARIO_PADRAO_NOME)

    def test_atualizar_perfil_usuario_padrao_nome(self):
        usuario_padrao = srv_cfg.obter_usuario_padrao()
        novo_nome = "Usuário Padrão Alterado"
        atualizado = srv_cfg.atualizar_perfil_usuario(usuario_padrao.id, nome=novo_nome)
        self.assertIsNotNone(atualizado)
        self.assertEqual(atualizado.nome, novo_nome)
        self.assertEqual(atualizado.email, usuario_padrao.email) # Email não deve mudar
        # Verifica no DB
        usuario_db = srv_cfg.obter_usuario_por_id(usuario_padrao.id)
        self.assertEqual(usuario_db.nome, novo_nome)

    def test_atualizar_perfil_usuario_padrao_email(self):
        usuario_padrao = srv_cfg.obter_usuario_padrao()
        novo_email = "padrao@exemplo.com"
        atualizado = srv_cfg.atualizar_perfil_usuario(usuario_padrao.id, email=novo_email)
        self.assertIsNotNone(atualizado)
        self.assertEqual(atualizado.email, novo_email)
        self.assertEqual(atualizado.nome, usuario_padrao.nome) # Nome não deve mudar
        usuario_db = srv_cfg.obter_usuario_por_id(usuario_padrao.id)
        self.assertEqual(usuario_db.email, novo_email)

    def test_atualizar_perfil_usuario_nome_vazio_erro(self):
        usuario_padrao = srv_cfg.obter_usuario_padrao()
        with self.assertRaises(ValueError): # No modelo Usuario, a validação é "O nome do usuário não pode ser vazio."
            srv_cfg.atualizar_perfil_usuario(usuario_padrao.id, nome="")

    def test_atualizar_perfil_usuario_inexistente(self):
        atualizado = srv_cfg.atualizar_perfil_usuario("id_fake", nome="Nome Fantasma")
        self.assertIsNone(atualizado)

    def test_obter_configuracoes_usuario_padrao(self):
        usuario_padrao = srv_cfg.obter_usuario_padrao()
        configs = srv_cfg.obter_configuracoes_usuario(usuario_padrao.id)
        self.assertIsNotNone(configs)
        self.assertEqual(configs.usuario_id, usuario_padrao.id)
        self.assertEqual(configs.idioma, 'pt-BR') # Default inicial
        self.assertEqual(configs.tema, 'claro')   # Default inicial

    def test_obter_configuracoes_cria_padrao_se_nao_existir_para_usuario_valido(self):
        # Criar um novo usuário sem configs diretamente no DB para simular
        novo_user_id = str(database.uuid4())
        conn = database.get_db_connection(db_name=":memory:")
        try:
            conn.execute("INSERT INTO usuarios (id, nome) VALUES (?, ?)", (novo_user_id, "Usuário Sem Configs"))
            conn.commit()
        finally:
            conn.close()
        
        configs = srv_cfg.obter_configuracoes_usuario(novo_user_id)
        self.assertIsNotNone(configs, "Deveria criar configs padrão para usuário novo sem configs")
        self.assertEqual(configs.usuario_id, novo_user_id)
        self.assertEqual(configs.idioma, 'pt-BR')
        self.assertEqual(configs.tema, 'claro')

    def test_atualizar_configuracoes_usuario_padrao(self):
        usuario_padrao = srv_cfg.obter_usuario_padrao()
        idiomas_validos = get_args(IDIOMAS_SUPORTADOS)
        temas_validos = get_args(TEMAS_SUPORTADOS)
        novo_idioma = idiomas_validos[1] if len(idiomas_validos) > 1 else idiomas_validos[0] # 'en-US'
        novo_tema = temas_validos[1] if len(temas_validos) > 1 else temas_validos[0]       # 'escuro'

        atualizadas = srv_cfg.atualizar_configuracoes_usuario(usuario_padrao.id, idioma=novo_idioma, tema=novo_tema)
        self.assertIsNotNone(atualizadas)
        self.assertEqual(atualizadas.idioma, novo_idioma)
        self.assertEqual(atualizadas.tema, novo_tema)

        # Verifica no DB
        configs_db = srv_cfg.obter_configuracoes_usuario(usuario_padrao.id)
        self.assertEqual(configs_db.idioma, novo_idioma)
        self.assertEqual(configs_db.tema, novo_tema)

    def test_atualizar_configuracoes_idioma_invalido(self):
        usuario_padrao = srv_cfg.obter_usuario_padrao()
        with self.assertRaisesRegex(ValueError, "Idioma 'xx-XX' não é suportado."):
            srv_cfg.atualizar_configuracoes_usuario(usuario_padrao.id, idioma='xx-XX')

    def test_atualizar_configuracoes_tema_invalido(self):
        usuario_padrao = srv_cfg.obter_usuario_padrao()
        with self.assertRaisesRegex(ValueError, "Tema 'vermelho' não é suportado."):
            srv_cfg.atualizar_configuracoes_usuario(usuario_padrao.id, tema='vermelho')

    def test_atualizar_configuracoes_usuario_inexistente(self):
        # A função obter_configuracoes_usuario retorna None se o usuario_id não existe,
        # e atualizar_configuracoes_usuario chama obter_configuracoes_usuario no final.
        # Se o update não afetar linhas (porque usuario_id não existe na tabela de configs),
        # ele tentará obter/criar, mas obter_usuario_por_id falhará para um usuario_id inexistente.
        configs = srv_cfg.atualizar_configuracoes_usuario("id_fake_user", idioma='en-US')
        self.assertIsNone(configs, "Atualizar configs de usuário inexistente deveria retornar None")

if __name__ == '__main__':
    unittest.main()
```
