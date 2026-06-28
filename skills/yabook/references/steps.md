# Acompanhamento de etapas do YABook

Use esta referência para a família `$yabook steps`.

## Objetivo

Manter visível, durante a conversa atual, uma sequência curta de ações
recomendada pelo YABook.

`steps` acompanha o trabalho da conversa. Não substitui planejamento,
milestones, issues ou tarefas do GitHub.

## Comandos

```text
$yabook steps start
$yabook steps
$yabook steps done <número>
$yabook steps cancel
```

- `steps start`: cria um checklist com base na sequência recomendada mais
  recente ou nas etapas informadas pela pessoa usuária;
- `steps`: mostra o checklist ativo;
- `steps done <número>`: conclui a etapa indicada e destaca a próxima;
- `steps cancel`: encerra o acompanhamento sem executar as etapas pendentes.

Se `steps start` não tiver uma sequência inequívoca no contexto, peça as etapas
antes de criar o checklist.

## Estado da conversa

- Mantenha somente um checklist ativo por conversa.
- Criar outro checklist exige concluir, cancelar ou substituir explicitamente o
  atual.
- O estado não deve ser gravado em arquivo, memória permanente ou GitHub.
- Em uma nova conversa, a pessoa usuária precisa iniciar outro checklist.

## Atualização em linguagem natural

Aceite confirmações inequívocas como `fiz a etapa 1`, `concluí a primeira etapa`
ou `terminei o diagnóstico`.

Marque uma etapa como concluída somente quando a pessoa usuária confirmar a
conclusão ou houver evidência na conversa de que o agente executou e validou a
etapa. Se houver ambiguidade, peça confirmação.

## Exibição obrigatória

Enquanto houver etapas abertas, finalize cada resposta com:

```text
Etapas em andamento

✅ 1. Etapa concluída
➡️ 2. Próxima etapa
⬜ 3. Etapa pendente
```

Preserve a ordem e mantenha o texto compacto. Após concluir todas as etapas,
mostre o checklist final uma vez e encerre o acompanhamento. Após
`steps cancel`, confirme o cancelamento sem repetir o checklist.

## Limites

- Criar ou atualizar o checklist não executa os comandos listados.
- `steps` não autoriza escrita que dependa de `$yabook do`.
- Não transforme brainstorming ou alternativas em etapas sem aprovação.
- Não use o checklist como status permanente de projeto.
