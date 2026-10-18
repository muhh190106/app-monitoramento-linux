# Contribuir com o STime NOW

O projeto está no início do desenvolvimento. Prefira alterações com objetivo claro, fáceis de revisar e de integrar ao trabalho da equipe.

## Antes de começar

Leia os [requisitos](docs/product.md), o [planejamento](docs/roadmap.md) e a [arquitetura](docs/architecture.md). Abra uma issue para discutir funcionalidades maiores ou novas dependências antes de implementá-las. Discussões e descrições de pull requests podem ser feitas em português ou inglês.

## Organização dos idiomas

- Documentação principal, requisitos, arquitetura, DER e planejamento: português brasileiro.
- Apresentação internacional: [README em inglês](README.en.md), alinhado ao [README principal](README.md).
- Código, identificadores, tabelas, campos, endpoints, erros técnicos, saída do terminal e mensagens de commit: inglês.
- Contrato OpenAPI legível por ferramentas: inglês; explicações da API: português.
- Interface: português brasileiro e inglês, com as mesmas funcionalidades nos dois idiomas.

Ao alterar instalação, funcionalidades ou limitações, atualize os dois READMEs. Não traduza comandos, nomes de pacotes ou chaves dos exemplos.

## Fluxo de desenvolvimento

1. Faça um fork se não tiver acesso de escrita e clone o repositório correspondente.
2. Crie um ambiente virtual seguindo o [guia de desenvolvimento](docs/development.md).
3. Crie uma branch, por exemplo `git switch -c codex/improve-summary`.
4. Mantenha o foco da alteração e acrescente testes quando mudar comportamentos.
5. Execute `python -m unittest discover -s tests -v` e `python -m activity_monitor --demo` com o Python do ambiente virtual.
6. Abra um pull request explicando o problema, a alteração e como ela foi verificada.

Preserve o trabalho existente, evite mudanças sem relação com a tarefa e não reescreva o histórico Git compartilhado.

## Dados de teste e privacidade

Use apenas eventos fictícios. Nunca envie exportações de atividade, títulos reais de janelas, histórico de navegação, credenciais ou bancos pessoais. Remova informações sensíveis de relatos e capturas de tela.

## Relatar um problema

Informe sistema operacional, versão do Python, comando utilizado, resultado esperado, resultado obtido e um exemplo mínimo com dados fictícios. Use o formulário de relato de problema. Vulnerabilidades devem seguir o processo privado de [SECURITY.md](SECURITY.md).

## Trabalho em equipe

Mantenha o respeito, dê sugestões que possam ser colocadas em prática e explique as decisões técnicas. Avalie o trabalho, não a pessoa, e mantenha as discussões relacionadas ao projeto.
