# Resolução do workspace

Use esta referência antes de qualquer comando YABook que dependa do repositório
atual.

## Regra principal

Não assuma que o `cwd` herdado pelo agente representa o workspace ativo. Resolva
primeiro a raiz do repositório e use essa raiz como `workdir` explícito em todas
as inspeções e ações seguintes.

## Ordem de resolução

Considere os sinais nesta ordem:

1. raiz de workspace fornecida pela IDE ou pelo ambiente;
2. caminhos absolutos ou qualificados dos arquivos ativos e abas abertas;
3. repositório ou caminho indicado explicitamente pela pessoa usuária;
4. repositório já confirmado na conversa, se o workspace não mudou;
5. `cwd` do processo.

Um nome de arquivo relativo ou uma aba sem caminho suficiente não identifica um
repositório sozinho.

## Validação do candidato

Antes de criar ou alterar issue, branch, commit, Pull Request ou release:

1. suba a partir do candidato até encontrar a raiz que contém `.git`;
2. confirme que os arquivos ativos pertencem a essa árvore, quando aplicável;
3. leia o `AGENTS.md` dessa raiz, se existir; em seguida, leia
   `.yabook/AGENTS.md` se existir;
4. execute `git remote -v` nessa raiz;
5. confirme que o remote corresponde ao projeto ativo;
6. use essa raiz como `workdir` explícito em todos os comandos seguintes;
7. somente então consulte ou altere branch, status, issue, PR ou GitHub.

O `cwd` é somente um candidato técnico e nunca prevalece sobre evidências claras
do workspace ativo. Não execute primeiro no `cwd` para depois corrigir.

## Ambiguidade e segurança

Peça confirmação antes de escrever quando:

- houver mais de um workspace ou repositório plausível;
- os arquivos ativos pertencerem a repositórios diferentes;
- o remote não corresponder ao repositório esperado;
- existirem apenas caminhos relativos que também ocorram em outro candidato;
- conversa, workspace e branch apontarem para demandas incompatíveis.

Se `cwd`, workspace, arquivos ativos, contexto e remote apontarem para projetos
diferentes, não realize nenhuma escrita, mesmo que um candidato pareça
inequívoco. Informe a divergência e peça confirmação do repositório correto.

Inspeções mínimas podem ser feitas em candidatos somente para desambiguar.
Git, GitHub e arquivos só podem ser alterados depois que uma única raiz for
confirmada.

## Cache da conversa

Guarde no cache da conversa:

- raiz resolvida;
- remote confirmado;
- sinais usados na escolha;
- branch e issue depois da resolução.

## Configuração local do YABook

Em rotas de repositório, leia `.yabook/AGENTS.md` após `AGENTS.md` se existir;
ausência não é erro. A precedência é global, `AGENTS.md`, configuração local:
esta não remove `do` nem permissões ou proteções de Git/GitHub. Rotas `help`,
`mode`, `steps`, `step` e `discuss` não a leem sem pedido explícito.

Invalide e resolva novamente quando mudar o workspace, o conjunto relevante de
arquivos ativos, o repositório informado, a branch ou o remote. `$yabook load`
também força uma nova resolução.

O cache opcional persistido em `.yabook/context-cache.md` segue contrato
separado em `context-cache.md` e nunca substitui esta validação do workspace.
