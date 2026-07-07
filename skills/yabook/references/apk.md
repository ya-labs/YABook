# Preparação rastreável de APKs

Use esta referência para `$yabook apk` e `$yabook do apk`.

## Objetivo

Preparar um APK Android com nome rastreável sem incorporar ao YABook comandos,
caminhos ou credenciais específicos de produto.

- `$yabook apk` valida o contexto e apresenta uma prévia somente leitura.
- `$yabook do apk` usa o artefato já gerado e prepara a cópia padronizada.

Nenhum dos comandos realiza upload.

## Configuração do aplicativo

O repositório adotante mantém `.yabook/apk.json`:

```json
{
  "appName": "YApp",
  "artifactPath": "<caminho relativo do APK gerado>"
}
```

Regras:

- os dois campos são obrigatórios, textuais e não podem estar vazios;
- `appName` aceita somente letras, números, ponto, hífen e sublinhado;
- `artifactPath` deve ser relativo à raiz do repositório e permanecer dentro
  dela depois da resolução;
- configuração, logs e respostas nunca devem expor credenciais.

Configuração ausente, JSON inválido, campo inválido, caminho absoluto ou fuga da
raiz interrompem o comando antes da prévia ou da cópia.

## Origem e nome

Leia a branch atual e classifique:

| Origem | Branch | Nome preparado |
| --- | --- | --- |
| Issue | `numero-descricao-curta` | `<app>-<numero>-<sequencial>.apk` |
| Desenvolvimento | `dev` | `<app>-dev-v<versao-sem-pontos>-<sequencial>.apk` |
| Release | `release/x.y.z` ou `release/vx.y.z` | `<app>-v<versao-sem-pontos>.apk` |

Use `git rev-parse --short HEAD` para obter a evidência técnica do build. Em
issue e `dev`, informe esse commit curto na saída do comando, mas não o inclua
no nome público do arquivo.

Para issue e `dev`, calcule o próximo sequencial a partir dos APKs preparados
existentes para a mesma origem lógica. Se não houver preparado anterior, use
`1`. Ainda assim, interrompa se o destino calculado já existir.

Em `dev`, use a versão declarada do aplicativo sem pontos. Se a versão não puder
ser determinada de forma inequívoca, bloqueie a preparação. Em release, remova o
`v` inicial da branch, valide a versão numérica e monte o nome sem pontos.

Bloqueie `main`, branches não reconhecidas e release sem versão numérica.

O APK preparado fica no mesmo diretório de `artifactPath`, preservando o
artefato original do build.

## `$yabook apk`

Não altere arquivos.

1. Resolva o workspace e valide `.git`, remote e `AGENTS.md`.
2. Leia e valide `.yabook/apk.json`.
3. Confirme que o worktree está limpo.
4. Classifique a branch e monte o nome esperado.
5. Resolva `artifactPath` e o destino preparado.
6. Informe:
   - aplicativo;
   - origem detectada;
   - artefato esperado;
   - nome e caminho do APK preparado;
   - aviso de que o comando não copia nem remove arquivos;
   - bloqueios encontrados.

## `$yabook do apk`

Execute sem build automático.

1. Repita todas as validações da prévia.
2. Confirme que `artifactPath` existe como arquivo regular.
3. Interrompa se o destino preparado já existir. Nunca sobrescreva
   silenciosamente.
4. Copie o artefato para o destino padronizado no mesmo diretório.
5. Confirme que origem e cópia têm o mesmo hash.
6. Remova outros APKs já preparados no mesmo diretório que correspondam ao
   mesmo `appName` e à mesma origem lógica, preservando o artefato original e o
   APK padrão `appdebug.apk`.
7. Informe o caminho final, o commit curto de origem quando aplicável, os
   arquivos preparados removidos e lembre que o upload permanece manual.

## Bloqueios

Interrompa sem preparar arquivo quando houver:

- worktree sujo antes da prévia ou da cópia;
- branch incompatível;
- configuração inválida;
- artefato ausente ou fora da raiz;
- destino já existente;
- divergência de hash depois da cópia.

Não execute build, não faça commit, push ou upload automaticamente.
