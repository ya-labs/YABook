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
- como usar o help por comando ou objetivo;
- como manter uma sequência recomendada visível durante a conversa.

## O que mudou nesta rodada

### YABook Skill como orquestrador

A YABook Skill é o orquestrador inteligente do Método YA LABS. A pessoa usuária
define projeto, prioridades e decisões; a skill interpreta a intenção, orienta
o caminho correto e executa somente o que foi autorizado.

Exemplo:

```text
$yabook desejo planejar a V1 do meu projeto
```

A skill infere `plan start v1`. Se precisar corrigir ou combinar comandos,
informa o roteamento no início. Ela avança por leituras seguras até encontrar
uma decisão ou escrita, mas nunca infere `do`.

Quando houver várias etapas, sugere `$yabook steps start` com um motivo curto,
sem iniciar o checklist automaticamente.

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

### Discussão geral

`$yabook discuss <tema>` analisa uma ideia, decisão ou mudança antes de
transformá-la em planejamento, documentação ou trabalho executável.

O comando adapta a análise ao assunto, separa decisões e pendências e recomenda
o próximo comando. Ele não altera arquivos ou GitHub.

`$yabook plan discuss <tema>` permanece disponível apenas como alias de
compatibilidade.

### Planejamento colaborativo

A família `plan` permite conversar antes de documentar:

| Comando | Função |
| --- | --- |
| `$yabook plan start v1` | Inicia a entrevista da versão. |
| `$yabook plan status` | Mostra maturidade e decisões abertas. |
| `$yabook plan next` | Recomenda uma única próxima ação. |
| `$yabook plan roadmap` | Propõe milestones, épicos e próximo bloco. |
| `$yabook plan review` | Revisa coerência e prontidão. |
| `$yabook do plan` | Consolida decisões aprovadas nos documentos. |
| `$yabook do plan roadmap` | Materializa o roadmap aprovado no GitHub. |

Comandos `plan` sem `do` não alteram arquivos ou GitHub.

### Acompanhamento de etapas

A família `steps` transforma uma sequência recomendada em checklist temporário:

| Comando | Função |
| --- | --- |
| `$yabook steps start` | Inicia o checklist com base na sequência discutida. |
| `$yabook steps` | Mostra o checklist ativo. |
| `$yabook steps done <número>` | Conclui uma etapa e destaca a próxima. |
| `$yabook steps cancel` | Encerra o acompanhamento. |

Enquanto houver etapas abertas, a IA repete um resumo compacto no final de cada
resposta:

```text
✅ 1. Etapa concluída
➡️ 2. Próxima etapa
⬜ 3. Etapa pendente
```

Confirmações inequívocas em linguagem natural, como `concluí a primeira etapa`,
também podem atualizar o checklist. O acompanhamento vale apenas para a conversa
atual, não executa os passos e não substitui planejamento, issues ou milestones.

Se uma ação acontecer fora da sequência, a skill classifica o desvio. Ela pode
registrar execução antecipada, reordenar etapas pendentes, adicionar correção ou
revalidação e explicar o recalculado.

Etapas concluídas permanecem no histórico. Mudanças de objetivo, escopo ou
decisões exigem confirmação.

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
- raiz resolvida do workspace ativo;
- `AGENTS.md` local;
- branch;
- `git status --short --branch`;
- `git diff --stat`.

`$yabook help` é a única exceção. `$yabook load` continua disponível para
recarregar o contexto depois de trocar repositório, branch ou regras locais.

Antes dessas leituras, a skill compara caminho explícito, raiz informada pela
IDE, arquivos ativos e `cwd`. O workspace inequívoco prevalece; o `cwd` é apenas
o último candidato. A raiz precisa conter `.git` e ter remote compatível.

Todos os comandos seguintes usam essa raiz como `workdir`. Se houver mais de um
repositório plausível, a skill pode inspecionar o mínimo necessário, mas deve
pedir confirmação antes de escrever em arquivos, Git ou GitHub.

### Trava de execução

A trava de `do` vale dentro da gramática `$yabook`:

- `$yabook issue` gera a proposta;
- `$yabook do issue` cria a issue;
- `$yabook plan roadmap` propõe a estrutura;
- `$yabook do plan roadmap` cria a estrutura;
- `$yabook sync` compara;
- `$yabook do sync` sincroniza.

`$yabook dev` é a exceção orientada ao objetivo: autoriza preparar a branch,
implementar e validar a issue atual. Não autoriza commit, PR ou merge sozinho.

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
-> $yabook dev
-> $yabook do pr
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

### Trava de mutações Git

Em projetos YA LABS, somente `$yabook do <ação>` ou `$yabook dev` dentro de seu
escopo autorizado podem alterar Git. A trava também vale para pedidos diretos
que não chamam a skill.

`$yabook status` e `$yabook commit message` podem consultar status, diff e
histórico. Já branch, switch, add, commit, stash, merge, rebase, tag, fetch,
pull e push exigem ação `do` explícita.

O escopo acompanha o objetivo: `$yabook do commit` isolado não autoriza `push`.
`$yabook do pr` pode criar commits coerentes, enviar a branch e abrir ou
atualizar o PR. `$yabook do merge` pode preparar o PR e integrar, mas não
autoriza outras branches ou tags.

### Checkpoint do worktree

Antes de novas edições, a IA verifica se as alterações pendentes formam um bloco
concluído de outra responsabilidade. Se formarem um commit independente e
reversível, pausa antes de continuar.

```text
Existem alterações concluídas que devem formar um commit separado.

Commit proposto: tipo: descrição

- $yabook do: cria o commit, executa os pré-requisitos mínimos e retoma a solicitação.
- $yabook continue: prossegue sem criar o commit.
```

`continue` vale apenas para checkpoint opcional. Outra issue ou branch mantém a
separação obrigatória.

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
$yabook discuss adicionar integração com IA
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

## Demonstração: acompanhamento de etapas

Depois que o help ou o planejamento recomendar uma sequência, execute:

```text
$yabook steps start
```

Em seguida, informe:

```text
concluí a primeira etapa
```

Valide que:

- somente um checklist fica ativo;
- a primeira etapa recebe `✅`;
- a próxima etapa recebe `➡️`;
- o checklist reaparece no final das respostas enquanto houver itens abertos;
- nenhuma etapa é executada automaticamente;
- desvios válidos recalculam somente etapas pendentes;
- dependências quebradas geram correção ou revalidação;
- trabalho desnecessário não entra no checklist;
- mudanças estruturais pedem confirmação;
- `$yabook steps cancel` encerra o acompanhamento.

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
- Quando usar `discuss` em vez de `plan start v2`?
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
