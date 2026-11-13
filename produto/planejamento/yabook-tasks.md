# YABook Tasks — V1

## Objetivo

Acompanhar, de forma individual, todas as tarefas de uma pessoa, inclusive as
que não existem como issue no GitHub, com prazos, status por projeto, perguntas
deixadas pelo agente e uma base diária de horas trabalhadas.

O agente registra e consulta as tarefas pelos comandos `task` e pelos hooks do
plugin. A pessoa acompanha e edita por um site local sempre aberto.

## Responsabilidades

| Lugar | Contém |
| --- | --- |
| YABook (este repositório) | Contrato do formato, comandos `task`, captura pelos hooks, site e servidor local, regra de escrita genérica. |
| Repositório de dados `YABook-task-<loginGitHub>` | Tarefas, quadro, histórico de ações, propostas, horas, fichas e trava de commit. Privado e pessoal. |
| Base confidencial local | Complementos confidenciais por tarefa, páginas de conhecimento sensível e lista de termos proibidos. Nunca versionada no repositório de dados. |
| Memória YABook | Conhecimento técnico reutilizável. Não referencia tarefas. |

O repositório de dados segue a convenção da memória: o mesmo repositório nas
duas máquinas, `dono/nome` explícito aceito e nunca uma segunda base criada por
inferência de login.

## Modelo de dados

Cada tarefa é um arquivo `tarefas/<id>.md` com frontmatter:

```yaml
id: demanda-1001
tipo: demanda          # demanda | projeto | especificacao | issue | tarefa | pergunta
nivel: historia        # epico | historia | tarefa
titulo: Ajustar limite de desconto do supervisor
coluna: andamento      # id de coluna definido em quadro.yml
ordem: 3
pai: projeto-2001      # épico ou história acima
projeto: "2001"
demanda: "1001"
issue: [org/repositorio#10]
prazo: 2026-11-14
size: 3
proximo_passo: Validar no aparelho
refs: [confidencial:<pagina>, yabook:<id-da-memoria>]
```

- `projeto` e `demanda` são códigos do sistema de trabalho da pessoa. O rótulo
  exibido é configurável; por exemplo, `demanda` pode aparecer como "Chamado".
- `issue` é referência interna e de visualização; não participa da ficha.
- `aguardando` diz de quem ou do quê a tarefa espera, em texto genérico; a
  gravação registra `aguardando_desde` quando o texto surge ou muda e remove os
  dois quando a espera termina. A tarefa continua na sua coluna; `review`, o
  início da sessão e o site mostram as esperas com os dias decorridos.
- `nivel` e `pai` formam a hierarquia épico, história e tarefa. Sem demanda ou
  projeto próprios, a tarefa herda o código mais próximo da cadeia.
- `pessoal` vem calculado (nenhuma demanda ou projeto na cadeia) e pode ser
  marcado ou desmarcado à mão. Tarefa pessoal é extra na ficha e exibe a issue
  como código, pois não usa a numeração da empresa.
- Perguntas do agente são tarefas `tipo: pergunta`, com `sobre:` e `resposta:`.
- O corpo guarda um registro curto e genérico do andamento da tarefa.

Arquivos do repositório de dados:

| Arquivo | Conteúdo |
| --- | --- |
| `config.yml` | Rótulos, horas por dia e arredondamento da ficha. |
| `quadro.yml` | Colunas com nome livre e papel fixo. |
| `tarefas/<id>.md` | Uma tarefa por arquivo. |
| `eventos/AAAA-MM-<maquina>.jsonl` | Histórico de ações, somente acréscimo. |
| `propostas/<id>.md` | Mudanças estruturais aguardando análise. |
| `horas/AAAA-MM-<maquina>.jsonl` | Janelas de atividade de 15 minutos por tarefa. |
| `fichas/AAAA-MM.jsonl` | Confirmações históricas preservadas, sem uso nos cálculos atuais. |
| `.githooks/pre-commit` | Trava de termos proibidos. |

Configuração da máquina, como caminho da base confidencial, nome da máquina e
caminho da lista de termos, fica fora do Git. Horários usam o fuso local com
deslocamento explícito.

## Quadro

As colunas são personalizáveis. O agente entende somente o papel:

```yaml
colunas:
  - {id: backlog,   nome: Backlog,        papel: entrada}
  - {id: pronto,    nome: Pronto pra dev, papel: pronto}
  - {id: andamento, nome: Em andamento,   papel: ativo}
  - {id: testes,    nome: Testes,         papel: validacao}
  - {id: concluido, nome: Concluído,      papel: concluido}
  - {id: arquivado, nome: Arquivado,      papel: arquivado}
```

Regras do agente por papel:

- a tarefa ativa é sugerida entre `ativo` e `pronto`, respeitando a ordem;
- o fim de `dev` leva a tarefa para `validacao`;
- PR integrado leva a tarefa para `concluido`;
- alertas de prazo ignoram `concluido` e `arquivado`.

Renomear uma coluna não altera o comportamento do agente. Criar, remover ou
mudar o papel de uma coluna é mudança estrutural.

## Histórico de ações

Toda ação gera um evento no arquivo da máquina em que ocorreu:

```jsonl
{"id":"ev-20261111-1432-trabalho-01","ts":"2026-11-11T14:32:05-03:00","origem":"quadro","acao":"mover","tarefa":"demanda-1001","de":"andamento","para":"testes","commit":"a1b2c3d"}
{"id":"an-20261111-1501-trabalho","origem":"agente","acao":"analise","eventos":["ev-20261111-1432-trabalho-01"],"resultado":"próximo passo atualizado"}
```

- Evento do quadro sem `analise` correspondente é não analisado. A apuração
  ocorre após o `pull`, o que cobre eventos da outra máquina.
- Ações do agente entram no histórico já analisadas.
- O `SessionStart` apresenta até 10 eventos não analisados e a contagem do
  restante. O `UserPromptSubmit` avisa somente eventos novos desde o último
  aviso da sessão.
- O agente analisa no fim da resposta quando o pedido atual não tem relação.
  `task review` força a análise.
- Na política `automatic`, o agente aplica os ajustes decorrentes e registra a
  `analise`. Na política `manual`, propõe os ajustes.

## Edição pelo site

O site tem modo de edição com salvamento explícito.

| Tipo | Exemplos | Aplicação |
| --- | --- | --- |
| Mecânica | Mover ou reordenar card, editar campos, renomear coluna, corrigir janelas. | O servidor grava, cria um commit por salvamento e registra eventos não analisados. |
| Estrutural | Criar ou remover coluna, mudar papel de coluna. | O servidor grava `propostas/<id>.md`; `task change` apresenta o impacto e `do task change <id>` aplica. |

- O salvamento exibe um resumo em Markdown com o que foi aplicado, o commit e as
  propostas criadas, com opção de copiar.
- Agente e servidor usam a mesma biblioteca de escrita.
- Cada tarefa carrega a revisão do arquivo. Salvamento sobre arquivo alterado
  depois da leitura é recusado e a tela recarrega.
- Rascunhos não salvos ficam no armazenamento do navegador para resistir ao
  encerramento da página.
- O servidor confere os termos proibidos antes de gravar e oferece mover o
  texto para o complemento confidencial.

## Comandos

A família `task` segue a família `memory` quando há equivalente.

| Grupo | Comandos |
| --- | --- |
| Configuração | `task init`, `do task init`, `do task policy automatic\|manual` |
| Consulta | `task`, `task show`, `task search`, `task recent`, `task review` |
| Escrita | `task add <texto livre>`, `task edit`, `task forget`, `task start <id>`, `task ask <pergunta>`, `task log <id> <horas> [obs]`, `task capture [assunto]`, `do task capture` |
| Quadro | `task board [--serve --port\|--output]`, `task change [<texto>]`, `do task change <id>` |
| Horas | `task sheet [dia\|semana]` |
| Manutenção | `task sync`, `task clean` |

- `task init` planeja e `do task init` cria ou conecta o repositório de dados,
  clona, grava a configuração da máquina e define `core.hooksPath`.
- `task add` interpreta tipo, códigos, prazo e projeto a partir do texto livre.
  O agente também propõe registro quando a conversa menciona prazo ou entrega.
- `task forget` arquiva ou cancela sem apagar histórico.
- Na política `automatic`, comandos de escrita gravam diretamente. Na política
  `manual`, o agente propõe e `do task` aplica.

## Captura

O plugin já registra `hooks/hooks.json` no Claude Code e no Codex. A captura usa
os eventos existentes:

| Evento | Ação |
| --- | --- |
| `SessionStart` | `pull` rápido sem bloquear; sugestão da tarefa ativa; regras de manutenção das tarefas; perguntas abertas, prazos atrasados ou em até 2 dias e eventos não analisados. |
| `UserPromptSubmit` | Marca a janela de 15 minutos da tarefa ativa em arquivo local, sem rede e de forma idempotente; lembra de atualizar a tarefa quando a mensagem cita prazo, código ou conclusão e repete uma vez a pergunta da tarefa ativa. |
| `Stop` | Commit local idempotente quando houver mudança, com proteção contra concorrência. |

- A pessoa confirma ou troca a tarefa ativa no início da sessão.
- O push ocorre em lote, por `task sync` ou quando o último envio tiver mais de
  30 minutos.
- No Codex, o `Stop` não injeta contexto e não precisa injetar.
- A captura não é registrada também em configuração global do host, para não
  executar duas vezes.

## Ficha de horas

- Conta na ficha a tarefa com `demanda` ou `projeto` na cadeia, inclusive a `tipo: especificacao`; sem código, a tarefa é pessoal por padrão.
  Com `demanda` e `projeto`, as horas vão para a demanda.
- A sugestão divide as horas do dia configuradas, 8 por padrão, entre as
  tarefas que contam, na proporção das janelas de atividade e com
  arredondamento configurado, 1 hora por padrão.
- As demais tarefas são extras: ficam registradas no dia com horas estimadas,
  fora do total.
- A ficha apresenta tipo, código, início e fim opcionais, total e observação.
  Demanda dispensa observação; nas demais linhas ela resume o que foi feito no
  dia (`Desenvolvimento: item; item.`), com o texto curto `ficha` de cada
  tarefa, sem registro, datas nem números. O complemento confidencial aparece
  à parte, só na máquina que possui a base.
- Lançamentos manuais (`task log`) cobrem trabalho fora do agente.

## Site

- Servidor `task board --serve` em Python com biblioteca padrão, escutando
  apenas em `127.0.0.1`, iniciado manualmente.
- Front em HTML, CSS e JavaScript sem etapa de build; atualização por SSE a
  partir da verificação periódica dos arquivos.
- Instalado como PWA nas duas máquinas.
- Visões: Hoje, Semana, Quadro, Épicos, Prazos, Perguntas, Ficha e Histórico.
- O card mostra título, nível, código (herdado ou a issue), selo pessoal, prazo,
  `Size`, próximo passo, indicador de pergunta aberta e indicador de referência
  confidencial.
- Porta padrão 8765, configurável em `tasks.port`; Host diferente de
  `127.0.0.1` ou `localhost` é recusado e a escrita exige o token da página.
- `task board --output` gera uma cópia estática somente leitura.
- Referência confidencial é resolvida quando a base local existe na máquina;
  caso contrário, aparece bloqueada.

## Proteção de dados

- Campos versionados usam texto técnico e genérico; dados sensíveis ficam no
  complemento confidencial.
- O `pre-commit` versionado bloqueia diffs com termos da lista local. Sem a
  lista, apenas avisa.
- Horários brutos de atividade e configuração da máquina não são versionados.

## Marcos

| Marco | Entrega |
| --- | --- |
| M1 | Repositório de dados, `task init`, comandos, captura nos dois hosts, histórico de ações e `task sheet` por comando. |
| M2 | Site com as visões, edição mecânica, resumo do salvamento e visão Histórico. |
| M3 | Quadro personalizável, propostas estruturais com `task change` e campo `Size`. |

## Fora da V1

- Labels e campos personalizados além de `Size`.
- Incorporação de bases confidenciais existentes ao modelo de tarefas.
- Aplicativo nativo; a V1 usa PWA.
- Comparação entre estimativa e tempo real, relatórios periódicos e mineração
  de transcrições.
- Login, uso multiusuário, integração com sistemas externos de atendimento e
  busca semântica.

## Riscos

| Risco | Mitigação |
| --- | --- |
| Vazamento de dado sensível em texto livre | Regra de escrita, `pre-commit` e checagem no servidor. |
| Custo de contexto do histórico | Limite de eventos e aviso apenas para eventos novos. |
| Latência do hook por mensagem | Escrita local sem rede, com meta abaixo de 100 ms. |
| Conflito entre máquinas | Um arquivo por tarefa; eventos e horas por máquina. |
| Memória limitada na máquina de trabalho | Servidor sem dependências, front sem framework e medição no M2. |
| Captura duplicada no Codex | Registro único pelo manifesto do plugin. |

## Critérios de pronto

- `do task init` funciona nas duas máquinas sobre o mesmo repositório.
- A captura funciona no Claude Code e no Codex.
- O hook por mensagem leva menos de 100 ms, medido.
- Eventos do quadro chegam ao agente e deixam de ser pendentes após a
  `analise`, inclusive quando vêm da outra máquina.
- Edição concorrente sobre a mesma tarefa é recusada sem perda de dado.
- O `pre-commit` bloqueia termo da lista, com teste automatizado.
- `task sheet` soma as horas configuradas nas tarefas que contam e lista os
  extras.
- Referência confidencial é resolvida na máquina que possui a base e aparece
  bloqueada nas demais.
- Na máquina de trabalho, o servidor usa menos de 40 MB e a página menos de
  100 MB com 300 tarefas.
- A capacidade é documentada em `skills/yabook/references/task.md` e roteada em
  `skills/yabook/references/roteamento.md`.
