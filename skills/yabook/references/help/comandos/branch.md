# `$yabook branch`

Sugere o nome da branch da issue no formato `numero-descricao-curta`. Com
`do branch`, cria a branch vinculada à issue no GitHub.

## Quando usar

- Você tem a issue e quer o nome de branch no padrão.
- Quer criar a branch vinculada sem iniciar a implementação.

## Altera alguma coisa?

`branch` é somente leitura e devolve só o nome. `do branch` cria e publica a
branch, vinculando-a à issue pela seção Development do GitHub; se o vínculo
nativo não estiver disponível, o agente avisa que a associação ficou manual.
`do branch` não edita arquivos. `dev` já prepara a branch sozinho, e em
`mode: auto` o objetivo delegado dispensa `do`.

O nome não leva tipo, área, `#`, acentos ou espaços, e o número precisa ser o da
issue. Cada issue tem sua branch; não misture issues na mesma branch.

## Sintaxe

```text
$yabook branch [name]
```

- `branch` é alias de `branch name`.
- `do branch`: valida nome e issue e cria a branch vinculada.

## Exemplos

```text
$yabook branch
$yabook do branch
```

- `branch`: para a issue `#92`, sugere algo como `92-reforcar-contratos`.
- `do branch`: cria `92-reforcar-contratos`, vincula à issue `#92` e prepara o rastreamento local.

## Relacionados

- `issue`: criar a issue antes da branch.
- `dev`: prepara a branch e já implementa.
- `commit`: mensagem dos commits na branch.
