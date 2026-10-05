# Pull Requests, merge e release no GitHub

Use ao criar, atualizar, revisar ou integrar PR e release.

PR usa título objetivo, corpo baseado no artefato aprovado e vínculo
`Closes #numero`.

## Merge de pacote

PR de issue pacote usa merge commit para preservar assuntos, corpos e commits
originais. Resuma assuntos e corpos contra a base, incluindo ambas as pessoas
em dupla, e confira o diff final para excluir entregas revertidas ou removidas.
Registre validações sem checklists, inclusive no bloco para IA. Confira se o repositório
permite essa estratégia antes de integrar; se não permitir, informe e obtenha
uma decisão que preserve os registros, sem trocar por squash silenciosamente.
Em ajuste pontual autorizado sem issue, omita `Closes` e registre a exceção.

## Squash merge

Assunto:

```text
tipo: descrição curta (#numero-do-pr)
```

Corpo:

```text
Histórico da branch contra branch-alvo:
- commit original 1 (hash)
- commit original 2 (hash)
```

Gere o histórico com:

```bash
git log --reverse --format='- %s (%h)' branch-alvo..branch-do-pr
```

Ao usar `gh pr merge --squash`, prefira `--body-file`.

## Branches de integração

- `main`: estado estável ou publicável.
- Crie `dev` quando começar um ciclo com integração de várias issues.
- `dev` representa o ciclo atual, não uma branch permanente.
- Após release, uma nova `dev` parte da `main`.
- Use `release/x.y.z` quando houver homologação ou ajustes finais.

PR de release usa o título `Publicar versão x.y.z`. A tag aponta para o commit
integrado na branch principal.
