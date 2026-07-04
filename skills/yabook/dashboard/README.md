# Dashboard hospedado de métricas de contexto

Esta pasta entrega a camada de leitura da issue #62.

O dashboard existe para facilitar a leitura visual das métricas já exportadas
pela telemetria oficial do YABook.

Ele:

- consome somente o payload oficial exportado pela telemetria da issue #61;
- não cria coleta nova;
- separa métricas exatas, aproximadas e indisponíveis;
- destaca regressões por rota, ampliações e redescobertas.

Para aprender a usar na prática:

- consulte [`docs/manual.md`](../../../docs/manual.md);
- use `$yabook help dashboard`.

## Arquivos

- `index.html`: página estática pronta para hospedagem em servidor simples;
- `context-dashboard.example.json`: dataset de exemplo para visualização local;
- `../scripts/build_context_dashboard.py`: consolida exportações oficiais em um dataset lido pela página.
