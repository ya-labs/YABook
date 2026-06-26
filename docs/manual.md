# Manual de uso do YABook

Este manual mostra como aplicar o YABook em projetos da YA LABS sem precisar ler todo o handbook antes.

## O que é

O YABook é o padrão organizacional da YA LABS.

Ele não substitui a documentação do projeto. Ele diz como o projeto deve organizar documentação, GitHub, IA e etapas de desenvolvimento.

## Quando usar

Use o YABook quando precisar:

- iniciar um projeto no padrão YA LABS;
- criar ou revisar issue, branch, commit, Pull Request ou release;
- organizar documentação técnica;
- orientar uma IA a seguir padrões da organização;
- conferir se um projeto está consistente com o fluxo de trabalho.

Não use o YABook para documentar fatos específicos de um produto.

## Como aplicar em projeto novo

1. Copie ou adapte os templates necessários.
2. Preencha o `README.md` do projeto com objetivo, stack, setup e links principais.
3. Mantenha um `AGENTS.md` com as instruções para IA naquele projeto.
4. Crie em `docs/` apenas os documentos que fazem sentido para o momento atual.
5. Declare labels, GitHub Project, campo `Size` e responsável padrão por novas issues.
6. Use o padrão de GitHub do YABook para issue, branch, commit, PR e release.

Não crie pastas vazias nem documentos só para "completar a estrutura".

## Uso no dia a dia

Use o fluxo mínimo para mudanças relevantes:

```text
Issue -> Branch -> Commit -> Pull Request -> Merge
```

Para formatos de issue, branch, commit e PR, consulte [Padrões rápidos](padroes-rapidos.md).

Ao criar issues, defina labels e `Size`. `Size` vai de `1` a `5` no GitHub Project e indica o tamanho da tarefa.

Use `main` para documentação inicial, planejamento e prototipagem. Crie `dev` apenas quando começar o desenvolvimento de produto. O fluxo completo de `main`, `dev`, `release/x.y.z` e `archive/dev-x.y.z` fica em [Fluxo de trabalho com GitHub](processos/fluxo-de-trabalho-github.md).

## Uso com IA

Antes de pedir execução para IA, garanta que ela consulte:

1. `AGENTS.md` do projeto.
2. Documentação local relacionada à tarefa.
3. YABook, quando a dúvida for sobre padrão organizacional.

A IA deve avisar antes de criar padrão novo, mudar fluxo de trabalho ou agir fora do YABook.

Quando a IA alterar arquivos em um projeto que segue YABook, ela deve terminar a resposta sugerindo a mensagem de commit para a alteração.

## Uso com a skill YABook

A skill YABook é a interface operacional para IA usar estes padrões no trabalho diário.

Comandos principais:

- `$yabook help`: lista os comandos disponíveis.
- `$yabook load`: carrega os padrões operacionais na conversa atual.
- `$yabook init`: inicializa o padrão YA LABS no repositório atual.
- `$yabook do`: executa os artefatos pedidos, como issue, branch, PR, release ou merge.
- `$yabook issue`: gera título e descrição de issue.
- `$yabook issue classify`: sugere labels e `Size` para a tarefa.
- `$yabook pr`: gera título e descrição de Pull Request.
- `$yabook commit message`: sugere mensagem de commit.
- `$yabook release`: gera descrição de release.
- `$yabook check`: verifica conformidade com o YABook.
- `$yabook docs`: indica onde documentar uma informação.

Use a skill para reduzir orientação repetida. A documentação continua sendo a fonte humana de consulta.

Para entender como a skill funciona por dentro, consulte [Skill YABook](guias/skill-yabook.md).

### Trava para escrita no GitHub

Ao usar a skill, diferencie geração de texto de execução.

Sem `$yabook do`, a IA não deve criar, editar, apagar, publicar, mover em Project, aplicar labels, abrir PR, fazer merge, dar push ou alterar qualquer estado no GitHub.

Comandos como `$yabook issue`, `$yabook pr`, `$yabook branch name`, `$yabook commit message`, `$yabook status`, `$yabook check` e `$yabook review` servem para gerar texto, inspecionar contexto ou apontar conformidade. Eles não executam escrita no GitHub.

Somente `$yabook do` ou alias documentado de `do`, como `$yabook create`, pode executar ações reais no GitHub. Mesmo nesses casos, a IA deve criar somente o que foi pedido e não deve fazer merge sem pedido explícito.

A IA deve seguir o formato documentado do YABook mesmo que o projeto tenha issues ou PRs antigos em outro padrão. Use o formato histórico do projeto apenas quando a pessoa usuária pedir explicitamente.

### Como usar `$yabook load`

Use `$yabook load` no início de uma conversa em que a IA vai trabalhar seguindo o YABook.

O comando carrega um cache operacional para a conversa atual. Esse cache inclui os padrões mais usados de issue, branch, commit, PR, release, labels, `Size` e rastreabilidade.

Durante o load, a IA deve:

1. ler o cache da skill;
2. ler o `AGENTS.md` do repositório atual, se existir;
3. conferir branch e estado do Git;
4. responder com um resumo curto do padrão carregado.

Depois disso, para comandos rotineiros como `$yabook issue`, `$yabook issue classify`, `$yabook branch name`, `$yabook commit message`, `$yabook pr`, `$yabook release` e `$yabook status`, a IA deve usar o cache carregado sem reler os arquivos do YABook toda vez.

Mesmo após o load, a IA ainda deve consultar o repositório quando precisar entender alterações reais, validar GitHub, executar `$yabook do`, revisar conformidade ou resolver dúvida que o cache não cobre.

O load vale apenas para a conversa atual. Em uma nova conversa, execute `$yabook load` novamente.

### Como encadear comandos

Use `&` para pedir vários comandos YABook na mesma mensagem.

Exemplos:

```text
$yabook init & load & commit msg
$yabook load & status & commit message
$yabook load & issue classify & branch name
```

A IA deve executar da esquerda para a direita, reaproveitar o contexto entre os comandos e responder em blocos curtos.

Se `load` aparecer no encadeamento, o cache carregado passa a valer para os comandos seguintes.

### Como usar `$yabook do`

Use `$yabook do` quando quiser que a IA execute uma ação do fluxo, não apenas gere texto.

O comando entende pedidos diretos e pedidos em linguagem natural. Ele deve considerar a conversa atual, a branch, o estado do Git e a issue relacionada quando existir.

Exemplos:

```text
$yabook do issue
$yabook do issue branch pr
$yabook do pr merge
$yabook do uma issue para essa tarefa
$yabook do uma issue, uma branch e um PR para main
$yabook do abra um PR e faça merge
```

Regras principais:

- cria somente o que foi pedido;
- não faz merge sem pedido explícito;
- usa labels e `Size` ao criar ou classificar issues;
- usa branch no formato `numero-descricao-curta`;
- usa o contexto das alterações atuais para PR, commit e release;
- em squash merge, usa o número do PR no assunto e inclui o histórico dos commits da branch contra a branch alvo;
- informa valores manuais quando não conseguir aplicar Project ou `Size` pela ferramenta.

### Como instalar a skill no agente

A skill versionada fica em:

```text
skills/yabook/
```

Para usar em um agente compatível com skills:

1. Copie ou registre a pasta `skills/yabook/` no local de skills do agente.
2. Recarregue o agente ou inicie uma nova conversa para ele reconhecer a skill.
3. Teste com:

```text
$yabook help
```

Se o agente aceitar referência direta por caminho ou repositório, aponte para `skills/yabook/`.

Não copie o YABook inteiro para dentro do agente. A skill deve carregar o comportamento operacional; a documentação continua no repositório para consulta.

## Onde consultar padrões

- [Padrões rápidos](padroes-rapidos.md): issue, branch, commit e PR.
- [Fluxo de trabalho com GitHub](processos/fluxo-de-trabalho-github.md): labels, Project, `main`, `dev`, release e tags.
- [Uso de IA](guias/uso-de-ia.md): contrato operacional para assistentes.
- [Documentação técnica](guias/documentacao-tecnica.md): como organizar documentação de projeto.
- [Template base de projeto](templates/projeto/README.md): estrutura inicial para novos projetos.

## O que não colocar no YABook

Não coloque no YABook:

- endpoints reais de produto;
- arquitetura específica de uma aplicação;
- variáveis de ambiente;
- deploy de projeto específico;
- fluxos de negócio exclusivos;
- roadmap interno de produto.

Essas informações devem ficar no repositório do próprio projeto.

## Checklist de conformidade

Use esta lista ao iniciar um projeto ou revisar um PR:

- O projeto tem `README.md` útil para entrada rápida.
- O projeto tem `AGENTS.md` com regras locais para IA.
- A documentação em `docs/` guarda conhecimento estável, não status operacional.
- Issues, branches, commits e PRs seguem o padrão da YA LABS.
- Exceções ao YABook estão explícitas no projeto.
- Não há documentação genérica, duplicada ou sem uso prático.

## Regra prática

Documento bom ajuda alguém a executar, revisar, decidir ou continuar o trabalho.

Se o texto não ajuda nenhuma dessas ações, corte, funda com outro documento ou não crie.
