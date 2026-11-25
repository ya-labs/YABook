# `$yabook diagnose`

Reconstrói o estado real do projeto com base em evidências: objetivo, o que já
foi concluído, o que está em andamento, pendências, bloqueios e divergências,
terminando com uma próxima etapa justificada.

## Quando usar

- Ao assumir um projeto ou retomá-lo depois de um tempo.
- Quando não está claro o que já foi entregue e o que falta.
- Antes de planejar, para saber de onde o projeto realmente parte.

## Altera alguma coisa?

Não. É somente leitura e não decide direção de produto. A forma padrão é
dirigida: lê README e índices de documentação, branch, status e último commit,
metadados de issues abertas, PRs abertos, branches e milestones, e aprofunda no
máximo três artefatos relevantes. Não consulta issues fechadas nem o Project
inteiro por padrão. A saída também informa as limitações das fontes.

## Sintaxe

```text
$yabook diagnose [full]
```

- `diagnose`: diagnóstico padrão, enxuto e limitado.
- `diagnose full`: auditoria ampla, pesada, só quando pedida; delimite
  repositório, período ou versão.
- `diagnóstico` é alias de `diagnose`.

## Exemplos

```text
$yabook diagnose
$yabook diagnose full
$yabook diagnose & plan next
```

- Mostra o estado atual do projeto e uma próxima etapa recomendada.
- Faz uma auditoria completa, com coleta em lotes filtrados e resumidos.
- Diagnostica e, em seguida, recomenda a ação que mais desbloqueia o trabalho.

## Relacionados

- `status`: resumo rápido só da branch e das alterações atuais.
- `plan`: depois do diagnóstico, decide o que fazer.
- `discuss`: analisa um tema específico encontrado no diagnóstico.
