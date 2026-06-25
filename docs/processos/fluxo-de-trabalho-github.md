# Fluxo de trabalho com GitHub

Este documento explica o fluxo da YA LABS para organizar trabalho com GitHub.

Use este guia quando for criar, revisar ou orientar trabalho executável no GitHub. Ele deve ser prático: a pessoa precisa entender a tarefa rápido, e a IA precisa ter regras claras para não inventar padrão.

## Regra principal

Toda mudança relevante deve manter rastreabilidade:

```text
Issue -> Branch -> Commit -> Pull Request -> Merge -> Release
```

Não trabalhe duas issues diferentes na mesma branch.

## GitHub Projects

O GitHub Project é o quadro oficial de acompanhamento do projeto.

Em projetos da YA LABS, toda issue relevante deve ser vinculada ao Project aplicável. Quando ainda não houver Project definido, a IA deve perguntar ou registrar a exceção.

Colunas recomendadas:

```text
Backlog
Pendente
Em andamento
Concluído
Ideias futuras
```

Use Markdown para conhecimento estável. Use GitHub para backlog, responsáveis, status, milestones, épicos, Pull Requests e progresso operacional.

## Labels

Labels classificam o tipo e a área da issue. Branch e título de PR não devem repetir essa classificação.

Base recomendada:

| Label | Tipo | Cor | Uso |
| --- | --- | --- | --- |
| `bug` | Tipo | `#D73A4A` | Algo não funciona como esperado. |
| `feature` | Tipo | `#0E8A16` | Nova entrega funcional. |
| `docs` | Tipo | `#0075CA` | Documentação, guias, contratos, ADRs ou ajustes textuais. |
| `refactor` | Tipo | `#C5DEF5` | Alteração interna sem nova funcionalidade ou correção de bug. |
| `tooling` | Tipo | `#5319E7` | Scripts, automações e ferramentas de desenvolvimento. |
| `frontend` | Área | `#FBCA04` | Interface, telas e componentes. |
| `backend` | Área | `#1D76DB` | Regras internas, APIs, comandos e integrações. |
| `infra` | Área | `#006B75` | Deploy, ambiente, rede e serviços. |
| `ui/ux` | Área | `#D876E3` | Experiência, layout e critérios visuais. |
| `architecture` | Área | `#5319E7` | Decisões estruturais. |
| `process` | Área | `#5319E7` | Fluxo de trabalho e governança. |
| `epic` | Especial | `#5319E7` | Agrupador macro de capacidade. |

Cada projeto deve declarar apenas as labels que realmente usa.

## Padrões operacionais

Os formatos oficiais de issue, branch, commit e Pull Request ficam em [Padrões rápidos](../padroes-rapidos.md).

Não repita esses formatos em documentos específicos de projeto. Referencie o padrão central e registre exceções apenas quando o projeto realmente precisar fugir dele.

Neste fluxo:

- issue define a tarefa e seus limites;
- branch isola o trabalho da issue;
- commits registram alterações pequenas e claras;
- Pull Request explica o que mudou e vincula a issue;
- merge integra o trabalho revisado.

## Releases

Use release quando houver uma versão consolidada para publicação ou validação.

Nem todo projeto precisa de branch `dev` desde o começo. Adote branch de desenvolvimento quando houver implementação ativa, trabalho paralelo ou necessidade de proteger a branch principal.

Padrão de branch de release:

```text
release/x.y.z
```

Título de PR de release:

```text
Publicar versão x.y.z
```

Descrição recomendada:

```md
## Contexto

Publica a versão x.y.z.

## O que mudou

- Principais entregas.
- Principais correções.
- Ajustes de documentação ou processo.

## Validações

- Testes, build ou conferências realizadas.

## Observações

- Riscos aceitos ou limitações conhecidas.
```

A tag deve ser criada somente depois que a release estiver integrada na branch principal.

## Orientação para IA

Antes de criar issue, branch, commit, PR, release ou documentação, a IA deve:

1. Ler o `AGENTS.md` do projeto.
2. Verificar se há padrão local documentado.
3. Consultar o YABook quando o projeto usar padrões da YA LABS.
4. Conferir issue, branch atual, tipo da mudança e área afetada.
5. Apontar divergências antes de executar.
6. Registrar exceção quando o usuário pedir algo fora do padrão.

A IA não deve inventar formatos quando já houver padrão documentado.

## Lotes documentais

Alterações pequenas e relacionadas podem ser agrupadas em uma issue, branch e PR quando fizerem parte do mesmo objetivo.

Use lote documental quando:

- os documentos forem pequenos e relacionados;
- a revisão puder acontecer no mesmo PR;
- a issue principal tiver escopo claro.

Use issues separadas quando:

- os temas forem independentes;
- houver impacto alto;
- a validação exigir revisão própria;
- existirem responsáveis ou dependências diferentes.

Mesmo em lote, preserve a rastreabilidade:

```text
Issue principal -> Branch de lote -> Commit -> Pull Request -> Merge
```

## Integração front-end e back-end

Quando uma API for criada ou alterada, documente o contrato na issue, no PR ou em `docs/contratos/`, conforme o tamanho da mudança.

Contrato mínimo:

- método e rota;
- parâmetros principais;
- exemplo de request, quando existir;
- exemplo de response;
- estados de sucesso, erro e vazio.

Front-end pode começar com mock enquanto o back-end não estiver pronto, mas a troca para API real deve estar clara na issue ou no PR.
