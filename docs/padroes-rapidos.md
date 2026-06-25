# Padrões rápidos da YA LABS

Este documento resume os padrões operacionais mais usados no dia a dia.

## Sumário

- [Por que temos padrões](#por-que-temos-padroes)
- [Como os padrões são feitos](#como-os-padroes-sao-feitos)
- [Padrão de issue](#padrao-de-issue)
- [Padrão de branch](#padrao-de-branch)
- [Padrão de commit](#padrao-de-commit)
- [Padrão de PR](#padrao-de-pr)

<a id="por-que-temos-padroes"></a>

## Por que temos padrões

Padrões evitam que cada projeto organize trabalho de um jeito diferente.

Eles ajudam a:

- encontrar tarefas rapidamente;
- manter histórico claro;
- reduzir decisões repetidas;
- facilitar trabalho com IA;
- manter os projetos da YA LABS consistentes.

<a id="como-os-padroes-sao-feitos"></a>

## Como os padrões são feitos

Um padrão deve ser simples, prático e reutilizável.

Antes de virar padrão, ele precisa:

- resolver um problema real;
- ser fácil de explicar;
- funcionar em mais de um projeto;
- evitar ambiguidade para pessoas e IA;
- ser objetivo o bastante para ser seguido sem interpretação.

Quando um projeto precisar fugir do padrão, registre a exceção no próprio projeto.

<a id="padrao-de-issue"></a>

## Padrão de issue

Título objetivo, sem prefixo de tipo.

Use labels para indicar tipo e área.

Estrutura base:

```md
## Resumo rápido

- Tarefa:
- Entrega esperada:
- Limite:

## Escopo

- 

## Critérios de aceite

- 
```

Contexto extra para IA deve ficar em `<details>` apenas quando for necessário.

<a id="padrao-de-branch"></a>

## Padrão de branch

Use o número da issue no início:

```text
numero-descricao-curta
```

Exemplo:

```text
17-reestrutura-yabook-para-ia
```

Não use tipo, área, `issue`, `#`, acentos ou espaços.

<a id="padrao-de-commit"></a>

## Padrão de commit

Use:

```text
tipo: descrição curta
```

Exemplos:

```text
docs: atualiza padrões rápidos
feat: adiciona tela de login
fix: corrige validação do token
chore: ajusta configuração de build
```

<a id="padrao-de-pr"></a>

## Padrão de PR

Use título objetivo, sem prefixo de tipo.

No corpo, vincule a issue:

```md
Closes #numero
```

Estrutura base:

```md
## Contexto

Explique em poucas linhas o objetivo do PR.

Closes #numero

## O que mudou

- 

## Observações

- 
```
