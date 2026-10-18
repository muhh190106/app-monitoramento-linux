# Contrato da API

Estado: especificação de integração v1. Ainda não existe servidor HTTP nem cliente implementado. O contrato legível por ferramentas está no [OpenAPI](contracts/openapi.json); armazenamento e relacionamentos estão no [modelo de dados](data-model.md).

## Escopo e responsabilidades

A primeira integração terá um backend local por espaço pessoal (`workspace`), com SQLite fora do repositório. Painel, coletor e extensão usam a mesma API; nenhum acessa o banco diretamente. Essa é uma configuração de desenvolvimento, não um serviço hospedado para famílias/equipes. Hospedagem, cadastro de contas e compartilhamento por perfil exigem revisão do contrato antes da disponibilização.

Todas as rotas usam `/api/v1`. Campos JSON e mensagens técnicas de erro ficam em inglês. O contrato segue [OpenAPI 3.1](https://spec.openapis.org/oas/v3.1.0.html).

| Frente | Responsabilidade |
| --- | --- |
| Agente desktop | Observar intervalos autorizados de uso/inatividade; manter fila e IDs estáveis nos reenvios; informar recursos não suportados. |
| Extensão e foco | Observar domínios ativos; enviar intervalos separados do navegador; aplicar regras suportadas com tratamento visível de permissões e estado. |
| Backend | Autenticar clientes, validar eventos, resolver conflitos, agregar uso e controlar autorização e ciclo das sessões de foco. |
| Banco | Garantir identidades, referências e unicidade; persistir transações; fornecer consultas indexadas e migrações. |
| Painel e qualidade | Consumir respostas da API, apresentar gráficos, tratar erros/ausência de dados e manter verificações entre os módulos. |

## Identidade e transporte

- Cada instalação local tem um UUID de espaço pessoal e UUIDs de dispositivos cadastrados. O espaço pertence a um único usuário local; não representa família ou equipe.
- O dispositivo deve ser vinculado explicitamente na configuração local antes do envio. Seu ID é emitido pelo servidor. Reinstalação ou revogação invalida seus tokens.
- Toda requisição exige token `Bearer`. O backend guarda apenas o hash do token. Tokens do agente/extensão ficam restritos ao respectivo dispositivo e origem, ao envio de eventos e à consulta da política de foco vigente. Tokens da interface consultam o espaço e administram suas metas, sessões e regras. O backend determina o espaço autorizado pelo token, nunca por um ID de proprietário enviado pelo cliente.
- Este contrato não expõe rotas de vínculo/emissão de tokens. O próximo incremento deve oferecer um comando local explícito de provisionamento antes de executar o fluxo. Não distribuir token compartilhado nem colocar credenciais nos exemplos ou no Git.
- No desenvolvimento, limitar o serviço ao endereço local (`loopback`). HTTP só é permitido nesse endereço para desenvolvimento isolado; tráfego externo exige HTTPS. Produção deve atender a `RNF-3`. CORS permite apenas origens explícitas da extensão, nunca `*` com credenciais. CORS e endereço local não substituem validação do token.

## Eventos de uso

`POST /api/v1/events/batch` recebe de 1 a 500 intervalos encerrados de um dispositivo e uma origem (`desktop` ou `browser`). O corpo tem limite de 1 MiB. São observações brutas, não totais agregados.

| Campo | Significado |
| --- | --- |
| `event_id` | UUID gerado pelo cliente e preservado nos reenvios. |
| `started_at`, `ended_at` | Horários UTC RFC 3339 terminados em `Z`, com segundos inteiros ou precisão de milissegundos; intervalo `[início, fim)`. |
| `state` | `active` ou `idle`. Eventos do navegador sempre são `active`; o desktop detecta inatividade. |
| `app_id`, `app_name` | Chave estável do aplicativo na plataforma e nome exibido; obrigatórios para desktop ativo e ausentes em inatividade. |
| `domain` | Obrigatório apenas para navegador: nome de domínio ASCII em minúsculas, sem protocolo, porta, caminho, consulta, fragmento ou ponto final. |

Chaves de aplicativo incluem a plataforma, como `windows:sample-editor.exe` ou `linux:org.example.SampleEditor`. Não enviar caminhos de executáveis, linhas de comando, títulos de janelas/páginas, URLs, teclas ou conteúdo do navegador. Converter domínios internacionalizados para ASCII antes do envio. A correspondência de domínio é exata; subdomínios são valores distintos na v1.

```json
{
  "device_id": "00000000-0000-4000-8000-000000000001",
  "source": "desktop",
  "events": [{
    "event_id": "00000000-0000-4000-8000-000000000002",
    "started_at": "2026-10-01T12:00:00Z",
    "ended_at": "2026-10-01T12:01:00Z",
    "state": "active",
    "app_id": "windows:sample-editor.exe",
    "app_name": "Sample Editor"
  }]
}
```

Validação e reenvio:

- Exigir início anterior ao fim, duração máxima de 60 segundos e fim no máximo cinco minutos à frente do UTC do servidor. Dividir observações longas. Rejeitar horários sem fuso, campos desconhecidos, dispositivos desconhecidos/revogados e tokens de origem incompatível.
- Começar com retenção configurável de 90 dias. Rejeitar eventos mais antigos com `outside_retention`; filas não podem recriar histórico excluído. Registrar o horário de recebimento separadamente do horário observado. Respeitar também o limite `ingestion_not_before` do dispositivo descrito no modelo de dados.
- Intervalos não podem se sobrepor em `(device_id, source)`, inclusive dentro do lote. Limites que apenas se encostam são permitidos. Comparar com registros persistidos dentro de uma transação. Rejeitar conflitos sem recortar, somar ou decidir pela ordem de chegada silenciosamente.
- `event_id` é único por dispositivo. Reenvio idêntico é sucesso duplicado; reutilizar o ID com conteúdo normalizado diferente gera `409 event_conflict`.
- Dentro do lote, IDs repetidos geram `422 duplicate_batch_id`, mesmo com conteúdo idêntico. As listas de confirmação contêm IDs únicos e não compartilham IDs entre si.
- O lote é atômico: validar tudo antes de gravar. A resposta `200` contém `accepted_event_ids` e `duplicate_event_ids`. Uma falha não grava nada, incluindo novos eventos enviados junto de um conflito. Serializar escritas conflitantes para que requisições simultâneas não contornem a validação de sobreposição.
- Após falha de rede ou `429`/`503`, reenviar os mesmos IDs com espera exponencial limitada e respeito a `Retry-After`. Não repetir erros de validação indiscriminadamente. Filas offline ficam locais, fora do Git, e limitadas pela retenção.

## Consultas do painel

`GET /api/v1/usage/summary` retorna totais, faixas da linha do tempo e ranking em uma resposta. São obrigatórios `device_id`, `date` (`YYYY-MM-DD`), `period` (`day`, `week`, `month`) e `timezone` (identificador IANA). `dimension=application|domain` é opcional e assume `application`.

- Dia é a data selecionada; semana vai de segunda a domingo e contém essa data; mês é o mês dessa data. Não são janelas móveis de 7/30 dias.
- Resolver os limites no fuso solicitado e convertê-los para UTC. Recortar intervalos em `[início, fim)` e dividi-los nas faixas do gráfico. Dias com mudança de horário podem ter 23 ou 25 horas. Emitir faixas vazias com valores zero.
- Relatórios diários têm faixas por hora; semanais/mensais, por dia. Cada faixa expõe `started_at` e `ended_at` em UTC. O painel localiza os rótulos, inclusive horas repetidas. Totais e durações são segundos, não minutos arredondados.
- Uso de aplicativos e inatividade vêm apenas de eventos desktop. Uso por domínio cruza eventos do navegador com intervalos desktop ativos do mesmo dispositivo. Sem contexto desktop, não se soma tempo ao domínio. Navegador é um detalhamento do uso desktop e nunca é somado ao total. Não inferir correlação entre aplicativo e navegador além dessa interseção na v1; lacunas de observação continuam sendo lacunas.
- Relatórios por domínio têm `idle_seconds=0`; o total ativo corresponde ao tempo de domínio observado e cruzado. `share` é a fração do total ativo da dimensão escolhida. Total zero produz ranking vazio.
- Ordenar por segundos em ordem decrescente e, nos empates, chave do recurso em ordem crescente. Não somar dispositivos na v1: uso simultâneo exige uma política futura específica.
- `coverage.desktop_seconds` indica tempo desktop observado, ativo mais inativo. `coverage.browser_seconds` indica tempo de domínio cruzado com uso desktop ativo. Cobertura zero significa ausência de observações, não ausência real de uso. As coberturas podem diferir por origem.
- Sem dados, retornar `200`, totais zero, ranking vazio e todas as faixas do período com valores zero. Datas/fusos inválidos retornam `422`.

A demonstração existente usa horários locais sem fuso e filtros móveis de 1/7/30 dias. Ela permanece assim até a troca do provedor por um adaptador de API. Não remover informação de fuso para alimentar eventos reais no relatório antigo. A nova agregação pertence ao backend; a interface não deve recalculá-la.

## Metas, foco e regras

Estas rotas reservam a comunicação para incrementos futuros. Não são critérios de conclusão da primeira entrega de recebimento e consulta de uso.

| Método e rota | Contrato |
| --- | --- |
| `GET /goals?device_id=…` | Listar metas com progresso calculado pelo servidor para o período atual no fuso de cada meta. |
| `POST /goals` | Criar um limite indicativo de tempo ativo por dia/semana/mês, para todos os aplicativos ou um aplicativo/domínio exato. Metas informam, não bloqueiam. |
| `DELETE /goals/{goal_id}` | Excluir meta do espaço autorizado; retornar `204`. |
| `GET /focus-sessions?device_id=…` | A interface lista sessões ativas e históricas, das mais recentes às mais antigas. Tokens de dispositivo leem somente a própria sessão ativa e a cópia imutável de suas regras. |
| `POST /focus-sessions` | Iniciar agora uma sessão por dispositivo, com duração de 60 a 14400 segundos e IDs de regras selecionadas. Copiar as regras e retornar `201`. |
| `POST /focus-sessions/{focus_id}/cancel` | Cancelar e retornar a sessão; repetir o cancelamento é seguro. |
| `GET /rules?device_id=…` | A interface lista regras do dispositivo; indisponível para tokens do agente/extensão. |
| `POST /rules` | Criar regra exata de aplicativo/domínio: `block` ou `allow`. |
| `DELETE /rules/{rule_id}` | Excluir regra sem modificar as cópias de sessões existentes. |

As rotas da tabela são relativas a `/api/v1`. Listagens usam `limit` (1–100, padrão 50) e `cursor` opaco. Respostas têm `items` e `next_cursor` (`null` ao terminar). Cursor e ordenação permanecem estáveis diante de inserções concorrentes; cursor inválido gera `422`. Metas, regras e sessões são ordenadas por data de criação e ID, em ordem decrescente.

Permitir apenas uma sessão de foco ativa por dispositivo (`409 focus_conflict`). Todas as regras selecionadas devem pertencer ao mesmo dispositivo autorizado; regras inexistentes ou fora do escopo geram `404`; IDs repetidos geram `422`.

Estados: `active -> completed` ao expirar ou `active -> cancelled` por ação explícita. Estados finais nunca retornam a ativo. Verificar expiração nas consultas e na reconciliação em segundo plano, inclusive após reinício. Cancelar uma sessão já concluída apenas a retorna sem alteração. O backend fornece início/fim em UTC; clientes devem desfazer as restrições autorizadas ao expirar, mesmo offline. Uma sessão no backend não comprova que o bloqueio funcionou.

Regras usam correspondência exata, sem curingas. Permissão explícita prevalece sobre bloqueio do mesmo alvo na política pessoal; sem regra, o uso é permitido. Aplicativos e domínios têm capacidades distintas: a extensão não bloqueia aplicativos e permitir um domínio não libera um navegador bloqueado como aplicativo. Informar alvos não suportados antes de iniciar. A precedência familiar/de equipe está fora da v1 e não deve herdar implicitamente essa regra pessoal. O protótipo atual não altera hosts/firewall nem suspende processos.

Criar metas/regras/sessões exige `Idempotency-Key` (UUID), com escopo de espaço pessoal e rota. Salvar hash da requisição e resposta atomicamente por 24 horas. Reenvios iguais retornam a resposta original; conteúdo diferente com a mesma chave gera `409`. Após expirar a chave, o cliente deve consultar o estado antes de tentar novamente automaticamente.

## Erros e aceitação

Formato: `{"error":{"code":"invalid_event","message":"Invalid interval","field":"events[0].ended_at"}}`. `field` pode ser `null`. Não repetir tokens nem conteúdo privado de eventos nos erros ou registros.

Usar `401` para token ausente/inválido; `403` para origem/capacidade proibida; `404` para recurso ausente ou fora do espaço; `409` para conflitos; `413` para corpo excessivo; `422` para campos inválidos; `429` para limitação de requisições; `503` para indisponibilidade temporária. A interface pode traduzir mensagens usando os códigos estáveis.

O primeiro incremento integrado deve demonstrar envio fictício, reenvio duplicado, rejeição atômica de sobreposição, persistência após reinício, relatórios com fuso, estado sem dados e consumo da API pelo painel. Deve testar isolamento de origem/dispositivo, cruzamento navegador/desktop sem duplicar tempo, limites de meia-noite UTC e horário de verão, exclusão e retenção.
