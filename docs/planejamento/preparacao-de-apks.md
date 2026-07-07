# Preparação de APKs

## Objetivo

Definir um fluxo reutilizável para preparar e identificar APKs Android antes do
upload manual para o armazenamento corporativo.

O YABook coordena e valida o processo. Cada aplicativo informa apenas como gerar
seu build e onde o artefato é produzido.

## Responsabilidades

### YABook

- `$yabook apk`: apresenta uma prévia somente leitura, sem gerar, copiar ou
  remover APK.
- `$yabook do apk`: valida o contexto, localiza o artefato já gerado, prepara a
  cópia padronizada e limpa cópias antigas da mesma origem.
- Impede sobrescrita silenciosa de um arquivo já preparado.
- Não realiza upload nesta primeira etapa.

### Aplicativo

Cada repositório adotante mantém `.yabook/apk.json`:

```json
{
  "appName": "YApp",
  "artifactPath": "<caminho do APK gerado>"
}
```

- `appName`: nome público usado no arquivo e no destino lógico.
- `artifactPath`: caminho do artefato esperado já gerado antes do comando.

Comandos, caminhos e particularidades reais permanecem no repositório do
aplicativo.

### Ambiente local

O alias `geraapk` não recebe parâmetros. Ele copia somente o APK já preparado
pelo YABook para o destino corporativo configurado localmente.

Credenciais, montagem de rede e caminhos internos não pertencem ao YABook nem à
configuração versionada do aplicativo.

## Nomes dos artefatos

O nome deve identificar o aplicativo e a origem do build:

| Origem | Nome |
| --- | --- |
| Issue | `YApp-<numero>-<sequencial>.apk` |
| `dev` | `YApp-dev-v<versao-sem-pontos>-<sequencial>.apk` |
| Release | `YApp-v<versao-sem-pontos>.apk` |

Regras:

- issue e `dev` usam sequencial para facilitar identificação manual no destino
  corporativo;
- `dev` e release usam a versão do aplicativo sem pontos: `4.0.3.0` vira
  `v4030`;
- issue e `dev` continuam informando o commit curto do código que gerou o
  artefato na saída do YABook, mas ele não entra no nome público;
- release usa a versão aprovada;
- builds em outras branches devem ser bloqueados ou tratados por uma regra
  futura explicitamente aprovada.

## Destino lógico

O alias local organiza os arquivos preparados em:

```text
apks_comercial/
└── YApp/
    ├── issues/
    ├── dev/
    └── releases/
```

O caminho físico desse destino é configuração local e não deve ser versionado.

## Validações

Antes de preparar o artefato, `$yabook do apk` deve:

1. confirmar que `.yabook/apk.json` existe e possui os dois campos obrigatórios;
2. identificar se a branch representa issue, `dev` ou release;
3. bloquear worktree com alterações que tornem a cópia não rastreável;
4. confirmar que o artefato esperado já existe;
5. montar o nome correspondente à origem e ao próximo sequencial aplicável;
6. impedir sobrescrita sem autorização explícita;
7. copiar o artefato preparado e validar o hash;
8. remover cópias antigas da mesma origem, preservando `appdebug.apk`;
9. informar o arquivo preparado, o commit curto usado como evidência técnica e
   o destino esperado para o alias local.

Antes disso, `$yabook apk` deve apresentar a mesma validação em modo somente
leitura, informando origem, artefato esperado e nome final sem copiar nem
remover arquivos.

## Fora de escopo

- Implementar os comandos nesta etapa de planejamento.
- Configurar um aplicativo real.
- Versionar caminhos internos, credenciais ou código sensível.
- Fazer upload automático.
- Distribuir ou publicar APKs em lojas.
