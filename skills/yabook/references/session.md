# `$yabook load`

Use este comando para carregar o cache operacional do YABook na conversa atual.

## Objetivo

Reduzir buscas repetidas no repositório durante a mesma conversa.

`$yabook load` não cria memória permanente e não altera arquivos.

## Como executar

Ao receber `$yabook load`:

1. Leia este arquivo por completo. Ele é o cache da sessão.
2. Leia `AGENTS.md` do repositório atual, se existir.
3. Inspecione o estado do Git: `git status --short --branch`, branch atual e `git diff --stat`.
4. Monte a resposta curta para a pessoa usuária.
5. Guarde o cache abaixo como fonte principal até o fim da conversa.

Não releia `github.md` nem `session.md` depois do load para comandos rotineiros listados nesta seção.

## Cache operacional da sessão

Use este bloco como fonte principal após o load.

### Rastreabilidade

```text
Issue -> Branch -> Commit -> Pull Request -> Merge -> Release
```

Regras:

- Não trabalhe duas issues diferentes na mesma branch.
- Issue relevante deve ter Project, labels e `Size` quando o projeto usa YA LABS.
- Use a issue como fonte principal quando ela já tiver contexto suficiente.

### Issue

- Título objetivo, sem prefixo de tipo.
- Labels para tipo e área.
- `Size` no GitHub Project, de `1` a `5`. Nunca é label e não entra no título.

Corpo base:

```md
## Resumo rápido

- Tarefa:
- Entrega esperada:
- Limite:

## Escopo

- 

## Critérios de aceite

- 
```

Use `<details>` apenas quando contexto extra para IA for realmente útil.

### `$yabook issue classify`

Retorne:

- labels de tipo;
- labels de área;
- `Size`;
- justificativa curta;
- nível de confiança;
- sugestão de quebra quando `Size` for `5`.

Escala de `Size`:

| Size | Uso |
| --- | --- |
| `1` | Ajuste rápido, baixo risco e escopo evidente. |
| `2` | Tarefa pequena, poucos arquivos ou pouca incerteza. |
| `3` | Tarefa média, exige implementação ou revisão normal. |
| `4` | Tarefa grande, envolve várias partes, análise relevante ou coordenação. |
| `5` | Tarefa muito grande, alta incerteza ou candidata a ser quebrada. |

### Branch

Formato YABook:

```text
numero-descricao-curta
```

Exemplo:

```text
17-reestrutura-yabook-para-ia
```

Não use tipo, área, `issue`, `#`, acentos ou espaços.

Base sugerida: `main` ou `dev`, conforme fluxo do projeto.

### Commit

Formato YABook:

```text
tipo: descrição curta
```

Tipos comuns: `feat`, `fix`, `docs`, `chore`, `refactor`.

Mensagem curta, objetiva e descrevendo exatamente a alteração.

### Pull Request

- Título objetivo, sem prefixo de tipo.
- Destino usual: `dev`, salvo regra local diferente.

Corpo base:

```md
## Resumo rápido

- Objetivo:
- Entrega:
- Issue:

Closes #numero

## O que mudou

- 

## Observações

- 

<details>
<summary>Informações para IA</summary>

- Contexto:
- Validações:
- Riscos:

</details>
```

Use `Informações para IA` apenas quando houver contexto útil para revisão ou continuidade.

### Release

Título de PR de release:

```text
Publicar versão x.y.z
```

Corpo base:

```md
## Resumo rápido

- Objetivo: publicar a versão x.y.z.
- Entrega:
- Issue:

## O que mudou

- 

## Validações

- 

## Observações

- 
```

A tag deve apontar para o commit integrado na branch principal.

### Labels base

| Label | Tipo | Uso |
| --- | --- | --- |
| `bug` | Tipo | Algo não funciona como esperado. |
| `feature` | Tipo | Nova entrega funcional. |
| `docs` | Tipo | Documentação, guias, contratos, ADRs ou ajustes textuais. |
| `refactor` | Tipo | Alteração interna sem nova funcionalidade ou correção de bug. |
| `tooling` | Tipo | Scripts, automações e ferramentas de desenvolvimento. |
| `frontend` | Área | Interface, telas e componentes. |
| `backend` | Área | Regras internas, APIs, comandos e integrações. |
| `infra` | Área | Deploy, ambiente, rede e serviços. |
| `ui/ux` | Área | Experiência, layout e critérios visuais. |
| `architecture` | Área | Decisões estruturais. |
| `process` | Área | Fluxo de trabalho e governança. |
| `epic` | Especial | Agrupador macro de capacidade. |

Cada projeto declara apenas as labels que usa.

### Fluxo `main`, `dev` e release

- `main`: branch estável, publicável ou pronta para tag.
- `dev`: ciclo atual de integração, quando o projeto usa esse fluxo.
- `release/x.y.z`: revisão, homologação ou ajuste final antes de `main`.

Se `AGENTS.md` definir outro fluxo, ele prevalece.

## Comandos que usam só o cache após o load

Depois de `$yabook load`, **não releia** `github.md` nem `session.md` para:

- `$yabook issue`
- `$yabook issue title`
- `$yabook issue desc`
- `$yabook issue classify`
- `$yabook branch name`
- `$yabook commit message`
- `$yabook pr`
- `$yabook pr title`
- `$yabook pr desc`
- `$yabook release`
- `$yabook status`

Para esses comandos, use:

1. o cache desta seção;
2. regras locais já lidas de `AGENTS.md` no load;
3. contexto da conversa;
4. estado do Git quando o artefato depender da alteração atual.

Em comandos encadeados com `&`, se um dos trechos for `load`, este cache passa a valer para os trechos seguintes.

Exemplo:

```text
$yabook init & load & commit msg
```

Nesse caso:

1. execute `init`;
2. carregue o cache com `load`;
3. gere `commit msg` usando o cache, regras locais e o diff atual.

## O que ainda exige inspeção após o load

Mesmo com o cache carregado, inspecione:

- `git diff` ou `git diff --stat` para commit, PR e release com base no código atual;
- issue, PR, labels, Project e `Size` reais quando for criar ou validar artefatos no GitHub;
- código e arquivos do projeto quando o pedido depender do conteúdo alterado.

## Quando reler referências mesmo após o load

Consulte documentos ou arquivos do projeto somente quando:

- o pedido for `$yabook init`, `$yabook docs`, `$yabook check` ou `$yabook review`;
- o pedido for `$yabook do` e exigir criação real no GitHub;
- o pedido contrariar o padrão carregado;
- houver dúvida sobre regra local não capturada no load;
- o contexto estiver incompleto;
- a pessoa pedir validação de conformidade.

Mapa de releitura:

| Comando | Referência |
| --- | --- |
| `$yabook init` | `init.md` |
| `$yabook docs` | `documentacao.md` |
| `$yabook check`, `$yabook review` | `github.md`, `documentacao.md`, `ia.md` conforme o artefato |
| `$yabook do` | `commands.md` + estado real do repo/GitHub |
| `$yabook help` | `commands.md` |

## Regras locais

Durante o load, leia `AGENTS.md` e registre na resposta as exceções que prevalecem sobre o YABook genérico.

Exemplos comuns de override:

- formato de branch diferente do padrão `numero-descricao-curta`;
- formato de commit com código de demanda;
- fluxo de merge diferente de `dev` -> `main`;
- tipos de commit específicos do projeto.

Quando houver override local, use o local nos comandos rotineiros sem reler `github.md`.

## Resposta esperada para a pessoa usuária

Responda de forma curta. Não copie este arquivo inteiro na resposta.

Modelo:

```text
YABook carregado para esta conversa.

Padrões principais:
- Issue: título objetivo, labels para tipo/área, Size no Project.
- Size: 1 rápido, 2 pequeno, 3 médio, 4 grande, 5 quebrar em issues menores.
- Branch: numero-descricao-curta.
- Commit: tipo: descrição curta.
- PR: título objetivo; corpo com Resumo rápido, O que mudou, Observações.
- GitHub: issue relevante deve ter Project, labels e Size.
- IA: usar a issue como fonte principal quando suficiente.

Regras locais:
- <resumo curto de AGENTS.md, se existir; senão "nenhuma exceção local encontrada">

Contexto atual:
- Branch: <nome>
- Issue inferida: <numero ou "não identificada">
- Alterações pendentes: <resumo curto ou "nenhuma">
```

Depois disso, use o cache desta sessão antes de consultar novamente o YABook.

## Limite

O contexto carregado vale apenas para a conversa atual.

Em nova conversa, carregue novamente com `$yabook load`.
