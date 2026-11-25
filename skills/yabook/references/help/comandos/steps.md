# `$yabook steps`

Mantém um checklist de etapas visível durante a conversa, para acompanhar uma
sequência de trabalho sem perder o fio. Enquanto estiver ativo, a resposta
mostra o estado compacto antes de `Próxima etapa`.

## Quando usar

- A tarefa tem vários passos e você quer acompanhá-los um a um.
- Você quer conduzir `init` ou `plan` com o progresso visível.
- Você quer discutir ou executar só a etapa atual, sem avançar o resto.

## Altera alguma coisa?

Não. O checklist existe só na conversa: não grava arquivo, memória nem GitHub e
não executa passos. Uma etapa só é marcada como concluída quando você confirma
(`steps done` ou um aviso claro, como “concluí a primeira etapa”); a entrega da
IA não basta. Para executar a etapa atual, use `$yabook dev step`.

## Sintaxe

```text
$yabook steps start [init|plan]
$yabook steps
$yabook step
$yabook steps done <número>
$yabook steps cancel
```

- `steps start`: cria etapas para o contexto já claro na conversa.
- `steps start init` e `steps start plan`: iniciam essas entrevistas com
  checklist.
- `steps`: mostra a lista inteira; `step`: detalha só a etapa atual.
- `steps done <número>`: marca a etapa como concluída.
- `steps cancel`: encerra o acompanhamento.

## Exemplos

```text
$yabook steps start
$yabook step
$yabook steps done 1
```

- Monta o checklist com entregas objetivas da tarefa em andamento.
- Explica objetivo, abordagem, dúvidas e riscos da etapa atual, sem alterar nada.
- Confirma a primeira etapa e passa para a seguinte.

## Relacionados

- `dev step`: executa somente a etapa atual do checklist.
- `init` e `plan`: entrevistas que podem ser acompanhadas por `steps`.
- `discuss`: análise que também pode seguir em etapas.
