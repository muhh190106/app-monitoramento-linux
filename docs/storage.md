# Banco de dados local

A primeira entrega da frente 4 implementa SQLite: tabelas do DER, migrações
versionadas, índices, gravação atômica de eventos, consultas de uso e manutenção
do histórico. A biblioteca fica em `activity_monitor/storage/`; os arquivos SQL,
em `activity_monitor/storage/migrations/`.

O painel ainda usa seu provedor fictício em memória. A API e a conexão do painel
ao banco pertencem às próximas entregas. As tabelas de metas, regras, foco, tokens
e idempotência já existem; seus fluxos completos de negócio e autenticação ainda
precisam ser implementados pelo backend. O módulo de banco é uma interface local
confiável, não uma barreira de autenticação para clientes externos.

## Instalação

Na raiz do projeto, use o Python do ambiente virtual:

```powershell
.\.venv\Scripts\python.exe -m pip install -e ".[storage]"
```

No Linux, substitua o executável por `.venv/bin/python`. O extra `storage`
instala os dados de fusos IANA, necessários especialmente no Windows. O módulo
`sqlite3` acompanha o Python; é necessário SQLite 3.37 ou superior.

## Criar uma base de demonstração

Escolha um arquivo separado, fora do repositório. No PowerShell:

```powershell
$demoDb = Join-Path $env:LOCALAPPDATA 'STimeNOW/demo.sqlite3'
.\.venv\Scripts\python.exe -m activity_monitor.storage --database "$demoDb" init
.\.venv\Scripts\python.exe -m activity_monitor.storage --database "$demoDb" seed
.\.venv\Scripts\python.exe -m activity_monitor.storage --database "$demoDb" summary --workspace 00000000-0000-4000-8000-000000000001 --device 00000000-0000-4000-8000-000000000002 --date 2026-10-01
```

No Linux:

```bash
demo_db="${XDG_DATA_HOME:-$HOME/.local/share}/STimeNOW/demo.sqlite3"
.venv/bin/python -m activity_monitor.storage --database "$demo_db" init
.venv/bin/python -m activity_monitor.storage --database "$demo_db" seed
.venv/bin/python -m activity_monitor.storage --database "$demo_db" summary --workspace 00000000-0000-4000-8000-000000000001 --device 00000000-0000-4000-8000-000000000002 --date 2026-10-01
```

Resultado esperado: **120 segundos ativos e 60 inativos**. Acrescente
`--dimension domain` à consulta para obter **60 segundos** de `study.example`.
O outro minuto observado pela extensão coincide com o editor em primeiro plano
e, por isso, não conta como uso do domínio.

Os exemplos têm data fixa em **1º de outubro de 2026**, não acompanham o relógio.
`seed` exige um caminho explícito, recusa bases pessoais e não reseta uma base
demonstrativa já carregada. Repetir o comando informa `created: false`.
Não há credenciais de exemplo nem coleta real nessa carga.

## Operações disponíveis

| Operação | Comportamento |
| --- | --- |
| `init` | Cria a estrutura ou aplica novas migrações sem substituir dados. |
| `seed` | Carrega explicitamente observações e exemplos de meta, regra e foco concluído. |
| `summary` | Consulta dia, semana de calendário ou mês; filtros `--period`, `--timezone` e `--dimension`. |
| `retain --workspace UUID` | Exclui eventos vencidos segundo a retenção do espaço e avança o limite de recebimento. |
| `delete-history --workspace UUID --device UUID --before UTC --confirm` | Exclui intervalos iniciados antes do corte e impede que sejam restaurados por reenvio. |

Sem `--database`, `init` utiliza `%LOCALAPPDATA%/STimeNOW/activity.sqlite3` no
Windows ou `$XDG_DATA_HOME/STimeNOW/activity.sqlite3` no Linux, com alternativa
`~/.local/share/STimeNOW/activity.sqlite3`. O comando `seed` nunca usa esse padrão.
Retenção e exclusão são operações explícitas; ainda não há serviço que as execute
automaticamente. Consultas refletem os dados armazenados até a manutenção.

## Usar na implementação do backend

```python
from datetime import date
from activity_monitor.storage import Database
from activity_monitor.storage.repository import UsageRepository

with Database() as db:
    db.migrate()
    repository = UsageRepository(db)
    workspace_id = repository.create_workspace("Personal workspace", "America/Sao_Paulo")
    device_id = repository.create_device(workspace_id, "Sample PC", "windows")
    report = repository.summary(workspace_id, device_id, date(2026, 10, 1))
```

Esse exemplo cria um novo espaço e dispositivo a cada execução; o backend deve
provisioná-los uma vez e guardar os IDs. `ingest(workspace_id, device_id, source,
events, browser_app_id=...)` recebe os eventos do [contrato](api.md). O backend
deve autenticar o cliente **antes** de chamar esse método e obter o vínculo do
navegador a partir do token, nunca de um campo livre da requisição.

`summary` retorna um dicionário no formato `UsageSummary` do OpenAPI. O cálculo
usa SQL com limites UTC e faixas de calendário no fuso solicitado. Uma transação
de leitura mantém totais, cobertura, ranking e linha do tempo consistentes.
Escritas usam `BEGIN IMMEDIATE`; cada thread/requisição deve ter sua própria
conexão. Erros de validação são `ValueError`; conflitos de restrições SQL usam
`sqlite3.IntegrityError`. A tradução para códigos HTTP fica para o backend.

Também há `revoke_device`, `delete_device`, `delete_history` e `apply_retention`.
Metas, regras e foco têm tabelas e restrições, mas ainda não têm serviço público
de criação/consulta nem cálculo de progresso. Validação de fusos/domínios,
autorização, expiração de foco e exigência de ao menos uma regra por sessão devem
ser respeitadas pelos futuros serviços; não são todas garantidas pelo SQL sozinho.

## Migrações e verificações

`001_schema.sql` cria as entidades. `002_integrity.sql` adiciona índices e
proteções contra sobreposição, alteração de eventos e inconsistências de
plataforma. `schema_migrations` registra versão, nome, checksum e aplicação.
Alterar uma migração já aplicada causa erro: mudanças futuras devem ganhar um
novo arquivo numerado. Falha em uma atualização desfaz a transação. Uma base de
outro aplicativo ou com versão mais nova é recusada, sem substituição.

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -p test_storage.py -v
```

Os testes usam bancos temporários e dados fictícios: atualização de esquema,
reabertura, transações, concorrência, duplicatas, escopo, horários, calendário,
horário de verão, referências, índices, carga de exemplos, retenção e exclusão.
A CI executa essa frente no Windows e Linux. A inclusão dos arquivos SQL no
pacote também é verificada com instalação fora da pasta de código.

Referências de implementação: [sqlite3](https://docs.python.org/3/library/sqlite3.html)
e [zoneinfo](https://docs.python.org/3/library/zoneinfo.html), da documentação Python.
