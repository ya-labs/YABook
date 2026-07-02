# Acompanhamento de etapas

`steps` mantém um checklist apenas na conversa e não executa seus itens.

```text
$yabook steps start
$yabook steps
$yabook steps done <número>
$yabook steps cancel
```

Mantenha um checklist ativo. Marque conclusão somente por confirmação ou
evidência. Não grave estado em arquivo, memória permanente ou GitHub.

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
