# Contratos canônicos de artefatos

Use esta referência com `issue`, `branch name`, `commit message`, `pr` e seus
subcomandos textuais. Ela define a saída reutilizável e a validação que precede
as ações `do`.

## Regras gerais

- Retorne somente os campos definidos para o comando solicitado. Não misture
  análise, justificativa, confiança, autorização operacional ou próximos passos
  dentro do artefato.
- Preserve decisões confirmadas na conversa, na issue, no diff e nas fontes
  aplicáveis. Não invente títulos, labels, caminhos, vínculos ou decisões.
- O diff é a fonte de verdade para arquivos alterados. Não o substitua por
  listas em issue, PR ou contexto de IA.
- `Size` é sempre um campo do Project; nunca label, título ou conteúdo de
  branch, commit e PR.
- Antes de `do issue`, `do branch`, `do commit` ou `do pr`, valide o artefato
  correspondente. Não corrija conteúdo silenciosamente.
- Em divergência, interrompa antes da mutação e informe `Campo inválido`,
  `Motivo` e `Correção necessária` de forma objetiva.

## Campos por comando

| Comando | Saída permitida |
| --- | --- |
| `issue title` | `Título` |
| `issue desc` | `Corpo` |
| `issue` | `Título`, `Corpo`, `Labels sugeridas` e `Size (Project)` |
| `branch name` e `branch` | `Nome` |
| `commit message` | `Mensagem` |
| `pr title` | `Título` |
| `pr desc` | `Corpo` |
| `pr` | `Título` e `Corpo` |

## Contexto obrigatório para IA

Issues e PRs sempre incluem o bloco recolhido abaixo, preenchido apenas com
fatos relevantes para a continuidade. Caminhos de arquivos só podem aparecer
quando explicarem uma decisão, risco ou ponto relevante de continuidade.

```md
<details>
<summary>Informações para IA</summary>

- **Contexto confirmado e objetivo:**
- **Decisões, limites e premissas:**
- **Abordagem e pontos relevantes para continuidade:**
- **Validações executadas ou esperadas:**
- **Riscos, dependências e pendências:**
</details>
```

Não transforme esse bloco em relação de arquivos alterados, histórico
transitório ou conteúdo que não tenha impacto na continuidade.

## Validação antes de ações `do`

| Ação | Campos e formato obrigatórios |
| --- | --- |
| `do issue` | título objetivo; corpo com `Resumo rápido`, `Escopo`, `Critérios de aceite` e `Informações para IA`; labels do catálogo confirmado; `Size` de `1` a `5` no Project. |
| `do branch` | uma issue inequívoca; nome no formato `numero-descricao-curta`; número igual ao da issue; sem tipo, `#`, acentos ou espaços. |
| `do commit` | mensagem única no formato `tipo: descrição curta`, com tipo aceito pelo fluxo local e descrição não vazia. |
| `do pr` | título objetivo; corpo com objetivo, entrega, vínculo `Closes #numero` e `Informações para IA`; número vinculado à issue confirmada. |

## Cenários de contrato

| Artefato | Aceitar | Rejeitar |
| --- | --- | --- |
| Issue | título, corpo, labels canônicas e `Size` no Project; corpo contém o bloco de IA. | `Size` em label ou título, label não confirmada, campo obrigatório ausente ou bloco de IA ausente. |
| Branch | `92-reforcar-contratos` para a issue `#92`. | número diferente da issue, `docs/92-contratos`, `#92 contratos` ou nome com acentos/espaços. |
| Commit | `docs: reforça contratos de artefatos`. | mensagem sem tipo, sem descrição, multilinha ou com conteúdo não confirmado. |
| PR | título e corpo com vínculo confirmado e bloco de IA factual. | `Closes` ausente ou divergente, contexto de IA ausente, listagem de arquivos como contexto ou decisão/vínculo inventado. |
