# Cenários de preparação de APKs

## Prévia

```text
$yabook apk
```

Confirme que:

- lê `.yabook/apk.json`;
- não cria, copia nem remove arquivos;
- informa origem, artefato esperado e nome preparado;
- informa o commit curto como evidência técnica quando aplicável;
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
- usa o próximo sequencial para issue e `dev`;
- remove cópias preparadas antigas da mesma origem;
- bloqueia sobrescrita;
- não faz upload, commit ou push.

## Nomes

| Branch | Nome esperado |
| --- | --- |
| `37-implementa-preparacao-apks` | `YApp-37-1.apk` |
| `dev` com versão `4.0.3.0` | `YApp-dev-v4030-1.apk` |
| `release/4.0.3.0` | `YApp-v4030.apk` |
