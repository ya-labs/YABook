# Preparação rastreável de APKs

Use esta referência para `$yabook apk` e `$yabook do apk`.

## Objetivo

Preparar um APK Android com nome rastreável sem incorporar ao YABook comandos,
caminhos ou credenciais específicos de produto.

- `$yabook apk` valida o contexto e apresenta uma prévia somente leitura.
- `$yabook do apk` executa um build novo e copia o artefato com o nome
  padronizado.

Nenhum dos comandos realiza upload.

## Configuração do aplicativo

O repositório adotante mantém `.yabook/apk.json`:

```json
{
  "appName": "YApp",
  "buildCommand": "<comando de build do aplicativo>",
  "artifactPath": "<caminho relativo do APK gerado>"
}
```

Regras:

- os três campos são obrigatórios, textuais e não podem estar vazios;
- `appName` aceita somente letras, números, ponto, hífen e sublinhado;
- `artifactPath` deve ser relativo à raiz do repositório e permanecer dentro
  dela depois da resolução;
- `buildCommand` pertence ao aplicativo e só pode ser executado por `do apk`;
- configuração, logs e respostas nunca devem expor credenciais.

Configuração ausente, JSON inválido, campo inválido, caminho absoluto ou fuga da
raiz interrompem o comando antes do build.

## Origem e nome

Leia a branch atual e classifique:

| Origem | Branch | Nome preparado |
| --- | --- | --- |
| Issue | `numero-descricao-curta` | `<app>-issue-<numero>-<commit-curto>.apk` |
| Desenvolvimento | `dev` | `<app>-dev-<commit-curto>.apk` |
| Release | `release/x.y.z` ou `release/vx.y.z` | `<app>-vx.y.z.apk` |

Use `git rev-parse --short HEAD` para o commit curto. Remova o `v` inicial da
branch de release antes de montar o nome para não duplicá-lo.

Bloqueie `main`, branches não reconhecidas e release sem versão numérica.

O APK preparado fica no mesmo diretório de `artifactPath`, preservando o
artefato original do build.

## `$yabook apk`

Não altere arquivos nem execute `buildCommand`.

1. Resolva o workspace e valide `.git`, remote e `AGENTS.md`.
2. Leia e valide `.yabook/apk.json`.
3. Confirme que o worktree está limpo.
4. Classifique a branch e monte o nome esperado.
5. Resolva o artefato de origem e o destino preparado.
6. Informe:
   - aplicativo;
   - origem detectada;
   - comando que seria executado, sem interpolá-lo em outro shell;
   - artefato esperado;
   - nome e caminho do APK preparado;
   - bloqueios encontrados.

A existência do artefato de origem é informativa na prévia. Sua ausência só
impede `do apk` depois do build.

## `$yabook do apk`

Execute somente com autorização explícita.

1. Repita todas as validações da prévia.
2. Interrompa se o destino preparado já existir. Nunca sobrescreva
   silenciosamente.
3. Registre antes do build a existência, data de modificação, tamanho e hash do
   artefato esperado.
4. Registre o instante inicial e execute exatamente `buildCommand` na raiz do
   repositório.
5. Exija código de saída zero.
6. Confirme que `artifactPath` existe, é arquivo regular e foi criado ou
   atualizado pelo build atual. Compare instante, metadados e hash com o estado
   anterior; não aceite apenas um arquivo antigo já presente.
7. Copie o artefato para o destino padronizado no mesmo diretório.
8. Confirme que origem e cópia têm o mesmo hash.
9. Informe o caminho final e lembre que o upload permanece manual.

Se o build modificar arquivos rastreados além do comportamento esperado do
projeto, informe a divergência e não trate o fluxo como concluído.

## Bloqueios

Interrompa sem preparar arquivo quando houver:

- worktree sujo antes do build;
- branch incompatível;
- configuração inválida;
- falha no comando de build;
- artefato ausente, antigo ou fora da raiz;
- destino já existente;
- divergência de hash depois da cópia.

Não remova artefatos, reverta o build nem faça commit, push ou upload
automaticamente.
