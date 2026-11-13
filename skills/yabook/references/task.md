# YABook Tasks

Use para `task` e `do task`. Acompanha tarefas pessoais num repositório de dados
privado próprio, separado da memória. Fluxo e decisões da capacidade:
`produto/planejamento/yabook-tasks.md` no repositório do YABook.

Execute `python3 scripts/yabook_tasks.py <serviço>` relativo à skill instalada.
A configuração da máquina fica na seção `tasks` de `~/.config/yabook/config.json`
(ou `YABOOK_CONFIG`), fora do Git.

## Inicialização

- `task init` roda `init-plan --output <arquivo>` e mostra repositório, pasta,
  máquina, operações e avisos, sem alterar nada. Opções: `--repository
  dono/nome`, `--root`, `--machine`, `--confidential <pasta>`, `--terms
  <arquivo>`.
- `do task init` roda `init-apply --plan <arquivo> --approval-hash <hash>` com o
  plano apresentado; plano, conta, remoto ou pasta alterados exigem novo plano.
- Padrão: `YABook-task-<loginGitHub>`, o mesmo nas duas máquinas (a segunda
  conecta o existente); outra conta exige repositório privado existente.
- A aplicação define `core.hooksPath` para `.githooks` e, com `--terms`, grava
  `yabook.terms` no Git local. Sem lista, o `pre-commit` apenas avisa.

## Formato

Cada tarefa é `tarefas/<id>.md` com frontmatter: `id`, `numero` (código `@n`,
dado na criação; comandos aceitam `@n`; `numerar [--corrigir]`), `descricao` (o que é, 1–3 linhas), `tipo` (`demanda`,
`projeto`, `especificacao`, `issue`, `tarefa`, `pergunta`), `titulo`, `coluna`
e, quando houver, `ordem`, `projeto`, `demanda`, `issue` (`dono/repo#n`),
`prazo` (`AAAA-MM-DD`), `proximo_passo`, `aguardando` (de quem ou do quê; a
gravação mantém `aguardando_desde`), `sobre`, `resposta` e `refs`
(`confidencial:`, `yabook:` ou `github:`). `config.yml` guarda rótulos e a
ficha; `quadro.yml`, colunas com papel `entrada`, `pronto`, `ativo`,
`validacao`, `concluido` ou `arquivado`.

Hierarquia: `nivel` (`epico`, `historia`, `tarefa`) e `pai` (id acima). Épico não
tem pai, história fica sob épico e tarefa sob história; o filho sem `nivel`
assume o nível abaixo do pai. `tipo` segue indicando a origem. `pessoal` vem
calculado (nenhuma demanda ou projeto na cadeia de `pai`) e só é gravado quando
a pessoa marca ou desmarca; `--unset pessoal` volta ao cálculo. Iniciativa
pessoal não usa a numeração da empresa: o código exibido é a issue.

- Grave somente pela biblioteca do runtime, que valida, preserva `criada`,
  atualiza `atualizada` e recusa escrita sobre revisão diferente da lida.
- Campos versionados usam texto técnico e genérico. Cliente, base, ambiente e
  acessos ficam no complemento confidencial local e entram só como `refs`.
- A gravação recusa termos da lista local; não contorne movendo o texto para
  outro campo versionado.
- `validate` confere configuração, quadro e todas as tarefas.

## Comandos

O agente interpreta o texto livre e chama o serviço com campos estruturados.

| Pedido | Serviço |
| --- | --- |
| `task` | `summary`: ativas, tarefa ativa, prazos, perguntas e colunas |
| `task show <id>` | `show`; inclui o complemento confidencial quando existe |
| `task search <termo>` | `search [--tipo] [--coluna] [--projeto] [--nivel] [--pai]`; `--projeto` inclui herdados |
| `task recent` | `recent [--limit]` |
| `task review` | `review`: perguntas abertas, atrasadas, próximas, sem prazo e paradas |
| `task add <texto livre>` | `add --tipo --titulo [--nivel --pai --pessoal sim\|nao --demanda --projeto --issue --prazo --coluna --proximo-passo --ref --sobre --body]` |
| `task edit <id> <mudança>` | `edit <id> [campos] [--unset] [--append <registro>] [--revision]` |
| `task forget <id>` | `forget <id> [--motivo]`: arquiva sem apagar |
| `task start <id>` | `start`: define a tarefa ativa e leva `entrada`/`pronto` ao papel `ativo` |
| `task ask <pergunta>` | `ask [--sobre <id>]`; a pessoa responde com `answer <id> <resposta>` |
| `task capture [assunto]` | `capture --input <lote.json> [--apply] [--approval-hash]`; ver Captura da conversa |
| `task log <id> <horas> [obs]` | `log [--data]`: horas manuais em `horas/AAAA-MM-<maquina>.jsonl` |
| `task board` | `board --serve [--port]`: site em `127.0.0.1` (porta `tasks.port` ou 8765), instalável como PWA, com modo Editar; `--output <arquivo>`: cópia estática |
| `task issue` | `issue --fase inicio\|revisao\|integrado [--ref] [--registro] [--pr]`: tarefa da issue; o hook aplica na branch, no PR e no merge |
| `task sync` | `sync`: commit local, pull com rebase e push; conflito aborta sem descartar |
| `task clean` | `clean [--days] [--apply]`: concluídas antigas e duplicatas |
| `task sheet [dia\|semana]` | `sheet [--data] [--semana]`: sugestão diária ou semanal |
| `task events` | `events [--pending] [--limit]`: histórico de ações |
| `task analyze` | `analyze --id <evento> --resultado <texto>` |
| `do task policy automatic\|manual` | `policy <modo>` |

- `--prazo` aceita `AAAA-MM-DD`, `DD/MM[/AAAA]`, `hoje`, `amanhã`, `+Nd` e dia da
  semana; prefira a data já resolvida quando a conversa for ambígua.
- Ao ouvir prazo ou entrega na conversa, proponha `task add` ou `task edit`.
- Política `automatic`: escrita direta, informando o que foi gravado. `manual`:
  mostre a mudança e aplique só após `do task`. Consulta nunca exige `do`.
- Escreva `titulo`, `proximo_passo`, registros e perguntas de forma genérica;
  sem termos da lista local nem dados de cliente.
- `clean` sem `--apply` só lista; duplicatas nunca são removidas sozinhas.

## Captura da conversa

`task capture [assunto]` registra o que a conversa tratou, sem a pessoa descrever.
Levante da conversa (ou do resumo compactado), da base confidencial do código, das
issues ligadas e das tarefas existentes; restrinja ao assunto quando informado.
Monte o lote JSON no scratchpad:

- `itens`: um por projeto, demanda, especificação ou issue, com `tipo`, `titulo`,
  códigos, `issue`, `nivel`, `pai` (chave ou id), `pessoal` só quando a pessoa
  disser, `estado` (papel ou coluna conforme a fase), `prazo`,
  `proximo_passo`, `registro` (o que foi feito), `complemento` (detalhe
  confidencial, só onde há base) e `chave` local.
- `perguntas` (`texto`, `sobre`), `ativa` (chave) e `horas` (`tarefa`, `data`,
  `horas`, `obs`) só quando a conversa informar dia e quantidade.

Sem `--apply`, o serviço devolve a prévia: criar, atualizar ou sem alteração. Ele
casa com a tarefa existente por `id`, issue, código ou título; repetir o lote não
duplica. Termo da lista local recusa o lote inteiro indicando o campo. Política
`automatic`: aplique com `--apply` e informe o resultado; `manual`: mostre a
prévia e aplique após `do task capture` com o `approval_hash`. A aplicação grava
sob uma trava, com um evento, e torna `ativa` a tarefa da sessão.

## Captura e histórico

O `hooks/hooks.json` do plugin serve Claude Code e Codex; não registre a
captura também na configuração global do host, ou ela roda duas vezes.

- `SessionStart` faz pull curto e entrega tarefa ativa sugerida, perguntas,
  prazos e até 10 ações do quadro não analisadas. Confirme a tarefa ativa com a
  pessoa uma vez por sessão e rode `start` com a escolhida; o hook vincula essa
  escolha à sessão.
- `SessionStart` também lembra as regras de manutenção: registro e próximo passo
  ao concluir etapa, dúvida da pessoa como `ask`, prazo citado e mudança de fase.
- `UserPromptSubmit` marca a janela de 15 minutos da tarefa escolhida na sessão em
  `horas/AAAA-MM-<maquina>.jsonl`, sem rede; comandos administrativos reconhecidos,
  como `task review` e `commit msg`, não geram janela. Pedidos ambíguos podem exigir correção. Mensagem com
  prazo, código ou conclusão gera um lembrete por janela; sem tarefa ativa, a
  pergunta volta uma vez após algumas mensagens.
- `Stop` faz commit local quando há mudança; o push vai em lote, em segundo
  plano, a cada 30 minutos ou por `sync`.
- Salvar no site grava pela mesma biblioteca, faz um commit e registra ações do
  quadro; o resumo copiado do site pode ser colado ao agente.
- Ações do agente entram em `eventos/` já analisadas. Ação do quadro fica
  pendente até `analyze`: analise no fim da resposta quando o pedido atual não
  tiver relação, aplique os ajustes decorrentes conforme a política e registre o
  resultado em texto genérico. `review` também traz as pendentes.

## Ficha de horas

- Use o código do próprio tipo ou do ancestral mais próximo; especificação usa
  o da cadeia e, sem código, é pessoal. Iniciativa própria é `tarefa` ou `issue`.
  Tarefa pessoal é extra; trabalho sem código vira linha `trabalho`. Horas do
  épico vão às histórias com demanda tocadas no dia.
- Na ficha, em Editar, desconsidere ou volte a considerar cada janela e salve;
  a correção preserva o histórico e vale entre máquinas. Após salvar, a
  sugestão e a cópia usam somente janelas consideradas.
- A sugestão divide `ficha.horas_dia` (8) entre as linhas na proporção das
  janelas e dos lançamentos manuais, em múltiplos de `ficha.arredondamento` (1),
  somando exatamente o total.
- Demanda dispensa observação. Nas demais linhas ela resume o dia para colar no
  sistema de horas: `Desenvolvimento: item; item.` com o campo curto `ficha` de
  cada tarefa trabalhada ou alterada no dia (ou o título) e as notas de `log`;
  sem registro, datas nem números. Preencha `ficha` ao criar histórias.
- A semana soma as sugestões diárias atuais. Arquivos de confirmações antigas
  permanecem preservados e não participam dos cálculos.
