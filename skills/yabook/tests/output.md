# Cenários de saída e próxima etapa

## Contratos de artefato

Confirme que os comandos retornam somente os campos previstos em
`references/artefatos/contratos.md` e não incluem análise, confiança,
autorização operacional ou orientação de fluxo dentro do artefato.

Valide os cenários de aceitação e rejeição da referência para issue, branch,
commit e PR. Em cada rejeição, confirme interrupção antes de `do` e diagnóstico
com `Campo inválido`, `Motivo` e `Correção necessária`.

Para issue e PR, confirme o bloco recolhido `Informações para IA`, seus cinco
tópicos obrigatórios e a ausência de uma listagem redundante de arquivos.

## Prévia de artefato

Para `$yabook issue`, `$yabook branch`, `$yabook commit message`, `$yabook pr`,
`$yabook release` e outros comandos que geram prévia sem `do`, confirme que:

- a autorização necessária para materializar o artefato aparece no resultado
  principal, fora de `Próxima etapa`;
- não é criado checklist apenas para exibir uma continuação;
- `Próxima etapa` não contém apenas `$yabook do <ação>`;
- quando conhecida e segura, `Próxima etapa` aponta para a ação posterior à
  materialização, como revisar a issue ou branch criada, abrir PR após commit
  aprovado ou seguir para merge após aprovação;
- quando não houver continuação posterior segura, a resposta informa que o
  fluxo depende de revisão ou aprovação da pessoa, sem inventar comando ou
  decisão;
- a verificação final de saída detecta como inválida a repetição isolada de
  `$yabook do <ação>` em `Próxima etapa`;
- a orientação não autoriza nem infere commit, PR, merge ou release.

Para `$yabook do issue`, `$yabook do branch`, `$yabook do commit`, `$yabook do
pr` e `$yabook do release`, confirme que o fluxo autorizado pode executar seus
pré-requisitos mínimos conforme o contrato específico, sem ampliar a
autorização para a próxima ação do fluxo.

## Rebase seguro

Para `$yabook rebase`, confirme que a resposta não altera estado e informa a
branch atual, base candidata, upstream, divergências, commits envolvidos, risco
de histórico compartilhado e a autorização necessária para executar.

Para `$yabook do rebase`, confirme que a skill bloqueia `main`, `dev`,
`release/*` e branch protegida, além de worktree com alterações. Em conflito,
ela para, explica como inspecionar e resolver cada arquivo e só retoma após
nova autorização explícita; nunca usa `--abort`, `--skip`, `--continue`,
`restore`, `reset`, stash ou push forçado automaticamente. Após sucesso,
informa as validações executadas, pendentes e se o PR precisa ser atualizado.

## Checklist e próxima etapa

Com checklist ativo, confirme que:

- o estado compacto aparece uma única vez, após o resultado;
- a etapa atual não avança apenas pela entrega do agente;
- `Próxima etapa` aponta para uma entrega fora do escopo do comando atual;
- o comando sugerido só aparece quando a rota é aplicável;
- em prévia sem `do`, `Próxima etapa` continua posterior à materialização e
  não repete isoladamente a autorização necessária;
- a resposta não inventa comando, issue, decisão ou objetivo.

Sem checklist ativo, confirme que o checklist compacto não é exibido e que
`Próxima etapa` ainda aponta para uma única continuação útil, posterior ao
comando atual.

## Saída encerrada

Confirme que `Próxima etapa` informa fluxo concluído quando não houver
continuação útil ou confiável.
