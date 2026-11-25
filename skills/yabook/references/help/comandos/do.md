# `$yabook do`

Transforma uma prévia em ação real. Sem `do`, os comandos do YABook só
inspecionam, conversam ou propõem texto; com `do`, o agente executa a ação
pedida.

## Quando usar

- Você revisou uma prévia (issue, branch, commit, PR, APK...) e quer criá-la de fato.
- O agente propôs um checkpoint de commit e você quer aceitá-lo.
- Você quer encadear uma entrega depois do `dev`.

## Altera alguma coisa?

Sim, mas só dentro da ação pedida. `do commit` cria o commit e não faz push;
`do branch` não edita arquivos; `do pr` pode criar commits, enviar a branch e
abrir ou atualizar o PR, mas não faz merge; `do merge` cumpre os pré-requisitos
do PR e integra. Antes de criar issue, branch, commit ou PR, o agente valida o
formato e interrompe se algo estiver inválido. Em `mode: auto`, o objetivo
delegado já autoriza essas ações sem `do`.

## Sintaxe

```text
$yabook do <ação>
```

- `do <ação>`: executa a ação, como `issue`, `branch`, `commit`, `pr`, `merge`, `release`, `apk` ou `rebase`.
- `do:` é equivalente a `do`; `create` é alias de `do`.
- `do` sozinho: aceita a única ação pendente apresentada, como um checkpoint de commit.
- `continue`: recusa o checkpoint opcional e retoma o pedido original.

## Exemplos

```text
$yabook do issue
$yabook do: commit
$yabook dev & do pr
```

- `do issue`: cria a issue a partir da prévia aprovada.
- `do: commit`: cria o commit, sem enviar ao remoto.
- `dev & do pr`: implementa e entrega o PR; a autorização vale só para o segmento que tem `do`.

## Relacionados

- `dev`: implementa sem precisar de `do`, mas para antes do commit.
- `bypass`: dispensa issue e branch, mas não substitui `do`.
- `mode`: `mode: auto` dispensa `do` no objetivo delegado.
