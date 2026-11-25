# `$yabook dev`

Desenvolve a demanda da issue atual até a validação: cria a issue se ainda não
existir, prepara a branch, implementa, testa e entrega um relatório com
`Como testar`.

## Quando usar

- Você já tem uma demanda delimitada e quer que o agente implemente.
- A issue existe (ou pode ser criada a partir da conversa) e falta preparar a branch.
- Há um checklist ativo e você quer executar só a etapa atual (`dev step`).

## Altera alguma coisa?

Sim. `dev` é executivo e não precisa de `do`: pode criar a issue, criar e
vincular a branch, mover a issue para `Em andamento` e editar arquivos.
Fora do `mode: auto`, ele para antes de commit, push, PR, merge e release; para
ir além, encadeie `do pr` ou `do merge`. Também não faz rebase: indica
`$yabook rebase` quando a base precisa de atualização.

## Sintaxe

```text
$yabook dev [quick|step|full]
```

- `dev`: fluxo balanceado (inspeciona, implementa e valida).
- `dev quick`: tarefa pequena e clara, com descoberta mínima.
- `dev step`: executa somente a etapa atual do checklist ativo.
- `dev full`: investigação profunda, sob pedido explícito, sem ampliar escopo.

## Exemplos

```text
$yabook dev
$yabook dev & do pr
$yabook dev & do merge
```

- `dev`: implementa e valida; você revisa e decide quando commitar.
- `dev & do pr`: também cria commits coerentes, envia a branch e abre ou atualiza o PR.
- `dev & do merge`: faz o fluxo anterior, valida as condições do PR e integra.

## Relacionados

- `issue`: preparar a issue antes de desenvolver.
- `do`: autorizar commit, PR ou merge depois do `dev`.
- `bypass`: ajuste pontual sem issue nem branch própria.
- `mode`: com `mode: auto`, o `dev` pode seguir até os commits.
