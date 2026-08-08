# Cenários de desenvolvimento orientado pela issue

## Profundidade

Confirme que:

- `dev quick` começa com no máximo 3 arquivos, evita GitHub já resolvido e usa
  validação focal;
- `dev` mantém descoberta e validação balanceadas;
- `dev full` exige pedido explícito, informa o motivo da profundidade e trabalha
  em lotes filtrados;
- `dev step` exige etapa atual inequívoca, executa somente essa etapa e não
  avança para os próximos itens sem confirmação explícita ou nova ação
  inequívoca da pessoa usuária;
- em checklist de desenvolvimento, mantém issue, branch e validação; em
  `init`, `planejamento` e `discussão`, atua no contexto atual sem exigir issue
  ou branch e sem implementar fora da autorização;
- nenhuma variação amplia escopo, autorização de commit, PR ou merge.
- um pedido direto inequívoco para implementar a issue atual também pode
  autorizar a edição dentro do escopo, inclusive em `prod`, sem exigir `dev`
  como gate exclusivo.

## Orientação de teste

Após concluir:

```text
$yabook dev
```

Confirme que a resposta:

- apresenta uma seção `Como testar`;
- usa passos específicos para a alteração implementada;
- informa pré-requisitos, comandos, ações manuais e resultados esperados quando
  aplicáveis;
- diferencia validações executadas pelo agente de verificações pendentes;
- explica quando não houver teste aplicável;
- não trata testes falhos ou não executados como aprovados.

A mesma orientação deve aparecer quando `dev` estiver encadeado com `do pr` ou
`do merge`.

## Relatório técnico

Após qualquer execução de `dev`, confirme que a resposta inclui um bloco
obrigatório com estes títulos exatos:

- `O que foi feito`;
- `Como foi feito`;
- `Por que foi feito assim`;
- `Observações para revisão`.

Resumo livre, lista de alterações, seção `Agora`, seção `Validações` ou texto
equivalente não substituem esse bloco. Em `dev step` de desenvolvimento, o
relatório deve ficar restrito à etapa atual. Nos demais contextos, confirme o
relato da investigação, decisão ou análise atual sem exigir esse relatório.
