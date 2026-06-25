# Fluxo de trabalho com GitHub

Este documento define o padrão da YA LABS para issues, branches, commits, Pull Requests, Projects e releases.

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

## Issues

Issue é cartão de tarefa. Ela deve ser rápida para leitura humana e suficiente para orientar execução.

Título:

```text
descrição objetiva da tarefa
```

Não use prefixos como `docs:`, `feat:` ou `fix:` no título. Use labels para tipo e área.

### Estrutura recomendada

```md
## Resumo rápido

- Tarefa: descreva em uma frase.
- Entrega esperada: informe o resultado visível ou documental.
- Limite: informe o principal fora de escopo, se existir.

## Escopo

- Item principal da tarefa.
- Arquivo, tela, fluxo, regra ou documento envolvido.
- Ajuste relevante para concluir a entrega.

## Critérios de aceite

- Resultado mínimo para considerar a issue pronta.
- Conferência essencial para validar a entrega.
```

Esse é o padrão base. Tarefas simples devem parar aqui.

### Contexto para IA

Quando a issue for usada como handoff para IA ou pessoa que precisa de mais contexto, coloque detalhes adicionais em bloco recolhido:

```md
<details>
<summary>Contexto para IA</summary>

## Referências

- Documentos, decisões, PRs ou issues relacionadas.

## Cuidados

- Limites, riscos ou decisões que evitam retrabalho.

## Validação sugerida

- Testes, build, revisão visual ou conferência manual relevante.

</details>
```

Use esse bloco só quando ele reduzir dúvida real. Não transforme toda issue em documento longo.

### Seções opcionais

Inclua somente quando forem úteis:

| Seção | Quando usar |
| --- | --- |
| `Fora de escopo` | Há risco claro de expansão indevida. |
| `Entrega visual esperada` | A tarefa altera interface ou fluxo visível. |
| `Referências` | A execução depende de documentos, PRs ou decisões. |
| `Riscos` | Há risco técnico, operacional ou de produto. |
| `Dependências` | Existe bloqueio real por outra entrega ou decisão. |

Não inclua `Dependências` quando não houver bloqueio.

## Branches

Cada issue deve ter branch própria.

Padrão:

```text
numero-da-issue-descricao-curta
```

Exemplos:

```text
17-reestrutura-yabook-para-ia
187-redesenha-preview-pacotes
28-corrige-total-com-desconto
```

Regras:

- Comece pelo número da issue.
- Use descrição curta em kebab-case.
- Não use `issue`, `#`, tipo ou área no nome.
- Não use acentos, espaços ou caracteres especiais.

Não use:

```text
docs017-reestrutura-yabook
docs/issue17-reestrutura-yabook
front/feat017-reestrutura-yabook
issue17-reestrutura-yabook
```

Tipo e área pertencem às labels da issue, não ao nome da branch.

## Commits

Use o padrão:

```text
tipo: descrição curta
```

Exemplos:

```text
docs: simplifica padrão de branches
feat: adiciona tela de login
fix: corrige validação do token
chore: ajusta configuração de build
refactor: reorganiza serviço de autenticação
```

Tipos comuns:

```text
feat
fix
docs
chore
refactor
```

Evite mensagens genéricas como `ajustes`, `update`, `alterações` ou `teste`.

Escopo opcional pode ser usado quando o projeto já adotar esse costume:

```text
docs(github): simplifica padrão de branches
feat(frontend): adiciona tela de login
```

Não torne escopo obrigatório no padrão da YA LABS.

## Pull Requests

O título do PR deve ser objetivo e não precisa repetir o tipo da mudança.

Título recomendado:

```text
Reestruturar YABook para melhorar contexto de IA
```

O vínculo com a issue deve ficar no corpo:

```md
Closes #17
```

### Template de PR

```md
## Contexto

Explique em poucas linhas o objetivo do PR.

Closes #numero

## O que mudou

- Mudança principal.
- Arquivo, fluxo, regra ou documento ajustado.
- Decisão relevante para revisão.

## Observações

- Validações feitas.
- Limitações conhecidas.
- Pontos que merecem atenção.
```

Se o PR alterar contrato de API, inclua uma seção curta com método, rota, request/response e estados relevantes. Se não alterar API, não inclua essa seção.

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
