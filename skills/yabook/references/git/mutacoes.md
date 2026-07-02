# Autorizações para mutações Git

Use quando a rota puder alterar Git local ou remoto.

Somente `$yabook do`, um alias documentado de `do` ou o escopo limitado de
`$yabook dev` autoriza mutações. Pedidos diretos não autorizam.

Exemplos de mutações:

```text
git switch
git checkout
git branch <nome>
git add
git restore
git commit
git stash
git merge
git rebase
git cherry-pick
git revert
git reset
git tag
git clean
git fetch
git pull
git push
```

## Escopo

- Execute apenas a ação autorizada.
- `do commit` não autoriza push.
- `do branch` não autoriza editar arquivos.
- `do pr` pode criar commits coerentes, enviar a branch e criar ou atualizar o
  PR; não autoriza merge.
- `do merge` pode cumprir pré-requisitos do PR e integrar após as validações.
- Merge exige pedido explícito.
- `bypass` não substitui `do`.
- `dev` termina antes de commit, PR ou merge.

Quando faltar autorização para uma dependência, execute somente o possível e
informe o comando necessário.
