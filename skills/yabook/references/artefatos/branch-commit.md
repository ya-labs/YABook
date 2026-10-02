# Branch e commit

Consulte [contratos.md](contratos.md) antes de gerar, criar ou validar branch e
commit.

## Branch

Use:

```text
numero-descricao-curta
```

Não inclua tipo, área, `issue`, `#`, acentos ou espaços. Use o número da issue
inequívoca e a base definida pelo fluxo local.

Criação real exige `do branch` ou `dev`, `github/branches.md`,
`git/checkpoint.md` e `git/mutacoes.md`. Prefira `createLinkedBranch` e confirme
em `issue.linkedBranches`. Em `do branch`, valide o nome e a issue conforme
`contratos.md` antes de criar ou publicar.

## Commit

Use:

```text
tipo: descrição curta
```

Tipos comuns: `feat`, `fix`, `docs`, `chore`, `refactor`.

Para sugerir a mensagem, use conversa, `git diff --stat` e `git diff` quando
necessário. Não carregue Project, release ou corpos de issues sem relação.
Fora de `auto`, criar commit exige `do`. Valide a mensagem antes da mutação.

Em `mode: auto`, a delegação substitui `do` dentro do objetivo solicitado.
Aceite assunto e corpo separados por linha em branco. Pacotes e ajustes via
`bypass` exigem descrição com motivo e alteração realizada,
proporcional à mudança. Após `bypass`, sugira sempre a mensagem completa e
registre a exceção; `do commit` conclui esse ajuste sem exigir issue novamente.

Em `auto`, ajuste pontual sem issue também exige corpo documentado e registro
desse caminho, sem declarar uso de `bypass` quando ele não foi invocado.

Nos demais commits, inclua descrição somente quando ajudar revisão ou continuidade.
Quando houver descrição, apresente dois blocos de código separados: **Mensagem**
contém o assunto e **Descrição** contém o corpo. Caso contrário, apresente apenas
a mensagem, sem bloco de descrição vazio. Não inclua validações na descrição;
relate-as no desenvolvimento e no PR. Ao criar o commit, preserve essas partes
como assunto e corpo da mesma mensagem Git, separados por linha em branco.
