# `$yabook check [full]` e `$yabook review [full]`

Use `check` para validar conformidade objetiva e `review` para analisar
qualidade, riscos e decisões do artefato solicitado.

## Padrão dirigido

`check` e `review` são rotas `C2`:

- use o artefato alvo e sua referência normativa direta;
- inspecione somente metadados e trechos relacionados;
- não leia coleções completas, issues fechadas ou documentação ampla;
- pare quando houver evidência suficiente;
- informe limitações sem ampliar preventivamente.

## Variação completa

`check full` e `review full` são rotas `C4` e exigem pedido explícito.

Antes de ampliar:

1. confirme o escopo da auditoria;
2. informe em uma frase por que a leitura profunda é necessária;
3. colete lotes filtrados;
4. resuma cada lote antes do próximo;
5. descarte fontes irrelevantes.

O sufixo `full` altera profundidade, não permissões. Essas rotas continuam
somente leitura sem um comando de escrita autorizado.
