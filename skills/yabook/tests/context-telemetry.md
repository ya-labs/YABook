# Telemetria externa opt-in

Use esta entrega para publicar métricas já observadas localmente sem expor
conteúdo sensível nem transformar a exportação em dependência da execução.

## Contrato

- a exportação parte de um relatório já validado por `check_context_runtime.py`;
- o payload envia apenas dados agregados e categóricos;
- nomes de arquivos, consultas direcionadas, notas livres e texto integral do
  relatório ficam fora da exportação;
- métricas `unavailable` permanecem sem valor inventado;
- o envio é opt-in e desativado por padrão.

## Configuração

Use `.yabook/context-telemetry.json` ou um caminho explícito por CLI:

```json
{
  "enabled": true,
  "endpoint": "https://telemetry.example.com/yabook/context",
  "token_env": "YABOOK_TELEMETRY_TOKEN",
  "timeout_seconds": 5,
  "headers": {
    "X-YABook-Source": "runtime-report"
  }
}
```

Segredos não ficam no arquivo. Use `token_env` para ler o token do ambiente.

## Estratégia de anonimização

- exporte contagens, classes, rota e agregados por ferramenta;
- não exporte `references`, `consulted_files` ou `directed_searches` crus;
- não exporte `note` de métricas indisponíveis;
- reduza ampliações a contagem e lista de métricas afetadas;
- mantenha `brief` e `cache` apenas como flags e status.

## Falha não bloqueante

Erro de rede, timeout ou endpoint inválido gera aviso local e não falha a
execução principal.

## Execução

```text
python skills/yabook/scripts/export_context_telemetry.py skills/yabook/tests/runtime-report.example.json --config skills/yabook/tests/context-telemetry-config.example.json --output skills/yabook/tests/context-telemetry-payload.example.json
```
