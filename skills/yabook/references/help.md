# Ajuda contextual do YABook

Use esta referência para qualquer comando `$yabook help`.

## Princípios

- Help nunca executa comandos nem altera estado.
- Não resolva nem carregue o repositório para responder help.
- Explique somente o tópico ou objetivo solicitado.
- Entregue exemplos prontos para copiar.
- Diferencie comandos somente leitura de comandos iniciados por `do`.
- Se o texto dentro de help mencionar `do`, explique o comando; não o execute.

## Formas aceitas

```text
$yabook help
$yabook help <comando>
$yabook help <família>
$yabook help <objetivo em linguagem natural>
```

`$yabook help <objetivo>` apenas explica um caminho. `$yabook <objetivo>` usa a
orquestração inteligente para executar comandos seguros de leitura até uma
decisão ou escrita.

## Help geral

`$yabook help` retorna um índice curto agrupado por finalidade:

- contexto: `load`, `status`, `diagnose [full]`;
- inicialização e planejamento: `init`, `discuss`, `plan`;
- acompanhamento da conversa: `steps`;
- modos de colaboração: `mode`;
- desenvolvimento e execução: `dev`, `do`, `apk`, `bypass`;
- GitHub: `issue`, `branch`, `commit`, `pr`, `release`;
- qualidade e documentação: `check`, `review`, `docs`;
- manutenção da skill: `sync`.

Finalize com dois exemplos:

```text
$yabook help plan
$yabook help planejar a V1 do projeto
```

## Help de comando específico

Para `$yabook help <comando>`, responda:

1. o que o comando faz;
2. quando usar;
3. se altera estado;
4. sintaxe;
5. dois ou três exemplos;
6. comandos relacionados.

Exemplo de entrada:

```text
$yabook help diagnose
```

Não explique famílias não relacionadas.

## Help de família

Quando o tópico for uma família, explique o comando-base e cada subcomando.

Para `$yabook help plan`, inclua:

| Comando | Uso | Exemplo |
| --- | --- | --- |
| `plan start <versão>` | Entrevistar e propor uma versão. | `$yabook plan start v1` |
| `discuss <tema>` | Avaliar mudança e impacto. | `$yabook discuss adicionar integração com IA` |
| `plan status` | Mostrar maturidade e decisões abertas. | `$yabook plan status` |
| `plan next` | Recomendar uma próxima ação. | `$yabook plan next` |
| `plan roadmap` | Propor milestones, épicos e próximo bloco. | `$yabook plan roadmap` |
| `plan review` | Revisar coerência antes de consolidar. | `$yabook plan review` |
| `do plan` | Gravar decisões aprovadas. | `$yabook do plan` |
| `do plan roadmap` | Criar a estrutura aprovada no GitHub. | `$yabook do plan roadmap` |

Deixe explícito que comandos `plan` sem `do` não escrevem.
Informe também que `plan discuss` continua aceito como alias de `discuss`.

Use a mesma estrutura para famílias como `issue`, `pr`, `sync` e `do`, listando
somente subcomandos realmente documentados.

Para `$yabook help steps`, inclua:

| Comando | Uso |
| --- | --- |
| `steps start` | Criar um checklist a partir da sequência discutida. |
| `steps` | Consultar o checklist ativo. |
| `steps done <número>` | Concluir uma etapa e destacar a próxima. |
| `steps cancel` | Encerrar o acompanhamento. |

Explique que o checklist vale apenas para a conversa atual, aparece no final das
respostas enquanto estiver aberto e não executa os passos listados. Informe que
ações fora da sequência podem recalcular etapas pendentes, mas mudanças de
objetivo, escopo ou decisão exigem confirmação.

Para `$yabook help dev`, explique:

- que a issue precisa existir ou ser indicada;
- que `dev` prepara branch, implementa e valida;
- que `dev` sozinho não cria commit nem PR;
- que `dev & do pr` entrega o PR completo;
- que `dev & do merge` também integra após as validações.

Para `$yabook help apk`, explique:

- que `.yabook/apk.json` pertence ao repositório do aplicativo;
- que `apk` valida o contexto e mostra a prévia sem executar build;
- que `do apk` executa um build novo e prepara o arquivo padronizado;
- que o upload continua manual e não faz parte desses comandos;
- que configuração inválida, worktree sujo, branch incompatível, build com
  falha, artefato antigo e sobrescrita são bloqueados.

Inclua exemplos:

```text
$yabook apk
$yabook do apk
```

Para `$yabook help mode`, explique:

- que modos ajustam a forma de colaboração da IA, não permissões;
- que `study` ensina um tema com estudo progressivo e interativo;
- que `dev` guia a pessoa usuária a implementar uma tarefa real;
- que `prod` delega a execução ao agente dentro das autorizações existentes;
- que `mode: dev` não é o mesmo que o comando `$yabook dev`;
- que `prod` não substitui `do`, `bypass` nem travas de Git/GitHub.

Inclua exemplos:

```text
$yabook mode: dev
$yabook mode: prod - faça os ajustes no estilo do site
$yabook def mode dev for front-end
```

## Help por objetivo

Quando o texto depois de `help` for uma intenção em linguagem natural:

1. identifique o resultado desejado;
2. proponha o menor fluxo YABook que chega ao resultado;
3. explique por que cada comando será usado;
4. marque quais etapas apenas analisam e quais executam;
5. entregue a sequência pronta para copiar;
6. não execute a sequência.

Exemplo:

```text
$yabook help planejar a V1 do projeto
```

Resposta esperada em essência:

```text
Fluxo recomendado:
1. $yabook init
   Analisa a adoção do YABook sem alterar arquivos.
2. $yabook do init
   Aplica a estrutura aprovada.
3. $yabook plan start v1
   Conduz a entrevista da primeira versão.
4. $yabook plan review
   Identifica lacunas antes de documentar.
5. $yabook do plan
   Consolida as decisões aprovadas.
6. $yabook plan roadmap
   Propõe milestones, épicos e o próximo bloco.
7. $yabook do plan roadmap
   Materializa a estrutura aprovada.
```

Adapte o fluxo ao objetivo. Exemplos de intenções:

- iniciar um projeto do zero;
- planejar V1 ou V2;
- descobrir a próxima etapa;
- adicionar uma capacidade à versão atual;
- criar issue e branch;
- preparar PR e release;
- verificar ou sincronizar a skill.

Para intenções como “corrigir um bug”, “fazer um ajuste” ou “adicionar uma
melhoria”, recomende primeiro:

```text
$yabook issue
$yabook do issue
$yabook branch name
$yabook do branch
```

Explique que a issue transforma a necessidade em trabalho executável e inicia o
fluxo normal de implementação.

Se o objetivo admitir caminhos diferentes, recomende um e explique brevemente a
condição que faria escolher o outro.

## Tópico desconhecido

Se não reconhecer comando, família ou intenção:

- diga que o tópico não foi identificado;
- sugira até três comandos próximos;
- mostre `$yabook help` para consultar o índice;
- não invente comandos.
