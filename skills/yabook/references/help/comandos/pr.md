# `$yabook pr`

Gera título e corpo do Pull Request no padrão YA LABS, com resumo, o que mudou,
observações, vínculo `Closes #numero` e informações para IA. Com `do pr`, cria
ou atualiza o PR.

## Quando usar

- A implementação está pronta e você quer o texto do PR.
- Quer um resumo curto da entrega para revisão (`pr brief`).
- Quer publicar a branch e abrir o PR de uma vez.

## Altera alguma coisa?

`pr` e seus subcomandos são somente leitura. `do pr` valida título, corpo e
vínculo com a issue e pode criar commits coerentes, enviar a branch e criar ou
atualizar o PR. Não faz merge: para isso use `do merge`. Em `mode: auto` o
objetivo delegado dispensa `do`.

PR de `issue package` resume os commits documentados e usa merge commit. Em
ajuste pontual sem issue, o PR omite `Closes` e registra a exceção.

## Sintaxe

```text
$yabook pr [title|desc|brief]
```

- `pr`: título e corpo completos.
- `pr title` / `pr desc`: só o título ou só o corpo (`pr description` é alias).
- `pr brief`: resumo de até 1.200 caracteres com validação e riscos.
- `do pr`: cria ou atualiza o PR.

## Exemplos

```text
$yabook pr
$yabook do pr
$yabook dev & do pr
```

- `pr`: propõe o texto a partir da conversa e do Git.
- `do pr`: envia a branch e abre o PR vinculado à issue.
- `dev & do pr`: implementa, commita, envia e abre o PR em sequência.

## Relacionados

- `commit`: mensagens que o PR vai resumir.
- `release`: publicar a versão depois dos merges.
- `do`: diferença entre `do pr` e `do merge`.
