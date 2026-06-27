# GitHub no padrão YABook

Use esta referência para issues, branches, commits, Pull Requests, labels, Projects e releases.

## Regra principal

Toda mudança relevante começa com uma demanda nova e deve manter rastreabilidade:

```text
Problema, ajuste ou melhoria
-> Issue
-> Branch
-> Implementação
-> Commit
-> Pull Request
-> Merge
-> Release
```

Não trabalhe duas issues diferentes na mesma branch.

## Issues

Quando a pessoa descrever algo novo para fazer, transforme a necessidade em uma
issue antes de criar branch ou implementar. Descubra somente o contexto
necessário e delimite tarefa, entrega esperada, limite e critérios de aceite.

`$yabook issue` propõe o artefato. `$yabook do issue` cria a issue aprovada.
Depois, use `branch name` e `do branch` para entrar no fluxo de execução.

Não exija uma issue pronta da pessoa e não invente requisitos ausentes.

Título objetivo, sem prefixo de tipo. Use labels para tipo e área. Use `Size` no Project para tamanho.

Estrutura base:

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

Use `<details>` apenas quando contexto extra para IA for realmente útil.

Ao criar issues com IA, sugira labels e `Size`. Se sugerir `Size 5`, proponha divisão em issues menores.

## Branches

Use:

```text
numero-descricao-curta
```

Exemplo:

```text
17-reestrutura-yabook-para-ia
```

Não use tipo, área, `issue`, `#`, acentos ou espaços.

## Commits

Use:

```text
tipo: descrição curta
```

Tipos comuns: `feat`, `fix`, `docs`, `chore`, `refactor`.

## Pull Requests

Título objetivo, sem prefixo de tipo.

Corpo base:

```md
## Resumo rápido

- Objetivo:
- Entrega:
- Issue:

Closes #numero

## O que mudou

- 

## Observações

- 

<details>
<summary>Informações para IA</summary>

- Contexto:
- Validações:
- Riscos:

</details>
```

Use `Informações para IA` apenas quando houver contexto útil para revisão ou continuidade.

## Squash merge

Quando fizer squash merge, a mensagem do commit final deve preservar rastreabilidade.

Assunto:

```text
tipo: descrição curta (#numero-do-pr)
```

Corpo:

```text
Histórico da branch contra branch-alvo:
- commit original 1 (hash)
- commit original 2 (hash)
- commit original 3 (hash)
```

Gere o histórico comparando a branch do PR contra a branch alvo:

```bash
git log --reverse --format='- %s (%h)' branch-alvo..branch-do-pr
```

Se usar `gh pr merge --squash`, prefira passar o corpo por arquivo com `--body-file`.

## Labels

Base oficial:

| Label | Tipo | Uso |
| --- | --- | --- |
| `bug` | Tipo | Algo não funciona como esperado. |
| `feature` | Tipo | Nova entrega funcional. |
| `docs` | Tipo | Documentação, guias, contratos, ADRs ou ajustes textuais. |
| `refactor` | Tipo | Alteração interna sem nova funcionalidade ou correção de bug. |
| `tooling` | Tipo | Scripts, automações e ferramentas de desenvolvimento. |
| `frontend` | Área | Interface, telas e componentes. |
| `backend` | Área | Regras internas, APIs, comandos e integrações. |
| `infra` | Área | Deploy, ambiente, rede e serviços. |
| `ui/ux` | Área | Experiência, layout e critérios visuais. |
| `architecture` | Área | Decisões estruturais. |
| `process` | Área | Fluxo de trabalho e governança. |
| `epic` | Especial | Agrupador macro de capacidade. |

Cada projeto deve declarar apenas as labels que usa.

## Projects

Toda issue relevante deve ser vinculada ao GitHub Project aplicável quando o projeto usa YA LABS.

Colunas recomendadas:

```text
Backlog
Pendente
Em andamento
Concluído
Ideias futuras
```

### Size

`Size` é campo do GitHub Project. Não é label e não deve aparecer no título da issue.

| Size | Uso |
| --- | --- |
| `1` | Ajuste rápido, baixo risco e escopo evidente. |
| `2` | Tarefa pequena, poucos arquivos ou pouca incerteza. |
| `3` | Tarefa média, exige implementação ou revisão normal. |
| `4` | Tarefa grande, envolve várias partes, análise relevante ou coordenação. |
| `5` | Tarefa muito grande, alta incerteza ou candidata a ser quebrada. |

Toda issue relevante vinculada ao Project deve receber `Size`.

Se a ferramenta não conseguir preencher `Size` no Project, informe o valor sugerido para preenchimento manual.

Se `Size` for `5`, sugira uma quebra em issues menores.

## `main`, `dev` e release

- `main`: branch estável, publicável ou pronta para tag.
- Não crie `dev` em documentação inicial, planejamento ou prototipagem.
- Crie `dev` quando começar desenvolvimento de produto e houver integração de várias issues.
- `dev` representa o ciclo atual, não uma branch permanente.
- Depois da release, crie nova `dev` a partir da `main` se houver novo ciclo.
- Arquive a anterior como `archive/dev-x.y.z` apenas se for útil.
- Use `release/x.y.z` quando houver revisão, homologação ou ajuste final antes de `main`.

## Release

Título de PR de release:

```text
Publicar versão x.y.z
```

Descrição base:

```md
## Resumo rápido

- Objetivo: publicar a versão x.y.z.
- Entrega:
- Issue:

## O que mudou

- 

## Validações

- 

## Observações

- 

<details>
<summary>Informações para IA</summary>

- Contexto:
- Validações:
- Riscos:

</details>
```

A tag deve apontar para o commit integrado na branch principal.
