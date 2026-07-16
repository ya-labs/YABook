# Roteiro temporário de repasse do YABook

Este repasse registra somente a rodada da issue `#56`.

## Objetivo desta rodada

Atualizar a documentação do YABook para refletir mudanças recentes da skill que
já estavam implementadas, mas ainda não estavam claras no manual e no repasse.

## Escopo consolidado

Esta rodada consolidou no texto as mudanças ligadas às issues:

- `#32`
- `#36`
- `#37`
- `#38`
- `#47`
- `#48`
- `#49`
- `#50`

O repasse, porém, deve ser lido como entrega da issue `#56`: ajustar a
documentação para explicar o comportamento atual da skill.

## O que foi atualizado

Os documentos ajustados nesta rodada foram:

- [Manual de uso](manual-de-uso.md)
- [Guia técnico da skill](skill-yabook.md)

## Mudanças que agora estão documentadas

### Economia de contexto

A documentação agora deixa explícito que a skill trabalha com classes de custo:

- `C0`: resposta instantânea;
- `C1`: contexto local mínimo;
- `C2`: artefato ou análise dirigida;
- `C3`: execução controlada;
- `C4`: profundidade explícita.

Também ficou registrado que:

- comandos explícitos devem abrir sua referência direta;
- `contexto.md` fica para auditoria, revisão do carregamento ou ambiguidade;
- contexto válido não deve ser redescoberto sem sinal de mudança;
- ampliação de leitura só deve acontecer com motivo concreto.

### `$yabook dev`

O manual agora diferencia melhor quando usar:

- `$yabook dev quick`;
- `$yabook dev`;
- `$yabook dev full`.

Regra consolidada:

- `dev quick`: tarefa pequena, clara, de baixo risco e com poucos arquivos;
- `dev`: caminho padrão para a maioria das implementações;
- `dev full`: demanda complexa, estrutural, sensível ou com pedido explícito de aprofundamento.

Também ficou explícito que toda execução de `dev` deve terminar com `Como testar`.

### Briefs reutilizáveis

Os comandos abaixo agora estão explicados de forma mais direta:

- `$yabook issue brief`
- `$yabook plan brief`
- `$yabook pr brief`

Pontos consolidados:

- brief é um contrato curto e reutilizável;
- brief não é etapa obrigatória antes da issue;
- `issue brief` é preferível quando a conversa estiver longa ou espalhada;
- em demanda curta e clara, pode ir direto para `$yabook issue`;
- rotas posteriores devem preferir brief válido antes de reler contexto longo.

### Observabilidade de contexto

Também ficou documentada a diferença entre:

- orçamento estático por rota;
- auditoria runtime por relatório observado.

O texto agora deixa claro que o teste runtime não mede sozinho uma sessão real
do agente: ele valida um relatório produzido externamente.

### Atalho para comandos completos da skill

O manual agora aponta explicitamente para o guia técnico da skill quando a
pessoa quiser ver a lista completa de comandos, variantes e comportamento
interno:

- [Skill YABook](skill-yabook.md)

## O que outra pessoa deve verificar

Ao continuar este trabalho, a próxima pessoa deve conferir:

1. se o manual está claro para alguém que usa a skill sem conhecer o histórico das issues;
2. se o guia técnico da skill está consistente com `SKILL.md` e com as referências em `skills/yabook/`;
3. se novas mudanças da skill continuarão sendo refletidas nesses documentos sem deixar repasses antigos acumulados.

## Critério de encerramento desta rodada

Esta rodada termina quando o repasse deixar de funcionar como histórico longo e
passar a registrar apenas a mudança documental atual da issue `#56`.
