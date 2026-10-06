# Memória própria do YABook

Use para `memory`, `memory search|show|add|edit|forget|review` e `do memory`.
`memory init` prepara inventário/curadoria; `do memory init` cria ou reutiliza
o repositório privado `YABook-memory-<loginGitHub>` e publica o pacote aprovado.
Use `inventory --agent codex|claude --source <pasta>` para levantar arquivos;
o adaptador não inclui memória oculta nem apaga a origem. Avalie os registros,
prepare payload e use `init-plan --curated <json> --output <plano>`. Depois da
aprovação, `init-apply --plan <plano> --curated <json> --approval-hash <hash>
--config <config>` aplica o mesmo plano. Conta, origem e conteúdo são revalidados.

Em base Git configurada, `apply` inclui commit dos paths aprovados e push.
Falha remota retorna `pending_push`; `publish` repete a publicação do commit
existente. Worktree sujo bloqueia nova escrita para preservar trabalho alheio.
Dados de máquina e autorizações ficam fora do repositório. Init não autoriza
convidar colaboradores. Configuração ou migração nativa divergente pede revisão.
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
