# Roadmap de capacidades planejadas

Este documento registra a sequência técnica aprovada. O estado operacional de
cada entrega permanece no GitHub.

## Preparação de APKs

### 1. Implementar o contrato no YABook

- Definir a leitura e a validação de `.yabook/apk.json`.
- Implementar a prévia `$yabook apk`.
- Implementar a preparação `$yabook do apk`.
- Cobrir nomes de issue, `dev` e release.
- Validar build novo, artefato esperado e prevenção de sobrescrita.

### 2. Adotar no primeiro aplicativo

- Criar `.yabook/apk.json` com os dados do próprio projeto.
- Validar o fluxo em issue, `dev` e release.
- Ajustar o alias local `geraapk` para copiar o artefato preparado sem
  parâmetros.

### 3. Avaliar evolução

- Revisar o uso real antes de padronizar novos tipos de branch.
- Avaliar upload automatizado somente depois que o fluxo manual estiver
  validado e houver contrato seguro para credenciais e destino.

As etapas 1 e 2 devem ser issues separadas: pertencem a repositórios, riscos e
validações diferentes.
