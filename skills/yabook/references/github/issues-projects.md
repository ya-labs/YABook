# Issues e Projects no GitHub

Toda mudança relevante mantém a sequência:

```text
Demanda -> Issue -> Branch -> Implementação -> Commit -> PR -> Merge -> Release
```

Não trabalhe duas issues na mesma branch.

`issue package` mantém descrição estável, sem lista de demandas ou pendências;
novos pedidos dispensam atualizar a issue. Issues e PRs não contêm checklists.
Ajustes pontuais via `bypass` ou
`auto` podem dispensar issue e branch própria, com commit documentado. Consulte
`artefatos/issue-package.md` para pacotes e `bypass.md` para ajustes pontuais.

`issue` propõe o artefato; `do issue` cria o conteúdo aprovado. Use título
objetivo, labels oficiais úteis à organização e `Size` no Project.

Labels oficiais:

- tipo: `bug`, `feature`, `docs`, `refactor`;
- domínio: `frontend`, `backend`, `infra`, `ui/ux`, `architecture`, `process`,
  `ai`, `tooling`;
- especial: `epic`.

Sugira uma ou mais labels canônicas quando elas melhorarem a organização da
demanda; não exija uma combinação fixa de categorias. Cada projeto deve adotar
essa nomenclatura sem criar variações de nome.

## Size

| Size | Uso |
| --- | --- |
| `1` | Agente conclui em menos de uma hora, uma sessão e um PR. |
| `2` | Uma sessão longa ou duas curtas, sem dependência externa. |
| `3` | Cerca de um dia ou validação fora do código. |
| `4` | Vários dias; outra equipe, QA ou retrabalho. |
| `5` | Semana ou mais; proponha divisão. |

Mede a entrega com agentes de IA (sessão, revisão e validação), não código
manual. Cresce com validação externa, regra indefinida e espera por terceiros.
Código que cabe numa sessão é `1`; `2`+ exige motivo fora do código. Risco
resolvido na sessão não conta; estimativa atribuída não é corrigida depois.

`Size` é campo do Project, nunca label ou parte do título. Toda issue relevante
recebe o valor quando o projeto usa YA LABS. Se a ferramenta não conseguir
preenchê-lo, informe o valor para ajuste manual.

Colunas recomendadas: `Backlog`, `Pendente`, `Em andamento`, `Concluído` e
`Ideias futuras`.
