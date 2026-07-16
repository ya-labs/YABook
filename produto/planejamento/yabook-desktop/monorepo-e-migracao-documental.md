# Monorepo e migração documental do YABook

## Objetivo

Definir a estrutura-alvo do repositório YABook e um caminho de migração que
permita receber o YABook Desktop sem misturar sua implementação com a
reorganização da documentação atual.

## Estrutura-alvo

```text
YABook/
├── .agents/
├── .codex/
├── apps/
│   └── desktop/
├── manual/
│   ├── README.md
│   ├── organizacao/
│   ├── processos/
│   ├── padroes/
│   ├── guias/
│   └── modelos/
├── produto/
│   ├── README.md
│   ├── visao/
│   ├── planejamento/
│   ├── arquitetura/
│   ├── decisoes/
│   ├── pesquisas/
│   └── sessoes/
├── skills/
│   └── yabook/
├── AGENTS.md
└── README.md
```

Os nomes de domínio ficam em português. `apps` e `skills` permanecem em inglês
por serem diretórios técnicos consolidados no ecossistema de desenvolvimento.
Não serão criados `packages/`, `extensions/` ou outros espaços de código antes
de haver uma necessidade concreta.

## Responsabilidade de cada área

| Área | Conteúdo | Não contém |
| --- | --- | --- |
| `manual/` | Conhecimento organizacional reutilizável: processos, padrões, guias e modelos. | Planejamento e decisões específicas do YABook Desktop. |
| `produto/` | Documentação do produto YABook, incluindo visão, planejamento, arquitetura, decisões e pesquisas. | Código do aplicativo ou documentos genéricos da organização. |
| `apps/desktop/` | Código, recursos e configuração de build do aplicativo desktop. | Documentação normativa do produto ou handbook. |
| `skills/yabook/` | Fonte da YABook Skill, referências, scripts e testes próprios. | Estado local do aplicativo ou conteúdo de produto sem relação com a skill. |

O `README.md` da raiz apresenta o repositório e aponta para `manual/`,
`produto/`, `apps/desktop/` quando existir e `skills/yabook/`. Os READMEs de
`manual/` e `produto/` são os índices de suas respectivas áreas.

## Relação com a documentação atual

Hoje o conteúdo se concentra em `docs/`, que combina padrões organizacionais,
planejamento do produto, templates e documentos temporários. A migração deve
classificar cada item antes de movê-lo:

| Origem atual | Destino provável | Critério de classificação |
| --- | --- | --- |
| `docs/guias/`, `docs/processos/`, `docs/padroes-rapidos.md`, `docs/manual.md` | `manual/` | Regra ou orientação reutilizável pela organização. |
| `docs/templates/` | `manual/modelos/` | Modelo reutilizável, sem fluxo de negócio próprio. |
| `docs/planejamento/YABook Desktop/` | `produto/planejamento/yabook-desktop/` | Decisão e planejamento específicos do produto. |
| `docs/sessoes/` | `produto/sessoes/` ou `manual/` | Destino definido pelo tema e pelo público do registro. |
| `docs/temporario-repasse-yabook.md` | Avaliar antes de migrar | Documento temporário não deve ganhar destino permanente sem revisão. |

Itens ambíguos não devem ser movidos por similaridade de nome. A classificação
considera a responsabilidade do conteúdo, e não apenas a pasta em que ele está
hoje.

## Estratégia de migração

### 1. Inventariar e decidir destinos

Criar uma issue exclusiva de migração documental e uma tabela de mapeamento
com origem, destino, responsável, links afetados e decisão para cada item. Esta
etapa não move arquivos.

### 2. Criar a estrutura e os índices

Adicionar os diretórios-alvo e seus READMEs de navegação. Os diretórios antigos
continuam existindo, de modo que links atuais e a YABook Skill permanecem
funcionais durante a transição.

### 3. Migrar o handbook em lotes pequenos

Mover primeiro conteúdos claramente organizacionais para `manual/`, com um
commit por grupo coerente. Após cada lote, atualizar links relativos, índices e
referências da skill que apontem para o caminho alterado.

### 4. Migrar a documentação de produto

Mover a documentação já classificada do YABook para `produto/`, preservando a
separação entre planejamento, arquitetura, decisões, pesquisas e sessões. O
planejamento do Desktop deve manter sua pasta própria enquanto houver vários
documentos relacionados.

### 5. Validar e remover o legado

Antes de remover `docs/`, executar busca por referências aos caminhos antigos,
revisar links Markdown e validar os comandos e testes da YABook Skill. A
remoção só ocorre quando não restarem referências internas ou instruções de uso
dependentes da estrutura antiga.

### 6. Criar o aplicativo em issue independente

Somente após a migração estar estável, uma issue de scaffold cria
`apps/desktop/`. A criação do aplicativo não deve ser bloqueada por documentos
ambíguos; ela depende apenas dos diretórios e contratos de produto que já foram
confirmados.

## Regras de segurança da migração

- Usar `git mv` para preservar a rastreabilidade dos documentos.
- Não combinar reorganização, mudança de conteúdo e scaffold do aplicativo no
  mesmo commit.
- Atualizar links, imagens e instruções no mesmo lote que mover seu destino.
- Manter `skills/yabook/` no caminho atual até uma issue específica comprovar
  que suas referências locais foram atualizadas e validadas.
- Não criar links simbólicos ou cópias permanentes de arquivos apenas para
  preservar caminhos obsoletos.
- Não apagar documentos temporários sem uma decisão explícita sobre seu valor
  histórico ou reaproveitamento.

## Fora do escopo

Esta etapa não move arquivos, não altera a YABook Skill, não cria o scaffold
Tauri e não define pacotes compartilhados. Ela prepara issues pequenas e
reversíveis para realizar essas mudanças posteriormente.
