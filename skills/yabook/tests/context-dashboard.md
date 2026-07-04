# Dashboard hospedado de contexto

Esta entrega usa somente o payload oficial da telemetria externa opt-in como
fonte de verdade.

## Objetivo

Permitir leitura visual das execuções já exportadas, com foco em:

- regressão por rota;
- distribuição por classe;
- ampliações registradas;
- redescobertas de fatos;
- confiabilidade de cada indicador.

## Contrato de leitura

O dashboard:

- aceita somente arquivos no formato exportado por `export_context_telemetry.py`;
- rejeita relatório bruto de runtime com `references`, `consulted_files`,
  `directed_searches` ou `expansions`;
- mantém métricas `unavailable` sem valor inventado;
- agrega operações por ferramenta sem reconstituir conteúdo original.

## Geração do dataset

Use:

```text
python skills/yabook/scripts/build_context_dashboard.py export-1.json export-2.json --output skills/yabook/dashboard/context-dashboard.json
```

O arquivo gerado concentra:

- visão geral;
- catálogo de origem dos indicadores;
- resumo por rota;
- distribuição por classe;
- qualidade por métrica;
- métricas com ampliação;
- operações agregadas.

## Publicação

A página `skills/yabook/dashboard/index.html` é estática. Basta hospedar a pasta
com o dataset JSON ao lado.

## Limites

- o dashboard não substitui validação local nem exportação oficial;
- sem novo payload exportado, não existe atualização automática;
- o painel é somente leitura e não introduz coleta adicional.
