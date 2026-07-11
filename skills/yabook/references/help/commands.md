# Help de comandos

Para um comando específico, explique apenas:

1. o que faz;
2. quando usar;
3. se altera estado;
4. sintaxe;
5. dois ou três exemplos;
6. comandos relacionados.

## Steps

Explique `steps start`, `steps`, `step`, `steps done <número>` e `steps cancel`.
O checklist vale para a conversa, não executa passos e pode recalcular somente
etapas pendentes sem mudar objetivo ou decisão. `steps` fala da lista inteira;
`step` fala apenas da etapa atual.

## Dev

A issue deve existir. `dev quick` limita descoberta para tarefa pequena, `dev`
usa profundidade balanceada, `dev step` desenvolve somente a etapa atual de um
checklist e `dev full` permite investigação profunda justificada. Todos
preparam branch, implementam e validam dentro do escopo autorizado, mas não
criam commit nem PR. `dev step` nunca executa todos os steps e deve relatar `O
que foi feito`, `Como foi feito`, `Por que foi feito assim` e `Observações para
revisão`. `dev` é o atalho para essa implementação; um pedido direto inequívoco
de implementar a issue atual também segue a mesma rota. `dev & do pr` entrega o
PR; `dev & do merge` também integra.

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

## Dashboard

`help dashboard` explica o dashboard de contexto sem executar nada. A resposta
deve cobrir:

- o que é o dashboard e sua relação com a telemetria exportada;
- quando ele é útil e quando não é necessário;
- que o painel é somente leitura;
- como gerar o dataset com `build_context_dashboard.py`;
- como abrir localmente por servidor HTTP simples.

Exemplos esperados:

```text
$yabook help dashboard
python skills/yabook/scripts/build_context_dashboard.py export-1.json export-2.json --output skills/yabook/dashboard/context-dashboard.json
python -m http.server 4173
```

## Mode

Modos ajustam colaboração, não permissões. `study` ensina, `work` orienta e
`prod` executa dentro das autorizações. `mode: work` não equivale a `$yabook dev`.
