# Cenários de roteamento e contexto

Use estes casos para revisar mudanças no roteador. Em todos, confirme resposta,
referências carregadas, fontes consultadas e respeito às travas.

| Entrada | Rota esperada | Referências iniciais | Não deve carregar |
| --- | --- | --- | --- |
| `$yabook help` | `help` | `help.md` | workspace, Git, GitHub |
| `$yabook mode: study` | `mode` | `modes.md` | workspace, GitHub |
| `$yabook steps` | `steps` | `steps.md` | Git, artefatos |
| `$yabook bypass ajuste o README na main` | `bypass` | `bypass.md` | planejamento, Project, release |
| `$yabook branch` | `branch name` | `roteamento.md`, `contexto.md`, `artefatos/branch-commit.md` | planejamento |
| `$yabook issue` | `issue` | `contexto.md`, `artefatos/issue.md` | planejamento, PRs não relacionados |
| `$yabook commit msg` | `commit message` | `roteamento.md`, `contexto.md`, `artefatos/branch-commit.md` | Project |
| `$yabook desejo saber a próxima etapa` | `plan next` | `orquestracao.md`, `contexto.md`, `planejamento/status-next.md` | diagnóstico completo |
| `$yabook plan start v1` | `plan start v1` | `contexto.md`, `planejamento/start.md` | GitHub completo |
| `$yabook plan review` | `plan review` | `contexto.md`, `planejamento/review.md` | issues fechadas |
| `$yabook diagnose` | `diagnose` | `contexto.md`, `planejamento/diagnose.md` | Project inteiro, corpos em massa |
| `$yabook diagnose full` | `diagnose full` | `contexto.md`, `planejamento/diagnose.md` | respostas brutas sem filtro |
| `$yabook dev` | `dev` | `contexto.md`, `dev.md`, `git.md` | release sem relação |
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
