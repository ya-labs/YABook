# Guardrails globais do YABook

Use esta referência para `$yabook guardrails` e `$yabook do guardrails <ação>`.

## Objetivo

Persistir o comportamento padrão do YABook no perfil Codex, inclusive quando a
conversa não começar com `$yabook`. A configuração vive em
`~/.codex/AGENTS.md`; o Codex a aplica em nova sessão.

## `$yabook guardrails`

É uma rota `C1`, sem escrita. Leia apenas `~/.codex/AGENTS.md` e informe se o
bloco está `ausente`, `instalado`, `divergente` ou `duplicado`. Não resolva
workspace nem carregue Git, GitHub ou planejamento.

## `$yabook do guardrails install`

É uma rota `C3`. Releia `~/.codex/AGENTS.md`, mostre a alteração pretendida e
crie ou atualize somente o bloco delimitado abaixo. Preserve instruções pessoais
fora dos marcadores. Se houver bloco duplicado, marcador incompleto ou conteúdo
ambíguo, pare sem escrever e informe a correção necessária.

```md
<!-- YABOOK-GUARDRAILS:START -->
## Comportamento padrão do YABook

- Aplique o fluxo YABook em repositórios YA LABS mesmo quando `$yabook` não for
  invocado explicitamente.
- Antes de editar, valide branch, status, diffs staged/unstaged e último commit.
  Se houver trabalho independente concluído, pare e proponha checkpoint.
- Não execute mutações Git sem `$yabook do <ação>`.
- Em `main`, `dev` ou release, bloqueie edição direta. `$yabook bypass <ação>`
  libera somente a edição anexada, nunca mutações Git.
- Encerre toda resposta operacional com `Próxima etapa`, indicando uma única
  ação útil e compatível com o estado atual. Quando não houver continuação,
  informe que o fluxo foi concluído.
- Sempre que alterar arquivos, sugira uma mensagem de commit no formato
  `tipo: descrição curta`, baseada nas alterações reais. Não crie o commit sem
  `$yabook do commit`.
<!-- YABOOK-GUARDRAILS:END -->
```

Depois da escrita, releia o arquivo e confirme `instalado`. Informe que o bloco
passa a valer em nova sessão do Codex.

## `$yabook do guardrails remove`

É uma rota `C3`. Releia o arquivo e remova somente um bloco canônico delimitado
pelos marcadores, preservando todo o restante. Se estiver ausente, divergente ou
duplicado, não corrija automaticamente. Releia o resultado e informe que uma
nova sessão deixa de aplicar o bloco removido.

## Limites

- `guardrails` não altera configurações da interface do ChatGPT/Codex.
- `install` e `remove` exigem `do`.
- O bloco não cria issue, branch, commit, PR, merge ou release.
