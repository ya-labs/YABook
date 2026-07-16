# Sessão de planejamento — YABook Desktop

Data: 2026-07-16
Rastreabilidade: [issue #18](https://github.com/ya-labs/YABook/issues/18) e
[épico #77](https://github.com/ya-labs/YABook/issues/77)

## Contexto

O YABook reúne documentação Markdown que hoje pode ficar distribuída em várias
raízes e níveis de pastas. A consulta manual por explorador de arquivos e
preview do VS Code não preserva bem o contexto entre projetos, organizações e
documentos relacionados.

Esta sessão definiu o MVP do YABook Desktop e preparou sua implementação em
issues pequenas, sem criar o aplicativo nesta etapa.

## Decisões aprovadas

- O aplicativo será local-first e lerá documentos diretamente dos repositórios
  ou diretórios cadastrados.
- Um projeto pode pertencer a uma organização ou ser avulso. O handbook é um
  acesso rápido da organização, sem painel permanente.
- A fonte da verdade continua sendo Markdown; o MVP não edita documentos.
- `.yabook/config.json` é a única escrita compartilhável no repositório e só
  pode ser salva após prévia, validação e confirmação explícita.
- Organização, favoritos, recentes, histórico, preferências e rascunhos ficam
  no estado local do aplicativo.
- O MVP usa Tauri, React e TypeScript, com SQLite local para estado pessoal e
  índice reconstruível de busca.
- As plataformas iniciais são Windows 11 x64 e Linux Mint 21.3 Cinnamon x64,
  distribuídas por NSIS e AppImage, respectivamente.
- O repositório evoluirá para monorepo com `manual/`, `produto/`,
  `apps/desktop/` e `skills/yabook/`, mediante migração documental separada.

## Limites mantidos

- Edição, movimentação e exclusão de Markdown ficam fora do MVP.
- Busca global, IA, Mermaid, integrações operacionais com YAHub, YAGit e a
  YABook Skill, Git e recursos gerenciais não entram nesta fase.
- A issue #18 não cria o scaffold, não move a documentação atual e não publica
  pacotes do aplicativo.

## Próximas entregas planejadas

1. [Migrar a estrutura documental para o monorepo (#78)](https://github.com/ya-labs/YABook/issues/78).
2. [Criar o scaffold do YABook Desktop (#79)](https://github.com/ya-labs/YABook/issues/79).
3. [Implementar biblioteca local e descoberta documental (#80)](https://github.com/ya-labs/YABook/issues/80).
4. [Implementar leitura e navegação documental (#81)](https://github.com/ya-labs/YABook/issues/81).
5. [Implementar personalização documental compartilhável (#82)](https://github.com/ya-labs/YABook/issues/82).
6. [Implementar busca e atualização por alterações externas (#83)](https://github.com/ya-labs/YABook/issues/83).
7. [Empacotar e validar o MVP do YABook Desktop (#84)](https://github.com/ya-labs/YABook/issues/84).

O detalhamento, as dependências e os limites dessas entregas estão em
[roadmap.md](../planejamento/roadmap.md). Esta sessão foi classificada como
registro de planejamento do produto e permanece em `produto/sessoes/`.
