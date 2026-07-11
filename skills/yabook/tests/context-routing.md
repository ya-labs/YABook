# Cenários de roteamento e contexto

Use estes casos para revisar mudanças no roteador. Em todos, confirme resposta,
referências carregadas, fontes consultadas e respeito às travas.

| Entrada | Rota esperada | Referências iniciais | Não deve carregar |
| --- | --- | --- | --- |
| `$yabook help` | `help` | `help.md` | workspace, Git, GitHub |
| `$yabook mode: study` | `mode` | `modes.md`, `modes/study.md` | workspace, GitHub |
| `$yabook mode: work` | `mode` | `modes.md`, `modes/work.md` | workspace, GitHub |
| `$yabook steps` | `steps` | `steps.md` | Git, artefatos |
| `$yabook step` | `step` | `steps.md` | Git, artefatos |
| `$yabook bypass ajuste o README na main` | `bypass` | `bypass.md` | planejamento, Project, release |
| `$yabook branch` | `branch name` | `roteamento.md`, `artefatos/branch-commit.md` | `contexto.md`, planejamento |
| `$yabook issue` | `issue` | `artefatos/issue.md` | `contexto.md`, planejamento, PRs não relacionados |
| `$yabook issue brief` | `issue brief` | `briefs.md` | GitHub, documentação ampla |
| `$yabook commit msg` | `commit message` | `roteamento.md`, `artefatos/branch-commit.md` | `contexto.md`, Project |
| `$yabook desejo saber a próxima etapa` | `plan next` | `orquestracao.md`, `planejamento/status-next.md` | `contexto.md`, diagnóstico completo |
| `$yabook plan start v1` | `plan start v1` | `planejamento/start.md` | `contexto.md`, GitHub completo |
| `$yabook plan brief` | `plan brief` | `briefs.md` | GitHub, histórico já condensado |
| `$yabook plan review` | `plan review` | `planejamento/review.md` | `contexto.md`, issues fechadas |
| `$yabook diagnose` | `diagnose` | `planejamento/diagnose.md` | `contexto.md`, Project inteiro, corpos em massa |
| `$yabook diagnose full` | `diagnose full` | `planejamento/diagnose.md` | `contexto.md`, respostas brutas sem filtro |
| `$yabook check` | `check` | `quality.md`, referência do alvo | coleções completas |
| `$yabook check full` | `check full` | `quality.md`, referência do alvo | fontes fora do escopo confirmado |
| `$yabook review` | `review` | `quality.md`, referência do alvo | coleções completas |
| `$yabook review full` | `review full` | `quality.md`, referência do alvo | fontes fora do escopo confirmado |
| `$yabook dev quick` | `dev quick` | `dev.md`, `git/checkpoint.md` | documentação geral, arquitetura inteira |
| `$yabook dev step` | `dev step` | `dev.md`, `git/checkpoint.md`, `steps.md` | etapas seguintes, documentação geral |
| `$yabook dev` | `dev` | `dev.md`, `git/checkpoint.md` | `contexto.md`, release sem relação |
| `$yabook dev full` | `dev full` | `dev.md`, `git/checkpoint.md` | fontes fora do escopo confirmado |
| `$yabook pr brief` | `pr brief` | `briefs.md` | GitHub, diff já confirmado |
| `$yabook dev & do pr` | `dev` → `do pr` | roteamento e referências das duas rotas | merge |

## Linguagem natural

As frases abaixo devem chegar à mesma rota:

```text
$yabook qual é a próxima etapa?
$yabook o que devo fazer agora?
$yabook veja o planejamento e recomende uma ação
```

Resultado: `plan next`, salvo quando a conversa indicar explicitamente status
local, caso em que `status` é mais adequado.

## Ambiguidade

```text
$yabook quero planejar o projeto
```

Pergunte se a pessoa quer iniciar uma versão, revisar a atual ou discutir uma
capacidade. Não escolha versão nem infira escrita.

## Segurança

```text
$yabook crie a issue e a branch
```

Gere a proposta ou informe `$yabook do issue branch`. Não transforme a intenção
em `do`.

```text
$yabook bypass faça commit
```

Recuse a mutação: `bypass` não substitui `$yabook do commit`.

## Encadeamento

Confirme que:

- os segmentos executam da esquerda para a direita;
- contexto válido é reutilizado;
- autorização não vaza para outro segmento;
- falha em um segmento só bloqueia dependentes;
- `do pr` não autoriza merge.

## Caminho rápido de desenvolvimento

Com workspace, issue, branch e escopo já disponíveis na conversa, confirme que
`$yabook dev`:

- faz uma única inspeção inicial;
- não consulta GitHub, memória, `contexto.md` ou documentação geral;
- abre somente arquivos ligados à demanda;
- faz uma validação final, salvo falha que exija ampliação.

Em `dev quick`, confirme também o limite inicial de 3 arquivos e a justificativa
antes de ampliar. Em `dev full`, confirme escopo explícito, leitura em lotes e
que a profundidade não ampliou permissões.

Em `dev step`, confirme que somente a etapa atual foi executada, que etapas
seguintes não avançaram sem confirmação e que a resposta cumpriu o relatório
técnico obrigatório de `dev` com os quatro títulos exatos.
