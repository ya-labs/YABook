# YABook Desktop — visão e limites do MVP

## Visão

O YABook Desktop será um aplicativo local para organizar, localizar e ler
documentações Markdown sem retirar os arquivos de seus repositórios de origem.

O produto deve tornar a consulta mais rápida e confortável do que navegar pela
árvore de arquivos e abrir manualmente o preview do VS Code. Ele complementa as
ferramentas de desenvolvimento existentes e não substitui o editor, o Git ou o
controle de versão.

## Problema

A documentação da YA LABS e de seus projetos já existe em Markdown, mas sua
consulta depende de conhecer o repositório, a estrutura de pastas e o arquivo
correto. Esse atrito cresce quando:

- um repositório possui mais de uma raiz documental;
- padrões organizacionais e documentos de produto precisam ser consultados em
  conjunto;
- a pessoa alterna entre projetos ou organizações;
- documentos relacionados ficam distribuídos em estruturas diferentes;
- a leitura é interrompida para localizar ou reabrir arquivos no VS Code.

Como consequência, informações úteis ficam difíceis de descobrir e a própria
estrutura da documentação perde valor no uso cotidiano.

## Público inicial

O MVP atenderá:

- pessoas da YA LABS que consultam o handbook e documentações de projetos;
- outras organizações da empresa que seguem o Método YA LABS;
- pessoas que desejam cadastrar repositórios pessoais ou avulsos, sem vínculo
  obrigatório com uma organização.

O MVP não assume distribuição pública, contas ou uma operação SaaS. O foco é
validar o produto no uso local real, sem impedir uma evolução futura para outros
públicos.

## Resultado esperado

Uma pessoa deve conseguir cadastrar uma fonte local, encontrar sua
documentação, organizar diferentes raízes, ler e pesquisar documentos e retomar
o contexto posteriormente sem depender da árvore de arquivos do VS Code.

O MVP será considerado útil quando:

- YABook e YAHub puderem ser cadastrados e consultados pelo aplicativo;
- organizações com handbook e projetos avulsos funcionarem sem fluxos
  separados ou obrigatórios;
- a organização documental puder ser compartilhada sem alterar os arquivos
  Markdown;
- favoritos, histórico e documentos recentes reduzirem a repetição de busca;
- alterações realizadas externamente aparecerem no aplicativo;
- os documentos continuarem acessíveis e editáveis sem o aplicativo;
- o fluxo funcionar no Windows 11 e no Linux Mint 21.3 Cinnamon, ambos em
  64 bits.

O principal indicador qualitativo será:

> Consultar e organizar a documentação pelo YABook Desktop deve ser mais rápido
> e confortável do que usar manualmente o preview de Markdown do VS Code.

## Princípios do MVP

### Local-first

Projetos, configurações e documentos permanecem locais. Depois de instalado, o
uso principal do aplicativo não depende de internet, conta ou serviço externo.

### Markdown como fonte da verdade

O aplicativo lê os documentos existentes. Ele não cria um formato proprietário
nem transforma seu armazenamento em fonte principal do conteúdo.

### Leitura sem edição de conteúdo

O YABook Desktop não edita Markdown no MVP. A edição continua no VS Code ou em
outro editor externo.

O único arquivo do repositório que o aplicativo poderá criar ou alterar será
`.yabook/config.json`, destinado à organização compartilhada da documentação.

### Organização opcional

Um projeto pode pertencer a uma organização ou existir de forma independente.
Organizações podem oferecer acesso rápido a um handbook, mas não são requisito
para cadastrar e consultar um projeto.

### Responsabilidades separadas

- o YABook Handbook mantém padrões e conhecimento organizacional;
- o YABook Desktop organiza e apresenta documentação local;
- a YABook Skill aparece como conteúdo documentado, sem integração operacional
  com o aplicativo no MVP;
- o YAHub continua responsável pela visão gerencial dos projetos;
- possíveis integrações com YAHub, YAGit e agentes ficam para fases futuras.

## Escopo do MVP

- cadastrar repositórios ou diretórios locais manualmente;
- aceitar projetos associados a organizações e projetos avulsos;
- associar um handbook a uma organização;
- reconhecer e organizar múltiplas raízes documentais;
- renderizar GitHub Flavored Markdown, imagens e links relativos;
- navegar e pesquisar no projeto atual;
- manter favoritos, histórico e documentos recentes;
- refletir alterações feitas externamente nos documentos;
- abrir arquivos no VS Code e revelá-los no sistema operacional;
- persistir localmente os projetos e preferências da pessoa;
- compartilhar a organização documental por `.yabook/config.json`;
- distribuir o aplicativo para Windows 11 e Linux Mint 21.3 Cinnamon em
  64 bits.

## Fora do escopo do MVP

- editar, mover, renomear ou excluir documentos Markdown;
- substituir o VS Code ou oferecer um editor de código;
- criar contas, permissões, sincronização em nuvem ou colaboração em tempo real;
- implementar inteligência artificial, busca semântica ou chat;
- oferecer busca global entre todos os projetos;
- renderizar diagramas Mermaid;
- criar templates guiados ou um editor visual;
- gerenciar Git, issues, Pull Requests ou releases;
- exibir métricas, status ou informações gerenciais dos projetos;
- integrar operacionalmente com YABook Skill, YAHub ou YAGit;
- criar extensão para VS Code, protocolo customizado ou API local;
- publicar o produto em lojas ou como serviço SaaS.

## Limite desta fase de planejamento

A issue #18 define o produto e prepara seu desenvolvimento. Ela não implementa
o aplicativo nem realiza a migração física da documentação atual.

A reorganização do repositório, o scaffold do aplicativo e as capacidades do
MVP devem ser executados posteriormente em issues próprias e ordenadas por
dependência.
