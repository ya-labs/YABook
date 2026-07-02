# Branches vinculadas no GitHub

Use para `do branch` e para preparação de branch em `dev`.

Identifique uma única issue. Diante de mais de uma candidata, peça a escolha.

Use:

```text
numero-descricao-curta
```

Prefira o vínculo nativo:

1. obtenha os Node IDs da issue e do repositório e o OID da base;
2. execute `createLinkedBranch` com `issueId`, `name`, `oid` e `repositoryId`;
3. consulte `issue.linkedBranches`;
4. confirme o nome retornado;
5. prepare a branch local rastreando a remota.

Criar ou publicar apenas com Git não comprova o vínculo.

Sem suporte a `createLinkedBranch`, use Git somente quando autorizado, informe
que o vínculo nativo ficou pendente e oriente a associação manual pela seção
Development.
