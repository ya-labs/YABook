# `$yabook bypass <ação>`

Autoriza somente a ação anexada diretamente em `main`, `dev`, release ou outra
branch incompatível, ignorando a exigência normal de issue e branch própria.

`bypass`:

- vale apenas para a solicitação atual;
- não autoriza mutações Git;
- não substitui `$yabook do`;
- não cria issue, branch, commit, PR, release ou merge;
- não autoriza merge implicitamente;
- não desativa proteções contra ações destrutivas;
- não dispensa regras locais relevantes.

Antes de editar, confirme somente a ação anexada, a branch e o worktree. Não
carregue planejamento, Project, release ou formatos de artefatos sem necessidade
demonstrada.

Depois da ação, informe a exceção aplicada e uma única próxima etapa.
