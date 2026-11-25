# `$yabook init`

Analisa como preparar ou adaptar o repositório à base mínima do YABook:
documentação, instruções para IA e fluxo no GitHub. Mostra o que seria criado
ou ajustado antes de qualquer mudança.

## Quando usar

- Em um projeto novo que ainda não segue o YABook.
- Em um projeto existente sem `README.md`, `AGENTS.md` ou `docs/` organizados.
- Para conferir o que falta na base do projeto antes de começar a trabalhar.

## Altera alguma coisa?

`$yabook init` é somente leitura: inspeciona README, `AGENTS.md`, `docs/`,
branch e padrões locais, faz perguntas curtas quando objetivo, stack ou fluxo
não estão claros e entrega estado atual, arquivos ausentes, adaptações
propostas, conflitos e o escopo da execução.

Quem altera é `$yabook do init`: aplica só a proposta aprovada, não sobrescreve
conteúdo existente sem apontar o conflito e não faz commit. Os arquivos mínimos
são `README.md`, `AGENTS.md`, `docs/README.md`, `docs/guia-da-documentacao.md`
e `docs/guia-de-documentacao-para-ia.md`, criados ou adaptados apenas se úteis.

## Sintaxe

```text
$yabook init
```

- `steps start init`: mesma entrevista, com checklist ativo na conversa.
- `do init`: aplica a proposta aprovada.

## Exemplos

```text
$yabook init
$yabook steps start init
$yabook do init
```

- Analisa o repositório e propõe a base mínima, sem alterar nada.
- Conduz a mesma análise acompanhada por um checklist de etapas.
- Cria ou adapta os arquivos aprovados e lista criados, adaptados e exceções.

## Relacionados

- `diagnose`: entende o estado do projeto antes de inicializar.
- `plan`: depois da base pronta, planeja versão ou roadmap.
- `configure`: propõe a configuração local em `.yabook/AGENTS.md`.
