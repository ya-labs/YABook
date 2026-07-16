# Configuração documental do YABook Desktop

## Objetivo

Definir o contrato inicial de `.yabook/config.json` e separar a organização
compartilhada da documentação do estado particular mantido pelo aplicativo.

O arquivo é opcional. Projetos sem configuração continuam utilizáveis por
descoberta automática, enquanto projetos configurados podem compartilhar nomes,
raízes e ordem de navegação entre as pessoas que usam o mesmo repositório.

## Camadas de persistência

| Camada | Responsabilidade | Não armazena |
| --- | --- | --- |
| `.yabook/config.json` | Organização compartilhada do projeto | Caminhos absolutos, favoritos, histórico e conteúdo de documentos |
| Biblioteca local do aplicativo | Catálogo de fontes locais e preferências pessoais | Cópias dos documentos ou regras compartilhadas do projeto |

### Configuração compartilhada

O arquivo `.yabook/config.json` pode registrar:

- identificador e nome de exibição do projeto;
- raízes documentais e seus documentos iniciais;
- nomes de exibição e ordem de raízes, pastas e documentos;
- documentos ou pastas ocultos da navegação.

O arquivo não registra caminhos absolutos, organizações, credenciais, conteúdo
de documentos, favoritos, histórico ou documentos recentes.

### Estado local

O aplicativo mantém localmente:

- caminhos canônicos de repositórios ou diretórios cadastrados;
- organizações, seus projetos associados e a raiz usada como handbook;
- projetos avulsos;
- favoritos, histórico e documentos recentes;
- último projeto, raiz e documento abertos;
- preferências de aparência e janela;
- rascunhos de personalização ainda não salvos no repositório.

O formato de armazenamento local será definido na etapa de arquitetura. Ele não
precisa ser versionado pelo Git nem ficar visível para outras pessoas.

## Descoberta sem configuração

Quando `.yabook/config.json` não existir, o aplicativo deve:

1. cadastrar a fonte local selecionada pela pessoa;
2. procurar um `README.md` na raiz e uma pasta `docs/` quando existirem;
3. permitir selecionar ou adicionar outras raízes documentais;
4. montar uma organização local provisória sem alterar arquivos do projeto.

A pessoa pode usar o projeto apenas com esse estado local ou escolher salvar a
organização como configuração compartilhada.

## Contrato de `.yabook/config.json`

O contrato usa chaves técnicas em inglês para acompanhar os arquivos de
configuração já usados pelo ecossistema YABook. Os rótulos apresentados pelo
aplicativo continuam em português ou no idioma escolhido pela equipe.

```json
{
  "version": 1,
  "project": {
    "id": "yabook",
    "name": "YABook"
  },
  "documentation": {
    "roots": [
      {
        "id": "manual",
        "label": "Handbook",
        "path": "manual",
        "entry": "README.md",
        "order": 10,
        "overrides": [
          {
            "path": "processos",
            "label": "Processos",
            "order": 10
          },
          {
            "path": "processos/fluxo-de-trabalho-github.md",
            "label": "Fluxo de trabalho com GitHub",
            "order": 20
          }
        ]
      },
      {
        "id": "produto",
        "label": "Produto",
        "path": "produto",
        "entry": "README.md",
        "order": 20,
        "overrides": [
          {
            "path": "pesquisas",
            "hidden": true
          }
        ]
      }
    ]
  }
}
```

### Campos

| Campo | Regra |
| --- | --- |
| `version` | Obrigatório. Inicia em `1` e identifica a versão do contrato. |
| `project.id` | Opcional. Identificador estável e compartilhável, sem caminho local. |
| `project.name` | Opcional. Nome de exibição padrão do projeto. |
| `documentation.roots` | Lista de raízes documentais configuradas. |
| `roots[].id` | Obrigatório e único no projeto. |
| `roots[].label` | Opcional. Usa o nome da pasta quando ausente. |
| `roots[].path` | Obrigatório, relativo à raiz do projeto e sem `..`. |
| `roots[].entry` | Opcional, relativo à raiz documental. |
| `roots[].order` | Opcional. Define ordem crescente; ausente usa ordem estável por nome. |
| `roots[].overrides` | Personalizações de pastas ou documentos abaixo da raiz. |
| `overrides[].path` | Obrigatório, relativo à raiz documental. |
| `overrides[].label` | Opcional. Altera apenas o nome exibido. |
| `overrides[].order` | Opcional. Define a posição entre elementos irmãos. |
| `overrides[].hidden` | Opcional. Oculta o elemento; uma pasta oculta também oculta seus descendentes. |

## Regras de validação

Antes de aplicar ou salvar a configuração, o aplicativo deve validar que:

1. o JSON é válido e possui `version` compatível;
2. IDs de raízes são únicos;
3. todos os caminhos são relativos e permanecem dentro do projeto;
4. cada documento inicial existe e pertence à sua raiz;
5. raízes não se sobrepõem;
6. cada `override` aponta para uma pasta ou documento existente abaixo da raiz;
7. não há dois `overrides` para o mesmo caminho dentro da mesma raiz;
8. a ordem só compara elementos irmãos;
9. o arquivo não remove, renomeia ou altera conteúdo Markdown.

Configuração inválida não impede a leitura por descoberta automática. O
aplicativo informa o problema e não sobrescreve o arquivo até que a pessoa o
revise ou restaure uma configuração válida.

## Personalização pela interface

O aplicativo deve permitir, por uma interface própria:

- adicionar, remover e reordenar raízes;
- escolher o documento inicial de cada raiz;
- renomear apenas o rótulo de raízes, pastas e documentos;
- reordenar pastas e documentos entre irmãos;
- ocultar ou reexibir itens da navegação;
- visualizar a diferença antes de salvar;
- descartar o rascunho ou restaurar a descoberta automática.

As alterações começam como rascunho local. A ação **Salvar como padrão do
projeto** valida o resultado, mostra a prévia de `.yabook/config.json` e só
então cria ou atualiza esse arquivo.

O aplicativo não pode gravar a configuração automaticamente ao detectar um
projeto. Se o arquivo for alterado externamente durante a edição, a interface
deve recarregar a versão externa ou pedir que a pessoa escolha qual versão
preservar, sem sobrescrita silenciosa.

## Limites desta etapa

Esta especificação não define:

- classes, tabelas, bibliotecas ou API de armazenamento local;
- componentes, atalhos ou layout da tela de personalização;
- mecanismo de monitoramento do arquivo de configuração;
- migração automática entre versões futuras do schema;
- configuração de organizações em arquivos de projeto.

Organizações permanecem na biblioteca local porque podem associar fontes de
repositórios diferentes e dependem de caminhos existentes na máquina.
