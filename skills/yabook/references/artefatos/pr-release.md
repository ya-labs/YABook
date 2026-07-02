# Pull Request e release

## Pull Request

Título objetivo, sem prefixo de tipo.

```md
## Resumo rápido

- Objetivo:
- Entrega:
- Issue:

Closes #numero

## O que mudou

-

## Observações

-
```

Adicione `<details>` com informações para IA somente quando houver contexto útil
para revisão ou continuidade.

## Release

Título:

```text
Publicar versão x.y.z
```

Corpo: objetivo, entrega, issue, mudanças, validações e observações. A tag aponta
para o commit integrado na branch principal.

Para conteúdo textual, use issue, diff e commits relevantes. Para criar,
atualizar, validar ou integrar, carregue também `github.md` e `git.md`.

No squash merge, use `tipo: descrição (#PR)` e inclua no corpo o histórico da
branch contra a base.
