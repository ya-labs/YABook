# Comandos YABook

Use estes comandos quando a pessoa usuária invocar `$yabook`.

Responda em português do Brasil, com texto pronto para uso.

## Comandos

| Comando | Saída |
| --- | --- |
| `$yabook help` | Lista curta dos comandos disponíveis. |
| `$yabook init` | Inicializa ou adapta o padrão YA LABS no repositório atual. |
| `$yabook status` | Resume branch, issue inferida, alterações pendentes e próximo passo. |
| `$yabook check` | Verifica conformidade com o YABook. |
| `$yabook issue` | Gera título e descrição completa da issue. |
| `$yabook issue title` | Gera apenas o título da issue. |
| `$yabook issue desc` | Gera apenas o corpo da issue. |
| `$yabook branch name` | Sugere branch baseada na issue. |
| `$yabook commit message` | Sugere mensagem de commit no padrão. |
| `$yabook pr` | Gera título e descrição completa do Pull Request. |
| `$yabook pr title` | Gera apenas o título do Pull Request. |
| `$yabook pr desc` | Gera apenas a descrição do Pull Request. |
| `$yabook release` | Gera descrição completa de release. |
| `$yabook docs` | Indica onde documentar uma informação. |
| `$yabook review` | Revisa issue, PR ou documentação contra o padrão YABook. |

## Aliases

| Alias | Comando oficial |
| --- | --- |
| `$yabook branch` | `$yabook branch name` |
| `$yabook commit msg` | `$yabook commit message` |
| `$yabook pr description` | `$yabook pr desc` |
| `$yabook issue description` | `$yabook issue desc` |
| `$yabook doc` | `$yabook docs` |
| `$yabook validate` | `$yabook check` |

## Contexto por comando

- Para `pr`, `pr desc`, `commit message` e `release`, use conversa atual e confirme com Git.
- Para `issue`, use o pedido do usuário, o escopo descoberto e o padrão de issue.
- Para `branch name`, use o número da issue quando existir.
- Para `docs`, leia `documentacao.md`.
- Para `init`, leia `init.md`.
- Para `check` e `review`, leia `github.md`, `documentacao.md` e `ia.md` conforme o artefato revisado.

## Formato do help

Quando o comando for `$yabook help`, responda curto:

```text
Comandos principais:
- $yabook init: inicializa o padrão YA LABS no repo.
- $yabook issue: gera título e descrição da issue.
- $yabook pr: gera título e descrição do PR.
- $yabook commit message: sugere mensagem de commit.
- $yabook release: gera descrição de release.
- $yabook check: verifica conformidade com o YABook.
- $yabook docs: indica onde documentar algo.
```

## Saídas

- Não explique o YABook inteiro quando a pessoa pedir um artefato.
- Entregue o texto pronto para copiar.
- Inclua observações apenas quando houver risco, exceção ou contexto faltante.
