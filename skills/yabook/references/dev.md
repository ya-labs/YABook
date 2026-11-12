# Desenvolvimento orientado pela issue

## Objetivo

Desenvolver até a validação, incluindo os pré-requisitos operacionais.

`dev` é executivo, exceção explícita às prévias sem `do`: cria a issue necessária,
prepara sua branch e implementa até a validação. Termina antes de commit, PR e
merge, salvo autorização encadeada; não é gate exclusivo para editar.
Com YABook Tasks, branch, PR e merge avançam a tarefa da issue pelo hook; ao
encerrar sem PR, rode `task issue --fase revisao --registro <resumo>`.

Em `auto`, implemente, valide e organize commits sem `do` ou checkpoint aprovado.
Escolha issue, pacote ou ajuste pontual documentado; este dispensa issue/branch.
Operações remotas dependem do pedido. As travas abaixo valem fora de `auto`.

## Profundidade

### `$yabook dev quick`

Use para tarefa pequena, clara e de baixo risco. É uma rota `C3`.

- use issue, brief ou conversa como fonte principal;
- abra inicialmente no máximo 3 arquivos diretamente relacionados;
- não consulte GitHub quando issue e branch já estiverem confirmadas;
- não leia documentação geral nem revise arquitetura;
- execute validação focal;
- pare diante de ambiguidade material;
- informe o motivo antes de ampliar.

### `$yabook dev`

Fluxo balanceado `C3`: inspecione, implemente, valide e apresente `Como testar`
com o relatório técnico obrigatório.

### `$yabook dev step`

Use quando houver um checklist ativo e a pessoa quiser desenvolver somente a
etapa atual. É uma rota `C3`.

- execute apenas a etapa marcada como atual;
- se não houver etapa atual inequívoca, pare e peça definição;
- não avance para etapas seguintes sem confirmação;
- execute conforme o contexto do checklist, definido em `steps.md`;
- em `desenvolvimento`, validação, preparação, commit e PR não viram etapa
  própria; exija issue e branch compatíveis;
- nos contextos `init`, `planejamento` e `discussão`, não exija issue ou branch
  e não implemente nem crie arquivos sem a autorização aplicável;
- avance só por confirmação explícita ou ação inequívoca da pessoa.

Em `desenvolvimento`, entregue relatório técnico e `Como testar`; nos demais
contextos, só o resultado para parecer antes de avançar.

### `$yabook dev full`

Use para demanda complexa sob pedido explícito. É uma rota `C4`.

Investigue documentação, arquitetura e impactos; justifique a profundidade e
leia em lotes filtrados. `full` não amplia escopo nem permissões.

## Descoberta da demanda

1. Reutilize workspace, branch, issue, brief e regras locais ainda válidos.
2. Se o workspace não estiver resolvido, aplique `workspace.md` e valide o remote.
3. Faça uma única inspeção inicial conforme `git/checkpoint.md`.
4. Identifique a issue pela conversa, branch ou referência explícita.
5. Prefira o brief válido; releia a fonte longa somente diante de lacuna.
6. Confirme a demanda; em pacote, use o pedido/documento atual, sem atualizar a issue.
7. Consulte GitHub somente quando faltar informação da issue, vínculo, status
   ou preparação da branch.
8. Se mais de uma issue for plausível, peça a escolha.
9. Sem issue adequada e com demanda delimitada, crie-a conforme o contrato:
   título, corpo, labels oficiais e Size no Project. Informe a criação,
   sem exigir `do issue` separado.
10. Reutilize issue existente; ambiguidade material exige esclarecimento.
Ajuste pontual autorizado por `bypass` ou elegível em `auto` pode dispensar issue.
Se workspace, branch e issue apontarem para repositórios incompatíveis,
interrompa antes de qualquer escrita.

### Caminho rápido

Quando workspace, issue, branch e demanda já estiverem inequívocos:

- não consulte `contexto.md`, GitHub, memória ou documentação geral;
- leia somente instruções e arquivos diretamente relacionados à mudança;
- use buscas direcionadas antes de abrir documentos;
- edite em uma rodada e valide em outra, salvo falha ou descoberta relevante;
- justifique qualquer ampliação além desse caminho.

## Preparação automática

Com issue existente ou criada, `dev` aciona sem pedir `do branch` separado:

- avaliar checkpoints pendentes;
- atualizar a base necessária;
- criar ou trocar para a branch da issue;
- publicar e vincular a branch à issue quando necessário;
- atualizar o status da issue para `Em andamento`;
- ler o contexto necessário;
- editar código e documentação dentro do escopo;
- executar testes, validações e correções da implementação.

Use branch `numero-descricao-curta`. Não misture issues na mesma branch.
Em pacote, documente commits e use merge commit no PR. Em dupla, mesma branch
por turnos; consulte `artefatos/issue-package.md` quando faltar coordenação.
Ao criar a branch, aplique `github/branches.md`: use
`createLinkedBranch`, confirme o nome em `issue.linkedBranches` e só então
prepare o tracking local. Se o vínculo nativo não estiver disponível, informe o
fallback manual sem apresentar a branch apenas publicada como vinculada.

## Limites

`dev` sozinho não amplia:

- ampliar escopo ou decidir produto;
- incluir mudanças alheias à issue;
- criar commit;
- fazer push de commits de implementação;
- abrir Pull Request;
- fazer merge ou release.
- rebasear a branch: mesmo quando a base precisar de atualização, interrompa e
  indique `$yabook rebase`; a mutação exige `$yabook do rebase`.

Interrompa diante de decisão pendente, conflito, risco relevante, dependência
externa ou critério de aceite impossível de validar.

## Orientação de teste no contexto de desenvolvimento

Ao concluir a etapa, faça a curadoria de `memory.md` com `learning.trigger: dev`:
só descobertas não óbvias e comprovadas; `learn` em automatic, proposta em manual.
No relatório, informe `Memória atualizada: <assunto>` ou que não houve novidade.

Ao concluir a implementação, `dev` e `dev step` em `desenvolvimento` apresentam
`Como testar` com passos específicos da alteração. `init`, `planejamento` e
`discussão` relatam investigação, decisão ou análise, sem simular validação.

Inclua, quando aplicável:

1. pré-requisitos para executar a validação;
2. comandos de testes automatizados;
3. ações manuais em ordem;
4. resultado esperado em cada verificação relevante.

Diferencie testes executados pelo agente das verificações que ainda dependem da
pessoa. Não repita comandos que já falharam como se fossem válidos e não invente
um procedimento sem evidência no projeto. Quando não houver teste aplicável,
informe o motivo explicitamente.

Também se aplica ao `dev` encadeado, dentro do escopo da issue.

Toda execução de `dev` de desenvolvimento também deve apresentar um relatório
técnico com os títulos exatos abaixo. Esse bloco não pode ser substituído por
resumo livre, lista de alterações, seção `Agora`, seção `Validações` ou texto
equivalente.

```md
## Desenvolvimento realizado

### O que foi feito

### Como foi feito

### Por que foi feito assim

### Observações para revisão
```

Explique mudanças, implementação, motivos e pontos pendentes de revisão.

Em `dev step` de desenvolvimento, mantenha `Como testar` e o relatório técnico
focados somente na etapa executada.

## Composição

Execute comandos encadeados da esquerda para a direita, reaproveitando o estado:

```text
$yabook dev & do pr
$yabook dev & do merge
```

- `dev & do pr`: prepara, implementa, valida, cria commits coerentes, envia a
  branch e cria ou atualiza o PR.
- `dev & do merge`: executa o fluxo anterior, valida as condições do PR e faz o
  merge.

Não peça confirmações intermediárias para pré-requisitos já autorizados pelo
objetivo. Fora de `auto`, nunca faça merge sem `do merge`; em `auto`, o pedido
de merge deve ser explícito, sem exigir essa sintaxe.
