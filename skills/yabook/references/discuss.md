# Discussões orientadas pelo YABook

Use esta referência para `$yabook discuss <tema>`.

## Objetivo

Analisar uma ideia, decisão ou mudança antes de transformá-la em planejamento,
documentação ou trabalho executável.

`discuss` é somente leitura. O comando não altera arquivos, GitHub, Git ou o
estado do projeto.

Uma discussão pode ser acompanhada por `steps` quando seu contexto já estiver
inequívoco. Nesse caso, `dev step` pesquisa e conduz somente a análise atual;
não exige issue ou branch e não conclui a etapa sem confirmação explícita ou
nova ação inequívoca da pessoa usuária.

## Como conduzir

Use o contexto da conversa e descubra somente o necessário para entender o tema.
Adapte a análise:

- planejamento: escopo, fora de escopo, riscos, dependências e roadmap;
- processo: regra atual, impacto operacional, exceções e compatibilidade;
- GitHub: rastreabilidade, issue, branch, PR, Project e release;
- documentação: fonte de verdade, local correto e risco de duplicação;
- implementação: necessidade, alternativas, custo, risco e trabalho executável.

Quando houver alternativas reais, recomende uma e explique brevemente o custo
das demais. Não trate brainstorming como decisão aprovada.

## Saída

Separe somente as partes aplicáveis:

- contexto;
- necessidade ou hipótese;
- alternativas;
- recomendação;
- impactos;
- decisão aceita;
- pendências;
- próximo comando recomendado.

Se a discussão afetar planejamento permanente, indique `$yabook do plan` após a
decisão. Se resultar em alteração concreta, indique `$yabook issue` antes de
branch ou implementação.

## Compatibilidade

`$yabook plan discuss <tema>` é alias de `$yabook discuss <tema>`.

O alias não limita a discussão ao planejamento. Use o tema e o contexto para
determinar a análise adequada.
