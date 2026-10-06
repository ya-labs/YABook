# Guardrails globais do YABook

Use esta referência para `$yabook guardrails` e `$yabook do guardrails <ação>`.

## Objetivo

O plugin substitui a instalação global após validar carregamento e hooks.
Empacote com `scripts/yabook_plugin.py build --output <destino-novo>`. Os hooks
carregam contexto no início da sessão e inspecionam chamadas suportadas;
formatos e julgamento continuam na skill. Instalação não equivale a confiança
dos hooks no host. Consulte o guia de memória para ativação por runtime.

`migrate-guardrails --agents <arquivo> --receipt <estado-da-sessão>` remove
somente um bloco canônico após evidência local de SessionStart/PreToolUse,
preservando backup e instruções pessoais. O receipt é observabilidade local,
não prova criptográfica de cobertura; valide negações reais antes de migrar.
Até essa migração, o mecanismo abaixo continua compatível.

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
  Fora de `auto`, se houver trabalho independente concluído, proponha checkpoint;
  em `auto`, preserve e separe responsabilidades sem pedir aprovação do próprio trabalho.
- Fora de `mode: auto`, não execute mutações Git sem `$yabook do <ação>`.
- Em `main`, `dev` ou release, bloqueie edição direta. `$yabook bypass <ação>`
  libera somente a edição anexada, nunca mutações Git. Em `auto`, ajuste pontual
  documentado dispensa `bypass`; trabalho com issue usa branch própria.
- `$yabook mode: auto` explicitamente ativado dispensa `do`, `bypass` e aprovação
  de checkpoints dentro do objetivo delegado. Preserve trabalho existente,
  validação e permissões do ambiente. Operações remotas dependem do pedido;
  merge exige pedido explícito. Outro modo, projeto ou sessão encerra `auto`.
- Encerre toda resposta operacional com `Próxima etapa`, indicando uma única
  ação útil e compatível com o estado atual. Quando não houver continuação,
  informe que o fluxo foi concluído.
- Sempre que alterar arquivos, sugira uma mensagem de commit no formato
  `tipo: descrição curta`, baseada nas alterações reais. Após `bypass`, apresente
  `Mensagem` e `Descrição` em blocos separados, com motivo, alteração e exceção,
  sem validações na descrição. Fora de `auto`, não
  crie o commit sem `$yabook do commit`; em `auto`, informe os commits realizados.
- `issue package` mantém descrição estável, sem listar demandas ou pendências.
  Novos pedidos geram commits documentados e PR por merge commit. Em dupla, use
  a mesma branch por turnos, preservando trabalho e autorizações de Git.
- Corpos de issues e PRs não contêm checklists, inclusive nas informações para IA.
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
