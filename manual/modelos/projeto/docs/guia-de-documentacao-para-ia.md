# Guia de Documentação Para IA

Este documento orienta assistentes de IA a consultar, manter e atualizar a documentação do projeto com economia de contexto.

Ele descreve onde buscar informação estável. Backlog, progresso, responsáveis, Project, milestones e execução devem ficar no GitHub.

## Fluxo de consulta

1. Leia o `AGENTS.md`.
2. Leia este guia quando a tarefa envolver documentação.
3. Identifique o tipo da tarefa.
4. Use a issue como fonte principal quando ela já tiver contexto suficiente.
5. Consulte [Guia de consulta da documentação](guia-da-documentacao.md) para decidir onde buscar ou atualizar informação.
6. Use `rg` com palavras-chave direcionadas.
7. Abra documentos completos somente quando o trecho localizado não for suficiente.

Não leia todos os documentos por padrão.

Quando o projeto seguir o YABook, consulte-o para validar padrões organizacionais antes de criar estrutura, fluxo ou formato novo.

## Quando consultar o guia fonte

Consulte [Guia de consulta da documentação](guia-da-documentacao.md) quando precisar decidir:

- onde registrar um assunto;
- se um documento novo faz sentido;
- se uma informação pertence ao Markdown ou ao GitHub;
- se um trecho repetido deve ser fundido ou removido.

## Leitura direcionada

Use leitura direcionada quando:

- a issue estiver objetiva;
- a mudança afetar um arquivo ou assunto claro;
- a tarefa for correção pequena;
- o padrão necessário já estiver documentado.

Fluxo recomendado:

1. Leia a issue.
2. Busque palavras-chave com `rg`.
3. Abra apenas os arquivos encontrados.
4. Consulte o YABook somente se a dúvida for sobre padrão organizacional.

## Quando ler documentação ampla

Leitura ampla é adequada quando:

- a issue estiver ambígua;
- a tarefa alterar documentação estrutural;
- a tarefa alterar requisito, contrato, fluxo, arquitetura, ADR ou processo;
- houver conflito entre código, documentação e issue;
- a mudança puder afetar mais de uma etapa, milestone ou épico;
- a pessoa usuária pedir atualização de contexto do projeto.

Fora desses casos, prefira leitura direcionada por issue, busca com `rg` e abertura pontual de arquivos.

## Antes de criar documento novo

Confirme:

- qual pessoa ou IA vai usar o documento;
- qual ação ou decisão ele apoia;
- se o conteúdo não pertence a um documento existente;
- se a informação é estável o bastante para Markdown.

## Quando propor poda

Proponha remoção, fusão ou reescrita quando encontrar documento ou trecho que:

- repete regra já documentada;
- descreve intenção sem orientar ação;
- guarda status operacional que deveria estar no GitHub;
- mistura proposta aberta com decisão aceita;
- usa texto genérico que não ajuda execução, revisão ou decisão.
