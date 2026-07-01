# Sessão de planejamento — preparação de APKs

Data: 2026-07-01  
Rastreabilidade: issue #36

## Contexto

Aplicativos Android precisam gerar APKs identificáveis e organizá-los para uso
comercial sem incorporar detalhes internos de cada produto ao YABook.

## Decisões

- O fluxo terá uma prévia somente leitura e uma execução autorizada.
- A configuração mínima do aplicativo ficará em `.yabook/apk.json`.
- Um build novo será obrigatório na preparação.
- Issue e `dev` usarão o commit curto; release usará a versão.
- O alias local copiará o artefato preparado sem receber parâmetros.
- O upload permanecerá manual nesta primeira etapa.
- O exemplo normativo será fictício e não conterá dados de empresas ou
  produtos.

## Pendências

- Criar uma issue para implementar os comandos e validações no YABook.
- Criar outra issue no primeiro aplicativo adotante.
- Definir critérios técnicos para reconhecer que o artefato pertence ao build
  atual durante a implementação.

## Impactos

- O YABook passa a ter um contrato planejado para preparação de APKs.
- Aplicativos continuam responsáveis por seus comandos e caminhos reais.
- Credenciais e destinos físicos permanecem fora dos repositórios.
