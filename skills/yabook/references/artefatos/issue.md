# Issues

## Formato

- Título objetivo, sem prefixo de tipo.
- Labels para tipo e área.
- `Size` de `1` a `5` no Project; nunca como label ou no título.

```md
## Resumo rápido

- Tarefa:
- Entrega esperada:
- Limite:

## Escopo

-

## Critérios de aceite

-
```

Use `<details>` somente para contexto de IA que altere execução ou continuidade.

## Classificação

Retorne labels, `Size`, justificativa curta, confiança e sugestão de quebra
quando `Size` for `5`.

- `1`: ajuste rápido e baixo risco;
- `2`: tarefa pequena;
- `3`: tarefa média;
- `4`: tarefa grande com várias partes;
- `5`: alta incerteza; proponha divisão.

Para criar ou validar no GitHub, carregue também `github.md` e confira labels,
Project, campos e itens equivalentes reais.
