# Cache compacto do projeto

`.yabook/context-cache.md` é opcional. Ele reduz redescoberta de fatos estáveis;
não substitui documentação, `AGENTS.md`, Git ou GitHub.

## Limites

- máximo de 3.000 caracteres;
- somente identidade, execução, regras locais, arquivos-chave e planejamento
  resumido;
- sem corpos completos, segredos, histórico ou dados operacionais voláteis;
- nenhuma criação, atualização ou sincronização em background.

## Metadados obrigatórios

```md
---
version: 1
branch: main
remote: https://github.com/org/repo.git
reference: <commit ancestral>
rules_sources: AGENTS.md
rules_fingerprint: <sha256>
planning_sources: docs/planejamento
planning_fingerprint: <sha256>
---
```

Separe múltiplas fontes com `;`. Use `-` somente quando a coleção não existir.
Caminhos são relativos à raiz e não podem sair do repositório.

O fingerprint inclui nomes relativos e bytes dos arquivos, em ordem
determinística. Diretórios incluem seus arquivos recursivamente.

## Validade

Use o cache somente quando:

- branch e remote coincidirem;
- `reference` for ancestral do `HEAD`;
- fingerprints de regras e planejamento coincidirem;
- tamanho e metadados forem válidos.

Mudança de branch, remote, fonte de regras ou planejamento invalida o cache.
Mudança em arquivo não observado não invalida por si só.

Valide com:

```text
python skills/yabook/scripts/check_context_cache.py <raiz>
```

Use `--fingerprints` para calcular os valores atuais das fontes declaradas.

Cache ausente ou inválido não bloqueia a rota: ignore-o e consulte as fontes
reais necessárias. Para decisão crítica, conflito ou risco, valide sempre na
fonte real. Remover o arquivo restaura o fluxo normal.
