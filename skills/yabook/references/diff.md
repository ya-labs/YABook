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

## Explain

`$yabook diff explain [arquivo]` explica cada bloco no VS Code:

1. `blocks [--arquivo]` devolve blocos numerados (`b1`...) em JSON;
2. escreva uma ou duas frases por bloco: o porquê e o efeito, sem repetir o
   código; use o contexto da sessão antes de reler fontes;
3. envie `{"b1": "texto"}` por heredoc a `explain [--arquivo]`, que valida os
   ids, grava `explain.json` e abre a sessão com os comentários.

Não crie arquivo para o JSON: o comando é consulta e o hook barra `Write`.

Sem `--sessao`, usa a sessão atualizada mais recentemente. Responda com a
lista de arquivos e o caminho do `.patch`; não repita o diff na conversa.
