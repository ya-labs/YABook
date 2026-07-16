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

## Resultado da migração documental

A migração foi executada na issue #78, preservando o histórico dos arquivos com
`git mv` e separando conteúdo organizacional de conteúdo específico do produto.

| Categoria | Destino | Decisão aplicada |
| --- | --- | --- |
| Handbook, guias, processos e padrões | `manual/` | Conteúdo reutilizável pela organização. |
| Modelos de projeto | `manual/modelos/` | Modelos reutilizáveis, sem fluxo de negócio próprio. |
| Planejamento do YABook e do Desktop | `produto/planejamento/` | Decisões e capacidades específicas do produto. |
| Sessões de planejamento | `produto/sessoes/` | Registros produzidos pelo comando `plan` para o produto YABook. |
| Repasse histórico da skill | `manual/guias/temporario-repasse-yabook.md` | Mantido como histórico consultável, sem transformá-lo em padrão normativo. |

Os índices de `manual/` e `produto/` substituem a navegação anterior. A
referência a `docs/` foi removida do repositório depois da atualização de links,
instruções e referências específicas da skill.

## Estratégia aplicada

1. A estrutura e os índices de `manual/` e `produto/` foram criados.
2. Handbook e modelos foram movidos para `manual/`.
3. Planejamento e sessões foram movidos para `produto/`.
4. Links, índices, instruções e referências específicas foram atualizados antes
   da remoção do caminho legado.

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
