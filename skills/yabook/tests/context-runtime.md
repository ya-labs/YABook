# Cenários de execução econômica

Este teste é separado da auditoria estática:

- `check_context_budget.py` mede tamanho e quantidade de referências previstas;
- `check_context_runtime.py` valida um relatório produzido a partir de uma
  execução controlada real.

## Métricas

- `class`: classe `C0` a `C4` observada na rota;
- `references`: arquivos de instrução efetivamente lidos;
- `operations[].commands`: comandos independentes executados;
- `operations[].output_chars`: caracteres realmente retornados;
- `rounds`: ciclos do agente que terminaram em ferramenta ou resposta;
- `rediscovered_facts`: workspace, issue, branch ou objetivo consultados
  novamente sem sinal de mudança;
- `expansions`: limites excedidos e sua justificativa.

Os limites ficam em `context-runtime-budgets.json`. Cada saída de terminal deve
ter até 4.000 caracteres; a soma obedece ao orçamento do cenário.

## Execução

1. Execute um cenário em conversa limpa ou registre o ponto inicial.
2. Copie para JSON somente referências e operações realmente observadas.
3. Informe os fatos reutilizados e redescobertos.
4. Valide:

```bash
python3 skills/yabook/tests/check_context_runtime.py relatorio.json
```

Use `runtime-report.example.json` apenas como exemplo de formato, não como prova
de uma execução real.

Uma ampliação só é aceita com justificativa não vazia. `contexto.md` continua
proibido em rota explícita. A classe observada deve corresponder à classe do
cenário e nunca pode ser justificada como divergente.
