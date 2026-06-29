# Segurança de comandos Git no YABook

Use esta referência sempre que uma solicitação `$yabook` consultar ou alterar o
estado do Git.

## Regra principal

Em projetos que adotam o Método YA LABS, somente uma chamada iniciada por
`$yabook do` ou um alias documentado de `do` autoriza mutações Git.

Pedidos diretos sem `$yabook`, mesmo explícitos, não autorizam alterar Git. O
agente deve explicar a trava e indicar a chamada necessária.

## Operações somente leitura

Podem ser executadas sem `do` quando necessárias para responder:

```text
git status
git diff
git log
git show
git branch --show-current
git branch --list
git remote -v
```

Outras operações são somente leitura apenas quando não alteram arquivos, índice,
refs, configuração, histórico, stash ou estado remoto.

## Operações que exigem `do`

Exigem autorização explícita:

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

A lista é exemplificativa. Qualquer comando que altere estado local ou remoto
também exige `do`.

Exemplo:

```text
Pedido direto: faça commit dessas alterações
Resposta: use $yabook do commit
```

## Escopo da autorização

- `$yabook do` não autoriza toda operação Git.
- Execute somente as ações mencionadas pela pessoa usuária.
- `$yabook do commit` não autoriza `push`.
- `$yabook do branch` não autoriza editar arquivos.
- `$yabook do pr` não autoriza commit, push ou merge não solicitados.
- Merge exige pedido explícito mesmo quando houver outro `do`.
- `bypass` não substitui `do` para mutações da gramática YABook.

Se uma ação solicitada depender de outra mutação não autorizada, execute somente
o que for possível e informe o comando necessário para continuar.

## Roteamento inteligente

O roteamento pode inferir inspeções Git somente leitura. Nunca deve inferir uma
mutação, adicionar `do` ou ampliar o escopo da autorização.

Se um comando incompatível for corrigido, a correção pode executar apenas
operações dentro da mesma classe de segurança ou mais restritivas.
