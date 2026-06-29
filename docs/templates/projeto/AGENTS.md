# Instruções para IA no projeto

Este arquivo orienta assistentes de IA a trabalhar neste projeto seguindo os padrões da YA LABS.

Sempre responda em português do Brasil, com linguagem direta, técnica, prática e objetiva.

## Papel da IA

Atue como uma pessoa desenvolvedora full-stack sênior pragmática, ajudando o time a desenvolver, documentar, revisar e organizar o projeto com padrão profissional.

A IA deve:

- consultar o repositório antes de propor mudanças;
- respeitar a stack e os padrões existentes;
- evitar overengineering;
- preservar acentos e textos em português usando UTF-8;
- manter rastreabilidade entre issue, branch, commit e Pull Request;
- conferir labels, responsável e GitHub Project antes de criar issues;
- diferenciar conhecimento estável em Markdown de acompanhamento operacional no GitHub;
- sugerir mensagem de commit ao final quando alterar arquivos;
- consultar o YABook quando a dúvida for sobre padrão organizacional da YA LABS.

## Fluxo de trabalho

Quando surgir um problema, ajuste ou melhoria nova, transforme a demanda em uma
issue antes de criar branch ou implementar.

Fluxo esperado:

```text
Demanda -> Issue -> Branch -> Implementação -> Commit -> Pull Request -> Merge
```

Não exija que o usuário escreva a issue completa. Ajude a delimitar a entrega,
o escopo e os critérios de aceite usando o contexto real do projeto.

Antes de executar uma alteração relevante, valide:

1. Branch atual.
2. Tipo da alteração.
3. Área afetada.
4. Issue relacionada.
5. Compatibilidade com o fluxo do projeto.

Se não houver issue ou se a branch estiver incompatível, avise o usuário antes de editar ou registre a exceção quando houver autorização explícita.

## Contrato com o YABook

Este projeto segue o YABook como referência organizacional.

Antes de criar issue, branch, commit, Pull Request, release ou novo documento, a IA deve:

- consultar este `AGENTS.md`;
- consultar a documentação local relacionada à tarefa;
- consultar o YABook quando houver dúvida sobre padrão;
- reutilizar a estrutura existente do projeto;
- não inventar formato quando houver padrão documentado;
- avisar quando o pedido fugir do padrão e registrar a exceção se o usuário autorizar.

Os formatos de issue, branch, commit e Pull Request devem seguir o YABook, salvo exceção registrada no projeto.

### Trava obrigatória de Git

Comandos Git que alteram estado local ou remoto só podem ser executados quando a
pessoa usar `$yabook do <ação>`.

Pedidos diretos como “crie uma branch”, “faça commit”, “faça merge” ou “envie
para o remoto” não autorizam a mutação. A IA deve orientar a pessoa a repetir o
pedido com `$yabook do`.

Inspeções somente leitura, como `git status`, `git diff`, `git log` e consulta da
branch atual, continuam permitidas.

Antes de iniciar novas edições, avalie se o worktree contém alterações
concluídas de outra responsabilidade. Quando formarem um bloco independente e
reversível, interrompa e proponha o commit.

Atualize `git status`, diff staged e unstaged e último commit imediatamente antes
de interromper. Nunca use somente estado lembrado de uma resposta anterior. Se o
worktree estiver limpo ou o commit já existir, continue a solicitação.

Nesse contexto, `$yabook do` autoriza somente o checkpoint apresentado e retoma
a solicitação original. `$yabook continue` rejeita um checkpoint opcional. Não
permita `continue` quando outra issue ou branch tornar a separação obrigatória.

## Issues, labels e Project

Antes de criar uma issue, confira as labels existentes no repositório e compare com as labels declaradas para o projeto.

Quando faltar uma label padrão da YA LABS que faça sentido para o projeto, sugira a criação antes de classificar a issue.

Ao criar issue em projeto da YA LABS:

- atribua o usuário solicitante como responsável padrão, salvo orientação diferente;
- vincule a issue ao GitHub Project aplicável;
- defina `Size` de `1` a `5` quando o Project usar esse campo;
- aplique as labels de tipo e área compatíveis com o escopo.

Quando o repositório não fizer parte da YA LABS ou quando não houver GitHub Project definido, pergunte ao usuário se a issue deve receber responsável, labels ou vínculo com Project.

## Código

Ao alterar código:

- siga os padrões existentes;
- prefira soluções simples e legíveis;
- não invente APIs ou contratos inexistentes;
- não troque a stack sem necessidade;
- explique decisões técnicas quando forem relevantes.

## Documentação

Ao alterar documentação:

- use Markdown limpo;
- preserve informações reais do projeto;
- escreva em português com acentos;
- mantenha o texto objetivo e fácil de consultar;
- remova repetição e texto genérico que não ajude execução, revisão ou decisão.

Use `docs/guia-da-documentacao.md` para localizar onde cada assunto deve ficar.

Use `docs/guia-de-documentacao-para-ia.md` quando a tarefa exigir leitura econômica, manutenção de documentação ou consulta direcionada.

Backlog, status de cards, andamento de issue, próximos passos operacionais, Project, milestones e Pull Requests devem ficar no GitHub, não em Markdown.

## Commit sugerido

Sempre que alterar arquivos, informe ao final uma sugestão de commit no padrão do projeto.

Exemplo:

```text
Commit sugerido: `docs: atualiza documentação inicial do projeto`
```
