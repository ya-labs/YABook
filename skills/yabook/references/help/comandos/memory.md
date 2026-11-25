# `$yabook memory`

Consulta e mantém a memória própria do YABook: descobertas, procedimentos,
preferências e experiências guardadas num repositório Git privado seu
(`YABook-memory-<seuLogin>`), o mesmo em casa e no trabalho. O agente usa essa
memória para não reinvestigar o que já foi resolvido.

## Quando usar

- Ao começar um assunto, para recuperar o que já se sabe sobre ele.
- Para registrar, corrigir ou esquecer um conhecimento específico.
- Para revisar pendências, hipóteses e duplicações, ou fazer a faxina.
- Para conectar a base de colegas e trazer aprendizados úteis.

## Altera alguma coisa?

As consultas são somente leitura: `index`, `context`, `retrieve`, `search`,
`show`, `review`, `recent`, `map`, e `clean`, `sync` e `init` sem `do`.

`add`, `edit` e `forget` não gravam direto: o agente avalia utilidade,
evidência e conflitos e prepara uma proposta. Na política `manual`, ela só é
aplicada com `do memory [id]`.

Na política `automatic`, o agente grava o aprendizado do dia a dia sem pedir
aprovação a cada registro e avisa com uma linha curta. Perfil e preferências
pessoais exigem que você os declare; conflitos e hipóteses ficam pendentes
para `review`. Cada lote gravado vira um commit na base de memória.

Inicializar a base, conectar fontes, mudar a política, sincronizar e aplicar a
faxina exigem `do` (ou pedido explícito, no caso da faxina).

## Sintaxe

```text
$yabook memory <subcomando> [...]
$yabook do memory [id]
```

- `index`: índice de assuntos e tipos do projeto.
- `context`: contexto carregado no início da sessão.
- `retrieve <situação>`: assuntos e conhecimento pertinentes; `--experiences`
  e `--evidence` aprofundam.
- `search <termos>`: busca textual nos registros.
- `show <id>`: examina um registro.
- `add`, `edit <id>`, `forget <id>`: preparam proposta de mudança.
- `review`: hipóteses, duplicações e propostas pendentes.
- `recent`: atualizações recentes.
- `clean`: diagnóstico de faxina; `do memory clean` aplica.
- `map`: mapa visual somente leitura, também aberto pela extensão do VS Code.
- `init`: plano de migração inicial; `do memory init` aplica.
- `source add <URL>`: prepara conexão com outra base.
- `sync`: mostra a política; `do memory sync` incorpora novidades das fontes.
- `do memory [id]`: aplica uma proposta pendente.
- `do memory policy automatic|manual`: define a política local.

## Exemplos

```text
$yabook memory retrieve checklist não chega no supervisor
$yabook memory add <descoberta>
$yabook do memory policy automatic
```

- O primeiro traz o que já foi aprendido sobre esse sintoma.
- O segundo avalia a descoberta e prepara a proposta de registro.
- O terceiro libera o aprendizado automático nesta máquina.

## Relacionados

- `task`: tarefas e horas ficam num repositório separado da memória.
- `sync`: atualiza o plugin, não o conhecimento.
