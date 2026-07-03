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

A issue deve existir. `dev` prepara branch, implementa e valida, mas não cria
commit nem PR. `dev & do pr` entrega o PR; `dev & do merge` também integra.

## APK

`apk` lê `.yabook/apk.json` e mostra a prévia sem build ou escrita. `do apk`
prepara a cópia padronizada de um artefato existente. Upload permanece manual.

## Mode

Modos ajustam colaboração, não permissões. `study` ensina, `work` orienta e
`prod` executa dentro das autorizações. `mode: work` não equivale a `$yabook dev`.
