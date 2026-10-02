# Modos de colaboração

`study`, `work` e `prod` ajustam postura e profundidade sem alterar autorizações.
`auto` concede autorização contínua dentro do objetivo delegado, dispensando
`do`, `bypass` e aprovação de checkpoints; não amplia permissões do ambiente.

Carregue somente o modo solicitado:

- [study](modes/study.md): aprendizagem progressiva;
- [work](modes/work.md): implementação guiada;
- [prod](modes/prod.md): execução delegada.
- [auto](modes/auto.md): execução autônoma com organização e rastreabilidade.

Sintaxe:

```text
$yabook mode: work
$yabook mode: prod - faça o ajuste
$yabook mode: auto - implemente as melhorias e organize os commits
$yabook def mode study for Angular
```

Precedência: modo da solicitação, conversa, área e padrão. Modo da conversa é
temporário. Modo por área só é persistido por `do plan`.

`auto` só pode ser ativado explicitamente para a conversa no projeto atual.
Não aceite `def mode auto for <área>` nem persista sua ativação. Outro modo,
troca de projeto ou nova sessão encerra essa autorização.
