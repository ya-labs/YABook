# Inspeções Git

Use para consultas Git somente leitura.

São permitidos sem `do` quando necessários:

```text
git status
git diff
git log
git show
git branch --show-current
git branch --list
git remote -v
```

Outro comando só é leitura quando não altera arquivos, índice, refs,
configuração, histórico, stash ou estado remoto.

O roteamento pode inferir inspeções somente leitura. Nunca infira mutação,
adicione `do` ou amplie a autorização.
