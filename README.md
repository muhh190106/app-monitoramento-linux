# app-monitoramento-linux

Base de desenvolvimento de um monitor pessoal inspirado na arquitetura do ActivityWatch. Código original; não é um fork. Esta primeira etapa valida o ambiente com dados fictícios, sem coletar atividade real.

## Executar

Requer Python 3.11 ou superior e Git. Não há dependências externas nesta base.

Windows:
```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
.\.venv\Scripts\python.exe -m monitoramento --demo
```

CachyOS/Linux:
```bash
python3 -m venv .venv
.venv/bin/python -m unittest discover -s tests -v
.venv/bin/python -m monitoramento --demo
```

A demonstração resume eventos fictícios em memória. Nenhum histórico real é lido ou salvo.

## Papel de cada ambiente

- GitHub guarda código e histórico de alterações.
- PC e notebook têm clones separados e ambientes virtuais próprios.
- Codex Cloud executa tarefas e testes sobre o código publicado.
- A coleta de janelas e inatividade será executada nativamente em cada computador; testes na nuvem usam eventos fictícios.

## Fluxo entre computadores

Clone o repositório privado em uma pasta nova em cada sistema, depois execute o setup acima. Não compartilhe a mesma pasta `.venv` entre Windows e Linux.

Antes de trabalhar: `git status` e, estando sem alterações, `git pull --ff-only`.
Crie uma branch por tarefa: `git switch -c codex/nome-da-tarefa`.
Revise os arquivos, faça commit e `git push -u origin HEAD`.
Use pull requests para integrar na main. No outro computador, obtenha a branch com `git fetch origin` e selecione-a. Alterações sem commit/push não são sincronizadas.
Se houver alterações locais, preserve-as em um commit antes de mudar de branch; não use reset ou limpeza destrutiva.

## Codex Cloud

1. Crie um repositório privado próprio e publique esta base na branch main.
2. Na instalação do GitHub para a conta, permita acesso somente ao novo repositório.
3. Na experiência atual: Work in > Cloud > Select environment > Create environment.
4. Selecione o repositório e deixe o Codex inspecionar o projeto.
5. Setup: `bash scripts/setup-cloud.sh`.
6. Testes: `.venv/bin/python -m unittest discover -s tests -v`.
7. Revise os resultados e publique o ambiente. Não há segredos ou serviços externos necessários nesta etapa.

## Próximas etapas

1. Definir métricas: tempo por aplicativo, inatividade e categorias.
2. Adicionar armazenamento SQLite local e política de retenção.
3. Implementar coletores separados para Windows e Linux. Identificar X11/Wayland e o compositor antes de escolher o coletor Linux.
4. Criar um painel local e controles de pausar/excluir dados.
5. Projetar sincronização opcional dos dados separadamente da sincronização do código.

Não versionar históricos reais, títulos de janelas, URLs, bancos locais nem credenciais. O `.gitignore` inclui proteções iniciais; revise sempre o conteúdo de cada commit.

## Referências

- https://github.com/ActivityWatch/activitywatch
- https://learn.chatgpt.com/docs/cloud

O ActivityWatch reúne componentes em submódulos. Esta base evita precisar compilar toda a suíte para começar. Se incorporarmos código dele futuramente, avaliaremos as licenças dos componentes antes da inclusão.
