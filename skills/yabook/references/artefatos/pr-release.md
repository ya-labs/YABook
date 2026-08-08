# Pull Request e release

Consulte [contratos.md](contratos.md) antes de gerar, criar ou validar o PR.

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

Inclua sempre o bloco `Informações para IA` de `contratos.md`, com contexto
factual útil para revisão ou continuidade.

Quando houver `pr brief` válido, use-o antes de reler issue, diff ou histórico.
Revalide a fonte somente se commits, diff, objetivo ou escopo mudarem.

## Release

Título:

```text
Publicar versão x.y.z
```

Corpo: objetivo, entrega, issue, mudanças, validações e observações. A tag aponta
para o commit integrado na branch principal.

Para conteúdo textual, use issue, diff e commits relevantes. Para criar,
atualizar, validar ou integrar, carregue `github/pr-release.md`,
`git/checkpoint.md` e `git/mutacoes.md`.

Em `do pr`, valide título, corpo, vínculo com a issue e contexto de IA antes de
criar ou atualizar o Pull Request.

No squash merge, use `tipo: descrição (#PR)` e inclua no corpo o histórico da
branch contra a base.
