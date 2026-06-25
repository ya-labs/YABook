# Uso de IA

Este guia define como a YA LABS usa assistentes de IA sem perder padrão, rastreabilidade ou responsabilidade técnica.

Use quando for pedir para IA criar issues, preparar PRs, alterar documentação, implementar tarefas ou revisar conformidade com o YABook.

## Princípios

- A IA deve consultar o repositório antes de assumir arquitetura, stack ou padrão.
- Em projetos YA LABS, a IA deve consultar o YABook quando a dúvida for sobre padrão organizacional.
- Mudanças relevantes devem manter rastreabilidade entre issue, branch, commit e Pull Request.
- A IA deve respeitar o padrão local do projeto.
- A IA não deve inventar formato quando já houver padrão documentado.
- Código gerado deve ser legível, simples e pronto para manutenção.
- Documentação gerada deve preservar fatos reais do projeto.
- O time continua responsável por revisar, validar e aprovar mudanças.

## Quando usar IA

Use IA para:

- escrever ou revisar documentação;
- preparar descrição de issues;
- preparar descrição de PRs;
- investigar bugs;
- explicar código existente;
- sugerir refatorações pequenas;
- gerar base inicial de arquivos repetitivos;
- revisar clareza, riscos e critérios de aceite.

## Quando ter cuidado

Tenha cuidado quando a tarefa envolver:

- alterações grandes de arquitetura;
- contratos de API ainda não definidos;
- dados sensíveis;
- regras de negócio críticas;
- mudanças em branch protegida;
- migrações, deploy ou comandos destrutivos.

Nesses casos, a IA deve ajudar a planejar e validar, mas a decisão precisa ser explícita do time.

## Padrão esperado de resposta

Em contexto de projeto, a IA deve:

- responder em português do Brasil;
- ser direta e prática;
- explicar o motivo técnico das decisões quando isso ajudar a revisão;
- evitar resposta genérica;
- entregar código completo quando a tarefa pedir implementação;
- sugerir mensagem de commit ao alterar arquivos;
- informar validações feitas e limitações conhecidas.

## Rastreabilidade

Toda mudança relevante deve se conectar ao fluxo:

```text
Issue -> Branch -> Commit -> Pull Request -> Merge
```

Se a IA identificar que não existe issue ou que a branch atual não combina com a mudança, deve avisar antes de editar ou registrar a exceção quando o usuário pedir para prosseguir.

## Contrato operacional obrigatório

Antes de criar ou alterar artefatos de projeto, a IA deve:

1. Ler o `AGENTS.md` local.
2. Consultar a documentação local relacionada à tarefa.
3. Consultar o YABook para padrões de GitHub, documentação, IA e condução de projeto.
4. Usar a estrutura existente do projeto.
5. Avisar quando houver divergência entre pedido, projeto e YABook.

Os formatos oficiais de issue, branch, commit e PR ficam em [Padrões rápidos](../padroes-rapidos.md). Labels, Project, `main`, `dev`, release e tags ficam em [Fluxo de trabalho com GitHub](../processos/fluxo-de-trabalho-github.md).

Não use variações locais salvo quando o projeto registrar a exceção.

## Uso econômico de contexto

Para tarefas bem descritas, a IA deve ler o mínimo necessário para executar com segurança.

Uma issue preparada para IA deve conter primeiro o que uma pessoa precisa ler rápido:

- resumo rápido;
- escopo curto;
- critérios de aceite objetivos.

Contexto detalhado para IA deve ficar em `<details>` quando for útil:

- referências documentais;
- riscos ou cuidados;
- validação sugerida;
- decisões relevantes.

Quando a issue já tiver contexto suficiente, ela deve ser a fonte principal da implementação. A IA deve buscar documentação adicional somente para confirmar regras, contratos, arquitetura ou riscos que afetem a entrega.

Leitura ampla continua adequada quando a tarefa alterar documentação estrutural, processo, requisito, contrato, fluxo, arquitetura, ADR, RFC ou planejamento.

## Limite saudável

IA não substitui revisão técnica.

O uso correto é tratar a IA como uma parceira de execução e análise, não como fonte automática de verdade.

## Regra de escrita

Texto gerado por IA deve ser podado antes de virar padrão.

Mantenha apenas o que ajuda alguém a executar, revisar, decidir ou continuar o trabalho. Corte repetição, explicação genérica e validações óbvias que não mudam a execução.
