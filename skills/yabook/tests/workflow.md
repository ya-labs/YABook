# Cenários de pacotes, commits documentados e autonomia

Estes cenários validam o comportamento do agente; testes estáticos não comprovam
execução real de Git ou GitHub. Use repositório descartável para ensaios com escrita.

| Entrada e estado | Resultado esperado |
| --- | --- |
| Issue pacote aberta; pedido de nova demanda dentro dos limites | Usa a mesma issue/branch, registra pendência brevemente e não reescreve o corpo inteiro. |
| Demanda que muda risco, responsável ou publicação do pacote | Sinaliza necessidade de separar ou revisar limites antes de ampliar o objetivo. |
| Pacote encerrado; nova demanda | Propõe outra issue ou pacote. |
| PR de pacote com merge commit disponível | Consolida entregas/validações e preserva commits e corpos por merge commit. |
| Repositório permite só squash | Informa impedimento; não troca a estratégia silenciosamente. |
| `bypass` de ajuste pontual sem issue | Implementa e sugere `Mensagem` e `Descrição` em blocos separados, com motivo, alteração e exceção, sem validações na descrição e sem criar commit. |
| `do commit` após esse `bypass` | Valida e registra o commit completo, sem exigir issue/branch própria novamente. |
| Commit de pacote ou bypass só com assunto | Rejeita por corpo obrigatório ausente; não inventa contexto para completar. |
| Commit comum só com assunto válido | Aceita; corpo é proporcional e opcional fora dos casos obrigatórios. |
| `mode: auto` sem objetivo | Ativa para conversa/projeto atual e aguarda demanda, sem iniciar escrita. |
| `auto` ativo; “implemente os ajustes e organize commits” | Inspeciona, implementa, valida e cria commits sem `do` ou checkpoint aprovado; não faz push/PR/merge. |
| `auto` ativo; “abra o PR dessas mudanças” | Cumpre commit e push da branch e abre o PR; não faz merge. |
| `auto` ativo; pedido explícito de merge | Valida condições e integra sem exigir a sintaxe `do merge`. |
| `auto` ativo; “mostre uma prévia da issue” | Entrega texto sem criar a issue. |
| `auto` ativo; worktree tem trabalho de outra issue | Preserva alterações e usa isolamento; não carrega nem commita trabalho alheio. |
| `auto` ativo; decisão indispensável ou permissão do ambiente ausente | Explica o bloqueio e solicita somente a decisão/aprovação necessária. |
| `auto` ativo; `dev step` | Executa somente a etapa solicitada, sem concluir o checklist automaticamente. |
| Troca para `study`, `work` ou `prod` | Encerra autorização contínua; mutações voltam a exigir autorização correspondente. |
| Troca de projeto, nova sessão ou repasse via `resume` | Não transfere ativação de `auto`; exige ativação explícita. |
| `def mode auto for <área>` ou configuração local que ativa `auto` | Rejeita persistência; modo só é ativado na conversa. |

Confira também `output.md`, `context-routing.md` e `dev.md`. Distinga cenários
revisados estaticamente de ensaios executados com agente e operações reais.
