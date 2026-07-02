# Comparação de contexto da issue #39

Valores aproximados por `caracteres / 4`. Eles servem para comparação interna e
não representam cobrança ou medição exata do plano do Codex.

## Antes

| Arquivo | Caracteres | Tokens aproximados |
| --- | ---: | ---: |
| `SKILL.md` | 13.031 | 3.258 |
| `references/session.md` | 15.387 | 3.847 |
| `references/commands.md` | 14.518 | 3.630 |
| `references/planejamento.md` | 6.364 | 1.591 |

O primeiro comando operacional exigia `SKILL.md`, `session.md`, workspace,
regras locais e estado Git. Aliases e planejamento podiam acrescentar os outros
arquivos antes da descoberta real.

## Metas

- `SKILL.md`: até 1.200 tokens aproximados.
- `bypass.md`: até 300.
- `session-minimo.md`: até 500.
- `roteamento.md`: até 1.000.
- subreferência individual de planejamento: até 700.
- nenhuma rota simples carrega a antiga sessão monolítica.

## Depois

| Arquivo | Tokens aproximados |
| --- | ---: |
| `SKILL.md` | até 1.200 |
| `references/roteamento.md` | 470 |
| `references/contexto.md` | cerca de 1.200 |
| `references/session-minimo.md` | 241 |
| `references/bypass.md` | 181 |
| subreferências de planejamento | 127 a 295 |

Rotas instantâneas seguem diretamente para sua referência e não pagam o custo
da matriz. Rotas dependentes do projeto usam a matriz antes de ampliar contexto.

## Verificação qualitativa

Além do tamanho, valide:

- intenção equivalente mantém a mesma rota;
- aliases e encadeamentos continuam funcionando;
- `do` nunca é inferido;
- as travas Git/GitHub permanecem;
- contexto aumenta somente quando falta evidência;
- comandos complexos preservam profundidade sob demanda.
