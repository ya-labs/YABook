# `$yabook diff`

Abre no VS Code, em uma única aba, tudo o que o agente alterou na sessão, com
cada arquivo expansível. `diff explain` acrescenta uma explicação curta em cada
bloco alterado, como comentário no próprio diff.

## Quando usar

- Ao final de uma tarefa, para revisar o que o agente mudou antes do commit.
- Quando quiser entender o motivo de cada trecho alterado.
- Para rever uma sessão anterior, ainda guardada.

## Altera alguma coisa?

Não altera o projeto, o Git nem o GitHub. Grava só na pasta de sessões de diff
(`~/.config/yabook/diffs/`): o `.patch` da sessão e, no `explain`, as
explicações. As sessões são apagadas após 14 dias, por padrão.

A versão anterior de cada arquivo é guardada antes da primeira edição do agente
na sessão. Edição por comando de shell comum não é capturada.

## Sintaxe

```text
$yabook diff [sessão]
$yabook diff explain [arquivo]
```

- `diff`: abre a sessão mais recente; informe a sessão para abrir outra.
- `diff explain`: explica os blocos da sessão; com arquivo, só dele.
- Sem a extensão, abre um diff por arquivo (até 8); sem o VS Code, só lista.

Na extensão do VS Code (barra lateral YABook e paleta):

- `YABook: Ver alterações da última sessão` e `YABook: Escolher sessão de diff`;
- visão **Alterações do agente**: clique em um arquivo para ver só o diff dele;
- `YABook: Navegar pelas explicações do diff` e `YABook: Ocultar explicações do
  diff`.

## Exemplos

```text
$yabook diff
$yabook diff explain
$yabook diff explain src/app.js
```

- O primeiro abre a aba com as alterações da sessão atual.
- O segundo comenta cada bloco com o porquê e o efeito da mudança.
- O terceiro explica só os blocos desse arquivo.

## Relacionados

- `review`: análise de qualidade e riscos da entrega.
- `commit message`: sugere a mensagem a partir do diff atual.
