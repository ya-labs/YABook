# Repasse temporário do YABook

Este repasse consolida as entregas integradas após a rodada encerrada pelo
[PR #57](https://github.com/ya-labs/YABook/pull/57). Ele substitui o conteúdo
anterior sobre a issue `#56` e não acumula aquela rodada histórica.

## Marco e escopo

- Marco inicial: [PR #57](https://github.com/ya-labs/YABook/pull/57), integrado
  pelo commit [`ce91515`](https://github.com/ya-labs/YABook/commit/ce915155b5efb4b13d9a9832be8306aa4dbd4e7b)
  em 03/07/2026.
- Marco final: [PR #108](https://github.com/ya-labs/YABook/pull/108), integrado
  pelo commit [`b14bd52`](https://github.com/ya-labs/YABook/commit/b14bd5295311b4e03368f8a3614332e49224801a)
  em 17/08/2026.
- Fonte de rastreabilidade: histórico da branch `main`, relacionando cada
  entrega à issue de origem, ao PR e ao commit de integração.

O intervalo inclui evolução da skill e dos fluxos YABook, além do planejamento
e da implementação inicial do YABook Desktop. Commits intermediários de
planejamento não são apresentados como entregas independentes.

## Evolução da skill e dos fluxos YABook

| Entrega | Rastreabilidade | Resultado consolidado |
| --- | --- | --- |
| Separar `dev` da autorização exclusiva para editar | [Issue #58](https://github.com/ya-labs/YABook/issues/58) · [PR #59](https://github.com/ya-labs/YABook/pull/59) · [`31713f6`](https://github.com/ya-labs/YABook/commit/31713f64866590deb06df843e9f6a9ae75138c2e) | Distinguiu o atalho de desenvolvimento das demais autorizações de edição. |
| Exportar telemetria de contexto | [Issue #61](https://github.com/ya-labs/YABook/issues/61) · [PR #65](https://github.com/ya-labs/YABook/pull/65) · [`429a2be`](https://github.com/ya-labs/YABook/commit/429a2bea1b01790388203f89a530694fb5db0312) | Adicionou exportação opt-in da telemetria de contexto. |
| Automatizar relatório de runtime | [Issue #66](https://github.com/ya-labs/YABook/issues/66) · [PR #67](https://github.com/ya-labs/YABook/pull/67) · [`826d2ca`](https://github.com/ya-labs/YABook/commit/826d2cab992ccff2993d336501e2c6f8a4a9ede3) | Automatizou a geração do relatório runtime da telemetria. |
| Publicar dashboard de métricas | [Issue #62](https://github.com/ya-labs/YABook/issues/62) · [PR #69](https://github.com/ya-labs/YABook/pull/69) · [`27866ba`](https://github.com/ya-labs/YABook/commit/27866ba9a41cce8490b920343df3405dc16dc14e) | Disponibilizou o dashboard hospedado para métricas exportadas. |
| Revisar nomes de APKs preparados | [Issue #70](https://github.com/ya-labs/YABook/issues/70) · [PR #71](https://github.com/ya-labs/YABook/pull/71) · [`d2c682a`](https://github.com/ya-labs/YABook/commit/d2c682a6a337f836e007ff6218acf284e0ed32ac) | Tornou a nomenclatura dos APKs preparados mais clara e rastreável. |
| Adicionar desenvolvimento incremental | [Issue #73](https://github.com/ya-labs/YABook/issues/73) · [PR #74](https://github.com/ya-labs/YABook/pull/74) · [`3746fa0`](https://github.com/ya-labs/YABook/commit/3746fa01af1b9b8f88eafee1889d1413a1382ece) | Introduziu execução de desenvolvimento por etapa com `dev step`. |
| Ajustar saídas e classificação | [Issue #76](https://github.com/ya-labs/YABook/issues/76) · [PR #90](https://github.com/ya-labs/YABook/pull/90) · [`40350df`](https://github.com/ya-labs/YABook/commit/40350df1e7904f31a2aeb536c2888dd3f554febe) | Reforçou contratos de saída e classificação da skill. |
| Evoluir entrevistas e etapas contextuais | [Issue #91](https://github.com/ya-labs/YABook/issues/91) · [PR #97](https://github.com/ya-labs/YABook/pull/97) · [`cc512a4`](https://github.com/ya-labs/YABook/commit/cc512a498b6a564c08b868d5d8fbef182bbe3066) | Tornou entrevistas acompanháveis por checklist opcional e adaptou `dev step` ao contexto, preservando as travas do desenvolvimento. |
| Reforçar artefatos Git e contexto para IA | [Issue #92](https://github.com/ya-labs/YABook/issues/92) · [PR #98](https://github.com/ya-labs/YABook/pull/98) · [`0ffefaa`](https://github.com/ya-labs/YABook/commit/0ffefaa138d4b29dff928ecf02795356260455a3) | Tornou explícitos os contratos de artefatos Git e contexto para IA. |
| Corrigir a próxima etapa de prévias | [Issue #93](https://github.com/ya-labs/YABook/issues/93) · [PR #99](https://github.com/ya-labs/YABook/pull/99) · [`bef9fd1`](https://github.com/ya-labs/YABook/commit/bef9fd109f4d30db4b7a9700b8c666f731b257e9) | Evitou que prévias de artefatos repetissem apenas a autorização pendente. |
| Criar fluxo seguro de rebase | [Issue #94](https://github.com/ya-labs/YABook/issues/94) · [PR #101](https://github.com/ya-labs/YABook/pull/101) · [`72d09d8`](https://github.com/ya-labs/YABook/commit/72d09d816a8c782c26c64594683cc850cc952364) | Adicionou inspeção e execução controlada de rebase. |
| Permitir comandos por repositório | [Issue #96](https://github.com/ya-labs/YABook/issues/96) · [PR #102](https://github.com/ya-labs/YABook/pull/102) · [`efe4660`](https://github.com/ya-labs/YABook/commit/efe4660d5653cbe9f887dd83f2a0d3c5f5129f19) | Passou a admitir comandos personalizados na configuração local do YABook. |
| Persistir comportamento padrão no Codex | [Issue #103](https://github.com/ya-labs/YABook/issues/103) · [PR #106](https://github.com/ya-labs/YABook/pull/106) · [`d5f24c5`](https://github.com/ya-labs/YABook/commit/d5f24c58e05a6629b32a6187f217f23cb9f204e7) | Instalou guardrails para preservar o comportamento padrão entre sessões. |
| Adicionar repasse do contexto atual | [Issue #107](https://github.com/ya-labs/YABook/issues/107) · [PR #108](https://github.com/ya-labs/YABook/pull/108) · [`b14bd52`](https://github.com/ya-labs/YABook/commit/b14bd5295311b4e03368f8a3614332e49224801a) | Criou o comando `resume` para transferir um recorte temático a outro chat. |

### Entrevistas e execução contextual de etapas

A [issue #91](https://github.com/ya-labs/YABook/issues/91), integrada pelo
[PR #97](https://github.com/ya-labs/YABook/pull/97), separou a entrevista do
acompanhamento por checklist. `$yabook init` e `$yabook plan` continuam
funcionando sem checklist obrigatório, enquanto `$yabook steps start init` e
`$yabook steps start plan` iniciam a respectiva entrevista com acompanhamento
ativo.

O comando `$yabook dev step` passou a executar somente a etapa atual e a
adaptar sua ação ao contexto:

- em desenvolvimento, implementa e valida com issue e branch compatíveis;
- em init, investiga e confirma o contexto do projeto;
- em planejamento, conduz a decisão ou consolidação atual;
- em discussão, pesquisa e conduz a análise pendente.

O avanço do checklist depende de confirmação explícita ou de uma nova ação
inequívoca da pessoa usuária. A resposta não marca a etapa como concluída apenas
porque o agente entregou uma análise, não persiste o checklist fora da conversa
e só apresenta guia de continuidade enquanto houver acompanhamento ativo.

A entrega também delimitou os comandos de planejamento:

- `diagnose` reconstrói o estado real com evidências, sem decidir direção de
  produto;
- `plan` inicia a entrevista geral para identificar o objeto de planejamento;
- `plan start <versão>` conduz a entrevista e propõe o planejamento da versão;
- `plan next` recomenda uma ação a partir de planejamento já existente.

As travas de issue, branch e validação permaneceram obrigatórias para etapas de
desenvolvimento, mas não para init, planejamento ou discussão. O checklist
continuou restrito à conversa, sem persistência em arquivos, GitHub ou memória
permanente.

## YABook Desktop e estrutura do produto

| Entrega | Rastreabilidade | Resultado consolidado |
| --- | --- | --- |
| Planejar o MVP do Desktop | [Issue #18](https://github.com/ya-labs/YABook/issues/18) · [PR #85](https://github.com/ya-labs/YABook/pull/85) · [`4139f3e`](https://github.com/ya-labs/YABook/commit/4139f3e7165946057e1e1d07286808a905d3849a) | Consolidou visão, escopo, arquitetura, navegação e roadmap do MVP. |
| Migrar a documentação para o monorepo | [Issue #78](https://github.com/ya-labs/YABook/issues/78) · [PR #87](https://github.com/ya-labs/YABook/pull/87) · [`260c5b5`](https://github.com/ya-labs/YABook/commit/260c5b53afd6a12eb7ad61e6ac2d90ccd80a4b4b) | Separou manual e produto, atualizou links e preparou a estrutura do ecossistema. |
| Criar o scaffold do Desktop | [Issue #79](https://github.com/ya-labs/YABook/issues/79) · [PR #89](https://github.com/ya-labs/YABook/pull/89) · [`79d3532`](https://github.com/ya-labs/YABook/commit/79d3532950d1055eaeced7e19be5a66ab4e66e41) | Criou a base executável em Tauri, React e TypeScript. |
| Implementar biblioteca e descoberta | [Issue #80](https://github.com/ya-labs/YABook/issues/80) · [PR #95](https://github.com/ya-labs/YABook/pull/95) · [`18b7a45`](https://github.com/ya-labs/YABook/commit/18b7a456bbf741012900fca871e9e2f2ed0a9b55) | Adicionou catálogo local e descoberta de raízes documentais. |
| Implementar leitura e navegação | [Issue #81](https://github.com/ya-labs/YABook/issues/81) · [PR #104](https://github.com/ya-labs/YABook/pull/104) · [`229838c`](https://github.com/ya-labs/YABook/commit/229838c2dd7cd2e6cc5900271b064a058b0364d6) | Entregou leitor Markdown, árvore, breadcrumbs, histórico, favoritos e recentes. |

## Estado para continuidade

Ao continuar o trabalho, use este repasse para identificar o que já foi
integrado até o PR `#108`. Consulte os documentos normativos atuais para regras
operacionais; este arquivo registra rastreabilidade, não substitui a skill, o
manual ou a documentação do produto.

Novas entregas devem ser avaliadas a partir desse marco. Quando o repasse for
atualizado novamente, substitua este recorte pelo intervalo posterior em vez de
acumular rodadas antigas.

## Critério de encerramento

Este repasse está encerrado no merge do [PR #108](https://github.com/ya-labs/YABook/pull/108),
commit [`b14bd52`](https://github.com/ya-labs/YABook/commit/b14bd5295311b4e03368f8a3614332e49224801a).
A próxima atualização deve adotar esse ponto como novo marco inicial e manter
somente o recorte ainda necessário para continuidade.
