# YABook Skill

Este documento explica como a skill YABook funciona por dentro e como cada comando deve atuar.

O YABook Handbook continua sendo a fonte normativa. A YABook Skill é o
orquestrador inteligente do Método YA LABS para agentes de IA.

## Objetivo

A skill YABook existe para reduzir orientação repetida ao agente.

Ela deve ajudar a IA a:

- carregar o padrão YA LABS na conversa atual;
- diagnosticar onde um projeto está e recomendar o próximo passo;
- planejar versões por entrevista e discutir mudanças de escopo;
- consolidar planejamento e estruturar roadmap;
- criar ou sugerir issues, branches, commits, PRs e releases;
- classificar issues com labels e `Size`;
- validar se uma tarefa segue o YABook;
- inicializar um repositório no padrão YA LABS;
- decidir onde documentar uma informação.

## Arquitetura

A skill fica em:

```text
skills/yabook/
```

Arquivos principais:

| Arquivo | Função |
| --- | --- |
| `SKILL.md` | Entrada da skill. Define gatilhos, workflow obrigatório, padrões centrais e regras de saída. |
| `agents/openai.yaml` | Metadados para agentes que usam manifesto YAML. |
| `references/commands.md` | Lista de comandos, aliases, roteamento e formato de saída esperado. |
| `references/github.md` | Regras de issue, branch, commit, PR, labels, Project, `Size`, `main`, `dev` e release. |
| `references/git.md` | Inspeções Git permitidas, trava de mutações e escopo de autorização. |
| `references/help.md` | Help geral, ajuda por comando/família e orientação por objetivo. |
| `references/documentacao.md` | Regras para estrutura documental, Markdown, poda e templates mínimos. |
| `references/dev.md` | Desenvolvimento orientado pela issue e autorização limitada de implementação. |
| `references/ia.md` | Contrato operacional para IA e uso econômico de contexto. |
| `references/init.md` | Comportamento esperado do `$yabook init`. |
| `references/orquestracao.md` | Interpretação de intenção, correção de comandos e limites de autonomia. |
| `references/discuss.md` | Discussões gerais antes de planejar ou executar mudanças. |
| `references/planejamento.md` | Diagnóstico, entrevista, discussão, documentos de versão e roadmap. |
| `references/steps.md` | Checklist temporário e acompanhamento de etapas na conversa. |
| `references/session.md` | Comportamento esperado do `$yabook load`. |
| `references/sync.md` | Comparação e sincronização da skill instalada. |

## Fluxo de execução

Quando a pessoa usuária invoca `$yabook`, o agente deve:

1. Ler `skills/yabook/SKILL.md`.
2. Identificar o comando ou alias em `references/commands.md`.
3. Ler apenas as referências necessárias para o comando.
4. Conferir `AGENTS.md` local quando existir.
5. Conferir estado do repositório quando o comando depende de trabalho atual.
6. Aplicar o padrão YABook ou apontar divergência.
7. Entregar o artefato pronto, a ação executada ou a checagem objetiva.

Quando a entrada for uma intenção em linguagem natural, a skill seleciona os
comandos necessários, executa leituras seguras até uma decisão ou escrita e
explica no início qualquer roteamento inferido, corrigido ou composto.

O usuário continua responsável por produto, escopo, prioridades e decisões. A
skill recomenda e facilita o trabalho, mas não infere `do`.

O agente não deve carregar todo o YABook para qualquer comando. A skill usa referências curtas para economizar contexto.

## Contexto local

Para comandos que dependem do trabalho atual, o agente deve conferir:

- conversa atual;
- `AGENTS.md` local;
- branch atual;
- issue inferida pela branch, quando houver;
- `git status --short --branch`;
- `git diff --stat`;
- `git diff`, quando necessário.

Para comandos que criam ou alteram GitHub, o agente também deve conferir, quando a ferramenta estiver disponível:

- issue relacionada;
- labels existentes;
- GitHub Project;
- campo `Size`;
- PRs abertos;
- destino do PR ou merge.

## Segurança dos comandos

A trava de `do` vale para solicitações que usam a gramática `$yabook` e,
globalmente, para qualquer mutação Git em projetos YA LABS. `$yabook dev` é a
exceção documentada para preparar e implementar a issue atual. Pedidos comuns em
linguagem natural seguem o fluxo normal do agente apenas para outras ações.

Dentro da gramática YABook, a skill só pode alterar estado quando o comando
começar com `$yabook do`, usar um alias documentado como `$yabook create` ou
usar `$yabook dev` dentro de seu escopo.

A regra global inclui mutações Git locais e remotas. Sem `do`, a skill pode inspecionar
status, diff, histórico, branch e remotes, mas não pode trocar branch, preparar
arquivos, criar commits, alterar histórico, usar stash, criar tags, buscar,
integrar ou enviar alterações.

Mesmo com `do`, cada ação precisa estar explicitamente solicitada. Autorizar
commit isolado não autoriza push. Autorizar PR permite enviar somente sua branch
de origem e não autoriza outras branches, tags ou merge.

Antes de novas edições, a skill avalia se o worktree contém um bloco concluído
de outra responsabilidade. Quando houver um checkpoint coerente, pausa e mostra
o commit proposto.

Essa decisão exige uma leitura atualizada de status, diff staged e unstaged e
último commit. A skill não pode interromper usando somente cache da conversa ou
resultado de turno anterior.

`$yabook do` sem complemento autoriza apenas uma ação contextual pendente e
inequívoca. `$yabook continue` rejeita um checkpoint opcional. Depois da escolha,
a skill retoma a solicitação original com seus pré-requisitos mínimos já
autorizados, sem confirmações redundantes.

Comandos como `$yabook init`, `$yabook diagnose`, `$yabook plan`, `$yabook issue`, `$yabook pr`, `$yabook branch name` e `$yabook commit message` apenas inspecionam, conversam ou produzem propostas.

Se a pessoa pedir apenas o artefato textual, entregue o texto pronto para uso. Se ela quiser ação real no GitHub, oriente a usar `$yabook do`.

Em `main`, `dev`, release ou branch incompatível, pedidos diretos devem gerar um
bloqueio. Confirmação comum não basta. `$yabook bypass <ação>` autoriza somente
a ação anexada fora do fluxo de issue/branch; não substitui comandos `do`.

## Comandos

| Comando | Como atua |
| --- | --- |
| `$yabook help [tópico ou objetivo]` | Lista comandos, explica uma família ou recomenda um fluxo por intenção. |
| `$yabook load` | Recarrega o cache operacional quando branch, repositório ou regras locais mudarem. |
| `$yabook init` | Analisa como inicializar ou adaptar o repositório, sem alterar estado. |
| `$yabook diagnose` | Reconstrói objetivo, progresso, lacunas, bloqueios e próximo passo. |
| `$yabook plan start <versão>` | Inicia entrevista colaborativa para uma versão. |
| `$yabook discuss <tema>` | Discute uma ideia, decisão ou mudança sem alterar estado. |
| `$yabook plan status` | Avalia maturidade e decisões abertas do planejamento. |
| `$yabook plan next` | Recomenda uma única próxima ação. |
| `$yabook plan roadmap` | Propõe milestones, épicos e próximo bloco. |
| `$yabook plan review` | Revisa o planejamento contra o YABook. |
| `$yabook steps start` | Cria um checklist para acompanhar uma sequência na conversa. |
| `$yabook steps` | Mostra o checklist ativo. |
| `$yabook steps done <número>` | Marca uma etapa como concluída. |
| `$yabook steps cancel` | Encerra o acompanhamento. |
| `$yabook bypass <ação>` | Autoriza uma ação direta fora do fluxo nesta solicitação. |
| `$yabook sync [local|remote]` | Compara a instalação com a origem sem alterar arquivos. |
| `$yabook status` | Resume branch atual, issue inferida, alterações pendentes e próximo passo recomendado. |
| `$yabook check` | Verifica conformidade com YABook para branch, issue, PR, documentação ou fluxo informado. |
| `$yabook do` | Executa somente a ação pedida: init, plan, sync, issue, branch, PR, release ou merge. |
| `$yabook continue` | Rejeita uma ação contextual opcional e retoma a solicitação. |
| `$yabook dev` | Prepara, implementa e valida a issue atual. |
| `$yabook issue` | Gera título e descrição completa de issue no padrão YABook. |
| `$yabook issue title` | Gera apenas o título objetivo da issue. |
| `$yabook issue desc` | Gera apenas o corpo objetivo da issue. |
| `$yabook issue classify` | Sugere labels, `Size`, justificativa curta, confiança e quebra em issues menores quando necessário. |
| `$yabook branch name` | Sugere branch no formato `numero-descricao-curta`, baseada na issue. |
| `$yabook commit message` | Sugere mensagem no padrão `tipo: descrição curta`, considerando o diff atual. |
| `$yabook pr` | Gera título e descrição completa do PR com base na conversa e no Git. |
| `$yabook pr title` | Gera apenas o título objetivo do PR. |
| `$yabook pr desc` | Gera apenas a descrição do PR. |
| `$yabook release` | Gera descrição de release e orienta tag quando aplicável. |
| `$yabook docs` | Indica onde documentar uma informação no projeto. |
| `$yabook review` | Revisa issue, PR ou documentação contra o padrão YABook. |

`$yabook plan discuss <tema>` permanece como alias de compatibilidade para
`$yabook discuss <tema>`.

## Comandos encadeados

A skill aceita vários comandos em uma única mensagem usando `&`.

Exemplo:

```text
$yabook init & load & commit msg
```

O agente deve interpretar como:

1. `$yabook init`;
2. `$yabook load`;
3. `$yabook commit message`.

Regras:

- executar da esquerda para a direita;
- aceitar o prefixo `$yabook` apenas no primeiro comando;
- aceitar prefixo repetido em comandos seguintes sem erro;
- aplicar aliases antes de executar;
- reaproveitar contexto já coletado;
- usar o cache do `load` nos comandos seguintes;
- agrupar a resposta por comando;
- evitar repetir o mesmo diagnóstico várias vezes.

O `&` aqui não representa execução paralela. Ele define ordem de execução dentro da skill.

## Help contextual

O help possui três níveis:

- `$yabook help`: índice curto agrupado por finalidade;
- `$yabook help plan`: explica cada comando da família com exemplos;
- `$yabook help planejar a V1 do projeto`: recomenda uma sequência e explica o
  motivo de cada etapa.

Help não executa load automático, não consulta o projeto e não dispara comandos
mencionados no texto. A referência normativa é `references/help.md`.

## `$yabook dev`

`dev` é a autorização orientada ao objetivo de implementar a issue atual.

Ele identifica a demanda, prepara e vincula a branch, atualiza o status,
implementa e valida. Não cria issue silenciosamente e para diante de ambiguidade
ou decisão pendente.

```text
$yabook dev
$yabook dev & do pr
$yabook dev & do merge
```

Sozinho, `dev` para antes do commit. Com `do pr`, entrega o PR completo. Com
`do merge`, também integra depois das validações.

## `$yabook do`

`$yabook do` é o comando operacional mais flexível da skill.

O `:` é opcional:

```text
$yabook do commit pr
$yabook do: commit pr
```

Ele aceita artefatos explícitos:

```text
$yabook do issue
$yabook do branch
$yabook do init
$yabook do plan
$yabook do plan roadmap
$yabook do sync
$yabook do pr
$yabook do release
$yabook do issues
$yabook do issue branch pr
$yabook do pr merge
```

Também aceita linguagem natural:

```text
$yabook do uma issue, uma branch e um PR para main
$yabook do abra um PR e faça merge
$yabook do só uma issue para essa tarefa
```

Regras:

- criar somente o que foi pedido;
- cumprir automaticamente os pré-requisitos do objetivo autorizado;
- permitir que `do pr` crie commits coerentes, envie a branch e abra ou atualize o PR;
- permitir que `do merge` prepare o PR ausente e integre após validar condições;
- usar `do init` para aplicar a inicialização proposta;
- usar `do plan` para consolidar decisões, sem commit automático;
- usar `do plan roadmap` para criar estrutura e somente o próximo bloco;
- usar `do sync` para atualizar somente a skill instalada e validar o resultado;
- não fazer merge se a pessoa não pediu merge explicitamente;
- conferir contexto local antes de criar artefatos;
- sugerir ou aplicar labels e `Size` em issues;
- vincular ao Project quando a ferramenta permitir;
- informar valor manual quando Project ou `Size` não puderem ser aplicados pela ferramenta.

Para squash merge:

- usar assunto com referência ao PR, como `tipo: descrição curta (#numero)`;
- montar o corpo com o histórico de commits da branch contra a branch alvo;
- gerar o histórico com `git log --reverse --format='- %s (%h)' base..head`;
- usar `--body-file` quando fizer merge por `gh pr merge --squash`.

## Classificação de issue

O comando `$yabook issue classify` deve retornar:

- labels de tipo;
- labels de área;
- `Size` de `1` a `5`;
- justificativa curta;
- nível de confiança;
- sugestão de quebra quando `Size` for `5`.

`Size` é campo do GitHub Project. Não é label e não deve entrar no título da issue.

## Carregamento automático e `$yabook load`

O primeiro comando operacional `$yabook` da conversa prepara automaticamente o
contexto. O agente lê `session.md`, `AGENTS.md`, branch e estado do Git e então
executa o comando solicitado sem exibir uma resposta separada de load.

O arquivo `references/session.md` concentra o cache operacional completo: templates de issue, PR e release, labels, `Size`, branch, commit, classificação e regras de releitura.

`$yabook help` pode responder sem carregar o repositório. `$yabook load` continua
disponível para atualizar o cache depois de mudanças de branch, repositório,
regras locais ou contexto relevante.

Durante o carregamento, o agente deve:

1. ler `session.md` por completo;
2. ler `AGENTS.md` do repositório atual, se existir;
3. inspecionar o estado do Git;
4. responder com um resumo curto para a pessoa usuária.

Depois de carregar, o agente deve usar esse cache para comandos rotineiros (`issue`, `issue classify`, `branch name`, `commit message`, `pr`, `release`, `status`) sem reler `github.md` nem `session.md`.

Diagnóstico e planejamento continuam exigindo `references/planejamento.md` e descoberta atual do projeto.

Sincronização exige `references/sync.md`. A verificação é somente leitura;
qualquer atualização da instalação exige `do sync`.

## Acompanhamento de etapas

`$yabook steps` mantém uma sequência recomendada visível durante a conversa.
Enquanto houver itens abertos, o agente repete um checklist compacto no final
de cada resposta, usando `✅` para concluído, `➡️` para a próxima etapa e `⬜`
para as demais.

O checklist pode ser atualizado por subcomando ou por confirmação inequívoca em
linguagem natural. Seu estado é temporário e não deve ser salvo em arquivo,
memória permanente, issue ou Project.

Esse recurso não substitui `$yabook plan`, não executa comandos e não remove a
exigência de `$yabook do` para ações de escrita.

Mesmo com o cache carregado, ele ainda deve consultar arquivos quando:

- precisar de `git diff` para commit, PR ou release baseados no código atual;
- a tarefa for `init`, `docs`, `check`, `review` ou `do` com ação real no GitHub;
- o pedido contrariar o padrão carregado;
- houver dúvida sobre regra local não capturada no load;
- o contexto estiver incompleto;
- a pessoa pedir validação de conformidade.

O carregamento não é memória permanente. Em uma nova conversa, o comando deve ser executado novamente.

## Saídas esperadas

A skill deve entregar texto pronto para uso.

Regras de saída:

- responder em português do Brasil;
- ser objetiva;
- evitar explicação longa quando a pessoa pediu só um artefato;
- agrupar respostas por comando quando a pessoa usar `&`;
- colocar contexto extenso para IA em `<details>` apenas quando útil;
- não incluir validações genéricas em issue;
- seguir o formato documentado do YABook em vez de copiar formatos históricos de issues ou PRs do projeto, salvo pedido explícito;
- apontar exceções e riscos antes de executar ações irreversíveis.
- sugerir mensagem de commit ao final quando alterar arquivos em repositório que segue YABook.

## Limites

A skill não substitui leitura do repositório.

Ela não deve:

- inventar padrão quando o YABook já define;
- sobrescrever arquivos existentes sem aviso;
- criar pastas vazias para preencher template;
- executar merge sem pedido explícito;
- executar um comando YABook de escrita sem `do`;
- tratar `Size` como label;
- criar memória permanente a partir de `$yabook load`;
- persistir checklist de `$yabook steps` fora da conversa atual;
- documentar no YABook conteúdo específico de produto.

## Manutenção

Ao alterar a skill:

1. Atualize `SKILL.md` quando mudar gatilho, workflow ou padrão central.
2. Atualize `references/commands.md` quando mudar comando, alias ou saída.
3. Atualize a referência específica quando mudar regra de GitHub, documentação, IA, help, init, planejamento, sessão ou sincronização.
4. Atualize este documento quando a mecânica da skill mudar.
5. Rode a validação da skill e `git diff --check`.

Comando de validação:

```bash
quick_validate.py skills/yabook
```
