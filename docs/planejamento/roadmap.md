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
