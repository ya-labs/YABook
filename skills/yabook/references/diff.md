# Diff das edições do agente

Use para `$yabook diff [sessão]`. É consulta: não altera o projeto, Git ou
GitHub; grava só na pasta de sessões de diff.

## Captura

O hook guarda, sem tokens, a versão de cada arquivo antes da primeira edição
do agente na sessão:

- `Edit`, `Write`, `MultiEdit` e `apply_patch`: cópia no `PreToolUse`;
- comando de edição (`diff.commands`, padrão `learning.edit_commands`): usa o
  backup que o próprio comando gravou (`diff.backups`, padrão
  `backup/<arquivo>.bak-AAAAMMDD-HHMMSS-<tag>`), sem cópia extra;
- edição por shell fora desses comandos não é capturada.

A cópia mantém a extensão original, para o editor aplicar a mesma linguagem e
encoding. Sessões ficam em `~/.config/yabook/diffs/<projeto>/<sessão>/` e saem
após `diff.retention_days` (padrão 14). `diff.enabled: false` desliga.

## Comandos

Rode `scripts/yabook_diff.py` no diretório do projeto. `$yabook diff` usa `open`:

- `open [--sessao] [--json]`: grava o `.patch` e abre a sessão no VS Code em
  uma aba única pela extensão `yalabs.yabook` (`apps/vscode`); sem ela, abre
  `code --diff` por arquivo alterado (até 8); sem `code`, só lista;
- `sessions`: sessões do projeto, da mais recente;
- `show [--sessao <prefixo>] [--json]`: arquivos alterados, estado e linhas;
- `patch [--sessao] [--saida <arquivo>]`: grava o `.patch` (UTF-8).

Sem `--sessao`, usa a sessão atualizada mais recentemente. Responda com a
lista de arquivos e o caminho do `.patch`; não repita o diff na conversa.
