# Issues

## Formato

- Título objetivo, sem prefixo de tipo.
- Sugira somente labels do catálogo oficial que melhorem a organização da
  demanda. Não exija combinação fixa de tipo e domínio.
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

## Saída de `$yabook issue`

Entregue somente o artefato operacional: título, corpo, labels oficiais
sugeridas e `Size` para o Project. Não inclua justificativa, confiança ou
sugestão de quebra no artefato final.

Para sugerir labels, carregue `github/issues-projects.md` e use o catálogo
canônico do YABook, mesmo que o repositório ainda não tenha todas as labels
configuradas. Não invente nomes, variações ou labels semânticas fora desse
catálogo.

## Classificação auxiliar

`$yabook issue classify` pode retornar labels, `Size`, justificativa curta,
confiança e sugestão de quebra quando `Size` for `5`. Mantenha justificativa,
confiança e sugestão de quebra em uma seção de análise auxiliar, separada do
artefato final da issue.

- `1`: ajuste rápido e baixo risco;
- `2`: tarefa pequena;
- `3`: tarefa média;
- `4`: tarefa grande com várias partes;
- `5`: alta incerteza; proponha divisão.

Para criar ou validar, confira Project, campos e itens equivalentes reais. A
criação com `do issue` mantém seu fluxo operacional.
