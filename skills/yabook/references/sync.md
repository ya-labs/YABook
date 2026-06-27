# Sincronização da skill YABook

Use esta referência para `$yabook sync` e `$yabook do sync`.

## Objetivo

Comparar ou sincronizar a skill instalada no diretório de skills do agente com
`skills/yabook/` da fonte oficial, sem alterar o checkout de origem.

## Comandos

```text
$yabook sync
$yabook sync local
$yabook sync remote
$yabook do sync
$yabook do sync local
$yabook do sync remote
```

- `sync`: somente compara e relata diferenças.
- `do sync`: aplica a sincronização e valida o resultado.
- Sem modo explícito, prefira `local` quando uma origem local válida for
  encontrada; caso contrário, use `remote`.

## Descoberta da origem local

Procure nesta ordem:

1. repositório atual, quando o remote corresponder a `ya-labs/YABook`;
2. caminho definido em `YABOOK_REPO_PATH`;
3. checkout local já conhecido na conversa.

A origem é válida somente quando contém:

```text
skills/yabook/SKILL.md
```

Confirme também que o frontmatter possui `name: yabook`. Não assuma caminhos
fixos de uma máquina como padrão organizacional.

## Origem remota

Use o repositório oficial:

```text
https://github.com/ya-labs/YABook
```

Por padrão, compare com a branch principal remota. Em `sync remote`, consulte
árvore e conteúdo por operações somente leitura, sem clonar, fazer `fetch` ou
alterar refs locais.

Em `do sync remote`, arquivos temporários são permitidos para baixar e validar o
conteúdo antes da instalação. Não execute `pull` no checkout local.

## Destino

Resolva o diretório de skills do agente nesta ordem:

1. `$CODEX_HOME/skills/yabook`, quando `CODEX_HOME` estiver definido;
2. `~/.codex/skills/yabook`.

Se a instalação não existir, relate isso em `sync` e trate como instalação nova
em `do sync`.

## Comparação

Compare recursivamente todos os arquivos da skill:

- normalize `CRLF` e `LF` antes de comparar arquivos textuais;
- compare arquivos binários por bytes;
- ignore caches temporários, `__pycache__`, `.DS_Store` e arquivos de sistema;
- liste arquivos alterados, ausentes no destino e excedentes no destino;
- informe origem, destino e modo utilizado;
- não exponha conteúdo sensível nem imprima arquivos inteiros.

Resultado possível:

- `Sincronizada`;
- `Desatualizada`;
- `Não instalada`;
- `Origem indisponível`;
- `Validação falhou`.

## `$yabook sync`

Não altere arquivos, Git ou GitHub. Retorne:

- origem utilizada;
- destino detectado;
- estado da sincronização;
- resumo das diferenças;
- comando exato para corrigir, quando necessário.

## `$yabook do sync`

1. Resolva e valide a origem.
2. Compare antes de escrever.
3. Se já estiver sincronizada, não reescreva arquivos.
4. Prepare uma cópia temporária completa.
5. Valide a cópia com o validador de skills disponível.
6. Substitua somente o diretório instalado `yabook`.
7. Remova arquivos excedentes do destino que não existam mais na origem.
8. Compare novamente origem e destino.
9. Valide a instalação final.
10. Informe arquivos alterados e resultado.

Não modifique a origem, não execute commit, push, pull ou merge e não altere
outras skills.

Se a validação prévia falhar, não toque na instalação atual. Se a instalação
final divergir da origem, informe falha e preserve evidências para recuperação.

## Segurança

`$yabook bypass` não substitui `$yabook do sync`. A sincronização instalada é uma
ação da gramática YABook e sempre exige `do`.
