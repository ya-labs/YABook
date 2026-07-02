# Cenários de preparação de APKs

## Prévia

```text
$yabook apk
```

Confirme que:

- lê `.yabook/apk.json`;
- não executa `buildCommand`;
- não cria ou copia arquivos;
- informa origem, artefato esperado e nome preparado;
- bloqueia configuração, worktree ou branch inválidos.

## Execução

```text
$yabook do apk
```

Confirme que:

- exige autorização explícita;
- executa um build novo na raiz do repositório;
- rejeita artefato antigo já existente;
- copia o artefato para um nome rastreável no mesmo diretório;
- compara os hashes da origem e da cópia;
- bloqueia sobrescrita;
- não faz upload, commit ou push.

## Nomes

| Branch | Nome esperado |
| --- | --- |
| `37-implementa-preparacao-apks` | `YApp-issue-37-<commit-curto>.apk` |
| `dev` | `YApp-dev-<commit-curto>.apk` |
| `release/1.2.3` | `YApp-v1.2.3.apk` |
