# Rebase seguro

Use para atualizar uma branch de trabalho sobre sua base correta sem substituir merge, Pull Request ou release.

## Comandos

`$yabook rebase [base]` é uma rota `C2` somente leitura. Ela inspeciona e orienta, mas não executa `fetch`, `rebase`, stash, reset, restore, push ou outra mutação.

`$yabook do rebase [base]` é uma rota `C3`. Ela autoriza somente o rebase que acabou de ser analisado. Uma base explícita tem prioridade; sem ela, determine a base por esta ordem: base confirmada na issue ou PR, base remota do tracking da branch e branch principal aplicável do projeto. Se a base continuar ambígua, pare e peça que a pessoa informe a branch.

## Inspeção obrigatória

Antes de orientar ou executar, confirme:

1. workspace e remote corretos;
2. branch atual, upstream e se ela é `main`, `dev`, `release/*` ou protegida;
3. worktree, incluindo mudanças staged e unstaged;
4. base candidata, seu remoto e a divergência em ambos os sentidos;
5. commits exclusivos da branch e commits que chegarão pela base;
6. PR aberto, quando existir, e se a branch já foi publicada ou compartilhada.

Mostre o diagnóstico com branch, base, divergência, commits envolvidos e risco antes de qualquer mutação. Sem `do`, conclua com a autorização necessária e não sugira um comando que reescreva histórico fora do fluxo.

## Bloqueios e confirmação

Nunca execute em `main`, `dev`, `release/*`, branch protegida, branch sem nome compatível com a issue ou worktree com alterações. Não libere o worktree com stash, restore, reset ou commit automático.

Se a branch tiver upstream publicado, PR aberto ou indício de uso por outras pessoas, avise que o rebase reescreve histórico e peça confirmação explícita antes da execução. Essa confirmação não autoriza push forçado: depois do rebase, informe que atualizar o remoto exige uma nova ação explícita e, quando for apropriado, `push --force-with-lease` revisado conscientemente.

## Execução e conflitos

Com `$yabook do rebase`, revalide o checkpoint imediatamente antes de executar. Busque a base somente quando essa atualização estiver autorizada pelo mesmo fluxo e então execute `git rebase <base-confirmada>` sem opções destrutivas.

Se houver conflito, pare no primeiro conflito e informe:

1. os arquivos em conflito e o commit em aplicação;
2. como revisar e resolver o conteúdo preservando a intenção de ambos os lados;
3. que a pessoa deve revisar o diff e solicitar continuação explícita antes de `git rebase --continue`.

Não use automaticamente `--continue`, `--skip`, `--abort`, `restore`, `reset`, stash nem resolução silenciosa. `$yabook continue` rejeita apenas um checkpoint opcional; não retoma um rebase interrompido nem remove a exigência de nova autorização para a mutação seguinte.

## Depois do rebase

Informe o resultado e diferencie validações executadas das pendentes. Valide ao menos o estado do worktree, o log/diff contra a base e os testes aplicáveis ao projeto. Se houver PR, revise seu diff e informe que sua atualização remota é uma ação separada. Use merge quando a preservação do histórico de integração for mais importante; use atualização de base pelo PR quando o repositório a oferece; recrie a branch quando a linha de commits estiver contaminada ou a base correta não puder ser determinada com segurança.
