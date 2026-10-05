# Padrões rápidos da YA LABS

Este documento resume os padrões operacionais mais usados no dia a dia.

## Sumário

- [Padrões rápidos da YA LABS](#padrões-rápidos-da-ya-labs)
  - [Sumário](#sumário)
  - [Por que temos padrões](#por-que-temos-padrões)
  - [Como os padrões são feitos](#como-os-padrões-são-feitos)
  - [Padrão de issue](#padrão-de-issue)
  - [Padrão de branch](#padrão-de-branch)
  - [Padrão de commit](#padrão-de-commit)
  - [Padrão de PR](#padrão-de-pr)

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

Issues, PRs, branches e commits antigos de um projeto podem servir como contexto, mas não substituem o padrão documentado aqui. Quando houver divergência, use este documento como fonte de verdade, salvo pedido explícito para manter um formato legado do projeto.

<a id="padrao-de-issue"></a>

## Padrão de issue

Toda coisa nova relevante no projeto começa aqui. Quando surgir um problema,
ajuste ou melhoria, transforme a necessidade em uma issue antes de criar branch
ou implementar.

Título objetivo, sem prefixo de tipo.

`$yabook issue package` prepara um registro estável do propósito geral do pacote.
Não liste demandas iniciais, pontos do documento recebido ou pendências no corpo.
Novos pedidos orientam o desenvolvimento sem atualizar a issue. Use uma branch,
commits documentados e um PR; o merge encerra o pacote. Em dupla, compartilhe a
branch trabalhando por turnos, conforme o [fluxo](../processos/fluxo-de-trabalho-github.md).

Issues e PRs são registros documentais: use texto ou bullets simples, sem
checklists ou caixas de progresso, inclusive nos blocos para IA.

Ajustes pontuais autorizados via `bypass` podem dispensar issue e branch própria.
Em `mode: auto`, o agente escolhe esse caminho sem exigir `bypass` a cada ajuste.

Use labels oficiais para indicar tipo, domínio ou agrupamento especial.

Use `Size` no GitHub Project para indicar tamanho. Não coloque tamanho no título.

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
 
## Observações

- 

<details>
<summary>Informações para IA</summary>

- Contexto:
- Validações:
- Riscos:

</details>
```

Use o bloco `Informações para IA` apenas quando houver contexto útil para revisão ou continuidade.

No squash merge, use o número do PR no assunto do commit final e inclua no corpo o histórico dos commits da branch contra a branch alvo.

Exemplo:

```text
docs: reestrutura YABook para contexto de IA (#19)

Histórico da branch contra main:
- docs: reestrutura yabook para leitura humana e ia (caa3513)
- docs: adiciona padrões rápidos da ya labs (7b87415)
```


Contexto extra para IA deve ficar em `<details>` apenas quando for necessário.

Se a issue for criada com IA, ela deve sugerir labels e `Size`. Quando sugerir `Size 5`, deve indicar como dividir a tarefa.

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

O assunto mantém esse formato. O corpo, separado por linha em branco, documenta
motivo e alteração realizada. É obrigatório para entregas
de pacote e ajustes via `bypass`; nos demais commits, use quando ajudar revisão
ou continuidade. Escreva proporcionalmente à mudança, sem formulário extenso.

Após implementar via `bypass`, sugira **Mensagem** e **Descrição** em blocos
de código separados. Não inclua validações na descrição; relate-as no
desenvolvimento e no PR.

**Mensagem:**

```text
fix: corrige mensagem de validação
```

**Descrição:**

```text
A mensagem indicava o campo obrigatório errado. Atualiza o texto para
identificar o campo correto.

Ajuste pontual via YABook bypass, sem issue.
```

Baseie a descrição no diff. No Git, mensagem e descrição são o assunto e corpo
do mesmo commit, separados por linha em branco. Fora de
`auto`, criar o commit exige `$yabook do commit`, sem exigir issue novamente.
Em `auto`, ajuste pontual sem issue também exige corpo documentado; registre
esse caminho sem afirmar uso de `bypass` quando ele não foi invocado.

<a id="padrao-de-pr"></a>

## Padrão de PR

Use título objetivo, sem prefixo de tipo.

No corpo, vincule a issue:

```md
Closes #numero
```

Estrutura base:

```md
## Resumo rápido

- Objetivo:
- Entrega:
- Issue:

Closes #numero

## O que mudou

- 

## Observações

- 

<details>
<summary>Informações para IA</summary>

- Contexto:
- Validações:
- Riscos:

</details>
```

Use o bloco `Informações para IA` apenas quando houver contexto útil para revisão ou continuidade.

PR de issue pacote resume os assuntos e corpos dos commits contra a base,
incluindo entregas de ambas as pessoas quando houver dupla. Confira o diff final
para não declarar alterações revertidas ou removidas. Registre validações e use
merge commit para preservar os commits originais e suas descrições. Se o repositório não permitir
merge commit, informe o impedimento e combine uma alternativa que preserve os
registros; não aplique squash silenciosamente.
