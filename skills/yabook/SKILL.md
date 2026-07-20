---
name: yabook
description: Orchestrate the YA LABS Method through $yabook commands, issue-driven development, planning, GitHub artifacts, documentation, and safe execution.
---

# YABook

Aplique o Método YA LABS sob demanda.

## Fluxo

1. Identifique o comando, alias ou intenção antes de carregar referências.
2. Use [roteamento.md](references/roteamento.md) só para aliases, encadeamentos
   ou gramática e [orquestracao.md](references/orquestracao.md) para linguagem
   natural.
3. Comandos explícitos usam sua referência direta. Consulte
   [contexto.md](references/contexto.md) só para auditoria ou ambiguidade.
4. Resolva [workspace.md](references/workspace.md) somente quando a rota depender
   do projeto. Workspace e arquivos ativos prevalecem sobre `cwd`.
5. Leia `AGENTS.md` apenas quando suas regras ainda não estiverem disponíveis.
6. Amplie quando faltar evidência. Responda em português, com concisão.

`load` atualiza só o contexto mínimo:
[session-minimo.md](references/session-minimo.md).

## Economia de contexto

Antes de ler, classifique a rota: `C0` instantânea, `C1` local mínima, `C2`
dirigida, `C3` execução incremental ou `C4` profundidade explícita. Não
ultrapasse a classe sem lacuna, risco, conflito, erro ou pedido; informe o motivo
antes de ampliar. Não leia por prevenção. Regras completas:
[contexto.md](references/contexto.md).

## Segurança

- Sem `do`, comandos YABook analisam, orientam ou geram texto.
- Nunca infira `do`.
- `$yabook dev` é o atalho para preparar, implementar e validar a issue atual;
  ele não é um gate exclusivo para editar arquivos nem substitui `do` para
  commit, PR, merge ou release.
- Mutações Git seguem `$yabook do <ação>`. Leia
  [git/mutacoes.md](references/git/mutacoes.md) somente quando houver mutação.
- `bypass` ignora apenas a exigência de issue/branch compatível para a ação
  anexada. Leia [bypass.md](references/bypass.md); ele não substitui `do`.
- Execute somente o objetivo autorizado. Merge exige pedido explícito.
- Antes de editar, atualize status, diffs staged/unstaged e último commit. Se
  houver outro bloco concluído, aplique
  [git/checkpoint.md](references/git/checkpoint.md).
- Reutilize contexto válido; consulte fontes adicionais somente diante de
  lacuna. Faça uma inspeção inicial e uma validação final.
- Limite saídas de ferramenta a 4.000 caracteres. Orçamentos:
  [ia.md](references/ia.md).
- Não invente fatos, requisitos ou decisões.

## Referências diretas

- Conversa: [help](references/help.md), [mode](references/modes.md),
  [steps](references/steps.md), [discuss](references/discuss.md).
- Artefatos: [issue](references/artefatos/issue.md),
  [branch/commit](references/artefatos/branch-commit.md),
  [PR/release](references/artefatos/pr-release.md).
- Briefs: [contrato](references/briefs.md).
- Execução: [dev](references/dev.md), [sync](references/sync.md),
  [apk](references/apk.md), [init](references/init.md),
  [docs](references/documentacao.md).
- Qualidade: [check/review](references/quality.md).
- Planejamento: [índice](references/planejamento/index.md).
- Contexto sob demanda: [workspace](references/workspace.md),
  [Git](references/git.md), [GitHub](references/github.md),
  [IA](references/ia.md), [load](references/session-minimo.md).

## Regras de execução

- Comandos encadeados com `&` executam da esquerda para a direita e reutilizam
  somente o contexto coletado que continuar válido.
- Issue usa título objetivo, labels oficiais úteis à organização e `Size` de
  `1` a `5` no Project.
- Branch usa `numero-descricao-curta`.
- Commit usa `tipo: descrição curta`.
- PR usa título objetivo e mantém vínculo com a issue.
- Em `do branch` ou `dev`, prefira `createLinkedBranch` e confirme
  `issue.linkedBranches`.
- `apk` apenas apresenta a prévia com base em `.yabook/apk.json`; `do apk`
  copia o APK já gerado para o nome padronizado e remove cópias preparadas
  antigas.
- Ao concluir `dev`, apresente `Como testar` e o relatório `O que foi feito`,
  `Como foi feito`, `Por que foi feito assim` e `Observações para revisão`.
- No squash merge, use `tipo: descrição (#PR)` e registre no corpo o histórico
  da branch contra a base.

## Saída

- Entregue somente o artefato ou resultado solicitado.
- Mostre roteamento apenas quando ele for inferido, corrigido ou composto.
- Enquanto houver checklist `steps` ativo, inclua uma única vez seu estado
  compacto na resposta final de qualquer comando YABook — inclusive em
  orientação, preparação de artefato, execução, validação ou bloqueio. Coloque
  o bloco após o resultado principal e imediatamente antes de `Próxima etapa`.
  Preserve os estados ✅, ➡️ e ⬜ conforme o checklist atual, sem inventar
  progresso nem avançá-lo automaticamente; a etapa atual deve permanecer ➡️.
  Não mostre o bloco quando não houver checklist ativo. `dev step` executa só a
  etapa atual.
- Encerre respostas YABook com `Próxima etapa`, indicando uma única ação útil;
  quando não houver outra ação, informe que o fluxo foi concluído.
- Quando alterar arquivos, sugira uma mensagem de commit.
