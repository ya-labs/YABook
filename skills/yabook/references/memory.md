# Memória própria do YABook

Use para `memory`, `memory search|show|add|edit|forget|review` e `do memory`.
A base configurada pertence ao YABook, não à memória nativa do agente.

## Curadoria

Antes de preparar uma escrita, procure conhecimento relacionado e avalie:
utilidade futura, evidência, novidade, conflito, escopo e situação. Escolha
adicionar, atualizar, relacionar, arquivar, remover, manter ou rejeitar.
Explique o veredito e quando o conhecimento será aplicado. Pedido de `add`,
`edit` ou `forget` não equivale a uma avaliação positiva nem a gravação.
Arquivamento preserva contexto histórico; remoção deve explicar seu impacto.

Guarde descobertas compactas com aplicação, condições e evidência; não copie
logs completos. Pessoa, organização, projeto e assunto são componentes de
escopo. Entidades identificam fontes/operacões pelo projeto e localização.
Grupos referenciam registros existentes; similaridade sugere relações, não
confirma equivalência. Hipótese não é diagnóstico. Veredito e motivo ficam no
histórico da operação. Segredos e autorizações de sessão não são conhecimento.

## Operações

Execute `python3 scripts/yabook_memory.py --root <base> <serviço>` relativo à
skill instalada. `list`, `show <id>` e `review` inspecionam a base; `prepare
--input <json> --actor <agente>` prepara a avaliação e mudanças; `pending [id]`
mostra a prévia. `apply <id> --approval-hash <hash>` só executa após aprovação
do conteúdo exato. Não trate o hash como prova independente de autorização:
o agente deve obter `do memory` ou autorização aplicável na conversa atual.

O payload contém `assessment` (`verdict`, `reason`, `utility`, `application`,
`evidence_status`) e `changes` (`collection`, `id`, `value` ou `delete`). Valores
canônicos têm ID, título, escopo e revisão; registros têm `content`, `state`,
`application`, `evidence` e opcional `conditions`, `last_verified`, `entities`,
`relations`. Grupos usam `members`, `summary` e `summary_sources` por revisão.

Sem ID, `do memory` exige uma única proposta pendente inequívoca. Mudança da
base invalida a proposta. O journal local permite concluir uma escrita
interrompida com `recover`; não remova o journal para esconder falhas.

## Desenvolvimento

Ao concluir `dev`, compare descobertas com registros existentes. Recomende
atualização somente quando mudar execução futura, incluindo hipótese refutada,
responsabilidade confirmada e limites de aplicação. A recomendação não grava.
Mesmo em `auto`, não transforme descoberta em memória sem a curadoria e a
autorização de memória pertinente ao objetivo. Memória externa é evidência de
origem identificada; confirme fontes atuais antes de decisões críticas.
