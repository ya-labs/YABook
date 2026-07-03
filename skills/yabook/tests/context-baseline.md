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

As classes normativas são `C0`, `C1`, `C2`, `C3` e `C4`. Todo cenário estático
e runtime declara sua classe; divergência de classe nunca é justificável.

Briefs são rotas `C2` com uma referência inicial, sem consulta externa quando a
conversa já sustenta objetivo, escopo, validação e riscos.

## Verificação qualitativa

Além do tamanho, valide:

- intenção equivalente mantém a mesma rota;
- aliases e encadeamentos continuam funcionando;
- `do` nunca é inferido;
- as travas Git/GitHub permanecem;
- contexto aumenta somente quando falta evidência;
- comandos complexos preservam profundidade sob demanda.

## Evolução da issue #43

A matriz deixou de ser um pedágio obrigatório. Comandos explícitos carregam
diretamente sua referência; `contexto.md` fica restrito a auditoria, revisão do
carregamento e ambiguidade entre rotas.

Metas adicionais:

- rota explícita não inclui `contexto.md` no conjunto inicial;
- demanda delimitada não consulta GitHub, memória ou documentação geral;
- execução começa com uma inspeção e termina com uma validação por padrão;
- toda ampliação acima do orçamento registra a dependência que a justificou.

As referências de Git, GitHub, help, modos e steps foram divididas por
capacidade. O teste verifica tamanho e quantidade máxima de referências por
rota, com saída detalhada somente em `--verbose`.

`check_context_runtime.py` complementa essa verificação com relatórios de
execução observada. Ele não presume acesso automático ao histórico de
ferramentas da plataforma.
