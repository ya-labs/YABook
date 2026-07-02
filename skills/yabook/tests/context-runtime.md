# Cenários de execução econômica

Registre as fontes e operações realmente usadas ao revisar estes cenários.

| Cenário | Referências máximas | Inspeções | Ampliação permitida |
| --- | ---: | ---: | --- |
| `help` geral | 1 | 0 | tópico solicitado |
| artefato textual com contexto completo | 1 | 0 | requisito ausente |
| `plan start` delimitado | 1 | 0 | documento equivalente |
| `dev` com issue e branch prontas | 2 | 1 inicial + 1 final | erro, risco ou evidência ausente |
| `do pr` | 4 | 1 inicial + validações remotas | checks, conflito ou proteção |

Em todos os cenários:

- limite a saída de cada comando ao trecho necessário;
- reutilize workspace, issue, branch e decisões ainda válidos;
- registre a justificativa ao ultrapassar a coluna prevista;
- não consulte `contexto.md` durante uma rota explícita.
