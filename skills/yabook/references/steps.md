# Acompanhamento de etapas

`steps` mantém um checklist apenas na conversa. `steps` fala da lista inteira;
`step` fala somente da etapa atual.

```text
$yabook steps start
$yabook steps start init
$yabook steps start plan
$yabook steps
$yabook step
$yabook steps done <número>
$yabook steps cancel
```

Mantenha um checklist ativo, apenas na conversa. Cada checklist tem um contexto:
`desenvolvimento`, `init`, `planejamento` ou `discussão`. Marque conclusão
somente por confirmação explícita da pessoa usuária ou por uma nova ação
inequívoca dela que confirme a etapa anterior antes de solicitar a seguinte.
Nunca marque uma etapa como concluída apenas porque o agente entregou seu relato.
Não grave estado em arquivo, memória permanente ou GitHub.

`steps start init` inicia a entrevista de `init` e um checklist contextual.
`steps start plan` inicia a entrevista geral de `plan` e um checklist
contextual. Ambos mantêm a mesma conversa de suas rotas sem checklist; só o
atalho adiciona o acompanhamento. `steps start` sem contexto explícito cria
etapas do contexto já inequívoco na conversa. Se ele não estiver claro, peça a
definição; não invente objetivo, decisão ou etapa.

Ao criar etapas, liste somente entregas objetivas adequadas ao contexto. Em
`desenvolvimento`, evite etapa inicial genérica de preparação, leitura de
contexto ou setup e evite etapa final genérica de validação, teste geral,
commit, PR ou encerramento. Em `init`, `planejamento` e `discussão`, as etapas
podem ser investigações, perguntas, decisões ou consolidações concretas; não
as trate como implementação.

Use `$yabook step` para detalhar a etapa atual sem executar alterações. A
resposta pode explicar objetivo, abordagem, dúvidas, riscos e possíveis ajustes
para parecer da pessoa.

`$yabook dev step` executa somente a etapa atual. Se não houver etapa atual
inequívoca, pare e peça definição. Nunca interprete `dev step` como autorização
para executar todos os itens abertos. A execução depende do contexto:

- `desenvolvimento`: implementa e valida a entrega atual; mantém exigência de
  issue e branch compatíveis;
- `init`: investiga e confirma o contexto mínimo do projeto, sem criar arquivos
  sem `do`;
- `planejamento`: conduz a decisão ou consolidação atual, sem implementar;
- `discussão`: pesquisa e conduz a análise pendente, sem transformar hipótese
  em decisão aprovada.

Os três últimos contextos não exigem issue nem branch. Nenhum contexto avança o
checklist pela entrega do agente.

Depois de executar uma etapa de desenvolvimento, relate a entrega para auditoria
passo a passo:

```md
## Desenvolvimento realizado

### O que foi feito

### Como foi feito

### Por que foi feito assim

### Observações para revisão
```

Esse bloco com os títulos exatos é obrigatório em `dev` e em `dev step` no
contexto `desenvolvimento`. Ele não pode ser substituído por resumo livre, lista
de alterações, `Agora`, `Validações` ou texto equivalente, porque permite que a
pessoa revise o desenvolvimento, entenda as decisões tomadas e aponte ajustes
antes da próxima etapa. Nos demais contextos, relate somente a investigação,
decisão, hipótese ou pendência da etapa atual.

Enquanto houver checklist ativo, toda resposta YABook deve incluir, uma única
vez e somente na resposta final, o estado compacto abaixo. Posicione-o após o
resultado principal e imediatamente antes de `Próxima etapa`, inclusive em
orientação, preparação de artefato, execução, validação e bloqueio. Reproduza
o estado real sem avançar automaticamente: a etapa atual é ➡️, as confirmadas
são ✅ e as demais são ⬜. Não inclua o bloco nem o guia `Próxima etapa` se não
houver checklist ativo. O guia aponta uma entrega posterior ao comando atual e
só sugere um comando quando a rota for aplicável; não invente comando, issue,
decisão ou objetivo.

```text
Etapas em andamento

✅ 1. Etapa concluída
➡️ 2. Próxima etapa
⬜ 3. Etapa pendente
```

O formato do exemplo não altera a regra de conclusão: marque uma etapa somente
por confirmação ou evidência.

Se uma ação sair da ordem ou exigir ajuste, carregue
[steps/replanning.md](steps/replanning.md). Mudanças de objetivo, escopo,
decisão, prioridade, issue ou versão exigem confirmação.
