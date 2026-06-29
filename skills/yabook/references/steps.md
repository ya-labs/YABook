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

## Replanejamento adaptativo

Enquanto houver checklist ativo, compare cada ação relevante da pessoa usuária
ou do agente com as etapas atuais antes de responder.

Classifique a ação como:

- **etapa atual**: conclua ou atualize a próxima etapa;
- **etapa futura antecipada**: registre a execução sem apagar sua posição
  histórica e avalie dependências;
- **desvio válido**: incorpore a ação e ajuste somente etapas pendentes;
- **ação prematura**: registre o fato e adicione repetição ou validação posterior
  quando o resultado puder ficar inválido;
- **desvio desnecessário**: não adicione ao checklist e explique por que não
  contribui para o objetivo;
- **desvio incompatível**: interrompa o fluxo e indique a correção necessária;
- **mudança estrutural**: proponha a remodelagem e peça confirmação.

### Ajustes automáticos

Recalcule automaticamente quando o objetivo e o escopo permanecerem iguais:

- marcar etapa concluída;
- registrar etapa futura executada antecipadamente;
- adicionar etapa corretiva exigida por dependência quebrada;
- adicionar revalidação necessária;
- reordenar apenas etapas pendentes;
- remover etapa pendente que se tornou comprovadamente desnecessária.

Explique o ajuste antes do checklist:

```text
Checklist recalculado

A validação foi executada antes da implementação. Ela foi registrada, mas será
necessário validar novamente depois das alterações.
```

### Ajustes que exigem confirmação

Não altere automaticamente:

- objetivo do checklist;
- escopo aprovado;
- decisões da pessoa usuária;
- prioridade entre entregas independentes;
- inclusão de trabalho opcional;
- troca da issue ou versão acompanhada.

Apresente a proposta e aguarde confirmação. Enquanto isso, preserve o checklist
atual.

### Histórico e ordem

- Nunca remova nem reordene etapas concluídas.
- Registre uma ação executada como fato mesmo quando estiver fora de ordem.
- Não trate uma ação mencionada como executada sem evidência.
- Numere novamente apenas etapas pendentes quando necessário para leitura.
- Se uma ação antecipada invalidar dependências, adicione a correção no ponto
  mais próximo em que ela possa ser executada.
- Diferencie ordem alternativa válida de ação que precisará ser repetida.

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

Quando houver recalculado, correção ou proposta estrutural, apresente a
explicação antes do rodapé obrigatório. O rodapé deve sempre refletir o estado
mais recente confirmado.

## Limites

- Criar ou atualizar o checklist não executa os comandos listados.
- `steps` não autoriza escrita que dependa de `$yabook do`.
- Não transforme brainstorming ou alternativas em etapas sem aprovação.
- Não adicione trabalho desnecessário apenas porque foi executado ou mencionado.
- Não use replanejamento adaptativo para mudar decisões da pessoa usuária.
- Não use o checklist como status permanente de projeto.
