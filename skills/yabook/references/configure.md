# Configuração local por repositório

Use esta referência para `$yabook configure`, `$yabook configure commands` e
`$yabook do configure`.

## Objetivo

Adaptar o YABook ao fluxo de um repositório sem alterar o método global. A
configuração vive em `.yabook/AGENTS.md`, é Markdown versionável e é carregada
somente em rotas que dependem do projeto.

## Precedência e limites

Da maior para a menor precedência: regras globais do YABook e do ambiente,
`AGENTS.md` do repositório e `.yabook/AGENTS.md`. Em conflito, a regra superior
vence e o agente explica o bloqueio.

Nenhum comando local pode remover a exigência de `do`, autorizar Git ou GitHub
implicitamente, trocar proteção de branch, criar commits, PRs, merges ou releases
fora das regras centrais. `bypass` continua restrito à sua referência e não é
uma permissão que a configuração local possa ampliar.

## `$yabook configure [commands]`

É uma rota `C2`, sem escrita. Resolva o workspace, leia as regras existentes e
informe se uma configuração local já existe. Conduza uma entrevista objetiva;
`configure commands` limita inicialmente as perguntas a comandos personalizados.

Colete somente o necessário:

1. contexto e produto do repositório;
2. comandos locais desejados, sintaxe e exemplos;
3. pré-condições, entradas e saídas esperadas;
4. comportamento sem `do` e com `do`;
5. fluxos de APK, build, validação, entrega, ambientes, branches, PRs e releases;
6. validações obrigatórias, riscos e regras da empresa.

Não invente comandos, executáveis, ambientes ou permissões. Diferencie o que o
comando apenas orienta do que pode executar com `do`. Ao final, apresente uma
proposta completa de `.yabook/AGENTS.md`, incluindo lacunas que ainda impedem a
materialização. Informe que `$yabook do configure` cria ou atualiza o arquivo
após a proposta estar confirmada.

## `$yabook do configure`

É uma rota `C3`. Revalide o worktree conforme `git/checkpoint.md`, a proposta
confirmada e o conteúdo atual, se houver. Crie `.yabook/AGENTS.md` quando estiver
ausente ou atualize apenas as seções confirmadas, preservando regras locais
válidas que não fazem parte da alteração. Nunca sobrescreva configuração existente
sem mostrar a diferença pretendida.

O arquivo deve usar esta estrutura:

```md
# Configuração local do YABook

> Esta configuração adapta o YABook a este repositório. Regras globais de
> segurança, `do`, Git, GitHub, branches, commits, PRs, merges e releases
> continuam prevalecendo.

## Contexto do projeto

## Comandos locais

### `<comando>`

- Sintaxe: `$yabook <comando> [opções]`
- Pré-condições:
- Sem `do`:
- Com `do`:
- Validações esperadas:
- Limites e riscos:

## Fluxos específicos

## Ambientes e entregas

## Limites locais
```

Inclua ao menos um exemplo concreto quando o projeto usar Android:

```md
### `apk homolog`

- Sintaxe: `$yabook apk homolog`
- Pré-condições: APK gerado e `.yabook/apk.json` válido.
- Sem `do`: valida a origem e mostra a prévia do nome de homologação.
- Com `do`: prepara a cópia rastreável conforme `$yabook do apk`; não faz upload.
- Validações esperadas: versão, branch autorizada e caminho dentro do repositório.
- Limites e riscos: não substitui o fluxo global de APK nem autoriza release.
```

Depois de gravar, releia o arquivo, valide a estrutura, reporte as regras locais
que poderão ser aplicadas e repita que elas não substituem o YABook global.

## Aplicação posterior

Quando uma rota dependente do repositório usar uma regra desse arquivo, sinalize:

```text
Regra local aplicada: <comando ou regra> (.yabook/AGENTS.md).
```

Se a regra local for inválida, ambígua ou contrariar uma regra superior,
interrompa a ação dependente, mostre `Campo inválido`, `Motivo` e `Correção
necessária`. Não execute uma interpretação permissiva.
