# Segurança e privacidade

## Escopo atual

STime NOW é um projeto em estágio inicial. A demonstração utiliza dados fictícios e não coleta atividade do computador nem executa um serviço em segundo plano. Ainda não há uma versão de produção ou compromisso de suporte de longo prazo.

## Relatar uma vulnerabilidade em particular

Use **Security > Report a vulnerability** no GitHub quando a opção de relato privado estiver disponível. Caso não esteja, abra uma issue pedindo um canal privado, sem publicar detalhes da vulnerabilidade, dados pessoais ou instruções de exploração. Aguarde esse canal antes de compartilhar informações sensíveis. Relatos podem ser escritos em português ou inglês.

Informe a versão ou commit afetado, uma reprodução mínima com dados fictícios, o impacto esperado e possíveis medidas de correção. Não publique históricos reais de atividade nem credenciais.

## Princípios para tratamento de dados

- Mantenha dados de atividade fora do Git, das issues, dos artefatos de CI e dos ambientes de desenvolvimento na nuvem.
- Exija uma ação explícita do usuário antes de iniciar futuros coletores.
- Restrinja o acesso de responsáveis e gestores à família ou equipe correspondente, com autorização verificada no backend.
- Defina confiança dos dispositivos, transporte HTTPS, retenção e revogação antes de habilitar a comunicação entre agente e backend.
- Trate títulos de janelas e URLs como informações sensíveis.
- Planeje retenção, exclusão e sincronização antes de implementar esses recursos.

Estas são exigências para o desenvolvimento dos próximos recursos, não uma afirmação de que coleta e armazenamento já foram implementados.
