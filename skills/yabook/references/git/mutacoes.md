# Autorizações para mutações Git

Use quando a rota puder alterar Git local ou remoto.

O pedido da pessoa autoriza mutações Git, seja `$yabook do <ação>` ou linguagem
natural interpretada pelo contexto (“pode commitar”, “sobe e abre o PR”). Autoriza
o objetivo, não um comando: inclui os passos necessários para cumpri-lo. Na
dúvida sobre o pedido, pergunte. O hook só barra push forçado, push em branch
protegida e merge sem pedido, descarte de trabalho e troca de branch com
worktree sujo. `$yabook dev` é o atalho de implementação da issue atual e não um
gate exclusivo para editar arquivos.

Com ativação explícita de `auto`, o objetivo delegado autoriza seus pré-requisitos, branches e commits,
sem aprovação de checkpoints. Operações remotas só entram no pedido autorizado;
abrir PR inclui push da branch, implementar não implica publicar. Merge exige
pedido explícito, mas não a sintaxe `do`. Preserve trabalho existente e respeite
permissões do ambiente. Não infira ativação nem ampliação do objetivo.

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

- Cumpra o objetivo autorizado; não amplie para outro.
- Push só quando o objetivo é publicar (`pr`, `push`, `branch`, `sync`,
  `release`, `merge`, operações de memória). `do commit` não autoriza push.
- `do branch` não autoriza editar arquivos.
- `do pr` pode criar commits coerentes, enviar a branch e criar ou atualizar o
  PR; não autoriza merge.
- `do rebase` não autoriza push, PR, merge, release ou resolução silenciosa de
  conflitos de conteúdo.
- `do merge` pode cumprir pré-requisitos do PR e integrar após as validações.
- Merge exige pedido explícito.
- `bypass` não substitui `do`.
- `do commit` de ajuste autorizado via `bypass` não volta a exigir issue ou
  branch própria; valide assunto e corpo documentado e registre a exceção.
- `dev` termina antes de commit, PR ou merge e não substitui `do` para essas
  etapas.

Quando faltar autorização para uma dependência, execute somente o possível e
informe o comando necessário.

## Validação de artefatos

Antes de `do issue`, `do branch`, `do commit` ou `do pr`, carregue e aplique
`artefatos/contratos.md`. Se um campo obrigatório estiver ausente, inválido ou
divergente do contexto confirmado, interrompa antes da mutação. Não reescreva
decisões de conteúdo para fazer o artefato passar na validação.
