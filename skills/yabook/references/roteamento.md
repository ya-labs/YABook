# Gramática e aliases YABook

Use somente quando houver alias, encadeamento ou dúvida de gramática. Comandos
explícitos conhecidos seguem direto para sua referência indicada em `SKILL.md`.

## Famílias

- orientação: `help`, `load`, `status`, `check [full]`, `review [full]`;
- planejamento: `diagnose [full]`, `discuss`, `plan [start <versão>|status|next|review|roadmap]`;
- conversa: `steps`, `step`, `mode`, `def mode`;
- artefatos: `issue`, `branch name`, `commit message`, `pr`, `release`, `docs`;
- artefatos Android: `apk`, `do apk`;
- execução: `do <ação>`, `dev [quick|step|full]`, `bypass <ação>`, `continue`, `sync`.

Subcomandos textuais:

- `issue title|desc|classify|brief`;
- `pr title|desc|brief`;
- `plan brief`;
- `steps start [init|plan]|done <número>|cancel`, `step`;
- `sync local|remote`.

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
- `dev` termina antes de commit.
- `do pr` pode cumprir commit e push necessários ao PR.
- `do merge` pode preparar o PR, mas merge continua explícito.
- `bypass` não autoriza Git nem substitui `do`.
