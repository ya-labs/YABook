# `$yabook check`

Verifica se um artefato segue o padrão YABook: branch, issue, PR, documentação
ou o fluxo que você indicar. O resultado lista o que está conforme e o que
diverge, com a regra que se aplica.

## Quando usar

- Antes de abrir ou atualizar um PR, para conferir branch, issue e PR.
- Depois de escrever uma issue ou um documento, para validar o formato.
- Quando tiver dúvida se o trabalho em andamento respeita o fluxo da YA LABS.

## Altera alguma coisa?

Não. É somente leitura, inclusive em modo `auto` e na variação `full`. O
`check` aponta divergências; corrigir depende de você pedir a ação
correspondente.

Por padrão a verificação é dirigida: o agente olha só o alvo e a regra que vale
para ele, e para quando já tem evidência suficiente. `check full` faz uma
auditoria ampla e só deve ser usado quando você quer essa profundidade: o agente
confirma o escopo, explica por que precisa ler mais e analisa em lotes
resumidos.

## Sintaxe

```text
$yabook check [full] [alvo]
```

- `check`: verificação dirigida do alvo informado ou em foco na conversa.
- `check full`: auditoria ampla, com pedido explícito.
- `validate`: alias de `check`.

## Exemplos

```text
$yabook check branch e PR atuais
$yabook check full documentação do projeto
$yabook check & review
```

- O primeiro confere nome da branch, vínculo com a issue e formato do PR.
- O segundo audita a documentação inteira em lotes, sem editar nada.
- O terceiro valida a conformidade e, em seguida, analisa qualidade e riscos.

## Relacionados

- `review`: analisa qualidade, riscos e decisões, além do formato.
- `docs`: orienta onde cada informação deve ser documentada.
- `status`: resume branch, issue inferida e alterações pendentes.
