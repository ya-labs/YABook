# Modos de colaboração

Modos ajustam postura, profundidade e autonomia; não alteram permissões,
exigência de issue, `do`, `bypass`, PR, merge ou release.

Carregue somente o modo solicitado:

- [study](modes/study.md): aprendizagem progressiva;
- [work](modes/work.md): implementação guiada;
- [prod](modes/prod.md): execução delegada.

Sintaxe:

```text
$yabook mode: work
$yabook mode: prod - faça o ajuste
$yabook def mode study for Angular
```

Precedência: modo da solicitação, conversa, área e padrão. Modo da conversa é
temporário. Modo por área só é persistido por `do plan`.
