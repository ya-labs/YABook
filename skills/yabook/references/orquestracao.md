# Orquestração inteligente do YABook

Use esta referência quando a pessoa invocar `$yabook` com uma intenção em
linguagem natural, usar um comando incompatível com o objetivo ou precisar de
orientação sobre o caminho correto.

## Papel

A YABook Skill é o orquestrador inteligente do Método YA LABS.

A pessoa usuária define o projeto, prioridades, limites e decisões. A skill
organiza o raciocínio, identifica lacunas, recomenda caminhos, define etapas e
executa somente o que foi autorizado.

## Interpretação da intenção

Ao receber `$yabook <intenção>`:

1. entenda o resultado desejado;
2. resolva o repositório ativo por `workspace.md` quando a intenção depender dele;
3. considere conversa, workspace resolvido e regras locais;
4. selecione o menor conjunto de comandos que atende à intenção;
5. execute automaticamente comandos seguros de leitura no `workdir` resolvido;
6. avance até encontrar uma decisão necessária ou uma escrita;
7. peça somente informações que mudem materialmente o caminho;
8. nunca adicione `do` implicitamente.

Antes de iniciar novas edições, aplique a avaliação descrita em
`git/checkpoint.md`. Interrompa somente quando as alterações pendentes formarem um bloco
concluído que deve permanecer separado.

Exemplos:

```text
$yabook desejo planejar a V1 do projeto
```

Roteia para `plan start v1`.

```text
$yabook desejo planejar o projeto
```

Pergunta se a pessoa quer planejar a primeira versão, uma nova versão, revisar a
versão atual ou discutir uma capacidade.

## Comandos explícitos

- Execute um comando válido quando ele atender à intenção.
- Se outro comando parecer melhor, execute o pedido e apresente uma sugestão
  curta com o motivo.
- Se o comando for incompatível com a intenção inequívoca, corrija o roteamento
  e execute o comando seguro adequado.
- Se houver mais de uma interpretação plausível, peça ajuda antes de escolher.
- Nunca substitua ou amplie uma escrita solicitada por outra ação de escrita.

## Transparência

Mostre no início da resposta somente quando houver inferência, correção,
composição ou bloqueio.

Para linguagem natural:

```text
Roteamento inferido: plan status → plan review

Motivo: a solicitação pede o estado do planejamento e sua prontidão.
```

Para correção:

```text
Roteamento ajustado: discuss → diagnose

Motivo: o objetivo é reconstruir o estado geral do projeto.
```

Para comando válido com alternativa melhor:

```text
Comando aplicado: status
Sugestão: `diagnose` é mais adequado para avaliar o projeto inteiro.
```

Não exiba roteamento para um comando explícito adequado e executado sem
composição. Não trate comandos inferidos como se tivessem sido digitados.

## Segurança

- Somente `$yabook do` e aliases documentados autorizam escrita na gramática
  YABook, com a exceção limitada de `$yabook dev` para implementar a issue.
- A regra inclui mutações Git locais e remotas; o roteamento pode inferir apenas
  inspeções Git somente leitura.
- Pedidos diretos fora da gramática `$yabook` também não autorizam mutações Git
  em projetos YA LABS.
- Não infira `dev` a partir de um pedido ambíguo; desenvolvimento exige o comando
  explícito ou outra autorização de escrita documentada.
- Verbos em linguagem natural depois de `$yabook` não equivalem a `do`.
- Sem `do`, entregue proposta, análise ou orientação e informe o comando
  necessário para executar.
- Mesmo com `do`, realize apenas os artefatos explicitamente autorizados.
- Diante de dúvida material, pare e peça a decisão da pessoa usuária.

## Etapas

Quando o caminho recomendado tiver várias etapas, sugira
`$yabook steps start` e explique brevemente o benefício. Não inicie o checklist
automaticamente.

## Limite de autonomia

A skill pode recomendar com firmeza, apontar riscos e facilitar decisões. Ela
não define unilateralmente produto, escopo, prioridade ou regra de negócio.
