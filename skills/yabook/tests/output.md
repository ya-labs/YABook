# Cenários de saída e próxima etapa

## Prévia de artefato

Para `$yabook issue`, `$yabook commit message`, `$yabook pr` e outros comandos
que geram prévia sem `do`, confirme que:

- o resultado pode informar a autorização necessária para materializar o
  artefato;
- não é criado checklist apenas para exibir uma continuação;
- com checklist já ativo, a orientação não repete apenas `$yabook do <ação>` e
  não autoriza nem infere merge.

## Checklist e próxima etapa

Com checklist ativo, confirme que:

- o estado compacto aparece uma única vez, após o resultado;
- a etapa atual não avança apenas pela entrega do agente;
- `Próxima etapa` aponta para uma entrega fora do escopo do comando atual;
- o comando sugerido só aparece quando a rota é aplicável;
- a resposta não inventa comando, issue, decisão ou objetivo.

Sem checklist ativo, confirme que não há guia `Próxima etapa`.

## Saída encerrada

Confirme que o resultado informa fluxo concluído quando não houver continuação
útil ou confiável, sem incluir o guia `Próxima etapa` se não houver checklist.
