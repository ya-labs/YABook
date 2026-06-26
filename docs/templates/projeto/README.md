# Nome do Projeto

Descreva em poucas linhas o objetivo do projeto e qual problema ele resolve.

## Visão geral

Explique o contexto do produto, o público-alvo e o resultado esperado.

## Stack

Liste as principais tecnologias usadas.

Exemplo:

- Front-end:
- Back-end:
- Banco de dados:
- Infraestrutura:
- Testes:

## Como rodar

Descreva o setup local mínimo.

```powershell
# exemplo
npm install
npm run dev
```

## Estrutura

```text
.
|-- docs/
|-- src/
`-- README.md
```

Adapte esta seção para a estrutura real do projeto.

## Documentação

A documentação técnica do projeto fica em:

```text
docs/
```

Para decidir onde registrar cada assunto, use:

- [Guia de consulta da documentação](docs/guia-da-documentacao.md)

Esse guia é a fonte do projeto para estrutura documental. Crie apenas documentos e pastas que ajudem alguém a executar, revisar, decidir ou continuar o trabalho.

## Fluxo de trabalho

Mudanças relevantes devem seguir o fluxo:

```text
Issue -> Branch -> Commit -> Pull Request -> Merge
```

Para condução do projeto, use o YABook como referência para:

- padrões de issue, branch, commit e PR;
- labels;
- Project e responsáveis;
- critérios de pronto e release.

### Labels do projeto

Use a base oficial de labels do YABook. Declare aqui somente as labels adotadas neste projeto.

- Tipo: `bug`, `feature`, `docs`, `refactor`, `tooling`
- Área: `frontend`, `backend`, `infra`, `ui/ux`, `architecture`, `process`
- Especial: `epic`

Remova as labels que não fizerem sentido para o projeto. Não crie variações de nomenclatura sem registrar a exceção.

### GitHub Project e responsável

- GitHub Project:
- Campo `Size`: `1` a `5`
- Responsável padrão por novas issues:

Em projetos da YA LABS, novas issues devem ser vinculadas ao GitHub Project aplicável, receber `Size` e ser atribuídas ao usuário solicitante, salvo orientação diferente.

Consulte o YABook para o padrão completo de issues, labels, branches, commits, PRs e releases.
