# Desenvolvimento orientado pela issue

Use esta referência para `$yabook dev`.

## Objetivo

Desenvolver a demanda atual de ponta a ponta até a validação, sem exigir que a
pessoa solicite separadamente cada pré-requisito operacional.

`dev` é uma autorização explícita de implementação e uma exceção documentada à
trava de `do`. Seu escopo termina antes de commit, Pull Request e merge, salvo
quando outro comando encadeado autorizar essas entregas.

## Descoberta da demanda

1. Reutilize workspace, branch, issue e regras locais ainda válidos na conversa.
2. Se o workspace não estiver resolvido, aplique `workspace.md` e valide o remote.
3. Faça uma única inspeção inicial de branch, status, diffs e último commit.
4. Identifique a issue pela conversa, branch ou referência explícita.
5. Confirme objetivo, escopo e critérios de aceite com o contexto disponível.
6. Consulte GitHub somente quando faltar informação da issue, vínculo, status
   ou preparação da branch.
7. Se mais de uma issue for plausível, peça a escolha.
8. Se não houver issue, pare e indique `$yabook do: issue`.

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

Quando houver issue inequívoca, `dev` autoriza:

- avaliar checkpoints pendentes;
- atualizar a base necessária;
- criar ou trocar para a branch da issue;
- publicar e vincular a branch à issue quando necessário;
- atualizar o status da issue para `Em andamento`;
- ler o contexto necessário;
- editar código e documentação dentro do escopo;
- executar testes, validações e correções da implementação.

Use branch `numero-descricao-curta`. Não misture issues na mesma branch.
Ao criar a branch, aplique o fluxo nativo descrito em `github.md`: use
`createLinkedBranch`, confirme o nome em `issue.linkedBranches` e só então
prepare o tracking local. Se o vínculo nativo não estiver disponível, informe o
fallback manual sem apresentar a branch apenas publicada como vinculada.

## Limites

`dev` sozinho não autoriza:

- ampliar escopo ou decidir produto;
- incluir mudanças alheias à issue;
- criar commit;
- fazer push de commits de implementação;
- abrir Pull Request;
- fazer merge ou release.

Interrompa diante de decisão pendente, conflito, risco relevante, dependência
externa ou critério de aceite impossível de validar.

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
