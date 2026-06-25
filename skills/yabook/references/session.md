# `$yabook load`

Use este comando para carregar um resumo operacional do YABook na conversa atual.

## Objetivo

Reduzir buscas repetidas no repositório durante a mesma conversa.

`$yabook load` não cria memória permanente e não altera arquivos.

## Resposta esperada

Ao receber `$yabook load`, responda com um resumo curto:

```text
YABook carregado para esta conversa.

Padrões principais:
- Issue: título objetivo, labels para tipo/área, Size no Project.
- Size: 1 rápido, 2 pequeno, 3 médio, 4 grande, 5 quebrar em issues menores.
- Branch: numero-descricao-curta.
- Commit: tipo: descrição curta.
- PR: título objetivo e descrição com Resumo rápido.
- GitHub: issue relevante deve ter Project, labels e Size.
- IA: usar a issue como fonte principal quando suficiente.
```

Depois disso, use estes padrões antes de consultar novamente o YABook.

## Quando consultar o repositório mesmo assim

Consulte documentos ou arquivos do projeto quando:

- o pedido contrariar o padrão carregado;
- houver regra local em `AGENTS.md`;
- a tarefa envolver criação real de issue, branch, PR, release ou merge;
- o contexto estiver incompleto;
- a pessoa pedir validação de conformidade.

## Limite

O contexto carregado vale apenas para a conversa atual.

Em nova conversa, carregue novamente com `$yabook load`.
