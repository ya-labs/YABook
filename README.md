# YABook - Handbook de Padrões Internos da YA LABS

Este repositório concentra os padrões internos da YA LABS para documentação, fluxo de trabalho, uso de IA e organização de projetos.

O objetivo do YABook é servir como fonte principal para decisões recorrentes da organização, evitando que cada projeto precise reinventar seu próprio processo do zero.

## Para que serve

Use este repositório para consultar e evoluir:

- fluxo de trabalho com GitHub Issues, Projects, branches, commits, Pull Requests e releases;
- condução de projetos, da descoberta inicial até release;
- orientações para uso de IA em tarefas de desenvolvimento e documentação;
- boas práticas de documentação técnica;
- templates iniciais para novos projetos da YA LABS.

## Como os projetos devem usar

Cada projeto da YA LABS deve manter sua própria documentação específica no repositório do produto.

Exemplos de documentação específica de projeto:

- objetivo do produto;
- stack usada;
- arquitetura real;
- endpoints;
- variáveis de ambiente;
- deploy;
- roadmap;
- integrações.

O YABook fica responsável pelo padrão organizacional. Projetos da YA LABS podem copiar os templates deste repositório e adaptar apenas o que for próprio do produto.

## Estrutura inicial

```text
docs/
|-- README.md
|-- processos/
|   |-- conducao-de-projetos.md
|   `-- fluxo-de-trabalho-github.md
|-- guias/
|   |-- documentacao-tecnica.md
|   `-- uso-de-ia.md
`-- templates/
    `-- projeto/
        |-- README.md
        |-- AGENTS.md
        `-- docs/
            `-- README.md
```

## Regras gerais

- Documentos devem ser escritos em português do Brasil.
- Textos devem preservar acentos e caracteres Unicode em UTF-8.
- Padrões da organização devem ficar neste repositório.
- Informações específicas de produto devem ficar no repositório do produto.
- Markdown deve guardar conhecimento estável; GitHub deve acompanhar execução, backlog e progresso.
- Mudanças relevantes devem seguir o fluxo documentado em [Fluxo de trabalho com GitHub](docs/processos/fluxo-de-trabalho-github.md).
