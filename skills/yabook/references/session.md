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
2. Resolva o repositório ativo conforme `workspace.md`, sem assumir o `cwd`.
3. Valide `.git`, arquivos ativos, `AGENTS.md` e remote na raiz resolvida.
4. Use essa raiz como `workdir` explícito para os comandos seguintes.
5. Inspecione o estado do Git: `git status --short --branch`, branch atual e `git diff --stat`.
6. Monte a resposta curta para a pessoa usuária.
7. Guarde o cache abaixo como fonte principal até o fim da conversa.

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

### Workspace e repositório

- O workspace ativo prevalece sobre o `cwd` quando identificar inequivocamente
  outro repositório.
- Caminhos explícitos, raiz informada pela IDE e arquivos ativos são sinais
  prioritários; `cwd` é apenas o último candidato.
- Valide a raiz por `.git`, `AGENTS.md` e remote antes de consultar branch,
  issue ou GitHub.
- Execute comandos com `workdir` definido para a raiz resolvida.
- Divergência ou ambiguidade material bloqueia escrita até confirmação.
- Mudança de workspace invalida o repositório guardado no cache.

Leia `workspace.md` para o fluxo completo.

### Segurança de comandos Git

- Sem `do`, execute somente inspeções como `status`, `diff`, `log`, `show` e
  consultas de branch ou remote.
- Branch, switch, add, restore, commit, stash, merge, rebase, cherry-pick,
  revert, reset, tag, clean, fetch, pull e push exigem `do`.
- A autorização vale somente para a ação explicitamente solicitada.
- `do commit` isolado não autoriza `push`; `do pr` pode enviar somente a branch
  necessária ao PR, criar commits coerentes e não autoriza merge.
- `do merge` pode preparar o PR ausente e integrar após as validações.
- `dev` autoriza preparar branch, implementar e validar, mas não entregar.
- `bypass` não substitui `do` para mutações Git.
- Pedidos diretos sem `$yabook` não autorizam mutações Git.

Leia `git.md` sempre que uma solicitação consultar ou alterar Git.

### Desenvolvimento da issue

- `$yabook dev` identifica a issue, prepara e vincula a branch, atualiza status,
  implementa e valida.
- Sem issue inequívoca, pare e solicite indicação ou criação.
- `dev` não cria commit, PR ou merge sozinho.
- `dev & do pr` entrega um PR completo.
- `dev & do merge` entrega e integra após validar condições.

Leia `dev.md` para esse fluxo.

### Modos de colaboração

- `study`: estudo interativo e progressivo para aprender um tema.
- `dev`: mentoria para a pessoa usuária implementar uma tarefa real.
- `prod`: execução delegada ao agente dentro das autorizações existentes.
- Modos ajustam postura, explicação e autonomia; não alteram travas de Git,
  GitHub, issue, `do`, `bypass`, PR, merge ou release.
- `mode: dev` é modo de colaboração e não equivale ao comando operacional
  `$yabook dev`.
- A precedência é: modo one-shot, modo da conversa, modo por área do projeto e
  padrão YABook.

Leia `modes.md` para `mode`, `mode:`, `def mode` e definições em linguagem
natural.

Antes de novas edições:

- atualize `status`, diff staged e unstaged e último commit no mesmo turno;
- nunca interrompa com base apenas no cache da conversa;
- avalie se o worktree contém um bloco concluído de outra responsabilidade;
- proponha um commit quando o bloco for independente e reversível;
- aceite `$yabook do` como autorização contextual somente para uma ação
  pendente inequívoca;
- aceite `$yabook continue` para rejeitar checkpoint opcional;
- retome a solicitação original após a escolha;
- execute seus pré-requisitos mínimos já autorizados sem nova confirmação;
- não permita `continue` quando issue ou branch incompatível tornar a separação
  obrigatória.

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
- `$yabook discuss <tema>`: discussão geral sem decisão automática.
- `$yabook plan discuss <tema>`: alias de compatibilidade para `discuss`.
- `$yabook plan roadmap`: proposta de milestones, épicos e próximo bloco.
- `$yabook plan review`: revisão antes da consolidação ou do roadmap.
- `$yabook do plan`: consolidação documental sem commit automático.
- `$yabook do plan roadmap`: materialização idempotente do próximo bloco.
- `$yabook sync`: comparação somente leitura entre origem e instalação.
- `$yabook do sync`: sincronização e validação da instalação.

Leia `planejamento.md` para esses comandos. O cache não substitui a descoberta
atual do projeto nem a conferência do GitHub.

Leia `discuss.md` para discussões gerais. Quando o tema afetar o planejamento,
aplique também as regras específicas de `planejamento.md`.

### Orquestração inteligente

- `$yabook <intenção>` seleciona internamente os comandos adequados.
- Comandos seguros de leitura avançam até uma decisão necessária ou escrita.
- Comando válido é executado; uma opção melhor pode ser sugerida brevemente.
- Comando incompatível com intenção inequívoca pode ser corrigido.
- Ambiguidade material exige pergunta.
- Roteamento inferido, ajustado ou composto aparece no início da resposta.
- `do` nunca é inferido.
- Fluxos com várias etapas apenas sugerem `$yabook steps start`, com motivo.

Leia `orquestracao.md` para aplicar essas regras.

### Acompanhamento de etapas

- `$yabook steps start`: cria um checklist a partir da sequência discutida.
- `$yabook steps`: mostra o checklist ativo.
- `$yabook steps done <número>`: conclui uma etapa.
- `$yabook steps cancel`: encerra o acompanhamento.
- Confirmações inequívocas em linguagem natural também podem concluir etapas.
- Ações fora da sequência devem ser classificadas antes da resposta.
- Ajustes que preservam objetivo e escopo podem recalcular etapas pendentes.
- Etapas concluídas permanecem no histórico e nunca são reordenadas.
- Dependências quebradas geram correção ou revalidação quando necessário.
- Mudanças de objetivo, escopo ou decisão exigem confirmação.
- Trabalho desnecessário não entra no checklist.
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
| Primeiro comando dependente do repositório ou mudança de workspace | `workspace.md` |
| `$yabook init` | `init.md` |
| `$yabook diagnose` e `$yabook plan ...` | `planejamento.md` |
| `$yabook discuss ...` | `discuss.md` |
| `$yabook <intenção em linguagem natural>` | `orquestracao.md` |
| Operações Git | `git.md` |
| `$yabook dev` | `dev.md` |
| `$yabook mode...` e definições de modo | `modes.md` |
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
