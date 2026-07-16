# Sessão de planejamento — preparação de APKs

Data: 2026-07-01
Rastreabilidade: issue #36

## Contexto

Aplicativos Android precisam gerar APKs identificáveis e organizá-los para uso
comercial sem incorporar detalhes internos de cada produto ao YABook.

## Decisões

- O fluxo terá uma prévia somente leitura em `apk` e uma execução autorizada em
  `do apk`, sem build automático.
- A configuração mínima do aplicativo ficará em `.yabook/apk.json`.
- O build continuará sob responsabilidade da pessoa usuária e fora do YABook.
- Issue e `dev` usarão o commit curto; release usará a versão.
- O nome de issue não terá o prefixo `issue`, pois a pasta e o número já dão o contexto.
- O alias local copiará o artefato preparado sem receber parâmetros.
- O upload permanecerá manual nesta primeira etapa.
- O exemplo normativo será fictício e não conterá dados de empresas ou
  produtos.

## Pendências

- Criar uma issue para implementar os comandos e validações no YABook.
- Criar a issue de adoção no repositório e no Project da organização
  responsável pelo primeiro aplicativo adotante.
- Definir critérios objetivos para remover apenas cópias preparadas antigas sem
  tocar no artefato original.

## Impactos

- O YABook passa a ter um contrato planejado para preparação de APKs.
- Aplicativos continuam responsáveis por seus comandos e caminhos reais.
- Credenciais e destinos físicos permanecem fora dos repositórios.
