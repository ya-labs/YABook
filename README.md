# YABook - Handbook da YA LABS

O YABook é o manual operacional da YA LABS para criar, documentar e evoluir projetos com o mesmo padrão de trabalho.

Ele existe para reduzir improviso: pessoas e agentes de IA passam a seguir o mesmo contrato para documentação, GitHub, issues, branches, commits, Pull Requests, releases e organização do projeto.

## O que o YABook entrega

- Um padrão único para condução de tarefas no GitHub.
- Um modelo objetivo para issues, PRs, commits, branches e releases.
- Uma estrutura de documentação reutilizável para novos projetos.
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

1. [Manual de uso](docs/manual.md)
2. [Padrões rápidos](docs/padroes-rapidos.md)
3. [Guia técnico da skill YABook](docs/guias/skill-yabook.md)
4. [Documentação do YABook](docs/README.md)
5. [Fluxo de trabalho com GitHub](docs/processos/fluxo-de-trabalho-github.md)
6. [Uso de IA](docs/guias/uso-de-ia.md)

## Como aplicar em um projeto

Cada projeto deve manter sua própria documentação no repositório do produto. O YABook define o padrão; o projeto guarda os fatos reais.

Use o YABook como base para:

- montar a documentação inicial do projeto;
- configurar o `AGENTS.md` local;
- orientar a IA sobre o padrão da YA LABS;
- criar issues com labels, Project e Size;
- manter rastreabilidade entre issue, branch, commit, PR e release.

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
