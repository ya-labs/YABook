# Cenários de preparação de APKs

## Prévia

```text
$yabook apk
```

Confirme que:

- lê `.yabook/apk.json`;
- não cria, copia nem remove arquivos;
- informa origem, artefato esperado e nome preparado;
- bloqueia configuração, worktree, branch ou artefato inválidos.

## Execução

```text
$yabook do apk
```

Confirme que:

- exige autorização explícita;
- não executa build novo;
- copia o artefato para um nome rastreável no mesmo diretório;
- compara os hashes da origem e da cópia;
- remove cópias preparadas antigas da mesma origem;
- bloqueia sobrescrita;
- não faz upload, commit ou push.

## Nomes

| Branch | Nome esperado |
| --- | --- |
| `37-implementa-preparacao-apks` | `YApp-37-<commit-curto>.apk` |
| `dev` | `YApp-dev-<commit-curto>.apk` |
| `release/1.2.3` | `YApp-v1.2.3.apk` |
