# GitHub no padrão YABook

Use esta referência para issues, branches, commits, Pull Requests, labels, Projects e releases.

## Regra principal

Toda mudança relevante deve manter rastreabilidade:

```text
Issue -> Branch -> Commit -> Pull Request -> Merge -> Release
```

Não trabalhe duas issues diferentes na mesma branch.

## Issues

Título objetivo, sem prefixo de tipo. Use labels para tipo e área.

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
