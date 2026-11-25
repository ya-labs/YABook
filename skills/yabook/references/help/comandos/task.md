# `$yabook task`

Gerencia o YABook Tasks: suas tarefas pessoais num repositório Git privado
(`YABook-task-<seuLogin>`), separado da memória, com quadro web, perguntas,
prazos e registro de horas. O agente marca o tempo da tarefa ativa enquanto
você conversa com ele.

## Quando usar

- Para ver o que está ativo, atrasado ou aguardando resposta.
- Para criar uma tarefa ou registrar o que a conversa tratou.
- Para indicar em que tarefa você está trabalhando e lançar horas.
- Para abrir o quadro e a ficha de horas no navegador.

## Altera alguma coisa?

Consultas (`task`, `show`, `search`, `review`, `events`, `sheet`) nunca
alteram nada e nunca exigem `do`.

Na política `automatic`, o agente grava direto e informa o que fez: criar,
editar, anotar, anexar, iniciar e capturar não pedem `do`. Na política
`manual`, as gravações só são aplicadas após `do task` (por exemplo,
`do task capture` e `do task retroativo`). `task init` só mostra o plano;
`do task init` cria ou conecta o repositório.

No início da sessão, o YABook sugere uma tarefa; confirme uma vez. As horas são
marcadas em janelas de 30 minutos da tarefa ativa, e o tempo antes da escolha é
atribuído à primeira tarefa da sessão.

## Sintaxe

```text
$yabook task [subcomando] [...]
```

- `task`: resumo das ativas, prazos, perguntas e colunas.
- `board`: site do quadro em `127.0.0.1` (porta 8765 por padrão), com modo
  Editar; também abre pela extensão do VS Code.
- `start <id>`: define a tarefa ativa. Sem ela, o agente não edita o projeto;
  `start --sem-tarefa` libera as edições sem atribuir horas. Quando um item
  entra em andamento, a história e o épico acima que ainda não começaram vão
  junto; concluir os itens não conclui o épico.
- `add <texto livre>`: cria tarefa com descrição e `size` de 1 a 5.
- `capture [assunto]`: registra tarefas, perguntas e horas a partir da conversa.
- `log <id> <horas>` ou `log <id> --inicio HH:MM --fim HH:MM`: lança horas.
- `sheet [dia|semana]`: sugestão da ficha de horas.
- `show`, `search`, `review`, `edit`, `anotacao`, `anexar`, `baixar-anexo`,
  `forget` (arquiva), `ask`, `answer`, `retroativo`, `issue`, `events`,
  `analyze`, `sync`, `clean`, `validate`: consulta e manutenção.
- `do task policy automatic|manual`: define a política local.

## Exemplos

```text
$yabook task board
$yabook task start @129
$yabook task log @129 --inicio 10:40 --fim 12:00 --data 2026-11-24
```

- O primeiro abre o quadro no navegador para ver e editar tarefas.
- O segundo marca a tarefa `@129` como ativa e leva as horas para ela.
- O terceiro lança o intervalo informado; a duração é calculada.

## Relacionados

- `memory`: conhecimento durável, em repositório separado.
- `issue`: tarefas vinculadas a issue acompanham branch, PR e merge.
