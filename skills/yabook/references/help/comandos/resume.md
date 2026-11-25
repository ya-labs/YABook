# `$yabook resume`

Gera um resumo neutro do assunto atual da conversa, pronto para colar em outro
chat e continuar dali sem levar o histórico inteiro.

## Quando usar

- A conversa ficou longa e você quer continuar o assunto em um chat novo.
- Você vai passar o contexto para outra pessoa ou outro agente.
- Você quer registrar decisões e pendências de um trecho da conversa.

## Altera alguma coisa?

Não. É somente leitura e usa apenas o que já está na conversa: não consulta
repositório, arquivos, Git, GitHub, memória nem outros chats. Por padrão, pega
o último bloco de assunto, a partir da última mudança clara de tema. Se não
conseguir identificar o recorte com segurança, pede um marco mais específico em
vez de misturar assuntos. O modo `auto` não é transferido: o novo chat precisa
ativá-lo de novo.

A saída traz objetivo ou ajuste, contexto necessário, decisões confirmadas,
restrições ou evidências, pendências e um pedido sugerido ao próximo chat.

## Sintaxe

```text
$yabook resume [até "<marco, assunto ou mensagem>"]
```

- `resume`: resume o último assunto ativo até agora.
- `resume até "<marco>"`: começa no marco informado (incluído) e vai até agora.

## Exemplos

```text
$yabook resume
$yabook resume até "quando definimos o comando resume"
$yabook resume até "a mensagem sobre o recorte semântico"
```

- Resume o assunto em andamento para abrir um novo chat.
- Resume desde a decisão citada até o momento atual.
- Usa uma mensagem reconhecível da conversa como ponto de partida.

## Relacionados

- `plan brief` e `issue brief`: condensam planejamento ou demanda em texto curto.
- `steps`: acompanha etapas da conversa atual.
