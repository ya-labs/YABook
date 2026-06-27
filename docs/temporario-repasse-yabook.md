# Roteiro temporário de repasse do YABook

Este documento é temporário. Use para apresentar o YABook ao Marco e validar se uma pessoa nova consegue entender o padrão sem explicação longa.

## Objetivo da apresentação

Mostrar que o YABook é o manual operacional da YA LABS para manter projetos, documentação, GitHub e IA trabalhando no mesmo padrão.

Ao final, o Marco deve entender:

- o que é o YABook;
- quando consultar o YABook;
- o que fica no YABook e o que fica no projeto;
- como funciona o fluxo Issue -> Branch -> Commit -> Pull Request -> Merge;
- como criar ou revisar issues com labels e `Size`;
- como usar a skill `$yabook` para reduzir orientação repetida à IA;
- onde encontrar os padrões sem ler o repositório inteiro.

## O que mudou nesta rodada

- O [README principal](../README.md) virou uma apresentação do YABook: o que ele entrega, para quem serve e como começar.
- O antigo primeiros passos virou [Manual de uso](manual.md), com jornada humana objetiva.
- O manual agora explica melhor o `$yabook do`, incluindo pedidos em linguagem natural.
- Foi criado o [Guia técnico da skill YABook](guias/skill-yabook.md), explicando arquitetura, comandos, limites e manutenção.
- A skill foi criada em `skills/yabook/` com referências curtas para GitHub, documentação, IA, init e sessão.
- O primeiro comando operacional `$yabook` carrega automaticamente o cache da sessão; `$yabook load` serve para atualização manual.
- O comando de ação agora é `$yabook do`, adaptável ao que a pessoa pedir.
- `$yabook create` fica apenas como alias de compatibilidade.
- A skill agora aceita múltiplos comandos na mesma mensagem usando `&`.
- Quando a IA altera arquivos em projeto que segue YABook, ela deve terminar sugerindo mensagem de commit.
- Foi criado o comando `$yabook issue classify` para sugerir labels e `Size`.
- `Size` foi documentado como campo do GitHub Project, não como label.
- PRs agora seguem o mesmo espírito das issues: resumo rápido para humano e informações extras para IA quando necessário.
- A documentação foi reorganizada para evitar repetição: cada assunto deve ter uma fonte principal.

## Preparação

Antes da conversa, deixe aberto:

- [README principal](../README.md);
- [Manual de uso](manual.md);
- [Padrões rápidos](padroes-rapidos.md);
- [Fluxo de trabalho com GitHub](processos/fluxo-de-trabalho-github.md);
- [Guia técnico da skill YABook](guias/skill-yabook.md);
- um projeto real ou repositório de teste.

Se for testar no Codex local, a skill já foi instalada em:

```text
/home/nmachado/.codex/skills/yabook
```

Depois de instalar ou atualizar a skill, reinicie o agente para ela aparecer na lista de skills disponíveis.

## Roteiro sugerido

### 1. Apresentar o YABook pelo README

Abra o [README principal](../README.md) e explique:

> O YABook é o manual operacional da YA LABS. Ele define o padrão reutilizável para documentação, GitHub, uso de IA e condução de projetos.

Reforce:

- o YABook não é documentação de um produto específico;
- cada projeto guarda seus fatos reais;
- o YABook guarda o padrão que todos os projetos devem seguir;
- a ideia é reduzir improviso e retrabalho com IA.

### 2. Mostrar a jornada humana no manual

Abra [Manual de uso](manual.md) e mostre:

- o que é;
- quando usar;
- como aplicar em projeto novo;
- uso no dia a dia;
- uso com IA;
- uso com a skill;
- onde consultar padrões.

Não leia tudo. A ideia é mostrar que o manual responde “por onde começo?”.

### 3. Mostrar os padrões rápidos

Abra [Padrões rápidos](padroes-rapidos.md) e destaque:

- issue tem título objetivo;
- labels indicam tipo e área;
- `Size` indica tamanho no GitHub Project;
- branch usa `numero-descricao-curta`;
- commit usa `tipo: descrição curta`;
- PR tem título objetivo e descrição curta para humano.

Resumo para falar:

> O padrão evita repetir informação. Tipo e área ficam nas labels; número da issue fica na branch; contexto longo vai para seção própria quando ajuda a IA.

### 4. Explicar `Size`

Explique que `Size` é um campo do GitHub Project:

| Size | Significado |
| --- | --- |
| `1` | Ajuste rápido, baixo risco e escopo evidente. |
| `2` | Tarefa pequena, poucos arquivos ou pouca incerteza. |
| `3` | Tarefa média, exige implementação ou revisão normal. |
| `4` | Tarefa grande, envolve várias partes ou análise relevante. |
| `5` | Tarefa muito grande, alta incerteza ou candidata a ser quebrada. |

Regra importante:

> Se a IA sugerir `Size 5`, ela deve sugerir divisão em issues menores.

### 5. Mostrar o fluxo GitHub

Abra [Fluxo de trabalho com GitHub](processos/fluxo-de-trabalho-github.md) e mostre:

- labels oficiais da YA LABS;
- Project e `Size`;
- quando usar `main`;
- quando criar `dev`;
- quando usar `release/x.y.z`;
- quando arquivar `dev` como `archive/dev-x.y.z`.

Mensagem principal:

> `main` é estável. `dev` só aparece quando começa desenvolvimento de produto. `dev` representa um ciclo, não uma branch eterna.

### 6. Apresentar a skill YABook

Explique:

> A documentação é a fonte humana. A skill é a interface operacional para a IA aplicar o padrão sem eu precisar explicar tudo de novo.

Mostre que a skill fica em:

```text
skills/yabook/
```

Mostre também o [Guia técnico da skill YABook](guias/skill-yabook.md) para explicar como ela funciona por dentro.

## Comandos principais para demonstrar

Use estes comandos em um repositório de teste.

### Encadeamento com `&`

Mostre que a skill aceita vários comandos na mesma mensagem.

Exemplos:

```text
$yabook init & load & commit msg
$yabook load & status & commit message
$yabook load & issue classify & branch name
```

Explique:

- os comandos rodam da esquerda para a direita;
- o prefixo `$yabook` só precisa aparecer no início;
- `load` carrega cache para os comandos seguintes;
- a resposta deve vir agrupada por comando;
- se houver alteração de arquivos, a IA deve fechar com `Commit sugerido`.

### `$yabook help`

Mostra a lista curta de comandos.

### `$yabook load`

Carrega o cache operacional do YABook na conversa atual.

Use para reduzir buscas repetidas durante a mesma conversa.

Explique que agora o load:

- lê o cache completo da skill;
- lê o `AGENTS.md` local, quando existir;
- confere branch e estado do Git;
- guarda os padrões principais para comandos rotineiros;
- evita reler `github.md` e `session.md` a cada comando simples.

Depois do load, a IA deve usar o cache para:

- `$yabook issue`;
- `$yabook issue classify`;
- `$yabook branch name`;
- `$yabook commit message`;
- `$yabook pr`;
- `$yabook release`;
- `$yabook status`.

Reforce o limite:

> O load reduz busca repetida, mas não substitui inspeção real do repo. Para diff, GitHub, `$yabook do`, `$yabook check`, `$yabook review` e `$yabook docs`, a IA ainda precisa conferir o contexto.

### `$yabook issue`

Gera título e descrição completa de issue.

Deve ser objetivo e evitar validações genéricas.

### `$yabook issue classify`

Sugere:

- labels;
- `Size`;
- justificativa curta;
- confiança;
- quebra em issues menores quando for `Size 5`.

### `$yabook do`

É o comando adaptável.

Antes de demonstrar, destaque a trava principal:

> Dentro da gramática `$yabook`, somente comandos iniciados por `$yabook do` executam ações. Pedidos normais seguem o fluxo do agente.
> Comandos como `$yabook issue`, `$yabook pr` e `$yabook branch name` apenas geram texto no padrão YABook.

Ele entende pedido direto:

```text
$yabook do issue
$yabook do issue branch pr
$yabook do pr merge
```

E também linguagem natural:

```text
$yabook do uma issue para essa tarefa
$yabook do uma issue, uma branch e um PR para main
$yabook do abra um PR e faça merge
```

Regras para explicar:

- cria somente o que foi pedido;
- entende o contexto da conversa e do Git;
- confere branch, issue e alterações quando necessário;
- não faz merge sem pedido explícito;
- em squash merge, usa o número do PR no assunto e inclui o histórico dos commits da branch contra a branch alvo;
- se não conseguir preencher Project ou `Size`, informa o valor para preenchimento manual.

### `$yabook pr`

Gera título e descrição completa do PR.

Modelo esperado:

- `Resumo rápido`;
- `O que mudou`;
- `Observações`;
- `Informações para IA`, apenas quando houver contexto útil.

### `$yabook commit message`

Sugere mensagem de commit com base no diff atual.

Padrão:

```text
tipo: descrição curta
```

### `$yabook docs`

Indica onde documentar uma informação.

Use para evitar criar documento novo sem necessidade.

## Exercício prático com Marco

Use um projeto real ou repo de teste e peça para ele executar:

1. Abrir `README.md` e `AGENTS.md` do projeto.
2. Identificar se o projeto segue o YABook.
3. Rodar `$yabook load`.
4. Descrever uma pequena melhoria.
5. Rodar `$yabook issue` e observar se a IA usa o cache sem reler o YABook.
6. Rodar `$yabook issue classify`.
7. Rodar `$yabook do issue` e observar se a IA confere GitHub quando necessário.
8. Sugerir branch com `$yabook branch name`.
9. Simular uma alteração pequena.
10. Pedir `$yabook commit message`.
11. Pedir `$yabook pr`.
12. Pedir `$yabook check`.

Se quiser testar o do completo:

```text
$yabook do uma issue, uma branch e um PR para essa melhoria
```

Se quiser testar economia de chamada:

```text
$yabook load & status & commit msg
```

O ponto do teste é observar se a IA cria só o que foi pedido e se aplica labels, Project e `Size` corretamente.

## Perguntas para validar entendimento

- O que o YABook resolve?
- O que fica no YABook e o que fica no projeto?
- Por que issue não precisa de tipo no título?
- Onde entram labels, Project e `Size`?
- Por que a branch começa com número da issue?
- Quando devo criar `dev`?
- Quando uso `release/x.y.z`?
- O que muda quando uso `$yabook load`?
- Quando a IA ainda precisa consultar o repositório mesmo após `$yabook load`?
- O que o `$yabook do` pode criar?
- Como rodar vários comandos YABook em uma única mensagem?
- O que a IA deve sugerir ao final quando altera arquivos?
- Quando a IA deve ler documentação ampla?
- O que fazer se o projeto precisar fugir do padrão?

## Critérios de sucesso

O repasse funcionou se o Marco conseguir:

- explicar o YABook em poucas frases;
- encontrar sozinho o documento certo;
- criar uma issue curta e objetiva;
- classificar labels e `Size`;
- sugerir branch, commit e PR no padrão;
- usar `$yabook do` sem esperar que ele faça etapas não pedidas;
- entender que a skill não substitui leitura do repositório;
- evitar documentação genérica ou duplicada.

## Pontos para observar

Durante o teste, anote:

- onde ele travou;
- se o README vende bem a ideia;
- se o manual responde rápido;
- se `Size` ficou claro;
- se `$yabook do` ficou natural;
- se algum comando ficou ambíguo;
- se a IA insistiu em reler o YABook mesmo após `$yabook load`;
- o que ainda precisou de explicação oral.

## Ajustes depois do teste

Depois do repasse, revisar:

- se o [README principal](../README.md) apresenta bem o YABook;
- se o [Manual de uso](manual.md) está claro para uma pessoa nova;
- se [Padrões rápidos](padroes-rapidos.md) resolve a consulta do dia a dia;
- se o [Guia técnico da skill](guias/skill-yabook.md) explica bem a mecânica;
- se a skill cobre os comandos que o Marco tentou usar;
- se algum trecho do YABook ainda força explicação oral demais.

Este documento pode ser removido ou convertido em guia oficial depois do teste.
