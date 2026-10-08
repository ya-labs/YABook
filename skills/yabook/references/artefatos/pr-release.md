# Pull Request e release

Consulte [contratos.md](contratos.md) antes de gerar, criar ou validar o PR.

## Pull Request

Título objetivo, sem prefixo de tipo.
Antes da prévia, confira em `recent` o aprendizado da entrega inteira e registre só
o que faltar, por `memory.md` com `learning.trigger: pr`.
Use texto e bullets simples para explicar entregas e validações, sem checklists
ou caixas de progresso no corpo, inclusive em `Informações para IA`.

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

PR de issue pacote consolida entregas e validações e usa merge commit para
preservar commits e descrições. Leia assuntos e corpos dos commits da branch
contra a base, incluindo os dois autores em trabalho compartilhado, e confira
o diff final. Não apresente como entrega algo removido ou revertido nem copie
uma lista de demandas da issue como prova de implementação. Se merge commit
estiver indisponível no repositório, informe o impedimento antes de escolher alternativa; não faça squash silenciosamente.
No ajuste pontual autorizado sem issue, omita `Closes` e registre a exceção.

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
