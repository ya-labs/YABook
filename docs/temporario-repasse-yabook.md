# Roteiro temporário de repasse do YABook

Este documento apresenta a rodada que expandiu o YABook de um conjunto de
padrões operacionais para um fluxo de condução de projetos apoiado por IA.

Use o roteiro para demonstrar as mudanças e validar se outra pessoa consegue
iniciar, planejar, diagnosticar e organizar um projeto sem orientação externa.

## Objetivo do repasse

Ao final, a pessoa deve compreender:

- como o YABook conduz um projeto da descoberta até a release;
- como planejar a V1 ou uma versão posterior com o Codex;
- como descobrir onde o projeto está e qual é a próxima etapa;
- o que comandos sem `do` analisam e o que comandos com `do` executam;
- como o carregamento automático funciona;
- quando usar `bypass`;
- como verificar e sincronizar a skill;
- como usar o help por comando ou objetivo.

## O que mudou nesta rodada

### Condução de projetos

O YABook agora define um ciclo reutilizável:

```text
Descoberta
-> planejamento colaborativo
-> documentação da versão
-> roadmap
-> próximo bloco de issues
-> implementação
-> estabilização
-> release
```

O planejamento cobre a versão inteira em alto nível, mas detalha somente o
próximo bloco acionável.

Documentação guarda conhecimento estável. GitHub guarda backlog, responsáveis,
status, milestones, épicos e progresso operacional.

### Diagnóstico do projeto

`$yabook diagnose` cruza documentação, código, Git e GitHub para apresentar:

- objetivo da versão;
- entregas concluídas;
- trabalho em andamento;
- pendências;
- bloqueios;
- divergências entre plano e execução;
- próximo passo recomendado.

Diagnóstico observa o projeto. Planejamento decide sua direção.

### Planejamento colaborativo

A família `plan` permite conversar antes de documentar:

| Comando | Função |
| --- | --- |
| `$yabook plan start v1` | Inicia a entrevista da versão. |
| `$yabook plan discuss <tema>` | Discute uma mudança e seus impactos. |
| `$yabook plan status` | Mostra maturidade e decisões abertas. |
| `$yabook plan next` | Recomenda uma única próxima ação. |
| `$yabook plan roadmap` | Propõe milestones, épicos e próximo bloco. |
| `$yabook plan review` | Revisa coerência e prontidão. |
| `$yabook do plan` | Consolida decisões aprovadas nos documentos. |
| `$yabook do plan roadmap` | Materializa o roadmap aprovado no GitHub. |

Comandos `plan` sem `do` não alteram arquivos ou GitHub.

### Núcleo documental adaptável

Quando o projeto não tiver estrutura equivalente, o padrão sugerido é:

```text
docs/planejamento/
├── visao-do-produto.md
├── roadmap.md
├── versoes/
│   └── v1.md
└── sessoes/
    └── AAAA-MM-DD-assunto.md
```

Sessões guardam contexto, decisões, pendências e impactos. Não guardam a
transcrição completa nem status operacional.

### Carregamento automático

Não é mais necessário iniciar a conversa com `$yabook load`.

No primeiro comando operacional `$yabook`, a skill carrega silenciosamente:

- `session.md`;
- `AGENTS.md` local;
- branch;
- `git status --short --branch`;
- `git diff --stat`.

`$yabook help` é a única exceção. `$yabook load` continua disponível para
recarregar o contexto depois de trocar repositório, branch ou regras locais.

### Trava de execução

A trava de `do` vale dentro da gramática `$yabook`:

- `$yabook issue` gera a proposta;
- `$yabook do issue` cria a issue;
- `$yabook plan roadmap` propõe a estrutura;
- `$yabook do plan roadmap` cria a estrutura;
- `$yabook sync` compara;
- `$yabook do sync` sincroniza.

Pedidos normais em linguagem natural continuam executáveis quando a branch é
compatível.

### Entrada do fluxo de trabalho

O foco do fluxo YABook é transformar uma coisa nova em trabalho executável.

Quando surgir um problema, ajuste, melhoria, funcionalidade ou necessidade de
documentação, a pessoa pode descrevê-lo em linguagem natural. A IA deve entender
e delimitar a demanda sem inventar requisitos.

```text
Problema, ajuste ou melhoria
-> $yabook issue
-> $yabook do issue
-> $yabook branch name
-> $yabook do branch
-> implementação
-> commit
-> Pull Request
-> merge
```

A issue não é burocracia posterior: ela é o ponto em que a demanda ganha
objetivo, limite e critérios de aceite antes da implementação.

### Proteção de `main`, `dev` e branches incompatíveis

Pedidos diretos em `main`, `dev`, release ou branch incompatível devem ser
bloqueados.

Uma confirmação comum não libera a execução. A exceção precisa ser explícita:

```text
$yabook bypass atualize o README diretamente na main
```

O `bypass` vale somente para a ação anexada e não substitui `do issue`,
`do branch`, `do commit`, `do pr`, `do release`, `do merge` ou `do sync`.

### Sincronização da skill

Use:

```text
$yabook sync
$yabook sync local
$yabook sync remote
```

Esses comandos apenas comparam a instalação com a origem.

Para atualizar:

```text
$yabook do sync
$yabook do sync local
$yabook do sync remote
```

O modo local prefere o checkout YABook atual ou `YABOOK_REPO_PATH`. O modo
remoto usa o repositório oficial sem executar `pull` no checkout local.

A sincronização valida antes e depois, ignora diferenças de quebra de linha e
altera somente a instalação `yabook`.

### Help contextual

O help agora possui três níveis:

```text
$yabook help
$yabook help plan
$yabook help planejar a V1 do projeto
```

- o primeiro apresenta o índice;
- o segundo explica uma família e mostra exemplos;
- o terceiro recomenda um fluxo e explica o motivo de cada etapa.

Help não carrega o repositório, não altera estado e não executa os comandos que
aparecem na explicação.

## Demonstração: projeto do zero

Execute em um repositório de teste:

```text
$yabook init
$yabook do init
$yabook plan start v1
$yabook plan review
$yabook do plan
$yabook plan roadmap
$yabook do plan roadmap
$yabook plan next
```

Durante a demonstração, confirme:

- `init` apenas propõe;
- `do init` aplica;
- `plan start` conduz perguntas em blocos curtos;
- hipóteses não viram decisões automaticamente;
- `do plan` não cria commit;
- o roadmap reutiliza itens existentes;
- somente o próximo bloco recebe issues detalhadas.

## Demonstração: expandir projeto existente

Para uma nova versão:

```text
$yabook diagnose
$yabook plan start v2
$yabook plan review
$yabook do plan
$yabook plan roadmap
$yabook do plan roadmap
```

Para alterar a versão atual:

```text
$yabook diagnose
$yabook plan discuss adicionar integração com IA
$yabook plan review
$yabook do plan
$yabook plan roadmap
$yabook do plan roadmap
```

## Demonstração: projeto sem direção

```text
$yabook diagnose
$yabook plan status
$yabook plan next
```

Valide a diferença:

- `status`: trabalho local atual;
- `diagnose`: estado do projeto inteiro;
- `plan status`: maturidade do planejamento;
- `plan next`: uma próxima ação recomendada.

## Demonstração: segurança

### Comando sem `do`

```text
$yabook issue
```

Resultado esperado: proposta textual, sem criação no GitHub.

### Comando com `do`

```text
$yabook do issue
```

Resultado esperado: criação somente depois de conferir contexto, labels,
Project e `Size`.

### Pedido direto em branch protegida

Em `main` ou `dev`, peça:

```text
atualize o README
```

Resultado esperado: bloqueio e orientação para usar `bypass`.

Depois:

```text
$yabook bypass atualize o README
```

Resultado esperado: execução apenas dessa ação, com a exceção registrada na
resposta.

## Demonstração: help e sync

```text
$yabook help plan
$yabook help criar uma issue e uma branch
$yabook sync local
```

Valide que:

- o help explica sem executar;
- o help por objetivo monta o menor fluxo;
- sync apenas compara;
- se houver diferença, a resposta sugere `$yabook do sync local`.

## Perguntas para validar entendimento

- Qual é a diferença entre `diagnose` e `plan status`?
- Quando usar `plan discuss` em vez de `plan start v2`?
- Por que o roadmap não cria o backlog detalhado inteiro?
- O que o primeiro comando `$yabook` carrega automaticamente?
- Quando ainda faz sentido usar `$yabook load`?
- Por que uma confirmação comum não substitui `bypass`?
- Por que `bypass` não substitui `do`?
- Como verificar a sincronização sem alterar arquivos?
- Como pedir ajuda para um objetivo em linguagem natural?
- Onde ficam decisões estáveis e onde fica o andamento operacional?

## Critérios de sucesso

O repasse foi bem-sucedido quando a pessoa consegue:

- explicar o ciclo de condução de projetos;
- iniciar o planejamento de uma versão;
- recuperar a direção de um projeto;
- distinguir análise de execução;
- prever quando o agente bloqueará uma alteração;
- escolher entre `load`, `diagnose`, `plan`, `sync` e `help`;
- executar o próximo passo sem inventar formato ou duplicar documentação.

## Referências

- [Manual de uso](manual.md)
- [Condução de projetos](processos/conducao-de-projetos.md)
- [Criar e expandir projetos com YABook](guias/criar-e-expandir-projetos-com-yabook.md)
- [Guia técnico da skill](guias/skill-yabook.md)
- [Fluxo de trabalho com GitHub](processos/fluxo-de-trabalho-github.md)
