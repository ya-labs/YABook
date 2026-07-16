# Roadmap de capacidades planejadas

Este documento registra a sequência técnica aprovada. O estado operacional de
cada entrega permanece no GitHub.

## Preparação de APKs

### 1. Implementar o contrato no YABook

- Definir a leitura e a validação de `.yabook/apk.json`.
- Implementar a prévia por `$yabook apk`.
- Implementar a preparação por `$yabook do apk`.
- Cobrir nomes de issue, `dev` e release.
- Validar artefato existente, limpeza de cópias antigas e prevenção de sobrescrita.

### 2. Adotar no primeiro aplicativo em outra organização

- Criar `.yabook/apk.json` com os dados do próprio projeto.
- Validar o fluxo em issue, `dev` e release.
- Ajustar o alias local `geraapk` para copiar o artefato preparado sem
  parâmetros.
- Planejar e acompanhar a adoção no repositório e no Project da organização
  responsável pelo aplicativo.

### 3. Avaliar evolução

- Revisar o uso real antes de padronizar novos tipos de branch.
- Avaliar upload automatizado somente depois que o fluxo manual estiver
  validado e houver contrato seguro para credenciais e destino.

Apenas a etapa 1 pertence ao Project do YABook. A etapa 2 deve ser uma issue no
repositório e no Project da organização responsável pelo aplicativo, pois possui
contexto, riscos e validações próprios.

## YABook Desktop

O MVP foi definido na [issue #18](https://github.com/ya-labs/YABook/issues/18).
Sua implementação é agrupada pelo [épico #77](https://github.com/ya-labs/YABook/issues/77).
As entregas abaixo foram criadas como subissues nativas do épico e mantêm ordem
de dependência.

### 1. [Migrar a estrutura documental para o monorepo (#78)](https://github.com/ya-labs/YABook/issues/78)

Status: **Pronto para dev** · Size: **4**

- Inventariar a documentação atual e aprovar o mapa de origem e destino.
- Criar os índices de `manual/` e `produto/`.
- Migrar em lotes pequenos, com links e referências atualizados no mesmo lote.
- Manter `skills/yabook/` no caminho atual até a migração específica da skill.

### 2. [Criar o scaffold do aplicativo desktop (#79)](https://github.com/ya-labs/YABook/issues/79)

Status: **Backlog** · Size: **3** · Depende da issue #78

- Criar `apps/desktop/` com Tauri, React e TypeScript.
- Preparar a execução local e o contrato inicial entre interface e núcleo.
- Não implementar funcionalidades de biblioteca, leitura ou configuração nesta
  entrega.

### 3. [Implementar a biblioteca local e a descoberta documental (#80)](https://github.com/ya-labs/YABook/issues/80)

Status: **Backlog** · Size: **4** · Depende da issue #79

- Cadastrar fontes locais, organizações opcionais e projetos avulsos.
- Persistir catálogo e preferências pessoais em SQLite local.
- Descobrir raízes documentais sem criar `.yabook/config.json` automaticamente.

### 4. [Implementar leitura e navegação documental (#81)](https://github.com/ya-labs/YABook/issues/81)

Status: **Backlog** · Size: **4** · Depende da issue #80

- Exibir árvore de raízes, pastas aninhadas e documentos Markdown.
- Oferecer breadcrumbs, índice de títulos, links relativos, histórico,
  favoritos, recentes e ações externas explícitas.
- Manter a leitura separada da edição de Markdown.

### 5. [Implementar personalização documental compartilhável (#82)](https://github.com/ya-labs/YABook/issues/82)

Status: **Backlog** · Size: **3** · Depende das issues #80 e #81

- Ler, validar, pré-visualizar e salvar `.yabook/config.json` mediante
  confirmação explícita.
- Permitir rótulos, ordem, itens ocultos e documento inicial pela interface.
- Separar rascunhos locais da configuração compartilhada do projeto.

### 6. [Implementar busca e atualização por alterações externas (#83)](https://github.com/ya-labs/YABook/issues/83)

Status: **Backlog** · Size: **3** · Depende das issues #80 e #81

- Criar o índice reconstruível por projeto e a busca limitada às raízes ativas.
- Refletir alterações, indisponibilidades e remoções sem perder o cadastro
  local ou o contexto de leitura.

### 7. [Empacotar e validar o MVP do YABook Desktop (#84)](https://github.com/ya-labs/YABook/issues/84)

Status: **Backlog** · Size: **3** · Depende das issues #81, #82 e #83

- Gerar instalador NSIS para Windows 11 x64 e AppImage para Linux Mint 21.3
  Cinnamon x64.
- Validar uso offline após a instalação, documentos reais e os critérios de
  utilidade definidos para o MVP.
- Manter autoatualização, lojas, telemetria e outras plataformas fora desta
  entrega.

## Eficiência de contexto da YABook Skill

### 1. Auditar os comandos

- Mapear contexto mínimo, referências, inspeções e saídas por rota.
- Identificar carregamentos redundantes e custos que pertencem à plataforma.
- Registrar uma linha de base comparável para comandos simples e complexos.

### 2. Reduzir o carregamento padrão

- Encaminhar comandos explícitos diretamente à referência necessária.
- Reservar a matriz geral para ambiguidades e composição.
- Criar um caminho rápido para demandas já delimitadas.
- Limitar inspeções e saídas sem reduzir as travas de segurança.

### 3. Proteger contra regressões

- Definir orçamento aproximado por classe de comando.
- Criar cenários que verifiquem referências e ampliações permitidas.
- Comparar o resultado com a linha de base da issue #39.

### 4. Evoluir observabilidade e automação segura

- Exportar métricas locais para telemetria externa opt-in, sem conteúdo sensível.
- Disponibilizar dashboard hospedado somente depois da exportação confiável.
- Documentar o dashboard em três níveis:
  - `README` curto para descoberta;
  - `docs/manual.md` para uso prático, interpretação e limites;
  - `help dashboard` para consulta rápida sem depender do manual.
- Deixar um comando operacional de build/serve como evolução posterior, caso o
  uso do dashboard se torne recorrente no fluxo da skill.
- Avaliar memória semântica em prova técnica controlada, com invalidação e
  critérios explícitos.
- Estudar sincronização automática em background apenas com contrato de
  consistência, auditoria e reversão.

Permanecem fora do escopo estrutural:

- inventar métricas quando o runtime não expuser o dado real;
- remover validações obrigatórias para reduzir custo.
