# `$yabook issue`

Gera uma issue no padrão YA LABS: título objetivo, corpo com resumo, escopo,
critérios de aceite e informações para IA, labels oficiais sugeridas e `Size`
de 1 a 5 para o Project.

## Quando usar

- Uma demanda nova foi decidida e precisa de registro antes da branch.
- Você quer só o título, só o corpo ou uma classificação de labels e `Size`.
- Vai reunir vários ajustes em uma branch e um PR (`issue package`).

## Altera alguma coisa?

Não. `issue` e seus subcomandos são somente leitura e devolvem texto pronto.
Para criar no GitHub, use `do issue` (ou `do issue package`); o agente valida
o formato antes. `dev` também cria a issue quando ela falta, e em `mode: auto`
o objetivo delegado dispensa `do`.

## Sintaxe

```text
$yabook issue [title|desc|classify|brief|package]
```

- `issue`: título, corpo, labels sugeridas e `Size (Project)`.
- `issue title` / `issue desc`: só o título ou só o corpo.
- `issue classify`: labels, `Size`, justificativa e sugestão de quebra quando `Size` é 5.
- `issue brief`: resumo curto (até 1.200 caracteres) da demanda.
- `issue package [propósito]`: issue de pacote com descrição estável, sem lista de demandas.
- `do issue` / `do issue package`: cria a issue da prévia aprovada.

## Exemplos

```text
$yabook issue
$yabook issue package ajustes da tela de login
$yabook do issue
```

- `issue`: propõe a issue a partir da conversa.
- `issue package ...`: propõe um pacote; as entregas ficam nos commits e no PR, com merge commit.
- `do issue`: cria a issue aprovada, com labels e `Size` no Project.

## Relacionados

- `dev`: desenvolver a issue criada.
- `branch`: nome da branch da issue.
- `bypass`: ajuste pontual sem issue.
