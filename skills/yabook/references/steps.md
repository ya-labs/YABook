# Acompanhamento de etapas

`steps` mantém um checklist apenas na conversa. `steps` fala da lista inteira;
`step` fala somente da etapa atual.

```text
$yabook steps start
$yabook steps
$yabook step
$yabook steps done <número>
$yabook steps cancel
```

Mantenha um checklist ativo. Marque conclusão somente por confirmação ou
evidência. Não grave estado em arquivo, memória permanente ou GitHub.

Ao criar etapas com `steps start`, liste apenas passos objetivos de
desenvolvimento do ajuste. Evite etapa inicial genérica de preparação, leitura
de contexto ou setup. Evite etapa final genérica de validação, teste geral,
commit, PR ou encerramento. Validações específicas podem aparecer dentro da
execução da etapa, mas não como item separado sem entrega própria.

Use `$yabook step` para detalhar a etapa atual sem executar alterações. A
resposta pode explicar objetivo, abordagem, dúvidas, riscos e possíveis ajustes
para parecer da pessoa.

`$yabook dev step` executa somente a etapa atual. Se não houver etapa atual
inequívoca, pare e peça definição. Nunca interprete `dev step` como autorização
para executar todos os itens abertos.

Depois de desenvolver uma etapa, relate a entrega para auditoria passo a passo:

```md
## Desenvolvimento realizado

### O que foi feito

### Como foi feito

### Por que foi feito assim

### Observações para revisão
```

Esse bloco com os títulos exatos é obrigatório em `dev` e `dev step`. Ele não
pode ser substituído por resumo livre, lista de alterações, `Agora`,
`Validações` ou texto equivalente, porque permite que a pessoa revise o
desenvolvimento, entenda as decisões tomadas e aponte ajustes antes da próxima
etapa.

Enquanto houver etapas abertas, finalize com:

```text
Etapas em andamento

✅ 1. Etapa concluída
➡️ 2. Próxima etapa
⬜ 3. Etapa pendente
```

Se uma ação sair da ordem ou exigir ajuste, carregue
[steps/replanning.md](steps/replanning.md). Mudanças de objetivo, escopo,
decisão, prioridade, issue ou versão exigem confirmação.
