# Primeiros passos com o YABook

Este guia ensina como aplicar o YABook em um projeto da YA LABS sem precisar conhecer todo o handbook antes.

## O que é

O YABook é o padrão organizacional da YA LABS.

Ele não substitui a documentação do projeto. Ele diz como o projeto deve organizar documentação, GitHub, IA e etapas de desenvolvimento.

## Como aplicar em um projeto

1. Copie ou adapte os templates necessários.
2. Preencha o `README.md` do projeto com objetivo, stack, setup e links principais.
3. Mantenha um `AGENTS.md` com as instruções para IA naquele projeto.
4. Crie em `docs/` apenas os documentos que fazem sentido para o momento atual.
5. Declare labels, GitHub Project e responsável padrão por novas issues.
6. Use o padrão de GitHub do YABook para issue, branch, commit, PR e release.

Não crie pastas vazias nem documentos só para "completar a estrutura".

## Fluxo mínimo de trabalho

```text
Issue -> Branch -> Commit -> Pull Request -> Merge
```

Para formatos de issue, branch, commit e PR, consulte [Padrões rápidos](padroes-rapidos.md).

Use `main` para documentação inicial, planejamento e prototipagem. Crie `dev` apenas quando começar o desenvolvimento de produto. O fluxo completo de `main`, `dev`, `release/x.y.z` e `archive/dev-x.y.z` fica em [Fluxo de trabalho com GitHub](processos/fluxo-de-trabalho-github.md).

## Como orientar a IA

Antes de pedir execução para IA, garanta que ela consulte:

1. `AGENTS.md` do projeto.
2. Documentação local relacionada à tarefa.
3. YABook, quando a dúvida for sobre padrão organizacional.

A IA deve avisar antes de criar padrão novo, mudar fluxo de trabalho ou agir fora do YABook.

## Checklist de conformidade

Use esta lista ao iniciar um projeto ou revisar um PR:

- O projeto tem `README.md` útil para entrada rápida.
- O projeto tem `AGENTS.md` com regras locais para IA.
- A documentação em `docs/` guarda conhecimento estável, não status operacional.
- Issues, branches, commits e PRs seguem o padrão da YA LABS.
- Exceções ao YABook estão explícitas no projeto.
- Não há documentação genérica, duplicada ou sem uso prático.

## Regra prática

Documento bom ajuda alguém a executar, revisar, decidir ou continuar o trabalho.

Se o texto não ajuda nenhuma dessas ações, corte, funda com outro documento ou não crie.
