# Planejamento incremental

## Objetivo de curto prazo

Entregar uma experiência de visitante utilizável no Windows: abrir o painel, consultar o uso ao longo do tempo e, em uma etapa posterior, controlar início e interrupção da coleta. Cada incremento deve ser executável e verificável antes da expansão para famílias ou equipes.

| Incremento | Resultado | Critérios de conclusão |
| --- | --- | --- |
| **1 · Painel demonstrativo** | Interface de visitante com dados fictícios. | Abrir no Windows/Linux; alternar português/inglês; filtrar aplicativo, data final e períodos de 1/7/30 dias; apresentar gráficos, totais e estados vazios corretos. |
| **2 · Fluxo integrado com dados fictícios** | Enviar eventos pela API, persistir no banco e mostrar no painel. | Provisionamento de clientes com acesso restrito; validação e deduplicação; migrações SQLite; consultas com calendário/fuso; painel conectado à API; testes de reinício, exclusão, retenção e isolamento. |
| **3 · Coleta no Windows** | Capturar aplicativo em primeiro plano e inatividade após ativação explícita. | Iniciar/pausar/parar; não coletar antes da ativação; persistir sem duplicar/sobrepor tempo; exibir estado e verificar integração com o sistema. |
| **4 · Sessões de foco** | Restringir aplicativos selecionados por um período (`V.02`). | Verificar permissões, confirmar a ação, restaurar com segurança ao expirar/falhar e testar nas sessões Windows suportadas. |
| **5 · Contas e famílias** | Seleção de perfil, vínculo familiar e limites definidos pelo responsável. | Contas únicas, acesso restrito, códigos válidos/revogados, auditoria de políticas e restrições para filhos (`U.01`, `U.02`, `PR.01`, `F.01`, `PR.02`). |
| **6 · Visões de famílias e equipes** | Painéis ampliados, acesso temporário, equipes e categorias. | Visões autorizadas, exceções com prazo, regras de participação, ciclo de relatórios e preservação do histórico de subgrupos. |
| **7 · Relatórios e conquistas** | Relatórios diários automáticos e indicadores somente para consulta. | Justificativas confirmadas imutáveis, filtros corretos e cálculo determinístico de sequências de dias (`GR.03`, `F.04`). |

## Incremento 1 · implementado

- Painel de visitante em Tkinter, pandas e matplotlib.
- Métricas de uso/inatividade, ranking de aplicativos e linha do tempo.
- Filtros por aplicativo, data e períodos de 1/7/30 dias.
- Mensagens em português brasileiro e inglês.
- Estados sem dados e com data inválida; rótulos legíveis e controles acessíveis pelo teclado.
- O painel usa somente dados fictícios em memória: sem conexão ao banco, coletor, contas ou serviço em segundo plano.
- Testes unitários, de gráficos e de abertura/interação básica do painel. Coleta nativa no Linux e auditoria completa de acessibilidade ainda estão pendentes.

Esta entrega demonstra parte de `V.01`; não conclui o monitoramento real. Testes da interface no Linux não comprovam suporte à coleta ou à suspensão de aplicativos.

## Base de integração · especificada

O [contrato da API](api.md), o [documento OpenAPI](contracts/openapi.json) e o [modelo de dados](data-model.md) estabelecem o acordo entre as cinco frentes. A especificação está acompanhada da primeira entrega de [armazenamento SQLite](storage.md): migrações, transações, consultas, exemplos fictícios e manutenção do histórico. Endpoints, clientes e testes do fluxo completo ainda não foram implementados. As rotas de foco e metas ficam reservadas para as próximas entregas; famílias/equipes exigem uma ampliação separada do modelo.

## Próximo incremento · fluxo integrado com dados fictícios

1. **Banco — primeira entrega implementada:** migrações SQLite versionadas, restrições, índices, transações, carga explícita de exemplos fictícios e exclusão/retenção local. Próximo passo: integrar ao backend e completar os serviços de metas e foco.
2. **Backend:** provisionar localmente espaço pessoal, dispositivo e tokens restritos; implementar recebimento em lote e consultas de uso sobre esse banco.
3. **Agente:** fornecer um emissor fictício com IDs estáveis e novas tentativas de envio; adicionar coleta real apenas depois de validar o fluxo.
4. **Extensão/foco:** enviar intervalos fictícios de domínios para a mesma API e verificar credenciais separadas por origem; implementar permissões e bloqueios posteriormente, seguindo o contrato de foco.
5. **Painel/documentação/testes:** adicionar o provedor de API, filtros de calendário e estados de erro; verificar o fluxo completo sem acesso direto dos componentes visuais ao banco.

**Aceitação:** uma instalação nova no Windows ou Linux deve provisionar o espaço local, enviar observações fictícias de aplicativos/inatividade/domínios, reiniciar o backend e mostrar os mesmos resultados no painel. Reenvios idênticos não aumentam os totais; lotes inválidos ou sobrepostos não gravam nada; eventos do navegador não inflam o tempo de aplicativos; dispositivos não autorizados são rejeitados.

Os testes devem cobrir fusos e horário de verão, ausência de observações, retenção e prevenção de restauração de dados excluídos por reenvio. Configuração e testes não devem iniciar coleta real, configurar início automático, alterar hosts/firewall ou suspender aplicativos.

## Alinhamento das prioridades

A [especificação da Sprint 2](product.md) mantém foco pessoal e recursos familiares essenciais em alta prioridade. Painéis familiares ampliados e equipes seguem em prioridade média; relatórios automáticos e conquistas de filhos, em baixa. `GR.05` aparece agrupado com categorização na tabela original e ainda precisa de uma prioridade própria confirmada.

## Definição de concluído

Um incremento está concluído quando atende aos critérios de aceitação, passa nos testes pertinentes, tem sua interface conferida visualmente quando houver alterações visuais e possui documentação fiel ao que funciona. Antes de afirmar suporte à coleta ou suspensão, faça verificações específicas por plataforma. Atualize o plano a cada entrega sem marcar uma área inteira como concluída a partir de uma demonstração.
