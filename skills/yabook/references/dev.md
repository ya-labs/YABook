# Desenvolvimento orientado pela issue

Use esta referência para `$yabook dev`.

## Objetivo

Desenvolver a demanda atual de ponta a ponta até a validação, sem exigir que a
pessoa solicite separadamente cada pré-requisito operacional.

`dev` é o atalho operacional para a implementação da issue atual. Ele não é um
gate exclusivo para editar arquivos e termina antes de commit, Pull Request e
merge, salvo quando outro comando encadeado autorizar essas entregas.

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

É o fluxo balanceado `C3`: inspecione o necessário, implemente com segurança,
valide o escopo e apresente `Como testar` com o relatório técnico obrigatório.

### `$yabook dev step`

Use quando houver um checklist ativo e a pessoa quiser desenvolver somente a
etapa atual. É uma rota `C3`.

- execute apenas a etapa marcada como atual;
- se não houver etapa atual inequívoca, pare e peça definição;
- não avance para etapas seguintes sem confirmação;
- execute conforme o contexto do checklist, definido em `steps.md`;
- no contexto `desenvolvimento`, não transforme validação geral, preparação,
  commit ou PR em etapa própria, valide o necessário e mantenha exigência de
  issue e branch compatíveis;
- nos contextos `init`, `planejamento` e `discussão`, não exija issue ou branch
  e não implemente nem crie arquivos sem a autorização aplicável;
- só avance por confirmação explícita ou por nova ação inequívoca da pessoa
  usuária que confirme a etapa anterior.

O relato pós-etapa faz parte da entrega. Em `desenvolvimento`, use o relatório
técnico obrigatório e `Como testar`; nos demais contextos, registre somente o
resultado contextual para parecer antes do avanço.

### `$yabook dev full`

Use para demanda complexa sob pedido explícito. É uma rota `C4`.

Pode investigar documentação relacionada, arquitetura e impactos maiores.
Informe o motivo da profundidade, leia em lotes filtrados e resuma cada lote
antes de ampliar novamente. `full` não amplia escopo nem permissões.

## Descoberta da demanda

1. Reutilize workspace, branch, issue, brief e regras locais ainda válidos.
2. Se o workspace não estiver resolvido, aplique `workspace.md` e valide o remote.
3. Faça uma única inspeção inicial conforme `git/checkpoint.md`.
4. Identifique a issue pela conversa, branch ou referência explícita.
5. Prefira o brief válido; releia a fonte longa somente diante de lacuna.
6. Confirme objetivo, escopo e critérios de aceite com o contexto disponível.
7. Consulte GitHub somente quando faltar informação da issue, vínculo, status
   ou preparação da branch.
8. Se mais de uma issue for plausível, peça a escolha.
9. Se não houver issue, pare e indique `$yabook do: issue`.

Não crie uma issue silenciosamente.
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

Quando houver issue inequívoca, `dev` aciona:

- avaliar checkpoints pendentes;
- atualizar a base necessária;
- criar ou trocar para a branch da issue;
- publicar e vincular a branch à issue quando necessário;
- atualizar o status da issue para `Em andamento`;
- ler o contexto necessário;
- editar código e documentação dentro do escopo;
- executar testes, validações e correções da implementação.

Use branch `numero-descricao-curta`. Não misture issues na mesma branch.
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

Interrompa diante de decisão pendente, conflito, risco relevante, dependência
externa ou critério de aceite impossível de validar.

## Orientação de teste no contexto de desenvolvimento

Ao concluir a implementação, `dev` e `dev step` no contexto
`desenvolvimento` devem apresentar uma seção `Como testar` com passos
específicos para a alteração realizada. Os contextos `init`, `planejamento` e
`discussão` relatam a investigação, decisão ou análise atual e não simulam
validação de implementação.

Inclua, quando aplicável:

1. pré-requisitos para executar a validação;
2. comandos de testes automatizados;
3. ações manuais em ordem;
4. resultado esperado em cada verificação relevante.

Diferencie testes executados pelo agente das verificações que ainda dependem da
pessoa. Não repita comandos que já falharam como se fossem válidos e não invente
um procedimento sem evidência no projeto. Quando não houver teste aplicável,
informe o motivo explicitamente.

Essa orientação é obrigatória também quando `dev` de desenvolvimento estiver
encadeado com outro comando. Ela não permite executar ações fora do escopo da
issue.

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

Use esse relatório para explicar a entrega de forma auditável: o que mudou, como
foi implementado, por que essa abordagem foi escolhida e quais decisões,
alternativas, riscos ou pontos de parecer ainda merecem revisão da pessoa.

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
objetivo. Nunca faça merge sem `do merge`.
