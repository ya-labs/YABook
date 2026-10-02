---
name: yabook
description: Orchestrate the YA LABS Method through $yabook commands, issue-driven development, planning, GitHub artifacts, documentation, and safe execution.
---

# YABook

## Fluxo

1. Identifique comando e intenção antes de ler.
2. Comando explícito usa referência direta. Use
   [roteamento.md](references/roteamento.md) para aliases ou encadeamentos e
   [orquestracao.md](references/orquestracao.md) para linguagem natural.
3. [contexto](references/contexto.md): auditoria/ambiguidade.
4. [workspace](references/workspace.md): rotas de projeto; arquivos ativos
   prevalecem sobre `cwd`.
5. Aplique `.yabook/AGENTS.md` existente e informe a regra local.
6. Amplie por lacuna. Responda em português, com concisão.

`load` atualiza [contexto mínimo](references/session-minimo.md).

## Economia de contexto

Classifique: `C0` instantânea, `C1` local mínima, `C2` dirigida, `C3` incremental,
`C4` profundidade explícita. Amplie por lacuna, risco, conflito, erro ou pedido;
informe o motivo. Não leia por prevenção.
Regras: [contexto.md](references/contexto.md).

## Segurança

- Fora de `auto`, não infira `do`: análise/prévia, salvo autorizações de `dev`
  e `bypass`.
- `dev` implementa e valida a issue; fora de `auto`, termina antes de commit/PR.
  Não é gate exclusivo para editar nem autoriza merge/release.
- `bypass` dispensa issue/branch só para a ação anexada; não autoriza Git.
- `auto` explícito dispensa `do`, `bypass` e aprovação de checkpoints no objetivo.
  Vale na conversa do projeto atual até outro modo; sem persistir ou transferir.
  Permissões do ambiente continuam válidas.
- Git: `do` ou delegação em `auto`. Leia [mutações](references/git/mutacoes.md)
  só ao executar. Respeite o objetivo; merge exige pedido explícito.
- Antes de editar, atualize status, diffs staged/unstaged e último commit;
  aplique [checkpoint](references/git/checkpoint.md) a trabalho independente.
- Reutilize contexto; uma inspeção inicial e validação final. Reabra por lacuna.
  Saídas de ferramenta: até 4.000 caracteres.
  Orçamentos: [ia.md](references/ia.md). Não invente fatos ou decisões.

## Referências diretas

- Conversa: [help](references/help.md), [mode](references/modes.md),
  [steps](references/steps.md), [discuss](references/discuss.md),
  [resume](references/resume.md).
- Artefatos: [issue](references/artefatos/issue.md),
  [branch/commit](references/artefatos/branch-commit.md),
  [PR/release](references/artefatos/pr-release.md),
  [contratos canônicos](references/artefatos/contratos.md), [briefs](references/briefs.md).
- Execução: [dev](references/dev.md), [sync](references/sync.md),
  [apk](references/apk.md), [rebase](references/rebase.md), [init](references/init.md),
  [docs](references/documentacao.md), [configure](references/configure.md),
  [guardrails](references/guardrails.md), [bypass](references/bypass.md).
- Qualidade: [check/review](references/quality.md).
- Planejamento: [índice](references/planejamento/index.md).
- Contexto: [workspace](references/workspace.md), [Git](references/git.md),
  [GitHub](references/github.md), [IA](references/ia.md).

## Execução e saída

- Encadeamentos `&`: esquerda para direita, reutilizando contexto válido.
- Issue: título objetivo, labels oficiais e `Size` de `1` a `5` no Project.
- Branch: `numero-descricao-curta`; prefira `createLinkedBranch` e confirme
  `issue.linkedBranches` ao preparar branch de issue.
- Commit: `tipo: descrição curta`. Pacotes e ajustes via `bypass` exigem corpo
  com motivo e alteração. Sugira `Mensagem` e `Descrição` em blocos separados,
  sem validações; após `bypass`, registre a exceção.
- PR: título objetivo e vínculo com a issue quando aplicável. PR de pacote usa
  merge commit; squash usa `tipo: descrição (#PR)` e histórico da branch no corpo.
- Valide contratos de issue, branch, commit e PR, inclusive em `auto`;
  interrompa por campo ausente ou inválido.
- `apk` mostra prévia de `.yabook/apk.json`; `do apk` copia APK já gerado e remove
  cópias preparadas antigas.
- `dev`: `Como testar` e relatório `O que foi feito`, `Como foi feito`,
  `Por que foi feito assim` e `Observações para revisão`.
- Entregue o resultado. Mostre roteamento só se inferido, corrigido ou composto.
  Sugira commit ao alterar arquivos; em `auto`, informe
  commits realizados ou sugira mensagem para alterações ainda sem commit.
- `steps` ativo: estado compacto uma vez antes de `Próxima etapa`, após o resultado,
  sem inventar progresso. `dev step` executa só a etapa atual.
- Encerre com `Próxima etapa`: ação útil posterior ou fluxo concluído. Na prévia,
  autorização fica fora dessa seção; não repita só `do` como continuação. Sem
  caminho seguro, informe revisão pendente sem inventar comando ou autorização.
  Confira antes da resposta final.
