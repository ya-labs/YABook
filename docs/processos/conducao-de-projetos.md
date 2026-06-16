# Condução de projetos

Este documento define um modelo reutilizável para iniciar, documentar e conduzir projetos da YA LABS sem transformar documentação em burocracia.

O objetivo é preservar clareza, rastreabilidade e velocidade desde a descoberta inicial até uma release validada.

## Princípio central

Projetos devem separar três camadas:

- conhecimento estável em Markdown;
- trabalho executável no GitHub;
- decisões técnicas registradas no momento certo.

Markdown deve explicar produto, arquitetura, requisitos, fluxos, contratos, decisões e critérios de pronto.

GitHub deve acompanhar backlog, issues, responsáveis, Project, milestones, épicos, Pull Requests, status e progresso operacional.

## Descoberta inicial

Antes de implementar, registre apenas o necessário para alinhar direção:

- problema que o projeto resolve;
- público ou pessoa usuária principal;
- objetivo da primeira versão;
- restrições conhecidas;
- alternativas consideradas;
- riscos relevantes;
- critérios mínimos para considerar a primeira entrega pronta.

Essa etapa não precisa fechar todas as decisões. Ela deve reduzir ambiguidade suficiente para criar as primeiras issues implementáveis.

## Documentação horizontal

Documentar horizontalmente significa mapear partes diferentes do projeto quando isso ajuda a entender o conjunto.

Exemplos:

- visão do produto;
- problema;
- público-alvo;
- requisitos;
- arquitetura conceitual;
- fluxos principais;
- contratos;
- ADRs;
- RFCs;
- provas técnicas;
- critérios de pronto.

Essa documentação pode antecipar assuntos de fases futuras, desde que não pareça implementação já decidida quando ainda for hipótese.

## Execução vertical

Executar verticalmente significa priorizar entregas implementáveis em ordem de dependência.

Em vez de tentar documentar ou construir o projeto inteiro antes de começar, a equipe deve executar por etapas, milestones ou fases.

Na prática:

- a milestone atual orienta o próximo bloco de issues;
- issues de fases futuras podem ficar no backlog quando preservarem contexto;
- somente a próxima issue realmente acionável deve ir para execução;
- documentação técnica deve acompanhar a capacidade que ela apoia;
- provas técnicas devem validar riscos antes de virarem contrato final;
- release deve consolidar uma versão candidata, não servir como planejamento solto.

Essa regra evita dois problemas comuns: documentação ampla virar bloqueio e execução pular base técnica necessária.

## Modelo de fases

Cada projeto pode adaptar suas fases, mas uma sequência inicial saudável costuma ser:

1. Descoberta e escopo inicial.
2. Base técnica e ambiente.
3. Primeira capacidade vertical.
4. Expansão das capacidades principais.
5. Estabilização.
6. Release.

Projetos pequenos podem usar uma lista simples de etapas. Projetos maiores podem usar milestones e épicos no GitHub.

## Issues, milestones e épicos

Use milestone quando o projeto tiver fases claras de entrega.

Use épico quando uma capacidade macro precisar agrupar várias tarefas relacionadas.

Uma issue implementável deve ter:

- contexto curto;
- objetivo claro;
- escopo;
- fora de escopo quando houver risco de expansão;
- critérios de aceite verificáveis;
- referências documentais quando necessário;
- milestone e épico quando fizer parte de uma fase.

Evite criar backlog completo do projeto inteiro no início. Crie apenas issues suficientes para orientar o próximo bloco de trabalho.

## Uso de IA

Quando a IA apoiar o projeto, prefira issues preparadas com referências claras.

A IA deve ler o mínimo necessário para executar com segurança. Leitura ampla é adequada quando a tarefa altera documentação estrutural, processo, arquitetura, requisito, contrato, ADR ou planejamento.

Para desenvolvimento comum, a issue deve ser a fonte principal da implementação.

## Ajustes de processo

Nem todo ajuste de processo precisa virar uma cerimônia pesada.

Use issue, branch e Pull Request para mudanças relevantes, mudanças estruturais ou decisões que afetam mais de um projeto.

Mudanças pequenas de texto, nomenclatura ou organização podem ser agrupadas em uma branch de lote documental quando fizerem parte da mesma intenção.

Não crie branch permanente de documentação. Cada lote deve ter começo, fim e objetivo claro.

## Branch de desenvolvimento e release

Nem todo projeto precisa de branch `dev` desde o começo.

Adote branch de desenvolvimento quando houver pelo menos dois sinais:

- implementação ativa além de documentação;
- trabalho paralelo com risco de conflito;
- necessidade de manter a branch principal apenas com conteúdo pronto para release.

Use branch `release/x.y.z` quando existir uma versão candidata consolidada.

A tag deve apontar para o commit integrado na branch principal que representa a versão publicada.

## Regra prática

Um projeto bem conduzido não precisa ter documentação grande. Ele precisa ter documentação suficiente para outra pessoa entender, executar, revisar e continuar o trabalho sem adivinhar decisões importantes.
