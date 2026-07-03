# Matriz de carregamento de contexto

Use esta referência para auditar dependências, revisar orçamento ou resolver
ambiguidade entre rotas. Não a carregue durante a execução normal de um comando
explícito: use diretamente a coluna `Referência inicial` já indicada em
`SKILL.md`.

## Princípios

- Metadados antes de corpos completos.
- Conversa antes de nova consulta.
- Não releia instruções já disponíveis e ainda válidas.
- Uma inspeção inicial e uma validação final por padrão.
- Workspace e `AGENTS.md` somente para rotas dependentes do repositório.
- Git e GitHub somente quando o resultado depender do estado atual.
- Pare quando houver evidência suficiente para responder com segurança.

## Classes de custo

| Classe | Uso | Limite inicial | Ampliação |
| --- | --- | --- | --- |
| `C0` | resposta instantânea | conversa e referência direta | não amplia para repositório; redirecione para outra rota |
| `C1` | contexto local mínimo | até 2 referências e metadados locais | somente por mudança ou dado local ausente |
| `C2` | artefato ou análise dirigida | até 3 referências e 3 corpos relevantes | somente por lacuna, conflito, risco ou pedido explícito |
| `C3` | execução controlada | até 4 referências antes do conteúdo da demanda | leitura incremental necessária para executar e validar |
| `C4` | auditoria ou execução profunda | escopo confirmado e lotes filtrados | proporcional ao escopo, com motivo antes de cada ampliação |

Toda ampliação acima do limite inicial registra o motivo em uma frase. Prevenção
genérica, curiosidade, completude e repetição de leitura válida não justificam
ampliação.

## Matriz

| Rota | Classe | Referência inicial | Contexto mínimo | Ampliação |
| --- | --- | --- | --- | --- |
| `help` | `C0` | `help.md` | nenhum | tópico solicitado, sem repositório |
| `mode` | `C0` | `modes.md`, modo solicitado | conversa | regras por área já citadas |
| `steps` | `C0` | `steps.md` | checklist da conversa | `steps/replanning.md` diante de desvio |
| `discuss` | `C0` | `discuss.md` | conversa | redirecione para rota dependente do projeto se precisar de fatos |
| `continue` | `C1` | `git/checkpoint.md` | checkpoint anterior e Git atual | somente mudança desde o checkpoint |
| `bypass` | `C1` | `bypass.md` | ação anexada | branch/status apenas se a ação editar |
| `load` | `C1` | `session-minimo.md`, `workspace.md` | raiz, remote, branch, status | nenhuma |
| `status` | `C1` | `workspace.md` | branch, status, diff stat | issue da branch se necessário |
| `branch name` | `C1` | `artefatos/branch-commit.md` | número e título da issue | issue recente somente se faltar na conversa |
| `commit message` | `C1` | `artefatos/branch-commit.md` | diff atual | diff completo quando o stat for ambíguo |
| `apk` | `C1` | `apk.md`, `workspace.md` | configuração, branch, worktree | Git somente para montar a prévia |
| `issue title` | `C2` | `artefatos/issue.md` | demanda da conversa | código/docs só para delimitar requisito |
| `issue`, `issue desc`, `classify` | `C2` | `artefatos/issue.md` | demanda e regras locais | `github/issues-projects.md` ao validar ou criar |
| `issue brief`, `plan brief`, `pr brief` | `C2` | `briefs.md` | conversa e fontes já válidas | fonte longa somente diante de lacuna concreta |
| `pr title` | `C2` | `artefatos/pr-release.md` | issue e diff stat | commits quando o título não for evidente |
| `pr`, `pr desc` | `C2` | `artefatos/pr-release.md` | issue, diff e commits | `github/pr-release.md` ao criar, atualizar ou revisar |
| `release` | `C2` | `artefatos/pr-release.md` | versão e diff contra base | `github/pr-release.md` para PRs/tags reais |
| `docs` | `C2` | `documentacao.md` | informação solicitada | árvore/documentos equivalentes |
| `check`, `review` | `C2` | `quality.md`, referência do artefato | artefato alvo | até 3 corpos e fontes normativas relacionadas |
| `init` | `C2` | `init.md`, `workspace.md` | estrutura e regras locais | documentos indicados por `init.md` |
| `sync` | `C2` | `sync.md` | origem e instalação | hashes/conteúdo divergente |
| `diagnose` | `C2` | `planejamento/diagnose.md` | descoberta progressiva | artefatos diretamente relevantes |
| `plan start` | `C2` | `planejamento/start.md` | documentos de visão | perguntas que mudem o plano |
| `plan status`, `plan next` | `C2` | `planejamento/status-next.md` | documentos de planejamento | GitHub se alterar a conclusão |
| `plan review` | `C2` | `planejamento/review.md` | visão, versão e roadmap | arquitetura/ADRs relacionados |
| `plan roadmap` | `C2` | `planejamento/roadmap.md` | plano aprovado e metadados GitHub | issues com equivalência incerta |
| `dev quick` | `C3` | `dev.md`, `git/checkpoint.md` | issue, branch, worktree e até 3 arquivos | motivo obrigatório antes de ampliar |
| `dev` | `C3` | `dev.md`, `git/checkpoint.md` | issue, branch, worktree | código e docs do escopo |
| `do plan` | `C3` | `planejamento/persistencia.md`, `git/checkpoint.md` | decisões e rastreabilidade | `git/mutacoes.md` quando alterar Git |
| `do plan roadmap` | `C3` | `planejamento/roadmap.md`, `github/issues-projects.md` | proposta e GitHub atual | conflitos item a item |
| `do apk` | `C3` | `apk.md`, `git/checkpoint.md` | configuração, branch, worktree e artefato | `git/mutacoes.md` quando necessário |
| `do <artefato>` | `C3` | referência do artefato e capacidades específicas | autorização e estado atual | pré-requisitos mínimos |
| `diagnose full` | `C4` | `planejamento/diagnose.md` | escopo confirmado | lotes filtrados com motivo |
| `check full`, `review full` | `C4` | `quality.md`, referência do artefato | escopo confirmado | lotes filtrados com motivo |
| `dev full` | `C4` | `dev.md`, `git/checkpoint.md` | issue, branch, worktree e escopo profundo | lotes filtrados com motivo |

As referências da tabela são carregadas diretamente. `contexto.md` não faz parte
do conjunto inicial de nenhuma rota.

## Limites de descoberta

No primeiro passe de `diagnose`, `roadmap`, `check` ou `review`:

- liste no máximo 20 itens por coleção;
- não leia issues fechadas por padrão;
- leia no máximo 3 corpos completos;
- filtre Project pelo repositório ativo;
- selecione campos necessários em vez de respostas brutas;
- informe a limitação antes de ampliar automaticamente.

As rotas `C4` permitem ampliar esses limites, mas ainda devem filtrar respostas,
evitar corpos irrelevantes e resumir cada lote antes do próximo.

## Orçamento de instruções

| Classe | Meta aproximada de instruções |
| --- | ---: |
| `C0` | até 2.000 tokens |
| `C1` | até 3.000 tokens |
| `C2` | até 3.000 tokens antes de consultar fontes externas |
| `C3` | até 4.000 tokens antes de ler o conteúdo da demanda |
| `C4` | proporcional ao escopo confirmado |

Use caracteres divididos por quatro apenas como indicador comparativo. Não
apresente essa aproximação como medição exata do plano do usuário.

Quando uma rota ultrapassar o orçamento inicial, registre qual dependência
justifica a ampliação. Histórico da conversa, instruções da plataforma e
conteúdo da própria demanda ficam fora dessa estimativa.
