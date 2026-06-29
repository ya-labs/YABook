# Resolução do workspace

Use esta referência antes de qualquer comando YABook que dependa do repositório
atual.

## Regra principal

Não assuma que o `cwd` herdado pelo agente representa o workspace ativo. Resolva
primeiro a raiz do repositório e use essa raiz como `workdir` explícito em todas
as inspeções e ações seguintes.

## Ordem de resolução

Considere os sinais nesta ordem:

1. repositório ou caminho indicado explicitamente pela pessoa usuária;
2. raiz de workspace fornecida pela IDE ou pelo ambiente;
3. caminhos absolutos ou qualificados dos arquivos ativos e abas abertas;
4. repositório já confirmado na conversa, se o workspace não mudou;
5. `cwd` do processo.

Um nome de arquivo relativo ou uma aba sem caminho suficiente não identifica um
repositório sozinho.

## Validação do candidato

Para cada candidato:

1. suba até encontrar a raiz que contém `.git`;
2. confirme que os arquivos ativos pertencem a essa árvore, quando aplicável;
3. leia o `AGENTS.md` dessa raiz, se existir;
4. confira o remote e compare-o com o repositório citado, a issue ou o contexto;
5. somente então consulte branch, status, issue, PR ou GitHub.

Se workspace e `cwd` apontarem para repositórios diferentes e o workspace for
inequívoco, use o workspace. Não execute primeiro no `cwd` para depois corrigir.

## Ambiguidade e segurança

Peça confirmação antes de escrever quando:

- houver mais de um workspace ou repositório plausível;
- os arquivos ativos pertencerem a repositórios diferentes;
- o remote não corresponder ao repositório esperado;
- existirem apenas caminhos relativos que também ocorram em outro candidato;
- conversa, workspace e branch apontarem para demandas incompatíveis.

Inspeções mínimas podem ser feitas em candidatos para desambiguar, mas Git,
GitHub e arquivos só podem ser alterados depois que uma única raiz for
confirmada.

## Cache

Guarde no cache da conversa:

- raiz resolvida;
- remote confirmado;
- sinais usados na escolha;
- branch e issue depois da resolução.

Invalide e resolva novamente quando mudar o workspace, o conjunto relevante de
arquivos ativos, o repositório informado, a branch ou o remote. `$yabook load`
também força uma nova resolução.
