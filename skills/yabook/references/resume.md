# Repasse do contexto atual

Use esta referência para `$yabook resume` e
`$yabook resume até "<marco, assunto ou mensagem>"`.

## Objetivo

Gerar um resumo neutro e reutilizável do recorte temático atual para encaminhar
a outro chat. `resume` é somente leitura, pertence à classe `C0` e usa apenas o
contexto já disponível na conversa.

Não resolva workspace nem consulte repositório, arquivos, Git, GitHub, memória,
outros chats ou o histórico completo da conversa por prevenção. Quando o pedido
depender de uma dessas fontes, indique a rota apropriada em vez de ampliar
`resume`.

## Recorte

Na forma padrão, selecione o último bloco temático ativo. O bloco começa após a
última mudança inequívoca de assunto e termina na mensagem atual. Não use uma
quantidade fixa de mensagens e não inclua contexto anterior apenas porque está
disponível.

Na forma com `até`, trate o marco informado como o início inclusivo do recorte e
inclua o conteúdo desde esse ponto até a mensagem atual:

```text
$yabook resume até "quando definimos o comando resume"
$yabook resume até "a mensagem sobre o recorte semântico"
```

O marco pode descrever um assunto, uma decisão ou uma mensagem reconhecível na
conversa. Se a mudança de assunto, o marco ou a correspondência entre mais de um
ponto não puder ser determinada com segurança, informe a ambiguidade e peça um
marco mais específico. Não escolha silenciosamente nem misture recortes.

## Formato da saída

Entregue o resumo com estes campos, preservando somente fatos, decisões,
restrições, evidências e pendências presentes no recorte:

```md
## Objetivo ou ajuste

## Contexto necessário

## Decisões confirmadas

## Restrições ou evidências

## Pendências

## Pedido sugerido ao próximo chat
```

O pedido sugerido é obrigatório e deve indicar a continuação sustentada pelo
recorte, sem inventar requisito, decisão ou autorização. Mantenha a redação
neutra: o destino pode ser administrativo, de desenvolvimento ou de qualquer
outro tipo. Quando um campo não tiver conteúdo confirmado, registre isso de
forma curta em vez de completar por inferência.
