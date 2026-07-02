# Issues e Projects no GitHub

Toda mudança relevante mantém a sequência:

```text
Demanda -> Issue -> Branch -> Implementação -> Commit -> PR -> Merge -> Release
```

Não trabalhe duas issues na mesma branch.

`issue` propõe o artefato; `do issue` cria o conteúdo aprovado. Use título
objetivo, labels de tipo e área e `Size` no Project.

Labels oficiais:

- tipo: `bug`, `feature`, `docs`, `refactor`, `tooling`;
- área: `frontend`, `backend`, `infra`, `ui/ux`, `architecture`, `process`;
- especial: `epic`.

Cada projeto declara somente as labels que utiliza.

## Size

| Size | Uso |
| --- | --- |
| `1` | Ajuste rápido, baixo risco e escopo evidente. |
| `2` | Tarefa pequena, poucos arquivos ou pouca incerteza. |
| `3` | Tarefa média, implementação ou revisão normal. |
| `4` | Tarefa grande, várias partes ou análise relevante. |
| `5` | Alta incerteza; proponha divisão. |

`Size` é campo do Project, nunca label ou parte do título. Toda issue relevante
recebe o valor quando o projeto usa YA LABS. Se a ferramenta não conseguir
preenchê-lo, informe o valor para ajuste manual.

Colunas recomendadas: `Backlog`, `Pendente`, `Em andamento`, `Concluído` e
`Ideias futuras`.
