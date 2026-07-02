# Manual de uso do YABook

Este manual mostra como aplicar o YABook em projetos da YA LABS sem precisar ler todo o handbook antes.

## O que é

O YABook é o padrão organizacional da YA LABS.

Ele não substitui a documentação do projeto. Ele diz como o projeto deve organizar documentação, GitHub, IA e etapas de desenvolvimento.

## Quando usar

Use o YABook quando precisar:

- iniciar um projeto no padrão YA LABS;
- diagnosticar o estado real de um projeto;
- planejar a V1 ou versões posteriores;
- discutir mudanças e estruturar roadmap;
- criar ou revisar issue, branch, commit, Pull Request ou release;
- organizar documentação técnica;
- orientar uma IA a seguir padrões da organização;
- conferir se um projeto está consistente com o fluxo de trabalho.

Não use o YABook para documentar fatos específicos de um produto.

## Como aplicar em projeto novo

Use o fluxo:

```text
$yabook init
$yabook do init
$yabook plan start v1
$yabook plan review
$yabook do plan
$yabook plan roadmap
$yabook do plan roadmap
$yabook plan next
```

O primeiro comando de cada par analisa ou propõe. O comando iniciado por
`$yabook do` aplica a proposta aprovada.

Não crie pastas vazias nem documentos só para "completar a estrutura".

O tutorial completo está em
[Criar e expandir projetos com YABook](guias/criar-e-expandir-projetos-com-yabook.md).

## Uso no dia a dia

O fluxo começa quando surge um problema, ajuste ou melhoria nova. Descreva a
necessidade; a IA deve ajudar a transformá-la em uma issue executável antes de
começar a implementação.

```text
Problema, ajuste ou melhoria
-> Issue
-> Branch
-> Implementação
-> Commit
-> Pull Request
-> Merge
```

Para formatos de issue, branch, commit e PR, consulte [Padrões rápidos](padroes-rapidos.md).

Com a skill:

```text
$yabook issue
$yabook do issue
$yabook branch name
$yabook do branch
```

O primeiro comando prepara a issue para revisão. O segundo cria a issue. Depois,
a branch coloca a demanda no fluxo normal de implementação, commit e PR.
Ao executar `$yabook do branch`, a skill usa o vínculo nativo do GitHub para que
a branch apareça na seção Development da issue e confirma o vínculo antes de
informar sucesso. Sem issue inequívoca, a criação é interrompida. Quando a
ferramenta não permitir o vínculo, a skill deve informar a limitação e orientar
o vínculo manual.

Ao criar issues, defina labels e `Size`. `Size` vai de `1` a `5` no GitHub Project e indica o tamanho da tarefa.

Durante documentação inicial, planejamento e prototipagem, crie branches de
issue a partir da `main`. Não altere `main` diretamente sem
`$yabook bypass <ação>`. Crie `dev` apenas quando começar o desenvolvimento de
produto. O fluxo completo de `main`, `dev`, `release/x.y.z` e
`archive/dev-x.y.z` fica em
[Fluxo de trabalho com GitHub](processos/fluxo-de-trabalho-github.md).

## Uso com IA

Antes de pedir execução para IA, garanta que ela consulte:

1. `AGENTS.md` do projeto.
2. Documentação local relacionada à tarefa.
3. YABook, quando a dúvida for sobre padrão organizacional.

A IA deve avisar antes de criar padrão novo, mudar fluxo de trabalho ou agir fora do YABook.

Quando a IA alterar arquivos em um projeto que segue YABook, ela deve terminar a resposta sugerindo a mensagem de commit para a alteração.

## Uso com a YABook Skill

A YABook Skill é o orquestrador inteligente do Método YA LABS. A pessoa define
o projeto e toma as decisões; a skill organiza o caminho, recomenda etapas e
executa somente o que foi autorizado.

### Como usar linguagem natural

Você não precisa conhecer previamente o comando correto:

```text
$yabook desejo planejar a V1 do meu projeto
```

A skill infere `plan start v1`. Quando precisar combinar ou corrigir comandos,
ela informa o roteamento no início. Comandos seguros de leitura avançam até uma
decisão necessária ou escrita.

Se a intenção estiver incompleta, a skill pergunta o que muda materialmente o
caminho. Ela pode sugerir uma opção melhor mesmo quando o comando informado for
válido, mas nunca infere `do`.

Comandos principais:

- `$yabook help`: lista os comandos disponíveis.
- `$yabook load`: atualiza o contexto mínimo quando repositório ou branch mudar.
- `$yabook init`: analisa como inicializar o padrão, sem alterar estado.
- `$yabook diagnose`: reconstrói progresso, bloqueios e próximo passo progressivamente.
- `$yabook diagnose full`: executa uma auditoria explicitamente aprofundada.
- `$yabook discuss`: analisa uma ideia, decisão ou mudança sem alterar estado.
- `$yabook plan`: entrevista, discute, revisa e estrutura versões.
- `$yabook steps`: acompanha uma sequência com checklist durante a conversa.
- `$yabook mode`: define como a IA deve colaborar: estudo, mentoria ou execução.
- `$yabook bypass <ação>`: autoriza uma ação direta fora do fluxo nesta solicitação.
- `$yabook sync`: verifica se a skill instalada está sincronizada com a origem.
- `$yabook apk`: valida o contexto e mostra como o APK será preparado, sem executar build nem alterar arquivos.
- `$yabook do apk`: usa o APK já gerado, cria a cópia rastreável e limpa cópias antigas da mesma origem.
- `$yabook do`: executa a ação pedida, como init, plan, sync, apk, issue, branch, PR, release ou merge.
- `$yabook dev`: prepara, implementa e valida a issue atual.
- `$yabook issue`: gera título e descrição de issue.
- `$yabook issue classify`: sugere labels e `Size` para a tarefa.
- `$yabook pr`: gera título e descrição de Pull Request.
- `$yabook commit message`: sugere mensagem de commit.
- `$yabook release`: gera descrição de release.
- `$yabook check`: verifica conformidade com o YABook.
- `$yabook docs`: indica onde documentar uma informação.

Use a skill para reduzir orientação repetida. A documentação continua sendo a fonte humana de consulta.

### Como preparar um APK

O aplicativo adotante mantém `.yabook/apk.json`:

```json
{
  "appName": "YApp",
  "artifactPath": "<caminho relativo do APK gerado>"
}
```

Confira primeiro a prévia:

```text
$yabook apk
```

Depois de gerar o APK no próprio aplicativo, execute:

```text
$yabook do apk
```

`$yabook apk` não copia nem remove arquivos. `$yabook do apk` valida o
contexto, usa o artefato existente em `artifactPath`, cria a cópia padronizada
no mesmo diretório e remove cópias antigas da mesma origem, preservando o
`appdebug.apk` padrão. Issue e `dev` usam o commit curto no nome; release usa
a versão. Worktree sujo, branch incompatível, configuração inválida, artefato
ausente e sobrescrita são bloqueados.

O upload, o build e os caminhos corporativos permanecem no ambiente local e não
fazem parte do comando.

Para entender como a skill funciona por dentro, consulte [Skill YABook](guias/skill-yabook.md).

### Como acompanhar uma sequência de etapas

Quando a IA recomendar vários passos e você quiser mantê-los visíveis durante a
conversa, use:

```text
$yabook steps start
```

Enquanto houver etapas abertas, a IA repete um checklist compacto no final das
respostas. Conclua uma etapa com `$yabook steps done 1` ou com uma confirmação
inequívoca, como `concluí a primeira etapa`. Use `$yabook steps` para consultar
o estado e `$yabook steps cancel` para encerrar o acompanhamento.

O checklist vale somente para a conversa atual. Ele não executa os passos, não
substitui issues ou milestones e não cria memória permanente.

Enquanto o checklist estiver ativo, a YABook Skill avalia ações executadas fora
da sequência. Ela pode registrar etapas antecipadas, reordenar itens pendentes,
adicionar correções ou exigir nova validação.

A skill explica o recalculado antes de mostrar o checklist atualizado. Etapas
concluídas permanecem no histórico. Alterações de objetivo, escopo ou decisões
continuam dependendo de confirmação.

### Como usar modos de colaboração

Use `mode` quando quiser mudar a postura da IA sem repetir um prompt longo.

```text
$yabook mode: dev
$yabook mode: prod - faça os ajustes no estilo do site
$yabook mode: study - me ensine requisições HTTP no React
```

Os modos são:

| Modo | Objetivo |
| --- | --- |
| `study` | Estudar um tema com explicação progressiva, exemplos e perguntas. |
| `dev` | Desenvolver uma tarefa real com mentoria, mantendo a pessoa no teclado. |
| `prod` | Delegar a execução ao agente. |

Também é possível definir um modo por área do projeto:

```text
$yabook def mode dev for front-end
$yabook def mode prod for estilos do site
```

Modos não alteram permissões. `prod` não substitui `do`, `bypass` nem as travas
de Git/GitHub. `mode: dev` é modo de colaboração e não equivale ao comando
operacional `$yabook dev`.

### Como usar o help

Use o help geral para consultar o índice de comandos:

```text
$yabook help
```

Passe um comando ou família para receber explicação, sintaxe e exemplos:

```text
$yabook help plan
$yabook help sync
$yabook help issue classify
```

Também é possível descrever um objetivo:

```text
$yabook help planejar a V1 do projeto
$yabook help descobrir a próxima etapa
$yabook help preparar uma release
```

Nesse formato, a skill recomenda o menor fluxo, explica por que cada comando
será usado e diferencia análise de execução. O help não carrega o repositório,
não altera estado e não executa a sequência sugerida.

### Trava dos comandos YABook

Ao usar a skill, diferencie geração de texto de execução.

A trava de `do` vale somente quando a pessoa invoca a gramática `$yabook`, com
uma exceção: mutações Git exigem `$yabook do` ou a autorização limitada de
`$yabook dev`.

Pedidos normais em linguagem natural podem autorizar outras alterações, mas não
podem criar ou trocar branch, preparar arquivos, criar commit, alterar histórico
ou interagir com remotes.

Comandos como `$yabook init`, `$yabook diagnose`, `$yabook plan`, `$yabook issue`, `$yabook pr`, `$yabook branch name`, `$yabook commit message`, `$yabook status`, `$yabook check` e `$yabook review` servem para conversar, gerar propostas, inspecionar contexto ou apontar conformidade.

Dentro da gramática YABook, um comando iniciado por `$yabook do`, um alias
documentado como `$yabook create` ou `$yabook dev` dentro de seu escopo pode
executar ações reais.

Sem `do`, a IA pode executar
somente inspeções como `git status`, `git diff`, `git log` e consultas de branch.
Criar ou trocar branch, preparar arquivos, criar commit, usar stash, alterar
histórico, criar tag, buscar, integrar ou enviar alterações exige uma ação
`$yabook do` explícita.

O escopo permanece restrito ao pedido. `$yabook do commit` isolado não autoriza
`push`. `$yabook do pr` pode enviar somente a branch necessária para abrir ou
atualizar o PR, mas não autoriza outras branches, tags ou merge.

### Checkpoint antes de novas alterações

Antes de editar, a IA avalia se o worktree contém um bloco concluído de outra
responsabilidade. Quando as mudanças forem independentes, reversíveis e
estiverem prontas, ela interrompe e propõe um commit separado.

Antes de interromper, a IA deve atualizar status, diff staged e unstaged e
último commit. Se o worktree estiver limpo ou o commit já existir, deve continuar
a solicitação sem exibir um aviso desatualizado.

Nesse contexto:

- `$yabook do` cria o commit, executa os pré-requisitos mínimos já autorizados e
  retoma a solicitação original;
- `$yabook continue` prossegue sem o checkpoint opcional.

Se a nova tarefa pertencer a outra issue ou branch, `continue` não pode ignorar
a separação obrigatória.

### Como usar `$yabook dev`

Use `dev` depois que a demanda estiver registrada:

```text
$yabook dev
```

A skill identifica a issue, prepara e vincula a branch, atualiza o status,
implementa e valida. Sem issue inequívoca, ela interrompe e pede a indicação.
O vínculo da branch é confirmado por leitura na própria issue; publicar uma
branch no remoto, isoladamente, não conta como vínculo concluído.

Para entregar:

```text
$yabook dev & do pr
$yabook dev & do merge
```

O primeiro fluxo cria commits coerentes, envia a branch e abre ou atualiza o PR.
O segundo também valida as condições e faz merge. `dev` sozinho para antes do
commit.

Antes de uma alteração direta em `main`, `dev`, release ou branch incompatível,
a IA deve bloquear a execução. Uma confirmação comum não é suficiente. Para
autorizar a exceção, repita a ação com:

```text
$yabook bypass atualize o README diretamente na main
```

O `bypass` autoriza somente a ação anexada fora do fluxo de issue/branch. Ele não
substitui `do issue`, `do branch`, `do commit`, `do pr`, `do release` ou
`do merge`, nem autoriza merge implicitamente.

A IA deve seguir o formato documentado do YABook mesmo que o projeto tenha issues ou PRs antigos em outro padrão. Use o formato histórico do projeto apenas quando a pessoa usuária pedir explicitamente.

### Como usar `$yabook load`

Você não precisa executar `$yabook load` no início da conversa. A skill identifica
primeiro o comando e carrega somente o contexto necessário para ele.

Use `$yabook load` quando quiser atualizar explicitamente o repositório, branch,
remote, regras locais e resumo do worktree mantidos na conversa. O comando não
antecipa formatos de issue, PR, release ou planejamento.

Durante o carregamento, a IA deve resolver a raiz pelo workspace da IDE e
arquivos ativos, validar `.git`, regras locais e remote, conferir branch e estado
do Git e responder com um resumo curto.

Quando workspace, arquivos ativos, repositório mencionado, contexto, `cwd` ou
remote apontarem para projetos diferentes, a skill não altera arquivos, Git ou
GitHub. Ela informa a divergência e pede confirmação do repositório correto.
O `cwd` é somente um candidato técnico e nunca prevalece sobre evidências claras
do workspace ativo.

Depois disso, cada comando carrega diretamente sua própria referência curta e
reutiliza somente o contexto local ainda válido. A matriz geral é reservada para
ambiguidade, auditoria ou revisão do carregamento. Git e GitHub são consultados
apenas quando o resultado depender do estado atual.

Referências amplas são divididas por capacidade. Por exemplo, uma inspeção Git
não carrega regras de merge, e uma issue não carrega regras de PR ou release.
As validações de orçamento mostram apenas um resumo; use `--verbose` para
detalhar todas as rotas.

O teste estático não representa uma sessão real. Relatórios de execução podem
ser validados separadamente para conferir quantidade de referências, comandos,
caracteres retornados, rodadas e redescobertas desnecessárias.

O contexto vale apenas para a conversa atual.

### Como encadear comandos

Use `&` para pedir vários comandos YABook na mesma mensagem.

Exemplos:

```text
$yabook init & load & commit msg
$yabook load & status & commit message
$yabook load & issue classify & branch name
```

A IA deve executar da esquerda para a direita, reaproveitar o contexto entre os comandos e responder em blocos curtos.

Se `load` aparecer no encadeamento, o contexto mínimo coletado pode ser
reutilizado pelos comandos seguintes.

### Como usar `$yabook do`

Use `$yabook do` quando quiser que a IA execute uma ação do fluxo, não apenas gere texto.

O `:` depois de `do` é opcional:

```text
$yabook do commit pr
$yabook do: commit pr
```

O comando entende pedidos diretos e pedidos em linguagem natural. Ele deve considerar a conversa atual, a branch, o estado do Git e a issue relacionada quando existir.

Exemplos:

```text
$yabook do issue
$yabook do init
$yabook do plan
$yabook do plan roadmap
$yabook do issue branch pr
$yabook do pr merge
$yabook do uma issue para essa tarefa
$yabook do uma issue, uma branch e um PR para main
$yabook do abra um PR e faça merge
```

Regras principais:

- cria somente o que foi pedido;
- cumpre automaticamente os pré-requisitos do objetivo autorizado;
- `do pr` pode criar commits coerentes, enviar a branch e abrir ou atualizar o PR;
- `do merge` pode preparar o PR ausente e integrar após validar as condições;
- consolida planejamento sem commit automático;
- cria somente o próximo bloco de roadmap;
- não faz merge sem pedido explícito;
- usa labels e `Size` ao criar ou classificar issues;
- usa branch no formato `numero-descricao-curta`;
- usa o contexto das alterações atuais para PR, commit e release;
- em squash merge, usa o número do PR no assunto e inclui o histórico dos commits da branch contra a branch alvo;
- informa valores manuais quando não conseguir aplicar Project ou `Size` pela ferramenta.

Para iniciar trabalho novo, descreva primeiro o problema, ajuste ou melhoria.
Use `$yabook issue` para revisar como a demanda será registrada e
`$yabook do issue` para criá-la antes da branch e da implementação.

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

### Como sincronizar a skill

Para verificar sem alterar arquivos:

```text
$yabook sync
$yabook sync local
$yabook sync remote
```

Para sincronizar:

```text
$yabook do sync
$yabook do sync local
$yabook do sync remote
```

O modo `local` usa o checkout YABook atual, `YABOOK_REPO_PATH` ou uma origem
local conhecida. O modo `remote` usa a branch principal do repositório oficial.

A sincronização:

- compara a árvore completa da skill;
- ignora diferenças entre `CRLF` e `LF`;
- valida antes e depois da instalação;
- remove arquivos excedentes somente do destino instalado;
- não executa `pull`, commit, push ou merge;
- não altera o checkout usado como origem.

Sem modo explícito, a skill prefere uma origem local válida e usa o remoto como
fallback.

## Onde consultar padrões

- [Padrões rápidos](padroes-rapidos.md): issue, branch, commit e PR.
- [Fluxo de trabalho com GitHub](processos/fluxo-de-trabalho-github.md): labels, Project, `main`, `dev`, release e tags.
- [Uso de IA](guias/uso-de-ia.md): contrato operacional para assistentes.
- [Criar e expandir projetos com YABook](guias/criar-e-expandir-projetos-com-yabook.md): tutorial de inicialização, diagnóstico e planejamento.
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
