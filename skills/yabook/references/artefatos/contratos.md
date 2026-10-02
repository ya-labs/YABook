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
- Em `auto`, valide os mesmos contratos antes de executar artefatos delegados.
  Ajuste pontual sem issue dispensa número e vínculo; não invente `Closes` nem
  branch numerada. Registre a exceção e use nome descritivo se criar branch.
- Em divergência, interrompa antes da mutação e informe `Campo inválido`,
  `Motivo` e `Correção necessária` de forma objetiva.

## Campos por comando

| Comando | Saída permitida |
| --- | --- |
| `issue title` | `Título` |
| `issue desc` | `Corpo` |
| `issue` | `Título`, `Corpo`, `Labels sugeridas` e `Size (Project)` |
| `branch name` e `branch` | `Nome` |
| `commit message` | `Mensagem` e `Descrição` quando houver corpo |
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
| `do commit` | assunto `tipo: descrição curta`, com tipo aceito e descrição não vazia; corpo separado por linha em branco, obrigatório para pacotes e ajustes via `bypass`. |
| `do pr` | título objetivo; corpo com objetivo, entrega, vínculo `Closes #numero` e `Informações para IA`; número vinculado à issue confirmada. |

## Cenários de contrato

| Artefato | Aceitar | Rejeitar |
| --- | --- | --- |
| Issue | título, corpo, labels canônicas e `Size` no Project; corpo contém o bloco de IA. | `Size` em label ou título, label não confirmada, campo obrigatório ausente ou bloco de IA ausente. |
| Branch | `92-reforcar-contratos` para a issue `#92`. | número diferente da issue, `docs/92-contratos`, `#92 contratos` ou nome com acentos/espaços. |
| Commit | assunto válido, com corpo documentado quando aplicável. | assunto sem tipo ou descrição; corpo obrigatório ausente ou conteúdo não confirmado. |
| PR | título e corpo com vínculo confirmado e bloco de IA factual. | `Closes` ausente ou divergente, contexto de IA ausente, listagem de arquivos como contexto ou decisão/vínculo inventado. |

Para pacotes, valide objetivo geral, limites, encerramento e registro mínimo de
pendências. Novas demandas compatíveis não exigem nova issue nem reescrita do
corpo inteiro. PR de pacote consolida entregas e validações e usa merge commit.
Nos contratos de branch e PR, as exigências de número e `Closes` aplicam-se ao
fluxo com issue; ajuste pontual autorizado sem issue é exceção explícita.
O ajuste pontual em `auto` também exige corpo documentado, com registro de ajuste
sem issue; não afirme uso de `bypass` se não foi invocado.

Sugestões de commit documentado usam dois blocos de código: `Mensagem` (assunto)
e `Descrição` (corpo). A descrição explica motivo, alteração e exceção quando
aplicável; validações ficam no relatório e no PR. No Git, assunto e corpo formam
um único commit; a separação dos blocos é o formato de apresentação à pessoa.
