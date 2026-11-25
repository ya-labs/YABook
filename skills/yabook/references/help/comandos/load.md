# `$yabook load`

Atualiza o contexto mínimo da conversa: qual repositório está ativo, a branch,
o remote, as regras locais e um resumo do que está alterado no worktree.

## Quando usar

- Você trocou de repositório, de branch ou de arquivos abertos no editor.
- A IA parece estar olhando o projeto errado ou uma branch antiga.
- Você quer conferir rapidamente o estado antes de pedir outro comando.

Não é obrigatório no início da conversa: cada comando já carrega o contexto de
que precisa.

## Altera alguma coisa?

Não. É somente leitura: resolve a raiz do projeto pelo workspace da IDE e pelos
arquivos ativos, confere `.git`, remote, `AGENTS.md` e `.yabook/AGENTS.md`, e
lê branch e status do Git. Não cria nem atualiza cache. Se workspace, arquivos
ativos e remote apontarem para projetos diferentes, ele avisa a divergência e
pede que você confirme o repositório certo.

## Sintaxe

```text
$yabook load
```

- Pode abrir um encadeamento com `&`, seguido de outros comandos.

## Exemplos

```text
$yabook load
$yabook load & status & commit message
$yabook load & issue classify & branch name
```

- Recarrega o contexto e responde com repositório, branch, worktree e regras locais.
- Atualiza o contexto, resume o estado e sugere a mensagem de commit.
- Atualiza o contexto antes de classificar a issue e sugerir o nome da branch.

## Relacionados

- `status`: resumo do trabalho em andamento com próximo passo recomendado.
- `diagnose`: visão mais ampla do projeto, com issues, PRs e roadmap.
