# Manual de uso do YABook

Este manual mostra como aplicar o YABook em projetos da YA LABS sem precisar ler todo o handbook antes.

## O que é

O YABook é o padrão organizacional da YA LABS.

Ele não substitui a documentação do projeto. Ele diz como o projeto deve organizar documentação, GitHub, IA e etapas de desenvolvimento.

## Quando usar

Use o YABook quando precisar:

- iniciar um projeto no padrão YA LABS;
- criar ou revisar issue, branch, commit, Pull Request ou release;
- organizar documentação técnica;
- orientar uma IA a seguir padrões da organização;
- conferir se um projeto está consistente com o fluxo de trabalho.

Não use o YABook para documentar fatos específicos de um produto.

## Como aplicar em projeto novo

1. Copie ou adapte os templates necessários.
2. Preencha o `README.md` do projeto com objetivo, stack, setup e links principais.
3. Mantenha um `AGENTS.md` com as instruções para IA naquele projeto.
4. Crie em `docs/` apenas os documentos que fazem sentido para o momento atual.
5. Declare labels, GitHub Project e responsável padrão por novas issues.
6. Use o padrão de GitHub do YABook para issue, branch, commit, PR e release.

Não crie pastas vazias nem documentos só para "completar a estrutura".

## Uso no dia a dia

Use o fluxo mínimo para mudanças relevantes:

```text
Issue -> Branch -> Commit -> Pull Request -> Merge
```

Para formatos de issue, branch, commit e PR, consulte [Padrões rápidos](padroes-rapidos.md).

Use `main` para documentação inicial, planejamento e prototipagem. Crie `dev` apenas quando começar o desenvolvimento de produto. O fluxo completo de `main`, `dev`, `release/x.y.z` e `archive/dev-x.y.z` fica em [Fluxo de trabalho com GitHub](processos/fluxo-de-trabalho-github.md).

## Uso com IA

Antes de pedir execução para IA, garanta que ela consulte:

1. `AGENTS.md` do projeto.
2. Documentação local relacionada à tarefa.
3. YABook, quando a dúvida for sobre padrão organizacional.

A IA deve avisar antes de criar padrão novo, mudar fluxo de trabalho ou agir fora do YABook.

## Uso com a skill YABook

A skill YABook é a interface operacional para IA usar estes padrões no trabalho diário.

Comandos principais:

- `$yabook help`: lista os comandos disponíveis.
- `$yabook init`: inicializa o padrão YA LABS no repositório atual.
- `$yabook issue`: gera título e descrição de issue.
- `$yabook pr`: gera título e descrição de Pull Request.
- `$yabook commit message`: sugere mensagem de commit.
- `$yabook release`: gera descrição de release.
- `$yabook check`: verifica conformidade com o YABook.
- `$yabook docs`: indica onde documentar uma informação.

Use a skill para reduzir orientação repetida. A documentação continua sendo a fonte humana de consulta.

## Onde consultar padrões

- [Padrões rápidos](padroes-rapidos.md): issue, branch, commit e PR.
- [Fluxo de trabalho com GitHub](processos/fluxo-de-trabalho-github.md): labels, Project, `main`, `dev`, release e tags.
- [Uso de IA](guias/uso-de-ia.md): contrato operacional para assistentes.
- [Documentação técnica](guias/documentacao-tecnica.md): como organizar documentação de projeto.
- [Template base de projeto](templates/projeto/README.md): estrutura inicial para novos projetos.

## O que não colocar no YABook

Não coloque no YABook:

- endpoints reais de produto;
- arquitetura específica de uma aplicação;
- variáveis de ambiente;
- deploy de projeto específico;
- fluxos de negócio exclusivos;
- roadmap interno de produto.

Essas informações devem ficar no repositório do próprio projeto.

## Checklist de conformidade

Use esta lista ao iniciar um projeto ou revisar um PR:

- O projeto tem `README.md` útil para entrada rápida.
- O projeto tem `AGENTS.md` com regras locais para IA.
- A documentação em `docs/` guarda conhecimento estável, não status operacional.
- Issues, branches, commits e PRs seguem o padrão da YA LABS.
- Exceções ao YABook estão explícitas no projeto.
- Não há documentação genérica, duplicada ou sem uso prático.

## Regra prática

Documento bom ajuda alguém a executar, revisar, decidir ou continuar o trabalho.

Se o texto não ajuda nenhuma dessas ações, corte, funda com outro documento ou não crie.
