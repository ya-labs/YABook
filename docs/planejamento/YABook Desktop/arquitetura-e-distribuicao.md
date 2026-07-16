# Arquitetura e distribuição do YABook Desktop

## Objetivo

Definir a arquitetura técnica inicial e a distribuição do MVP sem antecipar o
scaffold do aplicativo, bibliotecas de interface ou detalhes de implementação
que pertençam às issues de desenvolvimento.

## Decisões do MVP

| Decisão | Direção adotada |
| --- | --- |
| Plataforma | Aplicativo desktop com Tauri, React e TypeScript. |
| Núcleo local | Rust no processo Tauri para acesso ao sistema de arquivos e persistência. |
| Interface | React e TypeScript para biblioteca, árvore documental, leitor e personalização. |
| Conteúdo | Arquivos Markdown permanecem nos repositórios de origem. |
| Estado pessoal | Banco local do aplicativo, fora dos repositórios e não versionado. |
| Organização compartilhada | Apenas `.yabook/config.json`, gravado mediante confirmação explícita. |
| Plataformas iniciais | Windows 11 x64 e Linux Mint 21.3 Cinnamon x64. |
| Pacotes de instalação | NSIS no Windows e AppImage no Linux. |

Tauri foi escolhido para oferecer uma aplicação leve, com acesso nativo aos
arquivos locais e uma interface web moderna, sem exigir que o MVP execute um
servidor local ou dependa de serviços externos.

## Visão de componentes

```text
Interface React/TypeScript
├── Biblioteca e contexto de projeto
├── Navegação, histórico, recentes e favoritos
├── Leitor Markdown e busca do projeto atual
└── Personalização documental
        │ comandos tipados
        ▼
Núcleo Tauri/Rust
├── Catálogo local e preferências pessoais
├── Descoberta, leitura e monitoramento de fontes locais
├── Validação e gravação explícita de .yabook/config.json
├── Índice de busca por projeto
└── Ações no sistema operacional
        │
        ▼
Sistema de arquivos
├── Repositórios e documentos Markdown
├── .yabook/config.json opcional
└── Diretório de dados do aplicativo
```

A interface não acessa caminhos arbitrários diretamente. Ela solicita ações ao
núcleo, que valida o projeto cadastrado, a raiz documental e o destino antes de
ler, indexar, revelar ou abrir um arquivo externamente.

## Fronteiras de dados

### Repositórios cadastrados

O aplicativo lê Markdown, imagens locais e configuração somente dentro das
fontes cadastradas. Arquivos Markdown continuam sendo editados por ferramentas
externas e não são copiados para o banco local.

`.yabook/config.json` é a única escrita do MVP dentro de um repositório. Sua
criação ou atualização exige prévia da alteração, validação e confirmação da
pessoa.

### Diretório de dados do aplicativo

O aplicativo mantém, em diretório próprio do sistema operacional, o catálogo de
fontes, organizações, projetos avulsos, preferências, favoritos, histórico,
recentes e rascunhos de personalização. Esses dados são particulares da pessoa
e não integram o Git do projeto.

O formato inicial será um banco SQLite local. Ele permite persistir o estado
entre sessões e manter um índice de busca por projeto sem criar arquivos dentro
das fontes documentais.

### Índice de busca

O índice é persistente no banco local, mas sempre reconstruível a partir dos
documentos Markdown e da configuração efetiva. Ele armazena referências e
texto necessário à busca, nunca se torna uma fonte de verdade dos documentos.

Ao cadastrar uma fonte, o aplicativo cria ou atualiza seu índice. Alterações
externas em documento, raiz ou configuração invalidam apenas o trecho afetado
e atualizam a árvore, o leitor e os resultados do projeto. Se o índice estiver
ausente, inválido ou desatualizado, o aplicativo o reconstrói localmente sem
alterar o repositório.

## Contratos entre interface e núcleo

O núcleo deve expor comandos tipados para que a interface não conheça detalhes
do sistema operacional ou do armazenamento. Os grupos mínimos são:

- cadastrar, localizar, abrir e remover uma fonte da biblioteca local;
- descobrir raízes, montar a árvore e ler um documento permitido;
- pesquisar somente nas raízes ativas do projeto atual;
- registrar e consultar favoritos, recentes, histórico e contexto de leitura;
- carregar, validar, pré-visualizar e salvar `.yabook/config.json`;
- observar alterações externas e informar estados de indisponibilidade;
- abrir no VS Code, revelar no sistema e copiar caminhos por ação explícita.

Os formatos concretos dos comandos, tabelas, consultas e eventos serão
definidos nas issues de scaffold, persistência, leitura e busca.

## Segurança e disponibilidade local

- Caminhos recebidos da interface devem ser canônicos e permanecer dentro da
  fonte cadastrada ou de uma raiz documental válida.
- Links para fora do projeto e arquivos não Markdown exigem ação explícita,
  conforme a experiência de leitura.
- Falhas de acesso, remoção de arquivo ou raiz indisponível preservam o
  cadastro local e mostram uma recuperação possível; não removem dados em
  silêncio.
- O aplicativo funciona sem internet após a instalação. Não há conta,
  telemetria obrigatória, sincronização, serviço remoto ou dependência de API no
  MVP.

## Distribuição

### Windows

- Público inicial: Windows 11 em 64 bits.
- Entrega: instalador NSIS para arquitetura x64.
- O instalador pode depender de internet para ser obtido; o aplicativo instalado
  deve funcionar offline.

### Linux

- Público inicial: Linux Mint 21.3 Cinnamon em 64 bits.
- Entrega: AppImage para arquitetura x64.
- O pacote deve abrir sem exigir uma instalação de Node.js, Rust ou servidor
  local na máquina da pessoa usuária.

### Fora do escopo desta etapa

Não fazem parte do MVP: autoatualização, publicação em lojas, suporte a outras
arquiteturas ou versões de sistema operacional, assinatura de pacotes, canais
beta e telemetria. Essas decisões dependerão de necessidades reais de
distribuição e segurança após o primeiro uso local.

## Limites desta etapa

Esta arquitetura não cria `apps/`, dependências, banco, comandos Tauri,
componentes React, instaladores ou pipeline de CI. Ela serve como contrato para
ordenar as próximas issues de implementação.
