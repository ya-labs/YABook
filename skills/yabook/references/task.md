# YABook Tasks

Use para `task` e `do task`: tarefas pessoais num repositório de dados privado,
separado da memória. Execute `python3 scripts/yabook_tasks.py <serviço>` relativo
à skill; a máquina se configura na seção `tasks` de `~/.config/yabook/config.json`
(ou `YABOOK_CONFIG`).

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

Cada tarefa é `tarefas/<id>.md` com frontmatter: `id`, `numero` (`@n` na criação,
aceito nos comandos; `numerar [--corrigir]`), `descricao` (obrigatória ao criar
uma tarefa pelo agente, conforme o [contrato abaixo](#contrato-da-descrição)),
`maquina` (identificador da máquina na criação, de `tasks.machine`; cards
anteriores sem o campo aparecem como `trabalho`),
`size` (1–5 na escala das issues, obrigatório ao criar: o da issue ou estimado;
reestime só com mudança de escopo; `size_manual` prevalece), `rodada` (sobe ao voltar da
validação; com ajustes, vá à coluna Ajustes), `tipo` (`demanda`,
`projeto`, `especificacao`, `issue`, `tarefa`, `pergunta`), `titulo`, `coluna`
e, quando houver, `relatorio_conclusao` (Markdown), `ordem`, `projeto`, `demanda`, `issue` (`dono/repo#n`),
`prazo` (`AAAA-MM-DD`), `proximo_passo`, `aguardando` (de quem ou do quê; a
gravação mantém `aguardando_desde`), `sobre`, `resposta` e `refs`
(`confidencial:`, `yabook:` ou `github:`). `config.yml` guarda rótulos e a
ficha; `quadro.yml`, colunas com papel `entrada`, `pronto`, `ativo`,
`validacao`, `concluido` ou `arquivado`.

Hierarquia: `nivel` (`epico` > `historia` > `tarefa`) e `pai`; filho sem `nivel`
assume o nível abaixo do pai e `tipo` indica a origem. `pessoal` é calculado (sem
demanda ou projeto na cadeia), gravado só quando a pessoa marca; `--unset pessoal`
volta ao cálculo. Iniciativa pessoal exibe a issue como código.

- Grave só pela biblioteca do runtime (recusa revisão diferente da lida).
- Campos versionados usam texto técnico e genérico; cliente, base, ambiente e
  acessos vão ao complemento confidencial, só como `refs`.
- A gravação recusa termos da lista local; não os mova para outro campo.
- `validate` confere configuração, quadro e todas as tarefas.

## Contrato da descrição

Preencha `descricao` em Markdown com os mesmos campos do corpo de uma
[issue do YABook](artefatos/issue.md). Em uma tarefa com issue vinculada,
aproveite os fatos da issue e delimite a parte que pertence à tarefa.
Título, código, vínculo com a issue e tamanho continuam nos campos do card.
Preencha com fatos confirmados e indique o que ainda precisa ser definido.

```md
## Resumo rápido

- **Tarefa** — O que precisa ser feito.
- **Entrega esperada** — Resultado para quem vai usar ou receber a entrega.
- **Limite** — Até onde vai a tarefa.

## Escopo

- Mudanças incluídas nesta tarefa.

## Critérios de aceite

- Condições verificáveis para considerar a entrega concluída.

## Informações para IA

- **Contexto confirmado e objetivo** — Situação atual e o resultado pretendido.
- **Decisões, limites e premissas** — Condições que orientam a execução.
- **Abordagem e pontos relevantes para continuidade** — O que outra sessão precisa saber para retomar.
- **Validações executadas ou esperadas** — Como verificar a entrega e o que já foi verificado.
- **Riscos, dependências e pendências** — O que pode afetar a entrega ou ainda depende de definição.
```

Atualize a descrição com `task edit --descricao` ou pelo card à medida que
mudarem as decisões, o escopo ou o aceite. Registre a mudança relevante e sua
origem no histórico (`edit --append`). Mantenha referências detalhadas que
ajudam a retomar o trabalho em anotações, como um inventário confirmado de
fontes ou uma regra de negócio.

## Contrato do relatório de conclusão

Ao concluir uma tarefa, preencha `relatorio_conclusao` com fatos confirmados
da entrega. Use a estrutura do [corpo de um PR do YABook](artefatos/pr-release.md):

```md
## Resumo rápido

- **Objetivo** — O resultado que se pretendia alcançar.
- **Entrega** — O resultado que foi efetivamente entregue.
- **Issue ou PR** — Referência, se houver.

## O que mudou

- O que foi feito e como a entrega foi implementada.

## Observações

- Validações executadas, resultados e pendências relevantes.

## Informações para IA

- Decisões, restrições e pontos úteis para retomar o trabalho, quando houver.
```

O card exibe o relatório logo abaixo da descrição enquanto a tarefa estiver em
Concluído. A descrição continua explicando o objetivo e o escopo da tarefa.
Acrescente ou revise o relatório pelo modo Editar do card ou com
`task edit --relatorio-conclusao`. Na conclusão manual, grave o relatório junto
com a nova coluna. Se a tarefa for reaberta, revise o relatório na próxima entrega.

Ao concluir pela integração de um PR, o fluxo usa o título ou o corpo do PR e
inclui o vínculo quando o card ainda estiver sem relatório. O conteúdo segue
as mesmas regras de confidencialidade da descrição. Em tarefas concluídas
com informação insuficiente, deixe o relatório pendente de preenchimento.

## Comandos

O agente interpreta o texto livre e chama o serviço com campos estruturados.

| Pedido | Serviço |
| --- | --- |
| `task` | `summary`: ativas, tarefa ativa, prazos, perguntas e colunas |
| `task show <id>` | `show`; inclui o complemento confidencial quando existe |
| `task search <termo>` | `search [--tipo] [--coluna] [--projeto] [--nivel] [--pai]`; `--projeto` inclui herdados |
| `task review` | `review`: perguntas abertas, atrasadas, próximas, sem prazo, sem `size`, sem `descricao` e paradas |
| `task add <texto livre>` | `add --tipo --titulo --descricao --size [--nivel --pai --pessoal sim\|nao --demanda --projeto --issue --prazo --coluna --proximo-passo --ref --sobre --body]` |
| `task edit <id> <mudança>` | `edit <id> [campos] [--unset] [--append <registro>] [--revision]` |
| `task anotacao <id> <ação>` | `anotacao <id> <ação> [--numero N] [--titulo ... --texto ...] [--revision ...]` |
| `task anexar <id> <arquivo>` | `anexar <id> <arquivo> --local\|--compartilhado [--nome ...] [--revision ...]` |
| `task editar-anexo <id> <chave>` | `editar-anexo <id> <chave> --revision ... --nome ...\|--arquivo ...\|--excluir` |
| `task baixar-anexo <id> <chave>` | `baixar-anexo <id> <chave> --output <arquivo-novo>` |
| `task forget <id>` | `forget <id> [--motivo]`: arquiva sem apagar |
| `task start <id>` | `start`: define a tarefa ativa e leva `entrada`/`pronto` ao papel `ativo` |
| `task ask <pergunta>` | `ask [--sobre <id>]`; resposta dada na conversa: o agente grava `answer <id> <resposta>` |
| `task capture [assunto]` | `capture --input <lote.json> [--apply] [--approval-hash]`; ver Captura da conversa |
| `task retroativo` | `retroativo --sessao <id-do-aviso>` mostra as janelas. Após `do task retroativo`, use `--apply --approval-hash <hash-da-previa>` |
| `task log <id> <horas> [obs]` | `log [--data]`: duração manual sem horário |
| `task log <id>` com início e fim | `log <id> --inicio HH:MM --fim HH:MM [--data] [--observacao]`: calcula a duração do intervalo |
| `task horas mover` | `horas mover --data --de --para [--janelas]`: janelas do dia para outra tarefa |
| `task board` | `board --serve [--port]`: site em `127.0.0.1` (porta `tasks.port` ou 8765), com modo Editar; `--output <arquivo>`: cópia estática |
| `task issue` | `issue --fase inicio\|revisao\|integrado [--ref] [--registro] [--pr]`: tarefa da issue; o hook aplica na branch (e copia o `Size` por `--size-da-issue`), no PR e no merge |
| `task espelhar` | `espelhar [--simular]`: Status/Size no Project da issue, só avança (`tasks.espelho.status`) |
| `task estimativa` | `estimativa`: horas das concluídas por `size`, com as fora da faixa |
| `task sync` | `sync`: commit local, pull com rebase e push; conflito aborta sem descartar |
| `task clean` | `clean [--days] [--apply]`: concluídas antigas e duplicatas |
| `task sheet [dia\|semana]` | `sheet [--data] [--semana]`: sugestão diária ou semanal |
| `task events` | `events [--pending] [--limit]`: histórico de ações |
| `task analyze` | `analyze --id <evento> --resultado <texto>` |
| `do task policy automatic\|manual` | `policy <modo>` |

- `--prazo`: `AAAA-MM-DD`, `DD/MM[/AAAA]`, `hoje`, `amanhã`, `+Nd` ou dia da
  semana. Prazo citado na conversa vai para a tarefa.
- `automatic`: grave direto e informe; nunca peça `do` ou confirmação para manter
  tarefas. Só `manual` aplica após `do task`. Consulta nunca exige `do`.
- `clean` sem `--apply` só lista; duplicatas nunca são removidas sozinhas.

## Informações da tarefa

- A máquina de origem aparece em **Campos** ao abrir o card. O filtro **Máquina** no Quadro vale para as
  apresentações Quadro e Lista e pode ser combinado com os demais filtros.

- Use **Editar** no cabeçalho do card aberto para ativar o rascunho. **Sair** ou **Descartar** no mesmo lugar volta à leitura do card.
- Anotações têm número por tarefa, título e texto. O site aplica criar, editar e excluir no rascunho e grava em Salvar. Número excluído não é reutilizado.
- Ao receber informação nova e confirmada, abra a tarefa por `task show` e use a revisão lida. Se enriquecer uma nota do mesmo assunto, edite-a por número preservando o conteúdo válido. Se for assunto novo, crie uma nota. Exclua apenas a pedido da pessoa.
- Quando mudar o escopo, atualize a descrição e registre a mudança e a origem em `edit --append`. Atualize o próximo passo se a decisão afetar a execução. Se o inventário estiver pendente, aguarde a fonte confirmada.
- Anexe o arquivo real quando recebido ou localizado e relevante. Use `--local` para material interno ou confidencial e um nome genérico no card. Use `--compartilhado` para arquivo aprovado para o repositório privado de tarefas. A cópia estática não inclui anexos. Cada documento tem até 1 MB. Arquivos pendentes no site ficam na aba até salvar, e as notas usam o rascunho persistente existente.
- Abaixo de **Relacionamentos** no painel da tarefa ficam **Anexos**, **Links** e **Anotações**. Use **Editar → Links → Adicionar link** para incluir endereços HTTP ou HTTPS. O nome é opcional e pode ser adicionado ou alterado em **Editar nome**. As mudanças entram no rascunho e são gravadas ao usar **Salvar** no quadro. Os links ficam no repositório privado de tarefas e aparecem no painel ao vivo.
- Na política automática, use esses comandos quando a tarefa e a evidência forem claras. Se houver conflito com decisão anterior ou dúvida sobre o destino/sigilo, resolva antes de gravar.

## Captura da conversa

`task capture [assunto]` registra o que a conversa tratou, a partir dela (ou do
resumo), da base confidencial, das issues e das tarefas. Lote JSON no scratchpad:

- `itens`: um por tarefa, projeto, demanda, especificação ou issue. Em item novo,
  inclua `tipo`, `titulo`, `descricao` (use o [contrato acima](#contrato-da-descrição))
  e `size` (inteiro de 1 a 5, da issue ou estimado). Inclua, quando
  couber, códigos, `issue`, `nivel`, `pai` (chave ou id), `pessoal` só quando a pessoa
  disser, `estado` (papel ou coluna conforme a fase), `prazo`,
  `proximo_passo`, `relatorio_conclusao` (entrega final em Markdown), `registro`
  (histórico do que já foi feito), `complemento` (detalhe
  confidencial, só onde há base) e `chave` local.
- `perguntas` (`texto`, `sobre`), `ativa` (chave) e `horas` (`tarefa`, `data`,
  `obs` opcional). Em `horas`, use `inicio` e `fim` se a pessoa informar
  o horário. Use o campo `horas` se ela informar só a duração.

Sem `--apply`, devolve a prévia. A captura casa por `id`, issue, código ou título
e aceita atualizações parciais de tarefas existentes. A prévia e a aplicação
recusam o lote se um item novo estiver sem descrição ou Size válido. Termo da
lista local também recusa o lote indicando o campo. `automatic` aplica
com `--apply`; `manual` aplica após `do task capture` com o `approval_hash`. A
aplicação torna `ativa` a tarefa da sessão.

Anotações e anexos são gravados por comandos próprios. Ao concluir uma captura
que trouxe uma informação relevante ou um arquivo, confira os materiais já
registrados na tarefa e use `task anotacao` ou `task anexar` conforme a
política. Em `automatic`, faça isso ao identificar a informação, inclusive
durante o trabalho entre as mensagens, e mencione o que foi registrado.

## Captura e histórico

O `hooks/hooks.json` do plugin serve Claude Code e Codex; não registre a
captura também na configuração global do host, ou ela roda duas vezes.

- `SessionStart` faz pull curto e entrega tarefa sugerida, perguntas, prazos e até
  10 ações do quadro pendentes. Confirme a tarefa uma vez e rode `start`.
- Antes de trabalhar ou mudar de assunto identificável, rode `task start` na tarefa
  do chamado/issue; reuse a confirmação inicial e pergunte só se ambíguo. Trabalho
  geral fica no épico. `edit` numa tarefa abaixo da ativa troca a ativa sozinho;
  em tarefa sem relação, o hook avisa. Não reconstrua horas por eventos ou tamanho.
- Após a escolha inicial, pedido direto com uma referência inequívoca (código,
  `@n`, `dono/repo#n`, `issue #n`) troca a tarefa antes da janela; várias
  referências ou tarefa inexistente/encerrada suspendem a marca. Menção incidental
  e consulta administrativa não trocam. Sessões são isoladas.
- `UserPromptSubmit` marca a janela de 30 min da tarefa da sessão em
  `horas/AAAA-MM-<maquina>.jsonl`, sem rede; comandos administrativos (`task
  review`, `commit msg`) não geram janela. Prazo, código ou conclusão gera um
  lembrete por janela; sem tarefa ativa, a pergunta volta após algumas mensagens.
  Cada nova marca grava a duração em minutos. Registros antigos sem duração
  valem 15 minutos, inclusive os pendentes de atribuição.
- Antes da primeira escolha, o hook guarda as janelas elegíveis em
  `local/sessoes/<sessão>.json`. As janelas do mesmo dia local são atribuídas
  à primeira tarefa da sessão por `start`, `add` ou `capture --apply` com
  `ativa`. Um novo `add` com tarefa já escolhida deixa a sessão na tarefa atual.
  O agente informa a tarefa, a quantidade e o intervalo das janelas atribuídas.
  Na Ficha, elas aparecem como **Capturado** e podem ser movidas ou desconsideradas.
- Na política `manual`, mostre as janelas e a tarefa da prévia. Aplique com o
  hash da prévia só após `do task retroativo`. O destino continua sendo a primeira
  tarefa, mesmo se a sessão trocar de foco. As janelas vencem na virada do dia.
  Para desabilitar a captura retroativa, configure `tasks.retroativo: false`.
- `Stop` faz commit local quando há mudança; o push vai em lote, em segundo
  plano, a cada 30 minutos ou por `sync`.
- Salvar no site grava pela mesma biblioteca, com commit e ações do quadro
  pendentes até `analyze`: analise no fim da resposta, aplique os ajustes conforme
  a política e registre em texto genérico. Ações do agente já entram analisadas.

- Épicos podem ir a Concluído diretamente no quadro ou na CLI, inclusive com
  uma issue vinculada. Para histórias e tarefas com branch ou PR vinculado,
  o merge continua sendo exigido antes da conclusão.

## Ficha de horas

- Para usar só as horas de uma máquina na Ficha e na visão Semana, adicione
  `maquina: trabalho` à seção `ficha` do `config.yml` do repositório de dados.
  Use o valor de `tasks.machine` da máquina de trabalho. A configuração seleciona
  janelas e lançamentos manuais. Correções feitas em qualquer máquina continuam
  valendo. Sem `ficha.maquina`, a ficha usa as horas de todas as máquinas.
  Com o filtro ativo, a observação usa tarefas com horas da máquina selecionada,
  pois a data da última edição de uma tarefa não identifica sua origem.
- Código do próprio tipo ou do ancestral mais próximo; especificação sem código e
  tarefa pessoal são extras; trabalho sem código vira linha `trabalho`. Horas do
  épico ficam no projeto; eventos ou tamanho não comprovam horas de filhos.
- Na Ficha, em Editar, cada janela pode ser desconsiderada, considerada de novo ou
  movida para outra tarefa (`task horas mover --data --de --para [--janelas]`).
  Correções preservam o histórico, valem entre máquinas e não duplicam tempo.
- Em lançamentos manuais, registre o intervalo exato se informado, por exemplo
  `task log @129 --inicio 10:40 --fim 12:00 --data 2026-11-24`. A duração é
  calculada no mesmo dia. Use `24:00` como fim de um intervalo que termina
  à meia-noite e dois lançamentos para atravessar a virada.
- Na linha do tempo, intervalos manuais aparecem como **Informado**. Seus minutos
  têm prioridade sobre a captura automática. Intervalos manuais simultâneos
  dividem o minuto entre as tarefas e repetições da mesma tarefa contam uma vez.
  Lançamentos só com duração aparecem em Informado, sem posição na linha do tempo.
- **Tempo com horário** soma a captura efetiva e os minutos informados com horário.
  **Acumulado** soma as frentes automáticas simultâneas onde não há horário
  informado e inclui lançamentos sem horário. A Ficha, a Semana e o card usam
  a mesma prioridade. Esses tempos são estimativas a partir dos registros.
- `Rateado` sugere até +50% sobre a base, no máximo 1 h por código, limitado ao
  saldo de `ficha.horas_dia` (8), proporcional; não força a jornada nem reduz
  bases maiores; `ficha.arredondamento` não se aplica ao rateio. A pessoa escolhe
  os tempos no timesheet externo; o site mostra saldos, sem preencher ficha.
- Demanda tocada sob projeto capturado, sem janela própria, aparece sem captura e
  sem sugestão.
- Demanda dispensa observação; nas demais linhas ela é `Desenvolvimento: item;
  item.` com o campo `ficha` (ou o título) das tarefas do dia e as notas de `log`,
  sem datas nem números; só há cópia da observação não vazia. Preencha `ficha` ao
  criar histórias. A semana soma as sugestões diárias; confirmações antigas não
  entram nos cálculos.
