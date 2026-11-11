# Sessão de planejamento — YABook Tasks

Data: 2026-11-11
Rastreabilidade: [issue #155](https://github.com/ya-labs/YABook/issues/155)

## Contexto

A ideia partiu de acompanhar em tempo real a atividade feita com agentes de IA:
sessão, projeto, tarefa atual, notas e um quadro de tarefas. O GitHub Project
não atende, porque documenta repositórios específicos e não cobre tarefas que
existem apenas no sistema de trabalho da pessoa. A sessão discutiu
armazenamento, confidencialidade, captura, visualização e horas, e definiu a V1.

## Decisões aprovadas

- Uso individual, sem login nem backend remoto.
- Dados em repositório GitHub privado pessoal `YABook-task-<loginGitHub>`, com
  um arquivo Markdown por tarefa.
- Site e servidor local no YABook, instalados como PWA nas duas máquinas e
  iniciados manualmente; aplicativo nativo descartado na V1 pelo consumo de
  memória.
- Dados sensíveis permanecem numa base confidencial local e entram nas tarefas
  apenas como referência; o site os resolve somente onde a base existe.
- Campos versionados genéricos, trava de commit com lista local de termos e
  checagem no servidor.
- Comandos `task` alinhados à família `memory`, incluindo `task init` no mesmo
  modelo de inicialização.
- Captura pelos hooks já registrados no Claude Code e no Codex; a pessoa confirma
  a tarefa ativa no início da sessão.
- Colunas personalizáveis com papel fixo entendido pelo agente; edição mecânica
  aplicada pelo site e registrada como evento não analisado; mudança estrutural
  analisada pelo agente antes de aplicar.
- Campos `projeto`, `demanda` e `issue` no card; `Size` no M3.
- Ficha diária com horas configuradas divididas por proporção de atividade;
  com demanda e projeto, as horas vão para a demanda; trabalho sem código é
  extra, registrado fora do total.
- V1 entregue em três marcos: M1 dados, comandos e captura; M2 site e edição
  mecânica; M3 quadro personalizável, propostas estruturais e `Size`.

## Limites mantidos

- Labels e campos personalizados além de `Size` ficam fora da V1.
- A incorporação de bases confidenciais existentes ao modelo de tarefas fica
  fora da V1.
- Ideias para versões seguintes são registradas como issues, não em documentos
  versionados.

## Impactos

- O YABook passa a manter um segundo repositório pessoal por pessoa, além da
  memória, com o mesmo modelo de inicialização.
- Os hooks do plugin ganham captura de atividade, com orçamento de latência
  próprio.
- Bases confidenciais locais deixam de guardar estado e pendência de tarefas,
  que passam ao repositório de dados.

O detalhamento está em
[yabook-tasks.md](../planejamento/yabook-tasks.md) e a sequência em
[roadmap.md](../planejamento/roadmap.md).
