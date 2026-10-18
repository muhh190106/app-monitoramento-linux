# Guia de desenvolvimento

## Ambiente local

Use Git e Python 3.11+. Crie um ambiente virtual no repositório:

```bash
python -m venv .venv
```

No Linux, use `python3` se `python` não estiver disponível. Nos comandos abaixo, utilize `.venv/bin/python` no Linux ou `.venv\Scripts\python.exe` no Windows:

```bash
python -m unittest discover -s tests -v
python -m activity_monitor --demo
python -m activity_monitor --version
```

Para instalar em modo editável e disponibilizar o comando `activity-monitor`:

```bash
python -m pip install -e .
activity-monitor --demo
```

O núcleo não exige dependências externas de execução. A instalação usa setuptools; o painel opcional depende de pandas, matplotlib e Tk.

## Idiomas do projeto

A documentação de trabalho está em português brasileiro. O [README em inglês](../README.en.md) oferece a apresentação internacional e deve acompanhar alterações no [README principal](../README.md). Código, identificadores, tabelas, campos, endpoints, erros técnicos, saída do terminal, contrato OpenAPI e mensagens de commit permanecem em inglês. A interface mantém português brasileiro e inglês. Discussões e descrições de pull requests podem usar qualquer um dos dois idiomas.

## Trabalhar em vários computadores

Use um clone e um ambiente virtual independentes em cada sistema operacional, inclusive em máquinas com dual boot. Antes de começar, confira `git status`. Com a árvore limpa, atualize com `git pull --ff-only`. Crie uma branch para a tarefa, registre as alterações revisadas e envie ao GitHub antes de trocar de computador.

```bash
git switch -c codex/describe-your-change
git add path/to/changed-file
git commit -m "Describe the change in English"
git push -u origin HEAD
```

Abra um pull request para revisar e integrar. No outro dispositivo, busque as atualizações e selecione a branch. Alterações sem commit e dados locais não são sincronizados pelo GitHub.

## Codex Cloud

O repositório contém um comando reproduzível de configuração:

```bash
bash scripts/setup-cloud.sh
```

Ele cria `.venv`, instala as dependências do painel, executa testes unitários/de gráficos sem janela e roda a demonstração fictícia pelo terminal. Testes de janelas Tk precisam de sessão gráfica e são tratados separadamente na CI. A configuração não exige credenciais, serviços externos ou permissões de monitoramento. Novos ambientes de nuvem podem usar esse comando na instalação e os comandos de teste/demonstração nas verificações iniciais.

Ambientes configurados com `python -m monitoramento --demo` continuam compatíveis. A saída da demonstração usa nomes em inglês, como `Browser`.

O nome do produto é STime NOW. Pacotes e comandos técnicos mantêm os nomes existentes. O painel já inclui mensagens em português/inglês e gráficos de dados fictícios; o agente instalado ainda está planejado.

## Estrutura do repositório

```text
activity_monitor/        Núcleo portável e comandos em inglês
monitoramento/          Entradas de compatibilidade
tests/                  Testes com dados fictícios
scripts/                Configuração da nuvem
docs/                   Requisitos, arquitetura, API, DER e planejamento
docs/contracts/         Contrato OpenAPI em inglês
.github/                Integração contínua e formulários de contribuição
README.md               Apresentação principal em português
README.en.md            Apresentação internacional em inglês
```

## Cuidados com os dados

Mantenha bancos, exportações, registros e credenciais fora do controle de versão. As regras de exclusão ajudam, mas confira `git diff --cached` antes de registrar alterações. Use exemplos fictícios nas issues, testes, documentação e tarefas na nuvem.

## Desenvolvimento do painel

Instale as dependências opcionais com `python -m pip install -e '.[desktop]'` e execute `python -m activity_monitor --desktop`. Acrescente `--language pt-BR` para português ou `--language en` para inglês. A demonstração JSON existente continua sem dependências externas.

`reporting.py` contém intervalos tipados e agregação com pandas; `charts.py` desenha gráficos matplotlib; `desktop.py` contém os componentes Tkinter; `i18n.py` reúne as traduções. Os intervalos fictícios são gerados uma vez na abertura, para a data local atual e os 29 dias anteriores. Os filtros não recriam os dados.

O relatório atual recebe horários locais sem informação de fuso, rejeita sobreposições, recorta limites dos períodos e divide intervalos nas faixas do gráfico. Essa implementação demonstrativa não define o comportamento da coleta real em múltiplos dispositivos ou durante mudanças de horário de verão.

Execute os testes sem janela com as dependências do painel instaladas. Para os testes básicos de interface Tk, defina `STIME_DESKTOP_TESTS=1` em sessão gráfica. No Linux sem tela, use `xvfb-run -a env STIME_DESKTOP_TESTS=1 python -m unittest discover -s tests -v`. No PowerShell, defina `$env:STIME_DESKTOP_TESTS = '1'` antes do comando de testes. A CI verifica os dois modos. Instalações apenas do núcleo pulam os testes que exigem dependências opcionais.

O provedor atual fica em memória: não pede permissões de monitoramento, inspeciona aplicativos, salva atividade nem inicia automaticamente. Datas fora da amostra demonstram o estado sem dados.

## Revisar os contratos de integração

Leia [API](api.md), [modelo de dados](data-model.md) e o próximo incremento do [planejamento](roadmap.md) antes de implementar clientes ou armazenamento. O [documento OpenAPI](contracts/openapi.json) é uma especificação, não uma API em execução.

Revise alterações de esquema junto com o texto e o DER e mantenha os exemplos fictícios consistentes. Mudar a demonstração atual não comprova conformidade com a API.

Para validar o contrato, instale `python -m pip install -e '.[contracts]'` no ambiente virtual e execute `python -m unittest discover -s tests -p test_contract.py -v`. Para verificar apenas o documento, use `python -m openapi_spec_validator docs/contracts/openapi.json`. O extra fixa a versão do validador usada pela equipe e pela CI; ele não faz parte da execução do aplicativo. A validação do esquema não comprova regras entre campos, autorização, prevenção transacional de sobreposição ou agregação; isso exige implementação e testes de integração no próximo incremento.
