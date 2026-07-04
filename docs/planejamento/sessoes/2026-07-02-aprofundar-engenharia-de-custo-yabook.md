# Sessão de planejamento — aprofundar engenharia de custo da skill YABook

Data: 2026-07-02
Rastreabilidade: épico #46

## Contexto

A issue #43 melhorou o uso de contexto, mas a revisão posterior mostrou que ela
não bastava para sustentar economia de custo de forma previsível. A conversa
partiu de um estudo aprofundado consolidado fora do GitHub e concluiu que o
YABook ainda precisava transformar heurística em contrato observável.

O objetivo deixou de ser apenas “ler menos” e passou a ser “começar com o menor
contexto seguro, ampliar só quando houver motivo verificável e conseguir medir
quando a skill regredir”.

## Diagnóstico alinhado na sessão

- A redução de tamanho dos arquivos, sozinha, não garante economia real em uso.
- O problema estava distribuído entre roteamento, reaproveitamento de contexto,
  releituras desnecessárias e baixa observabilidade de execução.
- Comandos explícitos ainda podiam pagar custo de descoberta acima do
  necessário.
- Faltava separar melhor custo controlável pela skill de custo imposto pela
  plataforma.
- O trabalho era grande demais para uma issue única se quiséssemos validação,
  revisão e merge com rastreabilidade clara.

## Decisões

- Tratar a evolução como um épico próprio, e não como ajuste incremental solto.
- Quebrar a iniciativa em issues menores, cada uma com hipótese, entrega e
  validação verificáveis.
- Priorizar primeiro o contrato normativo do custo e da profundidade, depois os
  mecanismos de reaproveitamento e por fim a observabilidade.
- Manter as travas de segurança do YABook; redução de custo não autoriza pular
  confirmação, Git gate ou validação real.
- Diferenciar claramente:
  - contexto da conversa;
  - brief reutilizável;
  - cache persistido opcional;
  - métricas locais de observabilidade.

## Quebra aprovada

- #47 — classes de custo `C0` a `C4`, limites por rota e profundidade explícita
  para comandos como `dev`, `check` e `review`.
- #48 — briefs reutilizáveis para condensar contexto de issue, planejamento e
  PR sem reler fontes longas a cada etapa.
- #49 — cache compacto opcional de contexto do projeto, validado por branch,
  remote, referência e fingerprints.
- #50 — observabilidade local e testes de orçamento para detectar regressões e
  comparar cenários com métricas verificáveis.

## Sequência escolhida

1. Formalizar as classes de custo e o contrato de ampliação.
2. Criar atalhos reutilizáveis para evitar releitura desnecessária.
3. Adicionar cache opcional apenas para fatos estáveis e descartáveis.
4. Medir a execução real com relatórios e validadores simples.

Essa ordem foi escolhida porque observabilidade antes do contrato criaria
telemetria sobre um comportamento ainda instável, e cache antes da política de
validade aumentaria o risco de reaproveitar contexto errado.

## Fora de escopo mantido

- telemetria externa;
- dashboard hospedado;
- embeddings ou cache semântico;
- sincronização automática em background;
- métricas inventadas quando o runtime não expuser o dado real;
- remoção de validações obrigatórias para “ganhar desempenho”.

## Impactos esperados

- O YABook passa a ter engenharia de custo tratada como capacidade contínua, e
  não só como poda textual pontual.
- Revisões futuras ganham base para discutir comportamento observado, não apenas
  tamanho de arquivo.
- A skill fica mais previsível para comandos simples e mais auditável para
  comandos profundos.
- O roadmap de eficiência de contexto deixa de ser genérico e ganha bloco
  implementável rastreado no GitHub.

## Resultado da sessão

- O épico #46 foi definido como guarda-chuva da evolução.
- As issues #47, #48, #49 e #50 foram aprovadas como próximo bloco acionável.
- O planejamento passou a orientar execução incremental, com merge por etapas em
  vez de uma entrega única de alto risco.
