# Guia de Documentação Para IA

Este documento orienta assistentes de IA a consultar, manter e atualizar a documentação do projeto com economia de contexto.

Ele descreve onde buscar informação estável. Backlog, progresso, responsáveis, Project, milestones e execução devem ficar no GitHub.

## Fluxo de consulta

1. Leia o `AGENTS.md`.
2. Leia este guia quando a tarefa envolver documentação.
3. Identifique o tipo da tarefa.
4. Consulte a matriz documental.
5. Use `rg` com palavras-chave direcionadas.
6. Abra documentos completos somente quando o trecho localizado não for suficiente.

Não leia todos os documentos por padrão.

## Matriz documental

| Área | Função | Quando consultar | Quando atualizar |
| --- | --- | --- | --- |
| `README.md` | Entrada pública do projeto. | Visão geral e links principais. | Mudança de posicionamento ou leitura inicial. |
| `docs/produto/` | Conhecimento de produto. | Visão, problema, público e escopo. | Mudança de objetivo, público ou escopo. |
| `docs/arquitetura/` | Arquitetura conceitual. | Módulos, responsabilidades e comunicação. | Mudança estrutural relevante. |
| `docs/requisitos/` | O que o sistema deve fazer. | Requisitos funcionais e não funcionais. | Mudança de capacidade esperada. |
| `docs/fluxos/` | Sequências de uso. | Jornada da pessoa usuária. | Mudança na ordem ou comportamento de uso. |
| `docs/interface/` | Critérios de interface. | Entrega visual, estados e navegação. | Mudança visual recorrente ou critério de UX. |
| `docs/contratos/` | Formatos e operações. | APIs, eventos, arquivos, comandos, entradas e saídas. | Mudança de formato, validação, bloqueio ou falha esperada. |
| `docs/processos/` | Processo local. | Regras que complementam o YABook. | Mudança de fluxo operacional do projeto. |
| `docs/adrs/` | Decisões aceitas. | Confirmar decisão já tomada. | Nova decisão aceita ou substituição de decisão. |
| `docs/rfcs/` | Propostas abertas. | Ideias ainda não decididas. | Nova proposta em discussão. |
| `docs/prototipos/` | Provas e experimentos. | Evidência técnica ou validação experimental. | Nova prova, resultado ou limite observado. |
| `docs/release/` | Critérios de pronto. | Aceite final e limites de release. | Mudança nos critérios de pronto. |

## Premissas

- Markdown guarda conhecimento estável.
- GitHub guarda trabalho executável.
- ADRs registram decisões aceitas.
- RFCs registram propostas ainda abertas.
- Protótipos e provas técnicas são experimentais e não devem parecer documentação final de produto.
- O roteiro macro do projeto não deve virar status operacional.

## Quando ler documentação ampla

Leitura ampla é adequada quando:

- a issue estiver ambígua;
- a tarefa alterar documentação estrutural;
- a tarefa alterar requisito, contrato, fluxo, arquitetura, ADR ou processo;
- houver conflito entre código, documentação e issue;
- a mudança puder afetar mais de uma etapa, milestone ou épico;
- a pessoa usuária pedir atualização de contexto do projeto.

Fora desses casos, prefira leitura direcionada por issue, busca com `rg` e abertura pontual de arquivos.
