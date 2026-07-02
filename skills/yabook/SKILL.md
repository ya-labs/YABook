---
name: yabook
description: Orchestrate the YA LABS Method through natural-language routing, issue-driven development, planning, GitHub artifacts, documentation, and safe execution. Use when the user invokes $yabook, describes a YA LABS workflow goal, needs the correct command, plans or diagnoses a project, develops an issue, or creates and reviews GitHub artifacts.
---

# YABook

Roteie o Método YA LABS usando o Handbook como fonte normativa sob demanda.

## Fluxo

1. Identifique o comando, alias ou intenção antes de carregar referências.
2. Consulte [roteamento.md](references/roteamento.md) somente para aliases,
   encadeamentos ou dúvida de gramática; comandos explícitos conhecidos seguem
   direto para sua referência.
3. Em linguagem natural, correção de comando ou composição, leia
   [orquestracao.md](references/orquestracao.md).
4. `help`, `mode`, `steps`, `discuss` e `bypass` usam sua referência direta.
   As demais rotas explícitas também usam diretamente a referência indicada
   abaixo. Consulte [contexto.md](references/contexto.md) somente para auditar
   dependências, resolver ambiguidade entre rotas ou revisar o carregamento.
5. Resolva [workspace.md](references/workspace.md) somente quando a rota depender
   do projeto. Workspace e arquivos ativos prevalecem sobre `cwd`.
6. Leia `AGENTS.md` apenas quando suas regras ainda não estiverem disponíveis.
7. Amplie o contexto somente quando faltar evidência.
8. Responda em português do Brasil, de forma curta e prática.

`$yabook load` apenas atualiza o contexto mínimo do repositório conforme
[session-minimo.md](references/session-minimo.md).

## Segurança

- Sem `do`, comandos YABook analisam, orientam ou geram texto.
- Nunca infira `do`.
- `$yabook dev` autoriza preparar, implementar e validar a issue atual, mas não
  commit, PR, merge ou release.
- Mutações Git exigem `$yabook do <ação>` ou o escopo limitado de `dev`. Leia
  [git/mutacoes.md](references/git/mutacoes.md) somente quando houver mutação.
- `bypass` ignora apenas a exigência de issue/branch compatível para a ação
  anexada. Leia [bypass.md](references/bypass.md); ele não substitui `do`.
- Execute somente o objetivo autorizado. Merge exige pedido explícito.
- Antes de editar, atualize status, diffs staged/unstaged e último commit. Se
  houver outro bloco concluído, aplique
  [git/checkpoint.md](references/git/checkpoint.md).
- Reutilize contexto válido. Consulte memória, GitHub ou documentos adicionais
  somente diante de lacuna concreta.
- Por padrão, faça uma inspeção inicial e uma validação final; amplie diante de
  erro, ambiguidade ou risco.
- Limite cada saída de ferramenta a 4.000 caracteres. Orçamentos de operações e
  rodadas ficam em [ia.md](references/ia.md).
- Não invente fatos, requisitos ou decisões.

## Referências diretas

- Conversa: [help](references/help.md), [mode](references/modes.md),
  [steps](references/steps.md), [discuss](references/discuss.md).
- Artefatos: [issue](references/artefatos/issue.md),
  [branch/commit](references/artefatos/branch-commit.md),
  [PR/release](references/artefatos/pr-release.md).
- Execução: [dev](references/dev.md), [sync](references/sync.md),
  [apk](references/apk.md), [init](references/init.md),
  [docs](references/documentacao.md).
- Planejamento: [índice](references/planejamento/index.md).
- Contexto sob demanda: [workspace](references/workspace.md),
  [Git](references/git.md), [GitHub](references/github.md),
  [IA](references/ia.md), [load](references/session-minimo.md).

## Regras de execução

- Comandos encadeados com `&` executam da esquerda para a direita e reutilizam
  somente o contexto coletado que continuar válido.
- Issue usa título objetivo, labels de tipo/área e `Size` de `1` a `5` no
  Project.
- Branch usa `numero-descricao-curta`.
- Commit usa `tipo: descrição curta`.
- PR usa título objetivo e mantém vínculo com a issue.
- Para branch criada por `do branch` ou `dev`, prefira `createLinkedBranch` e
  confirme `issue.linkedBranches`.
- `apk` apenas apresenta a prévia com base em `.yabook/apk.json`; `do apk`
  copia o APK já gerado para o nome padronizado e remove cópias preparadas
  antigas.
- Ao concluir `dev`, apresente `Como testar` com passos específicos, validações
  já executadas e verificações ainda pendentes.
- No squash merge, use `tipo: descrição (#PR)` e registre no corpo o histórico
  da branch contra a base.

## Saída

- Entregue somente o artefato ou resultado solicitado.
- Mostre roteamento apenas quando ele for inferido, corrigido ou composto.
- Enquanto `steps` estiver ativo, repita seu estado compacto.
- Encerre respostas YABook com `Próxima etapa`, indicando uma única ação útil;
  quando não houver outra ação, informe que o fluxo foi concluído.
- Quando alterar arquivos, sugira uma mensagem de commit.
