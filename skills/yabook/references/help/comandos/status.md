# `$yabook status`

Resume onde você está no trabalho: branch atual, issue inferida pela branch,
alterações pendentes e o próximo passo recomendado.

## Quando usar

- Ao voltar para um trabalho e querer saber em que ponto ele parou.
- Antes de pedir commit, PR ou uma nova implementação.
- Para confirmar se a branch atual combina com a issue em que você está.

## Altera alguma coisa?

Não. É somente leitura. Consulta branch, `git status` e o resumo do diff; só
busca a issue ligada à branch quando isso for necessário para a resposta. Não
faz commit, não troca de branch e não mexe em arquivos.

## Sintaxe

```text
$yabook status
```

- Pode ser encadeado com outros comandos usando `&`.

## Exemplos

```text
$yabook status
$yabook load & status
$yabook load & status & commit message
```

- Mostra o estado atual da branch e o que falta fazer.
- Atualiza o contexto do repositório antes de resumir o estado.
- Resume o estado e já sugere a mensagem de commit para o diff atual.

## Relacionados

- `load`: força a releitura de repositório, branch e regras locais.
- `diagnose`: diagnóstico mais amplo, com issues, PRs, milestones e roadmap.
- `commit message`: sugere a mensagem para as alterações pendentes.
