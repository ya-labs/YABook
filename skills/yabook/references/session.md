# `$yabook load`

Use esta referência para o carregamento automático da primeira operação YABook
e para o comando explícito `$yabook load`.

## Objetivo

Reduzir buscas repetidas no repositório durante a mesma conversa.

O carregamento não cria memória permanente e não altera arquivos.

## Carregamento automático

No primeiro comando operacional `$yabook` da conversa, execute o fluxo de
carregamento abaixo silenciosamente e depois responda somente ao comando pedido.

Não repita o carregamento na mesma conversa. `$yabook help` é a única exceção e
pode responder sem contexto do repositório.

Use `$yabook load` para carregar explicitamente ou atualizar o cache quando a
branch, o repositório, as regras locais ou o contexto relevante mudarem.

## Como executar

Ao receber `$yabook load`:

1. Leia este arquivo por completo. Ele é o cache da sessão.
2. Leia `AGENTS.md` do repositório atual, se existir.
3. Inspecione o estado do Git: `git status --short --branch`, branch atual e `git diff --stat`.
4. Monte a resposta curta para a pessoa usuária.
5. Guarde o cache abaixo como fonte principal até o fim da conversa.

Não releia `github.md` nem `session.md` depois do load para comandos rotineiros listados nesta seção.

## Cache operacional da sessão

Use este bloco como fonte principal após o load.

### Rastreabilidade

```text
Demanda -> Issue -> Branch -> Implementação -> Commit -> Pull Request -> Merge -> Release
```

Regras:

- Não trabalhe duas issues diferentes na mesma branch.
- Issue relevante deve ter Project, labels e `Size` quando o projeto usa YA LABS.
- Use a issue como fonte principal quando ela já tiver contexto suficiente.

### Issue

- Título objetivo, sem prefixo de tipo.
- Labels para tipo e área.
- `Size` no GitHub Project, de `1` a `5`. Nunca é label e não entra no título.

Corpo base:

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

### `$yabook issue classify`

Retorne:

- labels de tipo;
- labels de área;
- `Size`;
- justificativa curta;
- nível de confiança;
- sugestão de quebra quando `Size` for `5`.

Escala de `Size`:

| Size | Uso |
| --- | --- |
| `1` | Ajuste rápido, baixo risco e escopo evidente. |
| `2` | Tarefa pequena, poucos arquivos ou pouca incerteza. |
| `3` | Tarefa média, exige implementação ou revisão normal. |
| `4` | Tarefa grande, envolve várias partes, análise relevante ou coordenação. |
| `5` | Tarefa muito grande, alta incerteza ou candidata a ser quebrada. |

### Branch

Formato YABook:

```text
numero-descricao-curta
```

Exemplo:

```text
17-reestrutura-yabook-para-ia
```

Não use tipo, área, `issue`, `#`, acentos ou espaços.

Base sugerida: `main` ou `dev`, conforme fluxo do projeto.

### Commit

Formato YABook:

```text
tipo: descrição curta
```

Tipos comuns: `feat`, `fix`, `docs`, `chore`, `refactor`.

Mensagem curta, objetiva e descrevendo exatamente a alteração.

### Pull Request

- Título objetivo, sem prefixo de tipo.
- Destino usual: `dev`, salvo regra local diferente.

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

### Squash merge

Quando fizer squash merge:

- inclua o número do PR no assunto do commit final, como `tipo: descrição curta (#numero)`;
- inclua no corpo o histórico dos commits da branch contra a branch alvo;
- gere o histórico com `git log --reverse --format='- %s (%h)' base..head`;
- use `--body-file` ao executar `gh pr merge --squash`.

### Release

Título de PR de release:

```text
Publicar versão x.y.z
```

Corpo base:

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
```

A tag deve apontar para o commit integrado na branch principal.

### Labels base

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

Cada projeto declara apenas as labels que usa.

### Fluxo `main`, `dev` e release

- `main`: branch estável, publicável ou pronta para tag.
- `dev`: ciclo atual de integração, quando o projeto usa esse fluxo.
- `release/x.y.z`: revisão, homologação ou ajuste final antes de `main`.

Se `AGENTS.md` definir outro fluxo, ele prevalece.

### Diagnóstico e planejamento

- `$yabook status`: branch, issue e alterações do trabalho local.
- `$yabook diagnose`: estado real do projeto inteiro.
- `$yabook plan status`: maturidade e lacunas do planejamento.
- `$yabook plan next`: uma próxima ação recomendada.
- `$yabook plan start <versão>`: entrevista colaborativa sem escrita.
- `$yabook plan discuss <tema>`: discussão sem decisão automática.
- `$yabook plan roadmap`: proposta de milestones, épicos e próximo bloco.
- `$yabook plan review`: revisão antes da consolidação ou do roadmap.
- `$yabook do plan`: consolidação documental sem commit automático.
- `$yabook do plan roadmap`: materialização idempotente do próximo bloco.
- `$yabook sync`: comparação somente leitura entre origem e instalação.
- `$yabook do sync`: sincronização e validação da instalação.

Leia `planejamento.md` para esses comandos. O cache não substitui a descoberta
atual do projeto nem a conferência do GitHub.

### Acompanhamento de etapas

- `$yabook steps start`: cria um checklist a partir da sequência discutida.
- `$yabook steps`: mostra o checklist ativo.
- `$yabook steps done <número>`: conclui uma etapa.
- `$yabook steps cancel`: encerra o acompanhamento.
- Confirmações inequívocas em linguagem natural também podem concluir etapas.
- Enquanto houver etapas abertas, repita o checklist compacto ao final de cada
  resposta.
- O checklist vale somente para a conversa e não executa ações por conta própria.

Leia `steps.md` para criar ou atualizar o checklist.

## Comandos que usam só o cache após o load

Depois de `$yabook load`, **não releia** `github.md` nem `session.md` para:

- `$yabook issue`
- `$yabook issue title`
- `$yabook issue desc`
- `$yabook issue classify`
- `$yabook branch name`
- `$yabook commit message`
- `$yabook pr`
- `$yabook pr title`
- `$yabook pr desc`
- `$yabook release`
- `$yabook status`

Para esses comandos, use:

1. o cache desta seção;
2. regras locais já lidas de `AGENTS.md` no load;
3. contexto da conversa;
4. estado do Git quando o artefato depender da alteração atual.

Em comandos encadeados com `&`, se um dos trechos for `load`, este cache passa a valer para os trechos seguintes.

Exemplo:

```text
$yabook init & load & commit msg
```

Nesse caso:

1. execute `init`;
2. carregue o cache com `load`;
3. gere `commit msg` usando o cache, regras locais e o diff atual.

## O que ainda exige inspeção após o load

Mesmo com o cache carregado, inspecione:

- `git diff` ou `git diff --stat` para commit, PR e release com base no código atual;
- issue, PR, labels, Project e `Size` reais quando for criar ou validar artefatos no GitHub;
- código e arquivos do projeto quando o pedido depender do conteúdo alterado.
- documentação, código e GitHub atuais para `diagnose`, `plan` e `do plan`.

## Quando reler referências mesmo após o load

Consulte documentos ou arquivos do projeto somente quando:

- o pedido for `$yabook init`, `$yabook docs`, `$yabook check` ou `$yabook review`;
- o pedido for `$yabook do` e exigir criação real no GitHub;
- o pedido contrariar o padrão carregado;
- houver dúvida sobre regra local não capturada no load;
- o contexto estiver incompleto;
- a pessoa pedir validação de conformidade.

Mapa de releitura:

| Comando | Referência |
| --- | --- |
| `$yabook init` | `init.md` |
| `$yabook diagnose` e `$yabook plan ...` | `planejamento.md` |
| `$yabook do plan ...` | `planejamento.md` |
| `$yabook steps ...` | `steps.md` |
| `$yabook sync` e `$yabook do sync` | `sync.md` |
| `$yabook docs` | `documentacao.md` |
| `$yabook check`, `$yabook review` | `github.md`, `documentacao.md`, `ia.md` conforme o artefato |
| `$yabook do` | `commands.md` + estado real do repo/GitHub |
| `$yabook help` | `commands.md` |

## Regras locais

Durante o load, leia `AGENTS.md` e registre na resposta as exceções que prevalecem sobre o YABook genérico.

Exemplos comuns de override:

- formato de branch diferente do padrão `numero-descricao-curta`;
- formato de commit com código de demanda;
- fluxo de merge diferente de `dev` -> `main`;
- tipos de commit específicos do projeto.

Quando houver override local, use o local nos comandos rotineiros sem reler `github.md`.

## Resposta esperada para a pessoa usuária

Responda de forma curta. Não copie este arquivo inteiro na resposta.

Modelo:

```text
YABook carregado para esta conversa.

Padrões principais:
- Issue: título objetivo, labels para tipo/área, Size no Project.
- Size: 1 rápido, 2 pequeno, 3 médio, 4 grande, 5 quebrar em issues menores.
- Branch: numero-descricao-curta.
- Commit: tipo: descrição curta.
- PR: título objetivo; corpo com Resumo rápido, O que mudou, Observações.
- GitHub: issue relevante deve ter Project, labels e Size.
- IA: usar a issue como fonte principal quando suficiente.

Regras locais:
- <resumo curto de AGENTS.md, se existir; senão "nenhuma exceção local encontrada">

Contexto atual:
- Branch: <nome>
- Issue inferida: <numero ou "não identificada">
- Alterações pendentes: <resumo curto ou "nenhuma">
```

Depois disso, use o cache desta sessão antes de consultar novamente o YABook.

## Limite

O contexto carregado vale apenas para a conversa atual.

Em nova conversa, o primeiro comando operacional `$yabook` executa novamente o
carregamento automático. Use `$yabook load` apenas para recarregar o contexto.
