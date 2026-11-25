# `$yabook sync`

Compara o plugin YABook instalado no seu agente com a versão de origem e diz se
está atualizado. `do sync` faz a atualização automaticamente.

## Quando usar

- Ao saber que saiu uma versão nova do YABook.
- Quando um comando ou regra parece diferente do que está no repositório.
- Depois de alterar o YABook localmente e querer usar a mudança no agente.

## Altera alguma coisa?

`sync` é somente leitura: compara arquivo por arquivo e relata origem, destino,
versão e diferenças, sem mexer em arquivos, Git ou configurações.

`do sync` atualiza a instalação: valida o pacote, substitui o plugin pelos
comandos oficiais do host e guarda a versão anterior para recuperação. Com
Claude Code e Codex instalados, atualiza os dois. Se já estiver sincronizado,
não reinstala. Preserva outros plugins, sua memória e suas configurações, e não
faz commit, push, pull nem troca de branch.

Depois de atualizar, abra uma nova sessão: a sessão atual continua com as
instruções já carregadas.

## Sintaxe

```text
$yabook sync [local|remote]
$yabook do sync [local|remote]
```

- `sync`: usa o checkout local do YABook, se válido; senão, o GitHub.
- `sync local`: compara com o checkout local.
- `sync remote`: compara com a branch principal de `YA-LABS/YABook`.
- `do sync`: aplica a atualização a partir da mesma origem.

## Exemplos

```text
$yabook sync
$yabook do sync remote
$yabook do sync local
```

- O primeiro mostra se a instalação está sincronizada ou desatualizada.
- O segundo instala a versão publicada no GitHub, sem alterar seu checkout.
- O terceiro instala o que está no seu checkout local do YABook.

## Relacionados

- `memory sync`: sincroniza conhecimento da memória, não o plugin.
- `task sync`: sincroniza o repositório de tarefas.
- `help`: lista os comandos da versão instalada.
