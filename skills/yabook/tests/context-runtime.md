# Cenários de execução econômica

Este teste é separado da auditoria estática:

- `check_context_budget.py` mede tamanho e quantidade de referências previstas;
- `check_context_runtime.py` valida um relatório produzido a partir de uma
  execução controlada real.

## Métricas

- `class`: classe `C0` a `C4` observada na rota;
- `route`: rota executada, como `dev`, `pr`, `check full`;
- `references`: arquivos de instrução efetivamente lidos;
- `consulted_files`: arquivos de projeto ou apoio realmente consultados;
- `operations[].commands`: comandos independentes executados;
- `operations[].output_chars`: caracteres realmente retornados;
- `rounds`: ciclos do agente que terminaram em ferramenta ou resposta;
- `directed_searches`: buscas direcionadas feitas para localizar evidência;
- `rediscovered_facts`: workspace, issue, branch ou objetivo consultados
  novamente sem sinal de mudança;
- `expansions`: limites excedidos e sua justificativa.
- `brief` e `cache`: registram disponibilidade e uso quando existirem.

## Qualidade das métricas

Use `measurements` para declarar se cada métrica é:

- `exact`: contagem observada diretamente no relatório;
- `approx`: aproximação explícita, como tokens estimados por caracteres;
- `unavailable`: dado não fornecido pelo runtime.

Para `unavailable`, informe `note` e não invente `value`.
Para métricas derivadas de listas e operações do próprio relatório, use `exact`.

Os limites ficam em `context-runtime-budgets.json`. Cada saída de terminal deve
ter até 4.000 caracteres; a soma obedece ao orçamento do cenário.

## Execução

1. Execute um cenário em conversa limpa ou registre o ponto inicial.
2. Copie para JSON somente referências, arquivos, buscas e operações realmente observados.
3. Preencha `measurements` com a qualidade de cada métrica.
4. Informe os fatos reutilizados e redescobertos.
5. Valide:

```bash
python3 skills/yabook/tests/check_context_runtime.py relatorio.json
```

Use `runtime-report.example.json` apenas como exemplo de formato, não como prova
de uma execução real.

Uma ampliação só é aceita com justificativa não vazia. `contexto.md` continua
proibido em rota explícita. A classe observada deve corresponder à classe do
cenário e nunca pode ser justificada como divergente.

## Exportação externa opt-in

Quando a telemetria externa estiver habilitada, exporte somente o payload
sanitizado descrito em `context-telemetry.md`.

Use:

```text
python skills/yabook/scripts/export_context_telemetry.py relatorio.json --config .yabook/context-telemetry.json
```

A exportação:

- depende de um relatório já validado localmente;
- envia apenas contagens, classes, flags e agregados;
- não envia arquivos consultados, buscas direcionadas cruas nem texto integral;
- não bloqueia a execução principal quando a rede falhar.

## Dashboard hospedado

Quando existir um conjunto de payloads exportados pelo contrato oficial,
consolide-os para leitura visual com:

```text
python skills/yabook/scripts/build_context_dashboard.py export-1.json export-2.json --output skills/yabook/dashboard/context-dashboard.json
```

O dashboard:

- lê apenas o payload oficial exportado;
- destaca regressões por rota, classes, ampliações e redescobertas;
- informa origem e confiabilidade dos indicadores;
- continua somente leitura, sem coleta paralela.
