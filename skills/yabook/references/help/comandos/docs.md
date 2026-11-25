# `$yabook docs`

Indica onde documentar uma informação no projeto e se ela deve virar Markdown.
A regra é simples: Markdown guarda conhecimento estável; o GitHub guarda
trabalho executável, como backlog, status, responsáveis e progresso.

## Quando usar

- Ao ter uma informação nova e não saber em qual documento ela cabe.
- Antes de criar um documento novo, para ver se um existente já resolve.
- Para identificar documentos repetidos, genéricos ou que misturam status com
  conhecimento e podem ser fundidos ou removidos.

## Altera alguma coisa?

Não por padrão: o comando orienta e pode propor texto, sem criar nem editar
arquivos. Para o agente escrever o documento, faça um pedido explícito ou use
o modo `auto`.

Em projetos no template YABook, a referência é `docs/guia-da-documentacao.md`.
Conteúdo específico de produto (endpoints, arquitetura, variáveis de ambiente,
deploy, regras de negócio) fica no repositório do projeto, nunca no YABook.

## Sintaxe

```text
$yabook docs [informação ou assunto]
```

- `docs`: orientação sobre onde documentar o que você descrever.
- `doc`: alias de `docs`.

## Exemplos

```text
$yabook docs onde registrar as variáveis de ambiente do deploy
$yabook docs devo documentar o andamento da sprint?
$yabook docs o que podar em docs/
```

- O primeiro aponta o documento do projeto adequado, fora do YABook.
- O segundo indica que andamento é status e pertence ao GitHub, não ao Markdown.
- O terceiro lista documentos que repetem regras ou não ajudam execução,
  revisão ou decisão.

## Relacionados

- `check`: confere se a documentação segue o padrão.
- `review`: analisa qualidade e clareza de um documento.
- `issue`: transforma trabalho a fazer em issue, em vez de documento.
