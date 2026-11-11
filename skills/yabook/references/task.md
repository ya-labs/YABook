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
- Sem indicação, o repositório é `YABook-task-<loginGitHub>` da conta
  autenticada. Use o mesmo repositório nas duas máquinas: na segunda, o plano
  conecta o existente. Repositório de outra conta precisa existir e ser privado;
  nunca crie uma segunda base por inferir o login de outra máquina.
- A aplicação define `core.hooksPath` para `.githooks` e, com `--terms`, grava
  `yabook.terms` no Git local. Sem lista, o `pre-commit` apenas avisa.

## Formato

Cada tarefa é `tarefas/<id>.md` com frontmatter: `id`, `tipo` (`demanda`,
`projeto`, `especificacao`, `issue`, `tarefa`, `pergunta`), `titulo`, `coluna`
e, quando houver, `ordem`, `projeto`, `demanda`, `issue` (`dono/repo#n`),
`prazo` (`AAAA-MM-DD`), `proximo_passo`, `sobre`, `resposta` e `refs`
(`confidencial:`, `yabook:` ou `github:`). `config.yml` guarda rótulos e a
ficha; `quadro.yml`, colunas com papel `entrada`, `pronto`, `ativo`,
`validacao`, `concluido` ou `arquivado`.

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
| `task search <termo>` | `search [--tipo] [--coluna] [--projeto]` |
| `task recent` | `recent [--limit]` |
| `task review` | `review`: perguntas abertas, atrasadas, próximas, sem prazo e paradas |
| `task add <texto livre>` | `add --tipo --titulo [--demanda --projeto --issue --prazo --coluna --proximo-passo --ref --sobre --body]` |
| `task edit <id> <mudança>` | `edit <id> [campos] [--unset] [--append <registro>] [--revision]` |
| `task forget <id>` | `forget <id> [--motivo]`: arquiva sem apagar |
| `task start <id>` | `start`: define a tarefa ativa e leva `entrada`/`pronto` ao papel `ativo` |
| `task ask <pergunta>` | `ask [--sobre <id>]`; a pessoa responde com `answer <id> <resposta>` |
| `task log <id> <horas> [obs]` | `log [--data]`: horas manuais em `horas/AAAA-MM-<maquina>.jsonl` |
| `task sync` | `sync`: commit local, pull com rebase e push; conflito aborta sem descartar |
| `task clean` | `clean [--days] [--apply]`: concluídas antigas e duplicatas |
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

## Captura e histórico

O `hooks/hooks.json` do plugin serve Claude Code e Codex; não registre a
captura também na configuração global do host, ou ela roda duas vezes.

- `SessionStart` faz pull curto e entrega tarefa ativa sugerida, perguntas,
  prazos e até 10 ações do quadro não analisadas. Confirme a tarefa ativa com a
  pessoa uma vez por sessão e rode `start` com a escolhida; o hook vincula essa
  escolha à sessão.
- `UserPromptSubmit` marca a janela de 15 minutos da tarefa ativa em
  `horas/AAAA-MM-<maquina>.jsonl`, sem rede, e avisa só ações novas.
- `Stop` faz commit local quando há mudança; o push vai em lote, em segundo
  plano, a cada 30 minutos ou por `sync`.
- Ações do agente entram em `eventos/` já analisadas. Ação do quadro fica
  pendente até `analyze`: analise no fim da resposta quando o pedido atual não
  tiver relação, aplique os ajustes decorrentes conforme a política e registre o
  resultado em texto genérico. `review` também traz as pendentes.
