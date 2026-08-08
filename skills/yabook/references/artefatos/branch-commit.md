# Branch e commit

Consulte [contratos.md](contratos.md) antes de gerar, criar ou validar branch e
commit.

## Branch

Use:

```text
numero-descricao-curta
```

Não inclua tipo, área, `issue`, `#`, acentos ou espaços. Use o número da issue
inequívoca e a base definida pelo fluxo local.

Criação real exige `do branch` ou `dev`, `github/branches.md`,
`git/checkpoint.md` e `git/mutacoes.md`. Prefira `createLinkedBranch` e confirme
em `issue.linkedBranches`. Em `do branch`, valide o nome e a issue conforme
`contratos.md` antes de criar ou publicar.

## Commit

Use:

```text
tipo: descrição curta
```

Tipos comuns: `feat`, `fix`, `docs`, `chore`, `refactor`.

Para sugerir a mensagem, use conversa, `git diff --stat` e `git diff` quando
necessário. Não carregue Project, release ou corpos de issues sem relação.
Criar commit exige autorização `do` e valida a mensagem antes da mutação.
