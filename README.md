# YABook — ecossistema do Método YA LABS

O YABook é o ecossistema que materializa o Método YA LABS para criar,
documentar e evoluir projetos com o mesmo padrão de trabalho.

## Nomenclatura

- **Método YA LABS**: princípios, processos e modelo de trabalho.
- **YABook**: ecossistema que materializa o método.
- **YABook Handbook**: documentação humana e fonte normativa.
- **YABook Skill**: orquestrador inteligente usado por agentes de IA.
- **YABook Platform**: futuro software do ecossistema, quando existir.

A YABook Skill consulta o YABook Handbook para orientar, planejar e executar o
trabalho com segurança.

Ele existe para reduzir improviso: pessoas e agentes de IA passam a seguir o mesmo contrato para documentação, GitHub, issues, branches, commits, Pull Requests, releases e organização do projeto.

## Áreas do repositório

- [Manual da YA LABS](manual/README.md): padrões, processos, guias e modelos
  reutilizáveis da organização.
- [Produto YABook](produto/README.md): visão, planejamento e decisões próprias
  do ecossistema YABook.
- [YABook Skill](skills/yabook/): instruções, referências, scripts e testes da
  skill.


## O que o YABook entrega

- Um padrão único para condução de tarefas no GitHub.
- Um modelo objetivo para issues, PRs, commits, branches e releases.
- Uma estrutura de documentação reutilizável para novos projetos.
- Um modelo de condução da descoberta inicial até a release.
- Orientações para usar IA sem deixar que o agente invente formatos.
- Uma skill `$yabook` para gerar, revisar e validar artefatos do fluxo.
- Critérios para manter documentação curta, útil e fácil de consultar.

## Para quem é

Use o YABook quando você precisa:

- iniciar um projeto seguindo o padrão da YA LABS;
- criar ou revisar issues, PRs, commits, branches e releases;
- orientar uma IA a trabalhar de forma consistente no repositório;
- organizar documentação técnica sem transformar o projeto em um arquivo morto;
- ensinar alguém novo a trabalhar dentro do fluxo da organização.

## Comece por aqui

Se você nunca usou o YABook, leia nesta ordem:

1. [Manual de uso](manual/guias/manual-de-uso.md)
2. [Padrões rápidos](manual/padroes/padroes-rapidos.md)
3. [Condução de projetos](manual/processos/conducao-de-projetos.md)
4. [Criar e expandir projetos com YABook](manual/guias/criar-e-expandir-projetos-com-yabook.md)
5. [Guia técnico da skill YABook](manual/guias/skill-yabook.md)
6. [Manual da YA LABS](manual/README.md)
7. [Fluxo de trabalho com GitHub](manual/processos/fluxo-de-trabalho-github.md)
8. [Uso de IA](manual/guias/uso-de-ia.md)

## Condução de projetos

O YABook orienta o projeto da descoberta até a release sem transformar
planejamento em burocracia.

O modelo combina:

- descoberta inicial do problema, público e objetivo da versão;
- planejamento colaborativo da V1 e das versões seguintes;
- documentação horizontal para compreender o produto;
- execução vertical por dependências e entregas utilizáveis;
- diagnóstico do que foi concluído, do que está em andamento e do que falta;
- roadmap macro com milestones e épicos;
- detalhamento somente do próximo bloco de issues acionáveis;
- estabilização e critérios de pronto antes da release.

Leia [Condução de projetos](manual/processos/conducao-de-projetos.md) para o
método organizacional. Para aplicar o fluxo com a skill, use
[Criar e expandir projetos com YABook](manual/guias/criar-e-expandir-projetos-com-yabook.md).

## Como aplicar em um projeto

Cada projeto deve manter sua própria documentação no repositório do produto. O YABook define o padrão; o projeto guarda os fatos reais.

Use o YABook como base para:

- transformar problemas, ajustes e melhorias em issues executáveis;
- montar a documentação inicial do projeto;
- configurar o `AGENTS.md` local;
- orientar a IA sobre o padrão da YA LABS;
- criar issues com labels, Project e Size;
- manter rastreabilidade entre issue, branch, commit, PR e release.

O fluxo de trabalho começa pela demanda, não pela branch:

```text
Problema, ajuste ou melhoria
-> Issue
-> Branch
-> Implementação
-> Commit
-> Pull Request
-> Merge
```

## O que fica aqui

- Processos de trabalho da YA LABS.
- Padrões de GitHub.
- Guias de documentação.
- Contratos de uso de IA.
- Templates para novos projetos.
- Skill `$yabook`.

## O que fica no projeto

- Objetivo real do produto.
- Stack, setup e comandos reais.
- Arquitetura real.
- Endpoints, contratos e integrações.
- Variáveis de ambiente.
- Deploy.
- Decisões específicas do produto.

## Regra prática

Antes de criar estrutura nova em um projeto da YA LABS, consulte o YABook, carregue a skill quando disponível e verifique o `AGENTS.md` local.

Se o projeto precisar fugir do padrão, registre a exceção no próprio projeto.
