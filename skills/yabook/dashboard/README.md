# Dashboard hospedado de métricas de contexto

Esta pasta entrega a camada de leitura da issue #62.

O dashboard:

- consome somente o payload oficial exportado pela telemetria da issue #61;
- não cria coleta nova;
- separa métricas exatas, aproximadas e indisponíveis;
- destaca regressões por rota, ampliações e redescobertas.

## Arquivos

- `index.html`: página estática pronta para hospedagem em servidor simples;
- `context-dashboard.example.json`: dataset de exemplo para visualização local;
- `../scripts/build_context_dashboard.py`: consolida exportações oficiais em um dataset lido pela página.

## Gerar dataset

Use somente payloads já exportados pelo contrato oficial:

```text
python skills/yabook/scripts/build_context_dashboard.py arquivo-1.json arquivo-2.json --output skills/yabook/dashboard/context-dashboard.json
```

## Hospedar

Qualquer host estático funciona, desde que publique a pasta `skills/yabook/dashboard/`.

Exemplo local:

```text
python -m http.server 4173
```

Depois abra:

```text
http://localhost:4173/skills/yabook/dashboard/
```

## Limites

- o painel não substitui o contrato oficial de exportação;
- métricas `unavailable` continuam sem valor numérico;
- a leitura depende do conjunto de exportações fornecido ao gerador.
