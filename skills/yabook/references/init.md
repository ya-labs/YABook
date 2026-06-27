# Inicialização YABook

Use esta referência para `$yabook init` e `$yabook do init`.

## Objetivo

Analisar ou preparar a base mínima para documentação, IA e fluxo GitHub.

## Separação entre análise e execução

- `$yabook init`: inspeciona o repositório e apresenta arquivos que seriam criados
  ou adaptados, conflitos, exceções e próximos passos. Não altera estado.
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

## Resultado do `$yabook do init`

Ao final, informar:

- arquivos criados;
- arquivos adaptados;
- exceções encontradas;
- próximos passos recomendados.
