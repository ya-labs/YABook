# Comandos YABook

Use estes comandos quando a pessoa usuária invocar `$yabook`.

Responda em português do Brasil, com texto pronto para uso.

## Comandos

| Comando | Saída |
| --- | --- |
| `$yabook help` | Lista curta dos comandos disponíveis. |
| `$yabook load` | Carrega explicitamente ou atualiza o cache operacional da conversa. |
| `$yabook init` | Analisa como inicializar ou adaptar o padrão YA LABS, sem alterar estado. |
| `$yabook diagnose` | Reconstrói objetivo, progresso, lacunas, bloqueios e próximo passo do projeto. |
| `$yabook plan start <versão>` | Inicia entrevista colaborativa para planejar uma versão. |
| `$yabook plan discuss <tema>` | Discute uma mudança e seus impactos no planejamento. |
| `$yabook plan status` | Avalia maturidade, decisões abertas e lacunas do planejamento. |
| `$yabook plan next` | Recomenda uma única próxima decisão ou entrega. |
| `$yabook plan roadmap` | Propõe milestones, épicos, encaixes e próximo bloco de issues. |
| `$yabook plan review` | Revisa o planejamento contra o YABook. |
| `$yabook steps start` | Inicia um checklist para acompanhar etapas na conversa atual. |
| `$yabook steps` | Mostra o checklist ativo. |
| `$yabook steps done <número>` | Marca uma etapa como concluída. |
| `$yabook steps cancel` | Encerra o checklist ativo. |
| `$yabook bypass <ação>` | Autoriza uma ação direta fora do fluxo de issue/branch nesta solicitação. |
| `$yabook sync [local|remote]` | Compara a skill instalada com a origem, sem alterar arquivos. |
| `$yabook do` | Executa a ação pedida, como init, plan, sync, issue, branch, PR, release ou merge. |
| `$yabook status` | Resume branch, issue inferida, alterações pendentes e próximo passo. |
| `$yabook check` | Verifica conformidade com o YABook. |
| `$yabook issue` | Gera título e descrição completa da issue. |
| `$yabook issue classify` | Sugere labels, `Size`, justificativa e possível quebra. |
| `$yabook issue title` | Gera apenas o título da issue. |
| `$yabook issue desc` | Gera apenas o corpo da issue. |
| `$yabook branch name` | Sugere branch baseada na issue. |
| `$yabook commit message` | Sugere mensagem de commit no padrão. |
| `$yabook pr` | Gera título e descrição completa do Pull Request. |
| `$yabook pr title` | Gera apenas o título do Pull Request. |
| `$yabook pr desc` | Gera apenas a descrição do Pull Request. |
| `$yabook release` | Gera descrição completa de release. |
| `$yabook docs` | Indica onde documentar uma informação. |
| `$yabook review` | Revisa issue, PR ou documentação contra o padrão YABook. |

## Comandos encadeados

Use `&` para executar vários comandos YABook na mesma mensagem.

Formato:

```text
$yabook comando 1 & comando 2 & comando 3
```

Exemplos:

```text
$yabook init & load & commit msg
$yabook load & status & commit message
$yabook load & issue classify & branch name
$yabook check & pr desc
```

Regras:

- Execute os comandos da esquerda para a direita.
- O prefixo `$yabook` é obrigatório apenas no início. Se aparecer de novo em outro trecho, ignore o prefixo repetido.
- Aplique aliases antes de executar cada comando.
- Reaproveite contexto, `AGENTS.md`, estado do Git e cache carregado por comandos anteriores.
- Se `load` aparecer no encadeamento, use o cache carregado para os comandos seguintes.
- Se um comando depender de alterações atuais, confirme com Git antes de responder aquele comando.
- A trava de `do` vale para comandos `$yabook`, não para pedidos normais em
  linguagem natural.
- Só comandos iniciados por `$yabook do` ou aliases documentados, como
  `$yabook create`, podem executar artefatos da gramática YABook.
- Comandos que geram artefatos textuais, como `$yabook issue`, `$yabook pr`,
  `$yabook branch name`, `$yabook commit message`, `$yabook status`, `$yabook check`
  e `$yabook review`, não podem executar comandos de escrita no GitHub, mesmo que
  o artefato pareça óbvio.
- Se um comando `do` criar, publicar, fazer merge ou alterar GitHub, confira risco e contexto antes de executar.
- Se algum comando não puder ser executado com segurança, informe o bloqueio e continue apenas com comandos que não dependem dele.

Pedidos diretos sem `$yabook` seguem o fluxo normal do agente. Antes de editar
em `main`, `dev`, release ou branch incompatível, bloqueie e oriente a pessoa a
repetir a ação com `$yabook bypass <ação>`. Uma confirmação comum não autoriza.

`$yabook bypass <ação>` vale somente para a ação anexada e ignora apenas a
exigência de issue/branch. Não use `bypass` como substituto de `do issue`,
`do branch`, `do commit`, `do pr`, `do release`, `do merge` ou outros comandos
YABook que alterem estado.

## Carregamento automático

No primeiro comando operacional `$yabook` da conversa:

1. leia `session.md` por completo;
2. leia o `AGENTS.md` local, quando existir;
3. confira branch, `git status --short --branch` e `git diff --stat`;
4. mantenha esse contexto como cache da conversa;
5. execute o comando solicitado sem responder com uma seção separada de load.

Não repita o carregamento nos comandos seguintes da mesma conversa.

Exceções:

- `$yabook help` pode responder sem carregar contexto do repositório;
- `$yabook load` força o carregamento ou atualiza o cache quando branch,
  repositório, regras locais ou contexto relevante mudarem.

Saída:

- Responda em uma seção curta por comando.
- Evite repetir o mesmo contexto em todas as seções.
- Se houver alteração de arquivos em repositório que segue YABook, finalize com `Commit sugerido`.

## `$yabook do`

`$yabook do` é adaptável à solicitação da pessoa usuária.

Aceite artefatos explícitos:

```text
$yabook do issue
$yabook do branch
$yabook do init
$yabook do plan
$yabook do plan roadmap
$yabook do sync
$yabook do sync local
$yabook do sync remote
$yabook do pr
$yabook do release
$yabook do issues
$yabook do issue branch pr
$yabook do pr merge
```

Aceite linguagem natural:

```text
$yabook do uma issue, uma branch e um PR para main
$yabook do abra um PR e faça merge
$yabook do só uma issue para essa tarefa
```

Regras:

- Crie somente o que foi pedido.
- Não faça merge se a pessoa não pediu merge explicitamente.
- Antes de criar artefatos, confira `AGENTS.md`, branch atual, issue relacionada, labels, Project e `Size`.
- Se a ferramenta GitHub não conseguir aplicar Project ou `Size`, entregue o valor sugerido para preenchimento manual.
- Se o pedido misturar criação e merge, confira destino, status e risco antes.

Por artefato:

- Init: aplicar a proposta produzida por `$yabook init`, preservando conteúdo existente.
- Plan: consolidar decisões aprovadas nos documentos e criar issue/branch de
  planejamento quando a rastreabilidade ainda não existir; nunca criar commit.
- Plan roadmap: materializar milestones, épicos, vínculos e somente o próximo
  bloco acionável; reler o resultado e não duplicar equivalentes.
- Sync: validar a origem, sincronizar somente a instalação `yabook`, remover
  excedentes do destino e validar novamente; nunca alterar ou atualizar a origem.
- Issue: gerar título, descrição, labels, `Size` e Project quando aplicável.
- Branch: usar `numero-descricao-curta`; basear em `main` ou `dev` conforme fluxo.
- PR: usar título objetivo e descrição com `Resumo rápido`, `O que mudou`, `Observações` e `Informações para IA`.
- Release: usar formato de release do YABook e tags quando aplicável.
- Merge: executar apenas com pedido explícito e depois de conferir risco.
- Squash merge: usar assunto com referência ao PR, como `tipo: descrição curta (#numero)`.
- Squash merge: montar o corpo com o histórico de commits da branch contra a branch alvo.

Para montar o histórico do squash merge, use a comparação entre base e head do PR:

```bash
git log --reverse --format='- %s (%h)' base..head
```

Exemplo conceitual:

```text
Assunto:
docs: reestrutura YABook para contexto de IA (#19)

Corpo:
Histórico da branch contra main:
- docs: reestrutura yabook para leitura humana e ia (caa3513)
- chore: exclui design system desatualizado (316fa7a)
- docs: adiciona padrões rápidos da ya labs (7b87415)
```

Ao usar `gh pr merge --squash`, prefira `--body-file` para evitar que quebras de linha virem texto literal.

## Aliases

| Alias | Comando oficial |
| --- | --- |
| `$yabook branch` | `$yabook branch name` |
| `$yabook commit msg` | `$yabook commit message` |
| `$yabook classify` | `$yabook issue classify` |
| `$yabook estimate` | `$yabook issue classify` |
| `$yabook create` | `$yabook do` |
| `$yabook issue batch` | `$yabook do issues` |
| `$yabook pr description` | `$yabook pr desc` |
| `$yabook issue description` | `$yabook issue desc` |
| `$yabook doc` | `$yabook docs` |
| `$yabook validate` | `$yabook check` |
| `$yabook diagnóstico` | `$yabook diagnose` |
| `$yabook planejamento` | `$yabook plan` |

## Contexto por comando

### Depois de `$yabook load`

Se a sessão já foi carregada na conversa atual:

- use o cache de `session.md` para `issue`, `issue classify`, `branch name`, `commit message`, `pr`, `release` e `status`;
- não releia `github.md` nem `session.md` para esses comandos;
- confirme com Git (`status`, `diff`) quando o artefato depender da alteração atual;
- aplique overrides locais já lidos de `AGENTS.md` no load.

### Sempre

- Para `pr`, `pr desc`, `commit message` e `release`, use conversa atual e confirme com Git.
- Para `issue`, use o pedido do usuário, o escopo descoberto e o padrão documentado do YABook.
  Trate a descrição de um problema, ajuste ou melhoria como entrada do fluxo e
  transforme-a em trabalho executável antes de branch ou implementação.
  Não copie o formato de issues anteriores do projeto quando ele divergir do YABook,
  salvo pedido explícito da pessoa usuária.
- Para `issue classify`, retorne labels, `Size`, justificativa curta, confiança e sugestão de quebra quando necessário.
- Para `do`, leia a solicitação e execute apenas os artefatos pedidos.
- Para `diagnose`, `plan` e `do plan`, leia `planejamento.md`.
- Para `steps` e enquanto houver checklist ativo, leia e aplique `steps.md`.
- Para `sync` e `do sync`, leia `sync.md`.
- Para qualquer `help`, leia `help.md`; não execute load automático nem o
  comando mencionado dentro da solicitação de ajuda.
- Para `init`, apenas inspecione e proponha; para alterar, exija `do init`.
- Para `branch name`, use o número da issue quando existir.
- Para `docs`, leia `documentacao.md`.
- Para `init`, leia `init.md`.
- Para `load`, leia `session.md` por completo e também `AGENTS.md` quando existir.
- Para `check` e `review`, leia `github.md`, `documentacao.md` e `ia.md` conforme o artefato revisado.

## Formato do help

Use `help.md` para distinguir:

- `$yabook help`: índice curto;
- `$yabook help <comando ou família>`: explicação, sintaxe e exemplos;
- `$yabook help <objetivo>`: sequência recomendada com o motivo de cada etapa.

Help é sempre somente leitura e não dispara o fluxo sugerido.

## Saídas

- Não explique o YABook inteiro quando a pessoa pedir um artefato.
- Entregue o texto pronto para copiar.
- Inclua observações apenas quando houver risco, exceção ou contexto faltante.
- Em comandos encadeados, agrupe a resposta por comando e reaproveite contexto já informado.
- Enquanto houver checklist `steps` ativo, repita o estado compacto ao final de cada resposta.
- Quando alterar arquivos em repositório que segue YABook, termine a resposta com uma sugestão de commit no padrão do projeto.
