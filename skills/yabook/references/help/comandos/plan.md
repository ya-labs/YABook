# `$yabook plan`

Conduz o planejamento do projeto: identifica o que planejar, entrevista sobre
uma versão, avalia maturidade, recomenda o próximo passo, propõe roadmap e,
quando você aprova, grava as decisões.

## Quando usar

- Para planejar uma nova versão ou capacidade do produto.
- Para saber o que ainda falta decidir antes de montar o roadmap.
- Para transformar um plano aprovado em milestones, épicos e issues.

## Altera alguma coisa?

Sem `do`, não: as variações abaixo só conversam, analisam e propõem. Só
escrevem `do plan` (atualiza documentos de visão, versão, roadmap e decisões;
cria issue e branch de planejamento se faltar rastreabilidade; sem commit) e `do plan roadmap` (cria a estrutura aprovada no GitHub). Fora do
modo `auto`, essas escritas exigem `do`; pedidos informativos nunca escrevem.

## Sintaxe

```text
$yabook plan [start <versão>|status|next|review|roadmap|brief]
```

- `plan`: entrevista para descobrir o que você quer planejar.
- `plan start <versão>`: entrevista e propõe uma versão.
- `plan status`: maturidade, decisões abertas e riscos.
- `plan next`: uma única ação recomendada.
- `plan review`: revisa coerência e conclui se está pronto para roadmap.
- `plan roadmap`: propõe milestones, épicos e próximo bloco.
- `plan brief`: condensa decisões e pendências em texto curto.
- `do plan` e `do plan roadmap`: gravam o que foi aprovado.

## Exemplos

```text
$yabook plan start v2
$yabook plan review
$yabook do plan roadmap
```

- Inicia a entrevista da versão 2 e entrega uma proposta ainda não gravada.
- Revisa o plano e responde pronto, pronto com ressalvas ou não pronto.
- Cria milestones, épicos e o próximo bloco de issues aprovados.

## Relacionados

- `diagnose`: quando o estado atual ainda é incerto.
- `discuss`: para analisar um tema antes de decidir.
- `steps`: `steps start plan` faz a entrevista com checklist.
