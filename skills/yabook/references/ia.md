# IA no padrão YABook

Use esta referência para orientar assistentes de IA.

## Contrato operacional

Antes de criar ou alterar artefatos de projeto, a IA deve:

1. Ler o `AGENTS.md` local.
2. Consultar documentação local relacionada à tarefa.
3. Consultar o YABook para padrões de GitHub, documentação, IA e condução de projeto.
4. Usar a estrutura existente do projeto.
5. Avisar quando houver divergência entre pedido, projeto e YABook.

Não invente formato quando já houver padrão documentado.

## Uso econômico de contexto

Para tarefas bem descritas, leia o mínimo necessário para executar com segurança.

Quando a issue já tiver contexto suficiente, ela deve ser a fonte principal.

Busque documentação adicional apenas para confirmar regras, contratos, arquitetura ou riscos que afetem a entrega.

## Quando ler documentação ampla

Leia mais contexto quando:

- a issue estiver ambígua;
- a tarefa alterar documentação estrutural;
- a tarefa alterar requisito, contrato, fluxo, arquitetura, ADR ou processo;
- houver conflito entre código, documentação e issue;
- a mudança puder afetar mais de uma etapa, milestone ou épico.

## Escrita

Texto gerado por IA deve ser podado antes de virar padrão.

Mantenha apenas o que ajuda alguém a executar, revisar, decidir ou continuar o trabalho.

Evite:

- repetição;
- explicação genérica;
- validações óbvias;
- contexto longo antes da tarefa real.
