# Instruções do projeto

Este é um monitor pessoal em fase inicial, com Python 3.11+ e sem dependências externas.

- Antes de editar, confira `git status`, a raiz Git e as instruções aplicáveis.
- Preserve alterações do usuário. Nunca execute reset --hard, clean ou force push sem pedido explícito.
- Teste com `python -m unittest discover -s tests -v`.
- Demonstração: `python -m monitoramento --demo`.
- Não inicie coleta real nem autostart durante setup/testes.
- Use apenas dados fictícios em fixtures, logs de testes e exemplos.
- Mantenha coletores específicos do sistema separados da agregação de dados.
- Nunca adicione históricos reais, bancos locais ou segredos ao Git.
