# Inicialização YABook

Use esta referência para `$yabook init`, `$yabook steps start init` e
`$yabook do init`.

## Objetivo

Analisar ou preparar a base mínima para documentação, IA e fluxo GitHub.

## Separação entre análise e execução

- `$yabook init`: conduz descoberta e entrevista sobre a base do projeto,
  inspeciona o necessário e apresenta arquivos que seriam criados ou adaptados,
  conflitos e exceções. Não cria checklist nem altera estado.
- `$yabook steps start init`: conduz a mesma descoberta e entrevista com
  checklist contextual ativo apenas na conversa.
- `$yabook do init`: aplica somente a proposta aprovada. Não sobrescreve conteúdo
  existente sem apontar o conflito e não cria commit automaticamente.

## Antes de propor ou alterar

Inspecione:

- `README.md`;
- `AGENTS.md`;
- `docs/`;
- branch atual;
- arquivos modificados;
- padrões locais já existentes.

Não sobrescreva conteúdo existente sem avisar.

## Arquivos mínimos

Criar ou adaptar:

- `README.md`;
- `AGENTS.md`;
- `docs/README.md`;
- `docs/guia-da-documentacao.md`;
- `docs/guia-de-documentacao-para-ia.md`.

## README do projeto

Deve declarar:

- objetivo do projeto;
- stack;
- como rodar;
- link para documentação;
- labels adotadas;
- GitHub Project;
- campo `Size` de `1` a `5`;
- responsável padrão por novas issues;
- referência ao YABook.

## AGENTS.md

Deve orientar IA a:

- consultar o repositório antes de propor mudanças;
- respeitar stack e padrões locais;
- consultar o YABook para padrão organizacional;
- manter rastreabilidade entre issue, branch, commit e Pull Request;
- não inventar formato quando houver padrão documentado.

## Docs

Crie apenas documentos úteis para o estágio atual.

Não crie pastas vazias para preencher estrutura.

## Resultado do `$yabook init`

Informar:

- estado atual;
- arquivos ausentes;
- adaptações propostas;
- conflitos e exceções;
- escopo que `$yabook do init` executaria.

Faça perguntas curtas quando objetivo, stack, documentação, regras de IA ou
fluxo GitHub ainda não estiverem evidentes. Não suponha que a ausência de um
arquivo exige criá-lo antes de confirmar sua utilidade.

## Resultado do `$yabook do init`

Ao final, informar:

- arquivos criados;
- arquivos adaptados;
- exceções encontradas;
- próximos passos recomendados.
