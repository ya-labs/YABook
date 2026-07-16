# Experiência de leitura do YABook Desktop

## Objetivo

Definir como a pessoa descobre, navega, lê e retoma documentos no MVP do
YABook Desktop, mantendo a estrutura real dos repositórios e sem introduzir
edição de Markdown.

## Estrutura de navegação

O aplicativo organiza a biblioteca sem exigir que todos os projetos pertençam a
uma organização.

```text
Biblioteca
├── Favoritos
├── Recentes
├── Organizações
│   └── Organização
│       ├── Acesso rápido ao handbook
│       └── Projetos
│           └── Raízes documentais
│               └── Árvore de pastas e documentos
└── Projetos avulsos
    └── Raízes documentais
        └── Árvore de pastas e documentos
```

Ao abrir um projeto, suas raízes aparecem como primeiro nível da navegação. A
árvore de cada raiz preserva as pastas e os documentos descobertos, incluindo
níveis como `planejamento/sessoes/`.

O handbook não ocupa um painel permanente. Quando o projeto pertence a uma
organização, a pessoa pode abri-lo por um atalho visível e retornar ao projeto
anterior sem perder o contexto de leitura.

## Fluxos principais

### Cadastrar e abrir um projeto

1. A pessoa seleciona manualmente um repositório ou diretório local.
2. O aplicativo procura `README.md` e `docs/` e apresenta as raízes
   encontradas.
3. A pessoa confirma as raízes ou adiciona outras pastas documentais.
4. O projeto fica disponível na organização escolhida ou em projetos avulsos.
5. Nas próximas aberturas, o aplicativo restaura o último projeto, raiz e
   documento quando eles ainda existirem.

O cadastro não cria `.yabook/config.json` automaticamente. A organização só se
torna compartilhada quando a pessoa escolhe salvá-la como padrão do projeto.

### Navegar pela documentação

1. A pessoa seleciona uma organização, um projeto avulso ou um item de recente.
2. Escolhe uma raiz documental na árvore do projeto.
3. Expande pastas até encontrar o documento desejado.
4. O leitor mostra o documento, seus breadcrumbs e o índice de títulos.
5. Os controles de voltar e avançar, sempre visíveis durante a leitura,
   percorrem o histórico dos documentos visitados.

Os controles de voltar e avançar podem mudar o contexto entre projetos. Ao
retornar para um documento de outro projeto, o aplicativo abre esse projeto e
restaura a raiz e o documento correspondentes. Se o destino não estiver mais
disponível, informa o problema sem apagar o restante do histórico.

Os breadcrumbs representam projeto, raiz, pastas e documento atual. O índice do
documento usa seus títulos Markdown e leva diretamente à seção escolhida.

### Ler um documento

O leitor do MVP deve oferecer:

- GitHub Flavored Markdown;
- tabelas, listas de tarefas e blocos de código;
- destaque de sintaxe e cópia de blocos de código;
- imagens locais dentro do projeto;
- links relativos entre documentos conhecidos;
- índice de títulos e breadcrumbs;
- tema compatível com a preferência da pessoa ou do sistema.

Diagramas Mermaid, edição e preview de edição permanecem fora do MVP.

### Seguir links

- Um link relativo para um documento dentro do projeto abre o destino no
  YABook Desktop.
- Um link relativo que aponta para arquivo não Markdown pode ser aberto pela
  aplicação externa apropriada, mediante ação explícita da pessoa.
- Um link web abre no navegador padrão.
- Um link que tente sair do projeto não é seguido automaticamente; o aplicativo
  informa que o destino está fora da fonte cadastrada.
- Link quebrado permanece visível como erro de navegação, sem interromper a
  leitura do documento atual.

### Pesquisar no projeto atual

1. A pessoa informa uma busca enquanto está em um projeto.
2. O aplicativo procura em nome de arquivo, título, cabeçalhos e conteúdo
   textual das raízes ativas do projeto.
3. Cada resultado apresenta título, raiz, caminho relativo e trecho encontrado.
4. Ao selecionar o resultado, o leitor abre o documento e posiciona a leitura
   na seção ou ocorrência disponível.

A busca global entre todos os projetos não entra no MVP. A busca não depende de
internet nem envia conteúdo para serviços externos.

### Retomar documentos

- **Favoritos** são documentos marcados intencionalmente pela pessoa e ficam
  disponíveis em uma seção própria.
- **Histórico** registra a sequência de documentos abertos para navegação de
  volta e avanço. Seus controles ficam disponíveis no leitor e representam a
  sequência exata de navegação da sessão.
- **Recentes** mostra documentos e projetos acessados recentemente para retorno
  rápido entre sessões. A seção permanece acessível durante a leitura, mas não
  altera a sequência dos controles de voltar e avançar.

Esses recursos armazenam referências locais, nunca cópias do conteúdo. Quando
um arquivo deixa de existir, o item permanece identificável e informa que o
destino precisa ser localizado novamente ou removido da lista.

### Abrir fora do aplicativo

O leitor oferece ações explícitas para:

- abrir o documento no VS Code;
- revelar o documento ou a pasta no sistema operacional;
- copiar o caminho local do documento.

Se o VS Code não estiver disponível, o aplicativo informa a falha e preserva a
leitura atual. Ele não altera o conteúdo para tentar abrir o arquivo.

### Refletir alterações externas

Quando documentos ou a configuração forem alterados fora do YABook Desktop, o
aplicativo deve atualizar a árvore e o leitor.

- Se o documento aberto mudar, o conteúdo é recarregado e a pessoa recebe uma
  indicação discreta da atualização.
- Se o documento aberto for removido, o leitor mantém uma mensagem clara e
  oferece retorno à árvore.
- Se uma raiz deixar de existir, ela é marcada como indisponível sem remover o
  cadastro local automaticamente.
- Se `.yabook/config.json` mudar durante uma personalização local, a pessoa
  escolhe entre recarregar a versão externa ou manter o rascunho para revisão.

## Estados importantes

| Situação | Comportamento esperado |
| --- | --- |
| Projeto sem Markdown | Informar que não há documentação descoberta e oferecer seleção de raízes. |
| Raiz vazia | Manter a raiz visível e explicar que não há documentos Markdown. |
| Documento não encontrado | Informar o caminho ausente e permitir voltar à árvore. |
| Configuração inválida | Exibir o problema e usar descoberta local sem sobrescrever o arquivo. |
| Projeto inacessível | Manter o cadastro, sinalizar indisponibilidade e permitir localizar outro caminho. |
| Resultado sem ocorrência | Informar que a busca não encontrou documentos no projeto atual. |

## Limites desta etapa

Esta etapa não define:

- wireframes, componentes, atalhos de teclado ou biblioteca visual;
- algoritmo, índice ou tempo de atualização da busca;
- integração técnica com VS Code, navegador ou explorador de arquivos;
- monitoramento de filesystem e tratamento de permissões;
- edição de Markdown, busca global, Mermaid ou integrações com YAHub, YAGit e
  YABook Skill.

Essas decisões serão tratadas pela arquitetura e pelas issues de implementação
posteriores.
