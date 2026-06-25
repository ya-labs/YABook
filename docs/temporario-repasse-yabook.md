# Roteiro temporário de repasse do YABook

Este documento é temporário. Use para testar o repasse do YABook com uma pessoa nova no padrão YA LABS.

## Objetivo do teste

Validar se uma pessoa consegue entender e aplicar o YABook em um projeto real sem depender de explicação longa.

Ao final, a pessoa deve conseguir:

- explicar o que é o YABook;
- saber quando consultar o YABook;
- entender o fluxo Issue -> Branch -> Commit -> Pull Request -> Merge;
- criar ou revisar uma issue no padrão;
- entender onde documentar informações de projeto;
- usar a skill `$yabook` como apoio operacional.

## Preparação

Antes da conversa, deixe aberto:

- [Manual de uso](manual.md);
- [Padrões rápidos](padroes-rapidos.md);
- [Fluxo de trabalho com GitHub](processos/fluxo-de-trabalho-github.md);
- [Skill YABook](../skills/yabook/SKILL.md);
- um projeto real ou repositório de teste.

Explique que o YABook não é documentação de produto. Ele é o padrão organizacional da YA LABS.

## Roteiro sugerido

### 1. Explicar o papel do YABook

Fale em termos simples:

> O YABook define como a YA LABS organiza documentação, issues, branches, commits, PRs, releases e uso de IA. Cada projeto guarda seus fatos reais; o YABook guarda o padrão reutilizável.

Reforce:

- YABook é padrão organizacional;
- documentação específica fica no projeto;
- exceções ao padrão devem ficar explícitas no projeto.

### 2. Mostrar o manual

Abra [Manual de uso](manual.md) e mostre:

- quando usar;
- como aplicar em projeto novo;
- uso no dia a dia;
- uso com IA;
- onde consultar padrões.

Não leia o documento inteiro. Mostre como encontrar a resposta certa rápido.

### 3. Mostrar os padrões rápidos

Abra [Padrões rápidos](padroes-rapidos.md) e mostre:

- padrão de issue;
- padrão de branch;
- padrão de commit;
- padrão de PR.

Explique a ideia principal:

> Labels indicam tipo e área. Branch e PR não repetem isso.

### 4. Mostrar o fluxo GitHub

Abra [Fluxo de trabalho com GitHub](processos/fluxo-de-trabalho-github.md) e mostre:

- labels oficiais;
- quando usar `main`;
- quando criar `dev`;
- quando usar `release/x.y.z`;
- por que `dev` é branch de ciclo, não permanente.

Não aprofunde tudo. O foco é a pessoa saber onde consultar.

### 5. Mostrar a skill

Explique que a skill reduz orientação repetida para IA.

Comandos principais:

- `$yabook help`;
- `$yabook load`;
- `$yabook init`;
- `$yabook create`;
- `$yabook issue`;
- `$yabook issue classify`;
- `$yabook branch name`;
- `$yabook commit message`;
- `$yabook pr`;
- `$yabook release`;
- `$yabook check`;
- `$yabook docs`.

Explique que a skill usa o YABook como referência, mas ainda precisa conferir o contexto real do repositório.

## Exercício prático

Peça para a pessoa executar este cenário em um projeto de teste:

1. Ler o `README.md` e o `AGENTS.md` do projeto.
2. Identificar se o projeto segue o YABook.
3. Criar uma issue para uma pequena melhoria documental.
4. Classificar labels e `Size` da issue.
5. Sugerir o nome da branch.
6. Sugerir a mensagem de commit.
7. Montar uma descrição de PR.
8. Dizer onde a melhoria deveria ser documentada.

Se a skill estiver disponível, peça para testar:

```text
$yabook load
$yabook issue
$yabook issue classify
$yabook create issue branch pr
$yabook branch name
$yabook commit message
$yabook pr
$yabook docs
$yabook check
```

## Perguntas para validar entendimento

Use estas perguntas no final:

- O que fica no YABook e o que fica no projeto?
- Por que o título da issue não precisa ter tipo?
- Por que a branch começa com número da issue?
- Quando devo criar `dev`?
- Quando uso `release/x.y.z`?
- O que faço se o projeto precisar fugir do padrão?
- Quando a IA deve ler documentação ampla?
- Quando a issue deve ser suficiente para executar?

## Critérios de sucesso

O repasse funcionou se a pessoa conseguir:

- encontrar sozinha o documento certo;
- explicar o fluxo de trabalho sem decorar tudo;
- criar uma issue curta e objetiva;
- sugerir branch e commit no padrão;
- evitar criar documentação genérica;
- entender que a IA deve consultar o YABook sem copiar o handbook inteiro para a conversa.

## Pontos para observar

Durante o teste, anote:

- onde a pessoa travou;
- quais documentos ficaram confusos;
- quais comandos da skill foram naturais;
- quais comandos ficaram ambíguos;
- quais trechos pareceram longos demais;
- o que precisou de explicação oral para fazer sentido.

## Ajustes depois do teste

Depois do repasse, revisar:

- se o [Manual de uso](manual.md) está claro o bastante;
- se [Padrões rápidos](padroes-rapidos.md) resolve a consulta do dia a dia;
- se a skill cobre os comandos que a pessoa tentou usar;
- se algum trecho do YABook ainda força explicação oral demais.

Este documento pode ser removido ou convertido em guia oficial depois do teste.
