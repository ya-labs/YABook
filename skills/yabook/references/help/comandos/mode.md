# `$yabook mode`

Muda a forma como a IA colabora com você na conversa: ensinando, orientando ou
executando. O modo `auto` é especial e concede autonomia dentro de um objetivo.

## Quando usar

- `study`: aprender um conceito, tecnologia ou padrão com exemplos.
- `work`: fazer uma tarefa real com mentoria, você no teclado.
- `prod`: delegar a execução de uma tarefa à IA.
- `auto`: delegar um objetivo inteiro, sem confirmar cada passo.

## Altera alguma coisa?

`study`, `work` e `prod` não alteram nada e não mudam autorizações: `do`,
issue, branch e travas de Git continuam valendo. `mode: work` não equivale a
`$yabook dev`.

`auto` dispensa `do`, `bypass` e aprovações de checkpoint no objetivo pedido; a
IA pode implementar, commitar, abrir e integrar PR. Perguntas e prévias seguem
sem escrita, e as permissões do ambiente continuam valendo. Vale só nesta
conversa e neste projeto, até você escolher outro modo; não é salvo nem passa
para outra sessão.

## Sintaxe

```text
$yabook mode: <study|work|prod|auto> [- objetivo]
$yabook def mode <modo> for <área>
```

- `mode: <modo>`: aplica o modo à conversa.
- `def mode <modo> for <área>`: define o modo de uma área do projeto, que só
  fica salvo no planejamento com `do plan`; não aceita `auto`.

## Exemplos

```text
$yabook mode: work
$yabook mode: study - me ensine requisições HTTP no React
$yabook mode: auto - implemente as melhorias e organize os commits
```

- Passa a orientar e revisar enquanto você implementa.
- Explica o tema progressivamente, com exemplos pequenos.
- Executa o objetivo de ponta a ponta, organizando branches e commits.

## Relacionados

- `dev`: implementa a issue atual, independente do modo.
- `bypass`: dispensa issue e branch para uma ação pontual.
- `resume`: repassa o contexto; o modo `auto` não é transferido.
