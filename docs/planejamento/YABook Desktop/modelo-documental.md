# Modelo documental do YABook Desktop

## Objetivo

Definir como o MVP representa organizações, projetos, raízes documentais e
documentos sem exigir que todo projeto pertença a uma organização.

O modelo descreve os conceitos e suas relações. O formato de
`.yabook/config.json`, a persistência local e os componentes da interface serão
detalhados nas etapas seguintes da issue #18.

## Visão geral

O aplicativo mantém uma biblioteca local com organizações e projetos
cadastrados. Organização é um agrupamento opcional; projeto continua sendo a
unidade principal de acesso aos arquivos.

```text
Biblioteca local
├── Organizações
│   └── Organização
│       ├── Handbook -> referência para uma raiz documental
│       └── Projetos
│           └── Projeto
│               └── Raízes documentais
│                   ├── Documentos
│                   └── Pastas documentais
│                       ├── Documentos
│                       └── Pastas documentais
└── Projetos avulsos
    └── Projeto
        └── Raízes documentais
            ├── Documentos
            └── Pastas documentais
                ├── Documentos
                └── Pastas documentais
```

Um projeto sem vínculo organizacional aparece como avulso. Ele possui as mesmas
capacidades documentais de um projeto associado a uma organização.

## Conceitos

### Biblioteca local

É o catálogo mantido pelo aplicativo na máquina da pessoa. Reúne organizações,
projetos cadastrados e seus vínculos sem mover os repositórios de origem.

A biblioteca não é um repositório central nem uma cópia da documentação. Ela
guarda referências para fontes locais e o estado necessário para reabri-las.

### Organização

Agrupa projetos relacionados e fornece acesso rápido a um handbook.

No MVP, uma organização possui:

- identidade e nome de exibição locais;
- uma raiz documental escolhida como handbook;
- zero ou mais projetos associados.

A organização não armazena métricas, equipes, permissões ou estado de
desenvolvimento. Essas responsabilidades permanecem fora do YABook Desktop.

### Projeto

Representa um repositório Git ou diretório local cadastrado pela pessoa.

Um projeto possui:

- uma fonte local identificada por seu caminho canônico na máquina;
- nome de exibição;
- zero ou mais raízes documentais configuradas;
- vínculo opcional com uma organização.

Metadados Git, como remote e branch, podem ajudar na identificação, mas não são
obrigatórios. Diretórios sem Git continuam válidos.

### Handbook

Handbook é um papel atribuído a uma raiz documental dentro de uma organização,
não um tipo diferente de arquivo ou projeto.

Essa decisão permite, por exemplo, usar a raiz `manual/` do próprio repositório
YABook como handbook da YA LABS, enquanto `produto/` e `skills/yabook/` continuam
como outras raízes do mesmo projeto.

A mesma raiz pode ser referenciada como handbook onde isso fizer sentido, sem
duplicar seus documentos.

### Raiz documental

É um diretório selecionado dentro do projeto que delimita uma árvore de
documentos.

Uma raiz possui conceitualmente:

- identificador estável no projeto;
- nome de exibição;
- caminho relativo ao projeto;
- documento inicial opcional;
- ordem de apresentação;
- conjunto de documentos descobertos abaixo do caminho.

Um projeto pode ter várias raízes, como:

```text
YABook
├── manual/
├── produto/
└── skills/yabook/
```

Os nomes apresentados no aplicativo podem ser diferentes dos nomes físicos das
pastas. A personalização não renomeia nem move diretórios.

### Pasta documental

É um diretório localizado abaixo de uma raiz documental. Pastas documentais
preservam a organização física do projeto e podem conter documentos e outras
pastas em qualquer profundidade necessária.

Uma pasta documental não se torna uma nova raiz automaticamente. Ela continua
pertencendo à raiz pela qual foi descoberta, salvo quando for configurada
explicitamente como uma raiz independente.

Por exemplo:

```text
docs/
└── planejamento/
    ├── yabook-desktop.md
    └── sessoes/
        ├── 2026-07-01-preparacao-de-apks.md
        └── 2026-07-04-dashboard-de-contexto.md
```

Nesse caso, `docs/` pode ser a raiz documental, enquanto `planejamento/` e
`sessoes/` são níveis preservados da mesma árvore. O aplicativo não deve
achatar todos os documentos em uma lista única.

### Documento

É um arquivo Markdown descoberto dentro de uma raiz documental.

O documento pode estar diretamente na raiz ou dentro de uma sequência de pastas
documentais. Ele é identificado pela combinação do projeto, da raiz e de seu
caminho relativo completo. O conteúdo permanece no arquivo original e nunca é
copiado para o catálogo do aplicativo como fonte principal.

Nome de exibição, ordem e visibilidade podem ser personalizados sem alterar o
arquivo Markdown.

## Relações

```text
Organização 1 ─── 0..N Projetos
Organização 1 ─── 1 Raiz documental como handbook
Projeto      1 ─── 0..N Raízes documentais
Raiz         1 ─── 0..N Pastas e documentos
Pasta        1 ─── 0..N Pastas e documentos
```

O vínculo com organização não faz parte da identidade do projeto. Remover um
projeto de uma organização apenas o transforma em projeto avulso; seus arquivos,
raízes e personalizações continuam preservados.

## Regras do modelo

1. Organização é opcional para cadastrar e consultar um projeto.
2. Cada organização cadastrada referencia uma raiz documental como handbook.
3. Um projeto pode existir sem Git e sem arquivo de configuração.
4. Toda raiz documental permanece dentro do diretório do projeto.
5. Raízes sobrepostas não podem fazer o mesmo documento aparecer duas vezes no
   mesmo projeto.
6. Pastas abaixo de uma raiz preservam sua hierarquia e não são achatadas na
   navegação.
7. Uma subpasta configurada como raiz independente precisa ser excluída da raiz
   ancestral ou a configuração deve ser bloqueada como sobreposta.
8. Todo documento apresentado pertence a uma raiz conhecida.
9. Caminhos absolutos são estado local e não podem ser versionados no
   repositório.
10. Identificadores, nomes e caminhos relativos compartilháveis poderão ser
   definidos em `.yabook/config.json`.
11. Alterar vínculos, nomes de exibição ou ordem não altera arquivos Markdown.
12. Favoritos, histórico e recentes referenciam documentos existentes; não
    armazenam cópias de seu conteúdo.

## Exemplos

### Organização com handbook

```text
YA LABS
├── Handbook
│   └── YABook / manual
└── Projetos
    ├── YABook
    │   ├── manual
    │   ├── produto
    │   └── skill
    └── YAHub
        └── docs
```

O acesso ao handbook aponta para uma raiz já cadastrada. O projeto YABook não é
duplicado por também fornecer essa raiz.

### Projeto avulso

```text
Projetos avulsos
└── Projeto pessoal
    ├── README
    └── docs
```

O projeto pessoal não precisa criar uma organização artificial e continua
podendo usar múltiplas raízes, busca, favoritos, histórico e recentes.

## Limites desta etapa

Este modelo não define:

- o schema JSON da configuração compartilhada;
- quais dados são gravados no armazenamento local;
- telas, componentes ou comportamento visual;
- algoritmo de descoberta, busca ou monitoramento de arquivos;
- tabelas, classes ou tipos da implementação.

Essas decisões dependem do modelo aqui estabelecido e serão detalhadas nas
próximas etapas da issue #18.
