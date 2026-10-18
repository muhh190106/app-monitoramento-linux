# Começar em equipe

Este repositório é a base do trabalho de Engenharia de Software do STime NOW.
Hoje é possível executar um painel desktop com dados fictícios, alternar o idioma
e consultar gráficos e filtros. Coleta, extensão, API, banco e bloqueios ainda
precisam ser implementados. Os contratos descrevem o destino desses módulos.

## Primeiro acesso

1. Siga a instalação para seu sistema no [README](../README.md). Cada computador
   e cada sistema do dual boot deve ter seu próprio clone e ambiente virtual.
2. Execute o painel e a demonstração pelo terminal. Nenhuma dessas ações coleta
   atividade real.
3. Leia os [requisitos](product.md) e o [planejamento](roadmap.md); depois consulte
   [API](api.md) e [DER](data-model.md) para entender as dependências da sua frente.
4. Crie uma branch para sua tarefa e envie um pull request com as verificações
   realizadas. Não trabalhe diretamente na branch de outro integrante.

Se a documentação estiver em um PR ainda aberto, selecione a branch desse PR
depois de clonar; a branch principal só recebe as alterações após a integração.
No GitHub, o PR informa a branch de origem e quais arquivos serão incorporados.

## Divisão das cinco frentes

| Frente | Ponto de partida | Primeira entrega verificável |
| --- | --- | --- |
| Agente desktop | Eventos em [API](api.md); manter coleta separada de cálculo e armazenamento. | Emissor fictício com IDs estáveis e reenvios. Depois, coleta explícita em Windows e investigação separada de X11/Wayland. |
| Extensão e foco | Eventos `browser`, vínculo com o aplicativo e rotas de foco em [API](api.md). | Eventos fictícios de domínio cruzados com o navegador em primeiro plano; depois extensão e aplicação das regras suportadas. |
| Backend/API | [OpenAPI](contracts/openapi.json) e regras adicionais em [API](api.md). | Provisionamento local, recebimento em lote e consulta de uso com isolamento por dispositivo. |
| Banco de dados | [DER e restrições](data-model.md). | Migrações SQLite, exemplos fictícios explícitos, transações, consultas, retenção e exclusão. |
| Painel/documentação/testes | `activity_monitor/desktop.py`, `reporting.py`, `charts.py`, `i18n.py` e `tests/`. | Adaptador que consulta a API; estados de erro; testes do fluxo entre módulos. |

O coletor e a extensão não acessam o banco. O painel recebe totais do backend.
Alterações em eventos, campos, períodos ou regras devem atualizar o OpenAPI,
a explicação da API e o DER no mesmo PR, com acordo entre as frentes afetadas.
O framework do backend e o mecanismo de comunicação da extensão ainda devem ser
escolhidos na implementação; o contrato não depende dessa escolha.

## Verificações antes de enviar

Use o Python do ambiente virtual (`.venv\Scripts\python.exe` no Windows ou
`.venv/bin/python` no Linux) nos comandos abaixo:

```bash
python -m pip install -e '.[desktop,contracts]'
python -m unittest discover -s tests -v
python -m activity_monitor --demo
python -m monitoramento --demo
```

Testes gráficos só rodam com `STIME_DESKTOP_TESTS=1` e sessão gráfica ou Xvfb;
o [guia de desenvolvimento](development.md) contém os comandos. A CI verifica
Windows/Linux e valida o contrato. Testes do esquema não substituem testes de
autorização, banco, agregação ou integração quando esses módulos existirem.

Documentação principal em português, [README internacional](../README.en.md) em
inglês, código e nomes técnicos em inglês, interface nos dois idiomas. Use apenas
dados fictícios. Consulte [CONTRIBUTING](../CONTRIBUTING.md) para o fluxo de revisão.
