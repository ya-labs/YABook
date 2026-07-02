# `$yabook load`

Atualize o contexto mínimo da conversa sem carregar formatos, planejamento ou
regras de comandos ainda não solicitados.

1. Resolva a raiz por `workspace.md`.
2. Valide `.git`, arquivos ativos e remote.
3. Use a raiz como `workdir`.
4. Aplique o `AGENTS.md` somente se ainda não estiver disponível ou tiver mudado.
5. Inspecione branch, `git status --short --branch`, `git diff --stat` e remote.
6. Guarde somente raiz, remote, branch, regras locais e resumo do worktree.

Não leia `github.md`, `git.md`, formatos de artefatos ou planejamento durante o
load. A rota posterior carrega diretamente sua referência conforme `SKILL.md`.

Atualize o contexto quando mudar workspace, branch, remote, arquivos ativos ou
regras locais. Confirme Git e GitHub novamente quando o comando depender do
estado atual.

Saída:

```text
YABook carregado.

- Repositório:
- Branch:
- Worktree:
- Regras locais:

Próxima etapa:
- <uma ação útil ou "informe o objetivo">
```
