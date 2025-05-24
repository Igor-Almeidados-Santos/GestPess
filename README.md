# GestPess - Sistema de Gestão Pessoal e Financeira

## Visão Geral

GestPess é um aplicativo móvel multiplataforma projetado para auxiliar na gestão financeira pessoal e na organização de tarefas pessoais. O objetivo é fornecer uma ferramenta intuitiva e completa para que os usuários possam controlar suas finanças, gerenciar seus cartões, organizar suas atividades diárias e obter insights sobre seus hábitos de consumo e produtividade.

## Estrutura do Projeto (Inicial)

A estrutura de diretórios inicial do projeto está organizada da seguinte forma:

-   **/app.py**: Ponto de entrada principal da aplicação.
-   **/assets/**: Para armazenar ativos estáticos como imagens, fontes, etc. (ainda não populado).
-   **/configuracoes/**: Módulo para configurações da conta do usuário, preferências, temas, etc. (esboço).
-   **/core/**: Para lógica de negócios central, entidades principais e serviços compartilhados (esboço).
-   **/gestao_financeira/**: Módulo dedicado à gestão de receitas, despesas, salários, cartões e métodos de pagamento.
    -   `servicos.py`: Esboço dos serviços financeiros.
-   **/gestao_pessoal/**: Módulo para gestão de tarefas pessoais, calendário e outras funcionalidades de organização pessoal.
    -   `servicos.py`: Esboço dos serviços de gestão pessoal.
-   **/models/**: Contém as definições dos modelos de dados da aplicação (Receita, Despesa, Tarefa, Cartao, etc.).
    -   `cartao.py`
    -   `categoria_despesa.py`
    -   `despesa.py`
    -   `metodo_pagamento.py`
    -   `receita.py`
    -   `tarefa.py`
-   **/relatorios/**: Módulo para geração de relatórios financeiros, análise de tendências e estatísticas.
    -   `servicos.py`: Esboço dos serviços de relatórios.
-   **/ui/**: Para componentes de interface do usuário (ainda não populado).
-   **/utils/**: Para funções utilitárias e helpers (ainda não populado).
-   **/.gitattributes**: Arquivo de configuração do Git.
-   **/README.md**: Este arquivo.

## Próximos Passos

Os próximos passos no desenvolvimento incluirão:
1.  Definição detalhada das classes de modelo.
2.  Implementação da lógica de negócios nos serviços de cada módulo.
3.  Desenvolvimento da interface do usuário.
4.  Configuração de um banco de dados ou mecanismo de persistência.
5.  Criação de testes unitários e de integração.

---

*Este é um projeto em desenvolvimento.*
