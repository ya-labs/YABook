# Sessão de planejamento — dashboard de contexto da YABook Skill

Data: 2026-07-04
Rastreabilidade: issues #61 e #62

## Contexto

A exportação opt-in de telemetria externa da issue #61 abriu caminho para a
leitura visual das métricas de contexto na issue #62. Depois da primeira
implementação do dashboard, surgiu a necessidade de transformar a entrega em um
recurso mais fácil de descobrir e usar por quem não acompanhou a implementação.

O problema deixou de ser apenas “ter um painel” e passou a ser “explicar para
que ele serve, quando ele ajuda de verdade e como alguém consegue usá-lo sem
precisar abrir documentação longa ou redescobrir comandos”.

## Decisões aprovadas

- O `README` do dashboard deve ser curto e servir principalmente para anunciar a
  existência do recurso.
- O uso prático do dashboard deve ser documentado no `docs/manual.md`, com foco
  em:
  - como gerar o dataset;
  - como abrir localmente;
  - quando o dashboard é útil;
  - quando ele não é necessário;
  - como interpretar os blocos principais.
- A skill deve ganhar `help dashboard` como ajuda rápida de consulta, sem
  executar nada e sem exigir leitura prévia do manual.
- O `help dashboard` deve explicar:
  - o que é o dashboard;
  - a diferença entre payload exportado e painel;
  - os comandos para gerar o dataset e abrir a página;
  - o caráter somente leitura e os limites do recurso.

## Decisões não aprovadas como entrega atual

- Criar agora uma rota operacional dedicada, como `dashboard build` ou
  `dashboard serve`.
- Tratar o dashboard como parte do roteamento principal da skill além do escopo
  de ajuda.

Esses pontos permanecem como evolução posterior, caso o uso recorrente mostre
que o atalho operacional vale o custo extra de gramática, testes e manutenção.

## Impactos esperados

- O dashboard deixa de ser um artefato escondido em arquivo local e passa a ter
  caminho de descoberta, consulta e uso mais claro.
- Pessoas que usam a skill sem contexto prévio conseguem entender o painel sem
  abrir documentação estrutural inteira.
- A documentação separa melhor três camadas:
  - descoberta rápida;
  - uso detalhado;
  - ajuda contextual imediata.

## Pendências mantidas

- Avaliar se o uso real justifica um comando operacional do dashboard.
- Validar se `help dashboard` cobre a maior parte das dúvidas sem aumentar
  demais o custo do help geral.

## Resultado da sessão

- Ficou aprovado registrar o dashboard no manual e no help da skill.
- O README permanece enxuto e apontando para os dois caminhos de consulta.
- O atalho operacional do dashboard foi explicitamente adiado para uma etapa
  futura.
