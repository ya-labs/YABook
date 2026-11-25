# `$yabook bypass`

Autoriza um ajuste pontual fora do fluxo de issue e branch: o agente executa só
a ação anexada, mesmo em `main`, `dev`, release ou branch incompatível.

## Quando usar

- O ajuste é pequeno e cabe em um commit compreensível e validável.
- Abrir issue e branch própria daria mais trabalho que a mudança.
- O agente bloqueou uma alteração direta em branch protegida e você quer a exceção.

Se o ajuste crescer, prefira uma issue individual ou um `issue package`.

## Altera alguma coisa?

Sim, mas só a ação anexada e só nesta solicitação. `bypass` não autoriza Git:
não cria commit, não faz push nem merge e não substitui `do`. Depois de
implementar, o agente registra a exceção e sugere `Mensagem` e `Descrição` do
commit, com motivo e alteração. Para criar o commit, use `do commit`, sem
precisar de issue. Em `mode: auto` não é preciso invocar `bypass`.

## Sintaxe

```text
$yabook bypass <ação>
```

- `<ação>`: descrição em linguagem natural do ajuste a fazer.

## Exemplos

```text
$yabook bypass atualize o README diretamente na main
$yabook do commit
```

- `bypass atualize o README...`: edita o README sem issue e sugere o commit documentado.
- `do commit`: cria o commit sugerido após o `bypass`, sem exigir issue de novo.

## Relacionados

- `do`: necessário para commit, push ou PR depois do ajuste.
- `issue`: quando o ajuste merece acompanhamento.
- `commit`: formato da mensagem e da descrição.
