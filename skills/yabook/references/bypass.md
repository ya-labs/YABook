# `$yabook bypass <ação>`

Autoriza só a ação anexada, inclusive em `main`, `dev`, release ou branch
incompatível, dispensando issue e branch própria.

Recomende para ajuste pontual que forme um commit compreensível e validável;
considere impacto e acompanhamento, não só número de commits. Se crescer,
proponha issue individual ou pacote.

`bypass` vale só na solicitação atual; não autoriza mutações Git, não substitui
`do`, não cria artefatos nem autoriza merge. Preserve regras locais e proteções
contra ações destrutivas.

Antes de editar, confira ação, branch e worktree. Não carregue planejamento,
Project ou release sem necessidade.

Após implementar, informe a exceção e sugira o commit completo: assunto
`tipo: descrição curta` e corpo com motivo, alteração e registro de ajuste via `bypass`, sem issue quando aplicável.
Use o diff real; não basta o assunto. Validações ficam no relatório e no PR.
Apresente `Mensagem` e `Descrição` em dois blocos de código separados.

Fora de `auto`, criar o commit exige `do commit`, sem exigir issue novamente.
Em `auto`, ajuste pontual dispensa invocar `bypass`. Encerre com uma próxima etapa.
