# `$yabook review`

Revisa uma issue, um PR ou uma documentação contra o padrão YABook, analisando
qualidade, riscos e decisões. Vai além do formato: aponta o que pode confundir,
faltar ou causar problema.

## Quando usar

- Antes de pedir revisão humana de um PR.
- Ao terminar uma issue ou documento e querer uma segunda leitura crítica.
- Para avaliar se uma decisão registrada está clara e justificada.

## Altera alguma coisa?

Não. É somente leitura, inclusive em modo `auto` e na variação `full`. A
revisão traz apontamentos; aplicar qualquer ajuste depende de você pedir.

Por padrão a revisão é dirigida: o agente lê o alvo e a referência que se
aplica a ele, sem varrer coleções inteiras. `review full` amplia a análise e só
deve ser usado quando você quer essa profundidade: o agente confirma o escopo,
explica por que precisa ler mais e resume cada lote antes do próximo.

## Sintaxe

```text
$yabook review [full] [alvo]
```

- `review`: revisão dirigida do alvo informado ou em foco na conversa.
- `review full`: revisão ampla, com pedido explícito.

## Exemplos

```text
$yabook review PR atual
$yabook review issue #42
$yabook review full docs/
```

- O primeiro analisa título, descrição e riscos do PR da branch atual.
- O segundo avalia se a issue está clara, bem delimitada e no padrão.
- O terceiro revisa a pasta de documentação em lotes, sem editar arquivos.

## Relacionados

- `check`: confere só a conformidade objetiva com o padrão.
- `pr brief`: resume a entrega pronta para revisão.
- `diff`: mostra no VS Code o que o agente alterou na sessão.
