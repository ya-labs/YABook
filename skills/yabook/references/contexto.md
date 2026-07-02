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

## Matriz

| Rota | Classe | Referência inicial | Contexto mínimo | Ampliação |
| --- | --- | --- | --- | --- |
| `help` | instantânea | `help.md` | nenhum | tópico solicitado |
| `mode` | instantânea | `modes.md` | conversa | regras por área, se citadas |
| `steps` | instantânea | `steps.md` | checklist da conversa | nenhuma |
| `continue` | instantânea | `git.md` | checkpoint anterior | Git atual antes de retomar |
| `discuss` | instantânea | `discuss.md` | conversa | repositório somente se o tema exigir fatos |
| `bypass` | local mínima | `bypass.md` | ação anexada | branch/status apenas se a ação editar |
| `load` | local mínima | `session-minimo.md`, `workspace.md` | raiz, remote, branch, status | nenhuma |
| `status` | local mínima | `workspace.md` | branch, status, diff stat | issue da branch se necessário |
| `branch name` | local mínima | `artefatos/branch-commit.md` | número e título da issue | issue recente somente se faltar na conversa |
| `commit message` | local mínima | `artefatos/branch-commit.md` | diff atual | diff completo quando o stat for ambíguo |
| `issue title` | artefato | `artefatos/issue.md` | demanda da conversa | código/docs só para delimitar requisito |
| `issue`, `issue desc`, `classify` | artefato | `artefatos/issue.md` | demanda e regras locais | `github.md` somente ao validar ou criar |
| `pr title` | artefato | `artefatos/pr-release.md` | issue e diff stat | commits quando o título não for evidente |
| `pr`, `pr desc` | artefato | `artefatos/pr-release.md` | issue, diff e commits | `github.md` ao criar, atualizar ou revisar |
| `release` | artefato | `artefatos/pr-release.md` | versão e diff contra base | `github.md` para PRs/tags reais |
| `docs` | artefato | `documentacao.md` | informação solicitada | árvore/documentos equivalentes |
| `init` | contextual | `init.md`, `workspace.md` | estrutura e regras locais | documentos indicados por `init.md` |
| `check`, `review` | contextual | referência do artefato | artefato alvo | fontes normativas aplicáveis |
| `sync` | contextual | `sync.md` | origem e instalação | hashes/conteúdo divergente |
| `apk` | local mínima | `apk.md`, `workspace.md` | configuração, branch, worktree | Git somente para montar a prévia |
| `diagnose` | planejamento | `planejamento/diagnose.md` | descoberta progressiva | artefatos diretamente relevantes |
| `diagnose full` | planejamento pesado | `planejamento/diagnose.md` | escopo confirmado | coleção completa com limites explícitos |
| `plan start` | planejamento | `planejamento/start.md` | documentos de visão | perguntas que mudem o plano |
| `plan status`, `plan next` | planejamento | `planejamento/status-next.md` | documentos de planejamento | GitHub se alterar a conclusão |
| `plan review` | planejamento | `planejamento/review.md` | visão, versão e roadmap | arquitetura/ADRs relacionados |
| `plan roadmap` | planejamento | `planejamento/roadmap.md` | plano aprovado e metadados GitHub | issues com equivalência incerta |
| `do plan` | execução | `planejamento/persistencia.md`, `git.md` | decisões e rastreabilidade | documentos equivalentes |
| `do plan roadmap` | execução | `planejamento/roadmap.md`, `github.md` | proposta e GitHub atual | conflitos item a item |
| `dev` | execução | `dev.md`, `git.md` | issue, branch, worktree | código e docs do escopo |
| `do apk` | execução | `apk.md`, `git.md` | configuração, branch, worktree e artefato | nenhuma |
| `do <artefato>` | execução | referência do artefato e `git.md` quando aplicável | autorização e estado atual | pré-requisitos mínimos |

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

`diagnose full` permite ampliar esses limites, mas ainda deve filtrar respostas,
evitar corpos irrelevantes e resumir cada lote antes do próximo.

## Orçamento de instruções

| Classe | Meta aproximada de instruções |
| --- | ---: |
| instantânea | até 3.000 tokens |
| local mínima | até 3.000 tokens |
| artefato | até 3.000 tokens antes de consultar fontes externas |
| planejamento dirigido | até 3.000 tokens antes de ampliar descoberta |
| execução | até 4.000 tokens antes de ler o conteúdo da demanda |
| diagnóstico completo | proporcional ao escopo confirmado |

Use caracteres divididos por quatro apenas como indicador comparativo. Não
apresente essa aproximação como medição exata do plano do usuário.

Quando uma rota ultrapassar o orçamento inicial, registre qual dependência
justifica a ampliação. Histórico da conversa, instruções da plataforma e
conteúdo da própria demanda ficam fora dessa estimativa.
