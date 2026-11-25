# `$yabook commit`

Sugere a mensagem de commit no padrão `tipo: descrição curta`, com base nas
alterações atuais. Com `do commit`, cria o commit.

## Quando usar

- Terminou uma alteração e quer a mensagem no padrão.
- Fez um ajuste via `bypass` ou um pacote e precisa da descrição documentada.
- O agente propôs um checkpoint e você quer revisar a mensagem antes.

## Altera alguma coisa?

`commit message` é somente leitura. `do commit` cria o commit depois de validar
a mensagem, mas não faz push. Em `mode: auto` o objetivo delegado dispensa `do`.

Tipos comuns: `feat`, `fix`, `docs`, `chore`, `refactor`. Quando houver corpo,
a sugestão vem em dois blocos: `Mensagem` (assunto) e `Descrição` (motivo e
alteração). O corpo é obrigatório em pacotes e ajustes via `bypass`; nos demais,
aparece só quando ajuda a revisão. Validações ficam no relatório e no PR, não no commit.

## Sintaxe

```text
$yabook commit message
```

- `commit msg` é alias de `commit message`.
- `do commit`: cria o commit com a mensagem validada.

## Exemplos

```text
$yabook commit msg
$yabook do commit
```

- `commit msg`: sugere algo como `docs: explicar o comando dev`.
- `do commit`: cria o commit; após um `bypass`, conclui o ajuste sem exigir issue.

## Contrato

```text
tipo: descrição curta
```

Tipos comuns: `feat`, `fix`, `docs`, `chore`, `refactor`. Quando há corpo, a
sugestão vem em dois blocos, **Mensagem** (assunto) e **Descrição** (corpo),
gravados como uma só mensagem Git separada por linha em branco. Corpo é
obrigatório em issue package e em ajuste via `bypass` (motivo e alteração) e
nunca lista validações: elas vão no PR.

## Relacionados

- `pr`: publicar a branch e abrir o PR.
- `bypass`: ajuste pontual que termina em `do commit`.
- `do`: o que cada ação autoriza.
