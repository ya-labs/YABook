# Criar e expandir projetos com YABook

Este tutorial mostra como usar a skill YABook para iniciar, planejar e expandir
um projeto sem misturar conversa, decisão, documentação e execução.

## Regra de segurança

Dentro da gramática `$yabook`, comandos sem `do` analisam, perguntam, revisam ou
geram propostas.

Pedidos normais em linguagem natural continuam executáveis. Se estiverem em
`main`, `dev`, release ou branch incompatível, o agente deve bloquear. Uma
confirmação comum não é suficiente.

`$yabook bypass <ação>` autoriza a ação anexada fora do fluxo de issue/branch,
mas não substitui `do` para executar comandos YABook.

## Carregamento automático

O primeiro comando operacional `$yabook` da conversa carrega automaticamente o
cache da skill, o `AGENTS.md` local e o estado do Git. Não é necessário executar
`$yabook load` antes.

Use `$yabook load` apenas para atualizar o contexto depois de mudar de
repositório, branch ou regras locais.

## Criar um projeto do zero

### 1. Analisar a inicialização

```text
$yabook init
```

O agente inspeciona o repositório e mostra os arquivos e adaptações necessárias.

### 2. Aplicar a inicialização

```text
$yabook do init
```

O agente aplica somente a proposta aprovada, sem criar commit automaticamente.

### 3. Planejar a primeira versão

```text
$yabook plan start v1
```

O agente conduz uma entrevista em blocos curtos sobre problema, público, escopo,
fluxos, riscos, alternativas e critérios de pronto.

Use discussões adicionais quando necessário:

```text
$yabook plan discuss estratégia de autenticação
```

### 4. Revisar e consolidar

```text
$yabook plan review
$yabook do plan
```

A revisão identifica lacunas. A execução consolida decisões aprovadas, preserva
pendências e registra um resumo da sessão. Se necessário, cria a issue e a
branch de planejamento. Não cria commit.

### 5. Preparar o roadmap

```text
$yabook plan roadmap
$yabook do plan roadmap
```

O primeiro comando propõe milestones, épicos, encaixes e o próximo bloco. O
segundo materializa a proposta aprovada, reutilizando itens existentes e
evitando duplicidades.

### 6. Confirmar a próxima etapa

```text
$yabook plan next
```

O agente recomenda uma única ação de maior valor. Para executar uma issue:

```text
$yabook do issue
$yabook branch name
$yabook do branch
```

Quando `do plan roadmap` já tiver criado a issue seguinte, não a crie novamente.

## Expandir um projeto existente

Comece reconstruindo o estado real. O contexto será carregado automaticamente:

```text
$yabook diagnose
```

### Planejar uma nova versão

```text
$yabook plan start v2
$yabook plan review
$yabook do plan
$yabook plan roadmap
$yabook do plan roadmap
```

### Alterar a versão atual

```text
$yabook plan discuss adicionar integração com IA
$yabook plan review
$yabook do plan
$yabook plan roadmap
$yabook do plan roadmap
```

O agente deve avaliar se a mudança cabe na versão atual ou pertence a uma versão
posterior. A discussão não altera documentos até `do plan`.

## Quando o projeto estiver sem direção

Use:

```text
$yabook diagnose
$yabook plan status
$yabook plan next
```

- `diagnose` informa o estado real do projeto inteiro;
- `plan status` mostra lacunas e decisões abertas do planejamento;
- `plan next` recomenda uma única próxima ação.

O diagnóstico deve indicar limitações quando GitHub ou outra fonte não estiver
disponível, em vez de inventar progresso.

## Diferença entre os comandos

| Comando | Responde |
| --- | --- |
| `$yabook status` | Em qual branch e issue estou trabalhando? |
| `$yabook diagnose` | Onde o projeto inteiro está? |
| `$yabook plan status` | O planejamento está pronto? |
| `$yabook plan next` | O que devemos fazer agora? |
| `$yabook plan review` | O planejamento está coerente com o YABook? |

## Resultado esperado

Ao final do fluxo:

- a versão possui objetivo, escopo e critérios de pronto;
- hipóteses e decisões estão diferenciadas;
- o roadmap está alinhado à documentação;
- milestones e épicos organizam a versão;
- somente o próximo bloco está detalhado;
- a próxima ação pode ser executada sem adivinhar contexto.
