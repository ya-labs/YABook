# Modo auto

Ativação explícita: `$yabook mode: auto [objetivo]`. Sem objetivo anexado,
ative o modo e aguarde uma demanda; a ativação não inicia trabalho por si só.
Vale para a conversa no projeto atual até selecionar outro modo. Não persista
em arquivo, definição por área, memória ou repasse para outra sessão.

## Autorização contínua

- Execute o objetivo delegado e seus pré-requisitos sem exigir `do`, `bypass`
  ou aprovação de checkpoints. Pedidos naturais inequívocos são executáveis.
- Investigue, implemente, valide, corrija e organize branches e commits.
- Escolha issue individual, issue pacote ou ajuste pontual documentado conforme
  impacto e necessidade de acompanhamento. Consulte os contratos aplicáveis.
- Use branch própria para trabalho acompanhado por issue; ajustes pontuais
  podem usar a branch atual com commit documentado, inclusive sem issue.
- Crie ou atualize a issue necessária ao objetivo, evitando duplicidades.
- Operações remotas, PR, merge e release só entram quando fazem parte do pedido.
  Abrir PR inclui commit e push da branch; implementar não implica publicar.
  Merge exige pedido explícito, mas dispensa a sintaxe `do merge`.
- Comandos informativos, discussões e pedidos de prévia continuam sem escrita.
  Ativar `auto` não converte uma pergunta em autorização de implementação.

## Organização e limites

- Antes de editar ou trocar de branch, confira status, diffs e último commit.
  Preserve trabalho existente e separe responsabilidades; prefira worktree
  separado quando houver alterações de outro escopo. Não descarte nem inclua
  trabalho alheio em commits para liberar o fluxo.
- Faça checkpoints do próprio trabalho sem pausa de aprovação, com commits
  compreensíveis e validação proporcional. Não avance etapas de `dev step`
  além da etapa solicitada nem mude decisões de produto unilateralmente.
- Interrompa somente diante de decisão indispensável, risco concreto de perder
  trabalho ou aprovação exigida pelo ambiente. Explique o impedimento real.
- As dispensas valem para travas do método YA LABS; permissões do ambiente,
  proteções reais de branch e regras locais externas ao método continuam válidas.
- Informe mudanças, validações e limitações. Se já houver commits, apresente-os;
  se houver alterações sem commit, sugira a mensagem correspondente.
