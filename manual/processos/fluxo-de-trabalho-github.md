# Fluxo de trabalho com GitHub

Este documento explica o fluxo da YA LABS para organizar trabalho com GitHub.

Use este guia quando for criar, revisar ou orientar trabalho executável no GitHub. Ele deve ser prático: a pessoa precisa entender a tarefa rápido, e a IA precisa ter regras claras para não inventar padrão.

## Regra principal

O fluxo começa quando surge uma coisa nova para fazer no projeto: problema,
ajuste, melhoria, funcionalidade, documentação ou decisão técnica.

Antes de implementar, transforme essa demanda em uma issue que deixe claro o
que precisa ser entregue e onde termina o trabalho.

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

Esse é o fluxo individual. Issues pacote registram o propósito geral de um
conjunto de entregas; ajustes pontuais podem seguir a exceção via `bypass`.
`mode: auto` dispensa confirmações do método dentro do objetivo delegado, sem
dispensar organização, validação ou preservação de trabalho existente.

## Entrada de uma nova demanda

Quando a pessoa citar algo novo que precisa ser feito:

1. entenda o problema ou resultado desejado;
2. consulte o contexto real necessário;
3. delimite escopo, entrega esperada e critérios de aceite;
4. proponha a issue;
5. crie a issue quando houver autorização;
6. somente então crie a branch e inicie a implementação.

Com a skill:

```text
$yabook issue
$yabook do issue
$yabook branch name
$yabook do branch
```

`$yabook issue` transforma a demanda em uma proposta pronta para revisão.
`$yabook do issue` cria o item aprovado no GitHub. A issue passa a ser a fonte
principal da execução individual. Use texto ou bullets simples em issues e PRs,
sem checklists de progresso, inclusive nos blocos para IA.

Não exija que a pessoa chegue com uma issue já escrita. Ela pode descrever a
necessidade em linguagem natural; a IA deve ajudar a convertê-la em trabalho
executável sem inventar requisitos.

### Issues pacote

`$yabook issue package [propósito geral]` prepara a prévia;
`$yabook do issue package` cria o pacote. `do issue` depois de uma prévia
inequívoca de pacote mantém esse formato. Não confunda com `issue batch`, que
prepara várias issues.

A issue identifica o pacote com uma descrição estável e genérica. Não exija
formulário de demandas iniciais, limites ou encerramento. Não copie os pontos de
um documento recebido para escopo, critérios de aceite ou informações para IA.
O documento e os pedidos autorizados orientam o desenvolvimento; podem ser
referenciados quando útil, sem duplicação na issue.

- Uma issue, uma branch e um PR organizam o pacote.
- Novas demandas entram pelos pedidos, sem editar o corpo ou registrar pendências
  na issue e sem exigir uma issue por entrada.
- Cada entrega fica registrada em um commit documentado.
- O PR resume assuntos e corpos dos commits contra a base e confere o diff final,
  evitando declarar entregas revertidas ou removidas.
- Use merge commit para preservar os commits e seus corpos. Se indisponível,
  informe o impedimento antes de escolher uma alternativa.
- O merge do PR encerra o pacote; demandas posteriores usam outro pacote ou issue.

#### Trabalho em dupla

As duas pessoas usam a mesma branch, trabalhando por turnos. Combine quem assume
o pedido atual e mantenha documentos e referências acessíveis a ambas.

Ao assumir, confira branch e worktree e atualize a partir dos commits publicados
pela outra pessoa, preservando alterações locais. Ao entregar o turno, valide,
registre commits documentados e publique o trabalho autorizado. Fora de `auto`,
as mutações seguem `do`; a coordenação não concede autorização Git.

Evite edição simultânea nessa branch. O PR final reúne as entregas das duas
pessoas, sem exigir issue ou branch por pessoa.

### Ajustes pontuais

Recomende `$yabook bypass <ajuste>` quando a alteração tiver objetivo específico,
impacto delimitado e puder formar um único commit compreensível e validável.
Um commit grande ou arriscado ainda pode justificar issue própria.

`bypass` dispensa issue e branch própria só para a ação anexada. Confira branch e
worktree e preserve trabalho de outra responsabilidade. Depois da implementação,
sugira o commit completo conforme [Padrões rápidos](../padroes/padroes-rapidos.md),
registrando motivo, alteração e exceção. Fora de `auto`, crie o commit
somente com `$yabook do commit`, sem voltar a exigir issue para essa conclusão.

### Execução autônoma

`$yabook mode: auto` ativa autorização contínua na conversa do projeto atual.
O agente escolhe o caminho adequado, implementa, valida, organiza branches e
commits sem exigir `do`, `bypass` ou aprovação de checkpoints do próprio trabalho.
Operações remotas só entram quando fazem parte do pedido; merge exige pedido
explícito, dispensando a sintaxe `do`. Pedidos informativos continuam sem escrita.

Preserve alterações existentes e use isolamento quando necessário. Interrompa
somente por decisão indispensável, risco concreto de perder trabalho ou aprovação
exigida pelo ambiente. Outro modo, troca de projeto ou nova sessão encerra essa
autorização; não persista a ativação. Veja [Skill YABook](../guias/skill-yabook.md).

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

### Size da issue

`Size` é um campo do GitHub Project para estimar o tamanho da issue. Não é label e não deve aparecer no título.

Toda issue relevante vinculada ao Project deve receber `Size`:

| Size | Uso |
| --- | --- |
| `1` | Ajuste rápido, baixo risco e escopo evidente. |
| `2` | Tarefa pequena, poucos arquivos ou pouca incerteza. |
| `3` | Tarefa média, exige implementação ou revisão normal. |
| `4` | Tarefa grande, envolve várias partes, análise relevante ou coordenação. |
| `5` | Tarefa muito grande, alta incerteza ou candidata a ser quebrada. |

Se a IA sugerir `Size 5`, ela deve sugerir também uma divisão em issues menores.

Use Markdown para conhecimento estável. Use GitHub para backlog, responsáveis, status, milestones, épicos, Pull Requests e progresso operacional.

## Labels

Labels classificam o tipo, o domínio ou o agrupamento especial da issue. Branch
e título de PR não devem repetir essa classificação.

Esta tabela é a base oficial de nomenclatura, cor e uso das labels da YA LABS:

| Label | Tipo | Cor | Uso |
| --- | --- | --- | --- |
| `bug` | Tipo | `#D73A4A` | Algo não funciona como esperado. |
| `feature` | Tipo | `#0E8A16` | Nova entrega funcional. |
| `docs` | Tipo | `#0075CA` | Documentação, guias, contratos, ADRs ou ajustes textuais. |
| `refactor` | Tipo | `#C5DEF5` | Alteração interna sem nova funcionalidade ou correção de bug. |
| `frontend` | Domínio | `#FBCA04` | Interface, telas e componentes. |
| `backend` | Domínio | `#1D76DB` | Regras internas, APIs, comandos e integrações. |
| `infra` | Domínio | `#006B75` | Deploy, ambiente, rede e serviços. |
| `ui/ux` | Domínio | `#D876E3` | Experiência, layout e critérios visuais. |
| `architecture` | Domínio | `#5319E7` | Decisões estruturais. |
| `process` | Domínio | `#5319E7` | Fluxo de trabalho e governança. |
| `ai` | Domínio | `#5319E7` | Skills, agentes, prompts e instruções de IA. |
| `tooling` | Domínio | `#5319E7` | Scripts, automações e ferramentas de desenvolvimento. |
| `epic` | Especial | `#5319E7` | Agrupador macro de capacidade. |

Sugira somente as labels oficiais que melhor organizem a demanda, sem exigir
uma combinação fixa de categorias. Cada projeto deve adotar essa nomenclatura
sem criar variações de nome quando a label oficial atender ao caso.

## Padrões operacionais

Os formatos oficiais de issue, branch, commit e Pull Request ficam em [Padrões rápidos](../padroes/padroes-rapidos.md).

Não repita esses formatos em documentos específicos de projeto. Referencie o padrão central e registre exceções apenas quando o projeto realmente precisar fugir dele.

Neste fluxo:

- demanda descreve o problema, ajuste ou melhoria desejada;
- issue transforma a demanda em trabalho executável e define seus limites;
- branch isola o trabalho da issue;
- commits registram alterações pequenas e claras;
- Pull Request explica o que mudou e vincula a issue;
- merge integra o trabalho revisado.

## Branches `main`, `dev` e `release`

Use esta seção para decidir quando trabalhar direto na `main`, quando criar `dev` e quando usar `release/x.y.z`.

`main` é a branch estável do projeto. Ela deve representar conteúdo publicado, pronto para release ou pronto para virar tag.

Não crie `dev` durante documentação inicial, planejamento, prototipagem exploratória ou provas técnicas que ainda não serão produto.

Nessas fases, use:

```text
main -> branch da issue -> Pull Request para main
```

Crie `dev` quando começar o desenvolvimento de produto:

- código que deve entrar em uma versão;
- mais de uma issue de implementação no mesmo ciclo;
- necessidade de integrar várias tarefas antes de publicar;
- necessidade de manter `main` estável enquanto o ciclo ainda está em andamento.

`dev` representa o ciclo atual de desenvolvimento. Ela não deve ser tratada como branch permanente do projeto.

Durante o ciclo:

```text
main -> dev
dev -> branch da issue
branch da issue -> Pull Request para dev
```

### Publicação direta a partir de `dev`

Quando `dev` já estiver validada e não precisar de revisão adicional por analista, homologação ou ajuste final, abra Pull Request de `dev` para `main`.

Depois do merge em `main`:

1. Crie a tag da versão em `main`.
2. Encerre a `dev` do ciclo.
3. Crie uma nova `dev` a partir da `main` para o próximo ciclo, se houver novo desenvolvimento.

Se o merge para `main` for feito com squash and merge, não continue usando a mesma `dev`. Como os commits originais não entram na `main` com os mesmos hashes, eles podem reaparecer em Pull Requests futuros.

### Mensagem de squash merge

Quando usar squash merge, o commit final deve preservar o PR e o histórico da branch.

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

Ao usar `gh pr merge --squash`, prefira passar o corpo por arquivo com `--body-file` para preservar quebras de linha.

### Branch de release

Use `release/x.y.z` quando a versão ainda precisar passar por revisão, homologação ou ajustes finais antes de entrar na `main`.

Padrão de branch de release:

```text
release/x.y.z
```

Fluxo:

```text
dev -> release/x.y.z
release/x.y.z -> ajustes finais
release/x.y.z -> Pull Request para main
main -> tag vx.y.z
```

Título de PR de release:

```text
Publicar versão x.y.z
```

Descrição recomendada:

```md
## Resumo rápido

- Objetivo: publicar a versão x.y.z.
- Entrega:
- Issue:

## O que mudou

- Principais entregas.
- Principais correções.
- Ajustes de documentação ou processo.

## Validações

- Testes, build ou conferências realizadas.

## Observações

- Riscos aceitos ou limitações conhecidas.

<details>
<summary>Informações para IA</summary>

- Contexto:
- Validações:
- Riscos:

</details>
```

A tag deve ser criada somente depois que a release estiver integrada na branch principal.

### Arquivamento de `dev`

Depois que uma versão for publicada, a fonte oficial da versão é `main` com a tag `vx.y.z`.

Se o time quiser preservar a branch de integração daquele ciclo, arquive a `dev` antiga antes de criar a próxima:

```text
archive/dev-x.y.z
```

Exemplo:

```text
archive/dev-1.0.0
```

Esse arquivamento é opcional. Use quando for útil consultar a integração do ciclo depois da publicação.

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
