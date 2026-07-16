# Sessão de planejamento — eficiência de contexto

Data: 2026-07-02
Rastreabilidade: issue #43

## Contexto

Execuções recentes de `dev` e `plan start` consumiram contexto
desproporcional ao tamanho das demandas. A otimização da issue #39 reduziu os
arquivos, mas não limitou suficientemente as decisões de carregamento.

## Decisões

- A revisão abrangerá todos os comandos, não correções isoladas por rota.
- Cada comando terá contexto mínimo, gatilhos de ampliação e orçamento
  aproximado.
- Comandos explícitos deverão evitar a matriz geral quando o roteamento já for
  inequívoco.
- Demandas delimitadas terão caminho rápido com uma inspeção inicial e uma
  validação final por padrão.
- Custos controláveis pela skill serão separados dos custos impostos pela
  plataforma.
- Travas de segurança não serão removidas para reduzir consumo.

## Pendências

- Levantar a matriz atual de comandos e referências.
- Medir cenários representativos simples, médios e complexos.
- Definir limites por classe sem tratar aproximações como medição de cobrança.
- Revisar a arquitetura somente depois da auditoria.

## Impactos

- A issue #43 passa a concentrar a auditoria e a proposta técnica.
- A linha de base da issue #39 continua válida como comparação histórica.
- Mudanças futuras poderão ser avaliadas por comportamento e não apenas pelo
  tamanho isolado dos arquivos.
