# `$yabook apk`

Prepara um APK Android com nome rastreável a partir de um build que você já
gerou. `apk` mostra a prévia; `do apk` faz a cópia padronizada.

## Quando usar

- Você gerou o APK e precisa de uma cópia com nome que identifique a origem.
- Quer conferir antes que nome e caminho o APK preparado terá.

## Altera alguma coisa?

`$yabook apk` é somente leitura: valida o contexto e mostra aplicativo, origem,
artefato esperado, nome e caminho finais e bloqueios. `$yabook do apk` copia o
artefato para o nome padronizado no mesmo diretório, confere o hash e remove
cópias preparadas antigas da mesma origem, preservando o original e o
`appdebug.apk`. Nenhum dos dois faz build, commit, push ou upload.

Exige `.yabook/apk.json` com `appName` e `artifactPath` (caminho relativo ao
repositório) e worktree limpo.

## Sintaxe

```text
$yabook apk
$yabook do apk
```

- Branch de issue `numero-descricao`: `<app>-<numero>-<sequencial>.apk`.
- Branch `dev`: `<app>-dev-v<versao-sem-pontos>-<sequencial>.apk`.
- Branch `release/x.y.z`: `<app>-v<versao-sem-pontos>.apk`.
- `main` e branches não reconhecidas são bloqueadas.

## Exemplos

```text
$yabook apk
$yabook do apk
```

- `apk`: na branch `42-ajustar-login`, mostra o nome esperado, como `YApp-42-1.apk`.
- `do apk`: depois do build, cria a cópia e informa o caminho final e o commit curto de origem.

## Relacionados

- `configure`: registrar o fluxo de APK do projeto.
- `do`: entender o que muda ao executar.
- `release`: preparar a versão que dará nome ao APK de release.
