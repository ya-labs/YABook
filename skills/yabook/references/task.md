# YABook Tasks

Use para `task` e `do task`. Acompanha tarefas pessoais num repositório de dados
privado próprio, separado da memória. Fluxo e decisões da capacidade:
`produto/planejamento/yabook-tasks.md` no repositório do YABook.

Execute `python3 scripts/yabook_tasks.py <serviço>` relativo à skill instalada.
A configuração da máquina fica na seção `tasks` de `~/.config/yabook/config.json`
(ou `YABOOK_CONFIG`), fora do Git.

## Inicialização

- `task init` roda `init-plan --output <arquivo>` e mostra repositório, pasta,
  máquina, operações e avisos, sem alterar nada. Opções: `--repository
  dono/nome`, `--root`, `--machine`, `--confidential <pasta>`, `--terms
  <arquivo>`.
- `do task init` roda `init-apply --plan <arquivo> --approval-hash <hash>` com o
  plano apresentado; plano, conta, remoto ou pasta alterados exigem novo plano.
- Sem indicação, o repositório é `YABook-task-<loginGitHub>` da conta
  autenticada. Use o mesmo repositório nas duas máquinas: na segunda, o plano
  conecta o existente. Repositório de outra conta precisa existir e ser privado;
  nunca crie uma segunda base por inferir o login de outra máquina.
- A aplicação define `core.hooksPath` para `.githooks` e, com `--terms`, grava
  `yabook.terms` no Git local. Sem lista, o `pre-commit` apenas avisa.

## Formato

Cada tarefa é `tarefas/<id>.md` com frontmatter: `id`, `tipo` (`demanda`,
`projeto`, `especificacao`, `issue`, `tarefa`, `pergunta`), `titulo`, `coluna`
e, quando houver, `ordem`, `projeto`, `demanda`, `issue` (`dono/repo#n`),
`prazo` (`AAAA-MM-DD`), `proximo_passo`, `sobre`, `resposta` e `refs`
(`confidencial:`, `yabook:` ou `github:`). `config.yml` guarda rótulos e a
ficha; `quadro.yml`, colunas com papel `entrada`, `pronto`, `ativo`,
`validacao`, `concluido` ou `arquivado`.

- Grave somente pela biblioteca do runtime, que valida, preserva `criada`,
  atualiza `atualizada` e recusa escrita sobre revisão diferente da lida.
- Campos versionados usam texto técnico e genérico. Cliente, base, ambiente e
  acessos ficam no complemento confidencial local e entram só como `refs`.
- A gravação recusa termos da lista local; não contorne movendo o texto para
  outro campo versionado.
- `validate` confere configuração, quadro e todas as tarefas.
