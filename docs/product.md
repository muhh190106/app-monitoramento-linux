# Especificação do produto

STime NOW é um aplicativo desktop de gestão do tempo de tela para uso pessoal, famílias e equipes de trabalho. Combina acompanhamento de uso, sessões de foco e acesso aos dados conforme o perfil.

Esta especificação resume os requisitos da Sprint 2 e mantém os identificadores das histórias para rastreabilidade. O escopo abaixo descreve o produto planejado. O incremento atual implementa o painel de visitante, mensagens em português/inglês e gráficos com pandas/matplotlib sobre dados fictícios. A camada SQLite também está implementada separadamente, com persistência e consultas. Integração do painel com o banco, monitoramento real, suspensão, contas e fluxos de famílias/equipes ainda estão planejados.

## Perfis de usuário

| Perfil | Acesso | Funcionalidades previstas |
| --- | --- | --- |
| Visitante (`V`) | Sem conta | Consultar o próprio uso e configurar sessões de foco. |
| Pai, mãe ou responsável (`PR`) | Usuário e senha | Administrar a família, definir limites dos filhos, consultar uso e decidir pedidos de acesso. |
| Filho (`F`) | Ingresso por código familiar; sem login com usuário/senha | Consultar uso próprio, tempo restante, restrições e conquistas; pedir acesso temporário. |
| Gestor (`GR`) | Usuário e senha | Administrar equipe, consultar uso individual/agregado, classificar aplicativos e acompanhar relatórios. |
| Colaborador (`CB`) | Conta autenticada e código de equipe | Consultar uso próprio e justificar atividades incluídas nos relatórios diários. |

Quem tiver mais de um perfil deve poder selecionar o perfil autorizado. Colaboradores acessam apenas seus próprios dados; gestores, a equipe administrada; responsáveis, os filhos vinculados. Filhos não podem alterar limites ou políticas do responsável.

## Requisitos funcionais

### Uso pessoal e foco

`V.01` oferece gráficos interativos, ícones e totais por aplicativo e filtros como dia, semana e mês. Ausência de dados e falta de permissão de monitoramento devem ter mensagens claras. Um gráfico de uso é gerado ao final de cada sessão (`RNG-4`).

`V.02` permite escolher aplicativos e uma duração de foco. Após obter permissão e confirmação, os aplicativos selecionados são suspensos ou restringidos pelo período e restaurados automaticamente ao término. Permissão negada e seleção vazia devem ser tratadas explicitamente.

### Contas e acesso

`U.01` solicita nome completo, e-mail, usuário, senha e perfil de responsável ou gestor. E-mail e usuário devem ser únicos; o cadastro bem-sucedido leva ao login. `U.02` autentica credenciais, trata tentativas inválidas e direciona ao perfil autorizado selecionado.

### Famílias

- `PR.01` / `F.01`: gerar e renovar um código familiar único; validá-lo antes de vincular um filho. Cada filho pertence a uma única família por vez. O responsável vê a atualização dos membros imediatamente e confirma a remoção. Códigos inválidos, expirados ou revogados não criam vínculo.
- `PR.02`: definir limites diários por filho, aplicativos a limitar/suspender e horários opcionais. Aplicar restrições quando o limite for alcançado. Registrar autor e horário de cada alteração de política.
- `PR.03` / `F.02`: apresentar o painel do perfil, filtros por período, regras ativas, tempo diário restante e aviso quando o limite estiver próximo. Filhos apenas consultam as políticas.
- `F.03`: permitir um pedido pendente por aplicativo restrito, com motivo e duração solicitada. O aplicativo continua bloqueado até a decisão. A aprovação libera acesso temporário; o término restaura a restrição. O tempo da exceção aprovada não consome o limite diário global.
- `F.04`: mostrar sequências de dias, horas de foco concluídas e comparação entre limites e uso real. Filhos não podem editar ou zerar essas métricas.

### Equipes

- `GR.01` / `CB.01`: criar equipes nomeadas e códigos renováveis. Um colaborador autenticado pode participar de apenas uma equipe ativa e deve aparecer imediatamente na lista do gestor. Códigos inválidos são rejeitados. Remoção e saída voluntária exigem confirmação.
- `GR.02` / `CB.02`: permitir ao gestor alternar entre totais individuais e da equipe e filtrar períodos. Colaboradores consultam seu uso e as categorias definidas pelo gestor. Resultados vazios têm explicação clara.
- `GR.04`: fornecer categorias padrão editáveis, como Produtivo, Comunicação e Lazer/Distração. Aplicar a classificação atual aos gráficos e relatórios, inclusive históricos, conforme `UC-11`.
- `GR.05`: criar subgrupos ou projetos, associar colaboradores e filtrar painéis por subgrupo. Excluir um subgrupo preserva a participação na equipe e o histórico individual.
- `GR.03` / `CB.03`: disponibilizar relatórios diários ao gestor ao final do turno ou sessão, com tempo ativo, distribuição por categoria e justificativas enviadas. Justificativas podem ser enviadas antes do fechamento e tornam-se imutáveis após confirmação. Relatórios têm filtros por data e colaborador.

## Requisitos de qualidade e plataforma

| ID | Requisito |
| --- | --- |
| `RNF-1` | Aplicação desktop. Windows e Linux são as plataformas-alvo do repositório. |
| `RNF-2` | Gráficos Python com pandas e matplotlib. Essas dependências pertencem ao painel opcional; a demonstração simples pelo terminal não precisa delas. |
| `RNF-3` | HTTPS na comunicação de rede. |
| `RNF-4` | Layout adaptável a diferentes tamanhos de tela. |
| `RNF-5` | Acessibilidade orientada pelas WCAG; versão e nível de conformidade ainda precisam ser definidos. |
| `RNF-6` | Interface em pelo menos português e inglês. |
| `RNF-7` | Agente instalado para monitoramento e suspensão de aplicativos, integrado ao backend. |

`RNG-1` exige telas e autorização por perfil. `RNG-2` exige tratamento amigável de conflitos de cadastro, acesso negado e falhas técnicas, com registros de diagnóstico. Esses registros não podem expor senhas ou atividade privada bruta. `RNG-3` exige dados de exemplo no banco para as histórias implementadas; os exemplos de desenvolvimento devem ser fictícios.

## Prioridades de entrega

| Prioridade | Histórias |
| --- | --- |
| Alta | `V.01`, `V.02`, `U.01`, `U.02`, `PR.01`, `F.01`, `PR.02` |
| Média | `PR.03`, `F.02`, `F.03`, `GR.01`, `CB.01`, `GR.02`, `GR.04`, `CB.02`, `CB.03` |
| Baixa | `GR.03`, `F.04` |

A tabela original agrupa subgrupos em `GR.04`, mas a história detalhada é `GR.05`. O planejamento mantém subgrupos junto da categorização; a prioridade própria ainda precisa de confirmação. Justificativas (`CB.03`) dependem do ciclo de relatórios, mesmo que a entrega automática (`GR.03`) tenha prioridade menor.

## Decisões pendentes antes da implementação

- **Cadastro de colaboradores:** eles devem se autenticar, mas a história de cadastro só oferece responsável e gestor. Definir convite e criação de conta.
- **Identidade de contas e dispositivos:** definir atribuição de múltiplos perfis e identificação persistente de filhos sem credenciais, incluindo desvinculação e troca de dispositivo.
- **Aplicação das restrições:** especificar sessões Windows/Linux suportadas, permissões, suspensão/restauração segura e convivência entre políticas familiares e foco pessoal.
- **Limites dos serviços:** a primeira integração escolhe Tkinter, backend local, SQLite e tokens locais com escopo; veja [API](api.md) e [modelo de dados](data-model.md). São decisões de implementação, não exigências da Sprint 2. Hospedagem, confiança entre usuários e compartilhamento familiar/de equipe continuam pendentes.

## Mapa de casos de uso

`UC-01` painel de uso; `UC-02` suspensão para foco; `UC-03` cadastro; `UC-04` login; `UC-05` gestão familiar; `UC-06` limites e políticas; `UC-07` uso do filho; `UC-08` ingresso familiar; `UC-09` gestão de equipe; `UC-10` visão da equipe; `UC-11` categorias e subgrupos; `UC-12` relatórios diários; `UC-13` acesso temporário; `UC-14` ingresso na equipe.
