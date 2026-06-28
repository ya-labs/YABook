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

## Planejamento colaborativo da versão

O planejamento de uma versão deve ser uma conversa guiada, não o preenchimento
cego de um template.

Antes de consolidar a V1 ou uma versão posterior, alinhe:

- problema e público;
- resultado esperado;
- escopo e fora de escopo;
- capacidades e fluxos principais;
- restrições, riscos e alternativas relevantes;
- critérios de pronto;
- ideias que pertencem a versões futuras.

Hipóteses, alternativas e decisões abertas não devem aparecer como contratos
fechados. Depois da discussão, consolide somente o que foi aceito e preserve as
pendências de forma explícita.

Quando o projeto evoluir, uma nova capacidade pode alterar a versão atual ou
iniciar uma versão posterior. Primeiro diagnostique o estado real e depois
decida qual dos dois casos se aplica.

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

- resumo rápido;
- escopo objetivo;
- critérios de aceite verificáveis;
- contexto adicional em bloco recolhido quando a tarefa for delegada para IA;
- milestone e épico quando fizer parte de uma fase.

Evite criar backlog completo do projeto inteiro no início. Crie apenas issues suficientes para orientar o próximo bloco de trabalho.

## Diagnóstico e recuperação de direção

Quando não estiver claro o que fazer em seguida, reconstrua o estado do projeto
antes de criar novas tarefas.

O diagnóstico deve cruzar:

- objetivo e roadmap da versão;
- documentação e decisões;
- implementação real;
- issues e Pull Requests concluídos ou abertos;
- milestones, épicos e GitHub Project;
- bloqueios e divergências.

O resultado deve distinguir o que foi concluído, o que está em andamento, o que
falta e qual é a próxima ação de maior valor. A recomendação pode ser uma
decisão, validação, atualização documental ou issue implementável.

Roadmap não substitui diagnóstico. O roadmap descreve direção; o GitHub registra
execução; o diagnóstico compara ambos com a realidade do projeto.

## Núcleo documental do planejamento

Projetos devem manter um núcleo adaptável, sem obrigação de copiar uma árvore
fixa quando já houver documentos equivalentes:

- visão do produto;
- escopo e critérios da versão atual;
- roadmap macro;
- decisões relevantes;
- resumos das sessões de planejamento.

Quando não existir estrutura equivalente, use:

```text
docs/planejamento/
├── visao-do-produto.md
├── roadmap.md
├── versoes/
│   └── v1.md
└── sessoes/
    └── AAAA-MM-DD-assunto.md
```

O resumo da sessão registra contexto, decisões, pendências e impactos. Não
armazene transcrições completas por padrão nem copie status operacional para
Markdown.

## Uso de IA

Quando a IA apoiar o projeto, prefira issues preparadas com referências claras.

A IA deve ler o mínimo necessário para executar com segurança. Leitura ampla é adequada quando a tarefa altera documentação estrutural, processo, arquitetura, requisito, contrato, ADR ou planejamento.

Para desenvolvimento comum, a issue deve ser a fonte principal da implementação.

Issues preparadas para IA podem usar seções extras, como `Fora de escopo`, `Entrega Visual Esperada`, `Validação`, `Dependências`, `Referências` e `Riscos`, quando isso reduzir ambiguidade.

Esse formato expandido é uma ferramenta de clareza, não uma obrigação para toda issue. Tarefas simples devem manter corpo simples.

## Conformidade com o YABook

Projetos da YA LABS devem consultar o YABook antes de criar ou alterar:

- estrutura de documentação;
- fluxo de issue, branch, commit, Pull Request e release;
- instruções de IA;
- critérios de pronto;
- templates reutilizáveis.

Adaptações são permitidas, mas devem estar explícitas no projeto. Se não houver exceção documentada, vale o padrão do YABook.

## Ajustes de processo

Nem todo ajuste de processo precisa virar uma cerimônia pesada.

Use issue, branch e Pull Request para mudanças relevantes, mudanças estruturais ou decisões que afetam mais de um projeto.

Mudanças pequenas de texto, nomenclatura ou organização podem ser agrupadas em uma branch de lote documental quando fizerem parte da mesma intenção.

Não crie branch permanente de documentação. Cada lote deve ter começo, fim e objetivo claro.

## Branch de desenvolvimento e release

Nem todo projeto precisa de branch `dev` desde o começo. Em documentação inicial, planejamento e prototipagem, trabalhe com branch de issue a partir da `main`.

Adote `dev` quando começar o desenvolvimento de produto e houver necessidade de integrar issues antes de publicar uma versão.

`dev` representa o ciclo atual, não uma branch permanente. Depois da release, crie uma nova `dev` a partir da `main`. Se precisar preservar o ciclo anterior, arquive como `archive/dev-x.y.z`.

Use `release/x.y.z` apenas quando a versão precisar de revisão, homologação ou ajustes finais antes de entrar na `main`.

A tag deve apontar para o commit integrado na branch principal que representa a versão publicada.

## Regra prática

Um projeto bem conduzido não precisa ter documentação grande. Ele precisa ter documentação suficiente para outra pessoa entender, executar, revisar e continuar o trabalho sem adivinhar decisões importantes.
