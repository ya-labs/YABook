# Checkpoint do worktree

Use antes de iniciar alterações ou imediatamente antes de propor separação de
um bloco concluído.

Atualize sempre:

```text
git status --short --branch
git diff --stat
git diff --cached --stat
git log -1 --oneline
```

Quando a ação depender do remoto, confira também divergência e PR existente.

Para rebase, o checkpoint é obrigatório e deve incluir a branch atual, o
upstream, a base candidata, os commits exclusivos e a divergência com a base e
com o remoto. Alterações staged ou unstaged bloqueiam o rebase; não use stash,
restore ou reset automaticamente para liberar o worktree.

Se o worktree estiver limpo ou o commit esperado já existir, continue sem
apresentar checkpoint.

Recomende commit quando o bloco anterior:

- está funcional e validado;
- possui objetivo próprio e reversível;
- pertence a outra responsabilidade, issue ou branch;
- prejudicaria a mensagem ou revisão do próximo commit.

Não interrompa quando o trabalho anterior estiver incompleto ou fizer parte da
mesma entrega.

Quando o checkpoint for opcional, apresente:

```text
Existem alterações concluídas que devem formar um commit separado.

Commit proposto: tipo: descrição

- $yabook do: cria o commit, executa os pré-requisitos mínimos e retoma a solicitação.
- $yabook continue: prossegue sem criar o commit.
```

`do` contextual vale somente para a ação apresentada e expira após execução ou
mudança de contexto. `continue` não pode ignorar separação obrigatória por issue
ou branch.

Antes do commit, confira os arquivos e não inclua mudanças de outro escopo.
Depois do commit autorizado, retome automaticamente a solicitação original.
