# Diagnóstico e planejamento no YABook

Use esta referência para `$yabook diagnose`, comandos `$yabook plan` e
execuções `$yabook do plan`.

## Princípios

- Diagnóstico observa o projeto; planejamento decide sua direção.
- Documentação guarda visão, escopo, roadmap e decisões relativamente estáveis.
- GitHub guarda andamento, responsáveis, bloqueios e trabalho executável.
- Planeje a versão inteira em alto nível, mas detalhe somente o próximo bloco.
- Reutilize documentos, issues, milestones e épicos antes de criar itens.
- Trate decisões recentes e entregas reais como evidência mais forte que texto antigo.
- Dentro da gramática `$yabook`, sem `do`, não altere arquivos nem sistemas externos.

## `$yabook diagnose`

Leia primeiro `AGENTS.md` e regras locais. Cruze, quando disponíveis:

- visão, requisitos, roadmap, arquitetura, ADRs e documentos da versão;
- árvore e implementação real do projeto;
- Git, branches e alterações locais;
- issues abertas e fechadas, PRs, milestones, épicos e Project.

Retorne:

1. objetivo da versão atual;
2. concluído;
3. em andamento;
4. pendente;
5. bloqueios;
6. divergências entre plano, código e GitHub;
7. próximo passo recomendado, com justificativa.

Se GitHub ou outra fonte não estiver acessível, continue com as fontes disponíveis
e identifique a limitação. Não transforme ausência de evidência em conclusão.

## `$yabook plan start <versão>`

Conduza uma entrevista colaborativa em blocos curtos. Pergunte apenas o que
materialmente altera o plano e não puder ser descoberto no repositório.

Cubra progressivamente:

- problema e público;
- resultado esperado da versão;
- escopo e fora de escopo;
- fluxos e capacidades principais;
- restrições e riscos;
- alternativas técnicas relevantes;
- critérios de pronto;
- ideias futuras que não pertencem à versão.

Não imponha arquitetura antes de entender o problema. Quando houver opções reais,
explique a recomendação e o custo das alternativas. Ao final, apresente uma
proposta consolidada ainda não gravada.

Se a versão for omitida, infira a versão em planejamento. Se houver mais de uma
possibilidade plausível, peça a versão antes de consolidar.

## `$yabook plan discuss <tema>`

Use para revisar uma parte do planejamento ou avaliar uma nova capacidade.
Separe:

- contexto;
- hipótese ou necessidade;
- alternativas;
- impacto no escopo e fora de escopo;
- decisão aceita;
- pendências;
- documentos, milestones, épicos e issues afetados.

Não trate brainstorming como decisão. A discussão só se torna permanente com
`$yabook do plan`.

## `$yabook plan status`

Avalie a maturidade do planejamento, não o estado da branch. Informe:

- versão analisada;
- partes definidas;
- decisões abertas;
- riscos sem tratamento;
- documentos ausentes ou conflitantes;
- condição para o planejamento ficar pronto para roadmap.

## `$yabook plan next`

Recomende uma única próxima ação de maior valor. Ela pode ser uma decisão,
validação, documento ou issue. Considere dependências, risco e capacidade de
desbloquear trabalho. Não crie o artefato.

## `$yabook plan roadmap`

Proponha:

- milestones da versão;
- épicos por capacidade macro;
- encaixe das issues existentes;
- dependências;
- próximo bloco de issues acionáveis;
- labels, Project, status e `Size`.

Não crie o backlog detalhado da versão inteira. Marque hipóteses e bloqueie a
materialização quando decisões essenciais ainda estiverem abertas.

## `$yabook plan review`

Revise o planejamento contra:

- problema e público;
- objetivo e limites da versão;
- coerência entre visão, escopo, arquitetura e roadmap;
- critérios verificáveis de pronto;
- riscos, dependências e decisões pendentes;
- separação entre versão atual e ideias futuras;
- separação entre documentação estável e status operacional;
- padrão YABook e exceções locais.

Retorne achados por prioridade e uma conclusão: pronto, pronto com ressalvas ou
não pronto para roadmap.

## `$yabook do plan`

Antes da primeira escrita, apresente o escopo final que será consolidado.

1. Confirme decisões aprovadas na conversa.
2. Localize documentos equivalentes e adapte-os em vez de duplicar.
3. Se não houver rastreabilidade compatível, crie uma issue de planejamento e
   uma branch `numero-descricao-curta`.
4. Atualize visão, versão, roadmap e decisões relevantes.
5. Registre um resumo da sessão com contexto, decisões, pendências e impactos.
6. Preserve hipóteses e pendências como não decididas.
7. Não crie commit.

Crie a issue e a branch antes de editar os documentos. Se a rastreabilidade for
obrigatória e GitHub ou Git não estiver disponível, não escreva arquivos:
informe o bloqueio e o comando necessário para continuar.

Núcleo padrão quando não houver estrutura equivalente:

```text
docs/planejamento/
├── visao-do-produto.md
├── roadmap.md
├── versoes/
│   └── v1.md
└── sessoes/
    └── AAAA-MM-DD-assunto.md
```

O resumo da sessão não deve ser uma transcrição. Status operacional não deve ser
copiado para Markdown.

## `$yabook do plan roadmap`

Use a proposta revisada como entrada:

1. Releia milestones, épicos, issues e Project atuais.
2. Atualize equivalentes antes de criar novos itens.
3. Crie milestones para fases da versão.
4. Crie épicos como issues com label `epic`.
5. Vincule tarefas por sub-issues nativas.
6. Se a relação nativa não estiver disponível, registre vínculo textual nos dois lados.
7. Encaixe issues existentes.
8. Aplique Project, status, labels, responsável e `Size`.
9. Crie somente o próximo bloco acionável.
10. Releia os itens e confirme campos e vínculos.

A execução deve ser idempotente. Se houver conflito sem equivalência segura,
pare o item afetado e informe a decisão necessária, sem duplicá-lo.

## Diferenças entre comandos

| Comando | Foco |
| --- | --- |
| `$yabook status` | Branch, issue e alterações do trabalho local. |
| `$yabook diagnose` | Estado real do projeto inteiro. |
| `$yabook plan status` | Maturidade e lacunas do planejamento. |
| `$yabook plan next` | Uma próxima ação recomendada. |
