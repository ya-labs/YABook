# Preparação de APKs

## Objetivo

Definir um fluxo reutilizável para preparar e identificar APKs Android antes do
upload manual para o armazenamento corporativo.

O YABook coordena e valida o processo. Cada aplicativo informa apenas como gerar
seu build e onde o artefato é produzido.

## Responsabilidades

### YABook

- `$yabook apk`: apresenta uma prévia somente leitura, sem gerar ou copiar APK.
- `$yabook do apk`: valida o contexto, executa um build novo, localiza o
  artefato e o prepara com o nome padronizado.
- Impede sobrescrita silenciosa de um arquivo já preparado.
- Não realiza upload nesta primeira etapa.

### Aplicativo

Cada repositório adotante mantém `.yabook/apk.json`:

```json
{
  "appName": "YApp",
  "buildCommand": "<comando de build do aplicativo>",
  "artifactPath": "<caminho do APK gerado>"
}
```

- `appName`: nome público usado no arquivo e no destino lógico.
- `buildCommand`: comando completo para gerar um APK novo.
- `artifactPath`: caminho do artefato esperado após o build.

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
| Issue | `YApp-issue-<numero>-<commit-curto>.apk` |
| `dev` | `YApp-dev-<commit-curto>.apk` |
| Release | `YApp-v<versao>.apk` |

Regras:

- issue e `dev` usam o commit curto do código que gerou o artefato;
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

1. confirmar que `.yabook/apk.json` existe e possui os três campos obrigatórios;
2. identificar se a branch representa issue, `dev` ou release;
3. bloquear worktree com alterações que tornem o build não rastreável;
4. executar o comando de build configurado e exigir sucesso;
5. confirmar que o artefato esperado foi gerado pelo build atual;
6. montar o nome correspondente à origem;
7. impedir sobrescrita sem autorização explícita;
8. informar o arquivo preparado para o alias local.

## Fora de escopo

- Implementar os comandos nesta etapa de planejamento.
- Configurar um aplicativo real.
- Versionar caminhos internos, credenciais ou código sensível.
- Fazer upload automático.
- Distribuir ou publicar APKs em lojas.
