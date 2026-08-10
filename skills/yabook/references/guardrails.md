# Guardrails globais do YABook

Use esta referência para `$yabook guardrails` e `$yabook do guardrails <ação>`.

## Objetivo

Aplicar o núcleo operacional do YABook em todos os repositórios atendidos pelo
perfil Codex, sem substituir instruções pessoais ou regras específicas de cada
projeto. A configuração vive em `~/.codex/AGENTS.md` e é lida pelo Codex no
início de uma nova sessão.

## `$yabook guardrails`

É uma rota `C1`, sem escrita. Leia apenas `~/.codex/AGENTS.md` e informe:
`ausente`, `instalado`, `divergente` ou `duplicado`. Não resolva workspace nem
carregue Git, GitHub ou planejamento.

## `$yabook do guardrails install`

É uma rota `C3`. Antes de escrever, releia `~/.codex/AGENTS.md` e mostre a
alteração pretendida. Crie o arquivo quando ausente; quando existir, acrescente
ou atualize somente o bloco entre os marcadores. Preserve todo conteúdo externo
aos marcadores. Diante de bloco duplicado, marcador incompleto ou conteúdo que
não possa ser atualizado sem ambiguidade, pare sem escrever e informe a correção
necessária.

```md
<!-- YABOOK-GUARDRAILS:START -->
## Guardrails YA LABS

- Antes de editar arquivos em um repositório Git, confirme a branch atual,
  `git status --short --branch`, os diffs staged e unstaged e o último commit.
- Se houver alteração concluída de outra responsabilidade, pare e peça um
  checkpoint antes de iniciar novo escopo. Não troque de branch com alterações
  fora do escopo de destino.
- Mutações Git locais ou remotas exigem `$yabook do <ação>`. Um pedido comum,
  `bypass` ou `dev` não autoriza commit, push, merge, tag, stash, reset ou
  mudança de branch fora de sua autorização documentada.
- Em `main`, `dev` ou branch de release, bloqueie edição direta por padrão.
  `$yabook bypass <ação>` autoriza somente a edição anexada nesta solicitação;
  ele não substitui `$yabook do` para mutações Git.
- Regras de segurança não podem ser removidas por instruções locais. Quando
  houver conflito, explique a divergência e peça autorização compatível.
<!-- YABOOK-GUARDRAILS:END -->
```

Depois da escrita, releia o arquivo e confirme `instalado`. Informe que a
proteção passa a valer em uma nova sessão do Codex.

## `$yabook do guardrails remove`

É uma rota `C3`. Releia o arquivo, remova somente um bloco canônico delimitado
pelos marcadores e preserve todo o restante. Se o bloco estiver ausente,
divergente ou duplicado, não tente corrigir automaticamente: informe o estado
e pare. Releia o resultado e informe que uma nova sessão deixa de aplicar o
bloco removido.

## Limites

- `guardrails` não altera configurações da interface do ChatGPT/Codex.
- `install` e `remove` exigem `do`; nenhum comando infere essa autorização.
- O bloco não cria issue, branch, commit, PR, merge ou release.
- O `bypass` liberado pelo bloco vale só para edição direta em branch
  incompatível; mutações Git continuam sob o contrato de `do`.
