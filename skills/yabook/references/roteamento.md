# Gramática e aliases YABook

Use somente quando houver alias, encadeamento ou dúvida de gramática. Comandos
explícitos conhecidos seguem direto para sua referência indicada em `SKILL.md`.

## Famílias

- orientação: `help`, `load`, `status`, `check [full]`, `review [full]`, `rebase [base]`;
- planejamento: `diagnose [full]`, `discuss`, `plan [start <versão>|status|next|review|roadmap]`;
- conversa: `steps`, `step`, `mode`, `def mode`, `resume`;
- artefatos: `issue`, `branch name`, `commit message`, `pr`, `release`, `docs`;
- artefatos Android: `apk`, `do apk`;
- execução: `do <ação>`, `dev [quick|step|full]`, `bypass <ação>`, `continue`,
  `sync`, `configure [commands]`, `guardrails`.

Subcomandos textuais:

- `issue title|desc|classify|brief|package`;
- `pr title|desc|brief`;
- `plan brief`;
- `steps start [init|plan]|done <número>|cancel`, `step`;
- `resume [até "<marco, assunto ou mensagem>"]`;
- `sync local|remote`.
- `rebase [base]`, em que `base` é uma branch base informada explicitamente.
- `mode: auto [objetivo]` ativa autorização contínua na conversa do projeto atual;
  outro modo encerra. Não aceite definição persistente de `auto` por área.

`issue package [propósito]` usa diretamente `artefatos/issue-package.md` e
`artefatos/contratos.md`, sem inferir `do`. `do issue package` cria esse artefato;
`do issue` mantém o tipo da prévia aprovada. Não confunda com `issue batch`,
que prepara múltiplas issues. `issue desc` de pacote usa seu contrato próprio.

## Aliases

| Alias | Comando |
| --- | --- |
| `branch` | `branch name` |
| `commit msg` | `commit message` |
| `classify`, `estimate` | `issue classify` |
| `create` | `do` |
| `issue batch` | `do issues` |
| `pr description` | `pr desc` |
| `issue description` | `issue desc` |
| `doc` | `docs` |
| `validate` | `check` |
| `diagnóstico` | `diagnose` |
| `planejamento` | `plan` |
| `plan discuss <tema>` | `discuss <tema>` |

## Linguagem natural

Leia `orquestracao.md`, selecione o menor fluxo suficiente e mostre o roteamento
inferido. Nunca infira `do` ou `dev`.
Em `auto` explicitamente ativo, pedidos naturais inequívocos autorizam o objetivo
sem exigir `do`; perguntas e prévias continuam informativas. Não infira o modo.

## Encadeamento

Separe comandos com `&`. O prefixo `$yabook` é obrigatório somente no início.
Execute da esquerda para a direita e reutilize apenas contexto ainda válido.

`do` e `do:` são equivalentes:

```text
$yabook dev & do pr
$yabook do: commit
```

Se um segmento falhar, continue somente segmentos independentes. A autorização
de escrita de um segmento não se estende aos demais.

## Segurança

- Sem `do`, produza texto, inspeção ou orientação.
- `configure` conduz uma entrevista e propõe a configuração local; `do configure`
  pode criar ou atualizar `.yabook/AGENTS.md` somente a partir dessa proposta.
- `guardrails` audita o bloco global do YABook; `do guardrails install|remove`
  altera somente esse bloco em `~/.codex/AGENTS.md`.
- `dev` termina antes de commit.
- `do pr` pode cumprir commit e push necessários ao PR.
- `do merge` pode preparar o PR, mas merge continua explícito.
- `bypass` não autoriza Git nem substitui `do`.
- As exigências de `do` acima valem fora de `auto`. Em `auto`, execute o objetivo
  delegado sem `do`, `bypass` ou aprovação de checkpoints, preservando trabalho
  existente; operações remotas e merge dependem do pedido correspondente.
