# Help de comandos

Para um comando específico, explique apenas:

1. o que faz;
2. quando usar;
3. se altera estado;
4. sintaxe;
5. dois ou três exemplos;
6. comandos relacionados.

## Steps

Explique `steps start`, `steps`, `steps done <número>` e `steps cancel`. O
checklist vale para a conversa, não executa passos e pode recalcular somente
etapas pendentes sem mudar objetivo ou decisão.

## Dev

A issue deve existir. `dev quick` limita descoberta para tarefa pequena, `dev`
usa profundidade balanceada e `dev full` permite investigação profunda
justificada. Todos preparam branch, implementam e validam, mas não criam commit
nem PR. `dev & do pr` entrega o PR; `dev & do merge` também integra.

## Check e review

`check` valida conformidade e `review` analisa qualidade e riscos do alvo.
Ambos são dirigidos por padrão. `check full` e `review full` exigem pedido
explícito e ampliam a auditoria sem conceder permissão de escrita.

## Briefs

`issue brief`, `plan brief` e `pr brief` condensam contexto em até 1.200
caracteres. São somente textuais e não substituem `do` para persistência.

## APK

`apk` lê `.yabook/apk.json` e mostra a prévia sem build ou escrita. `do apk`
prepara a cópia padronizada de um artefato existente. Upload permanece manual.

## Mode

Modos ajustam colaboração, não permissões. `study` ensina, `work` orienta e
`prod` executa dentro das autorizações. `mode: work` não equivale a `$yabook dev`.
