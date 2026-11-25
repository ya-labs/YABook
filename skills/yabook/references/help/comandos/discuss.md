# `$yabook discuss`

Analisa uma ideia, decisão ou mudança antes de virar planejamento, documentação
ou trabalho executável. Ajuda a comparar alternativas e chegar a uma
recomendação.

## Quando usar

- Você tem uma ideia e quer avaliar necessidade, custo e riscos.
- Há mais de um caminho possível e você quer uma recomendação justificada.
- Uma mudança de processo, documentação ou GitHub precisa ser pensada antes.

## Altera alguma coisa?

Não. É somente leitura: não altera arquivos, Git, GitHub nem o estado do
projeto. Brainstorming não vira decisão aprovada. A resposta separa o que se
aplicar entre contexto, necessidade, alternativas, recomendação, impactos,
decisão aceita, pendências e próximo comando. Se a decisão afetar o
planejamento, ela indica `$yabook do plan`; se gerar alteração concreta, indica
`$yabook issue`.

## Sintaxe

```text
$yabook discuss <tema>
```

- `plan discuss <tema>`: alias, sem limitar a discussão ao planejamento.
- Pode ser acompanhada por `steps` quando o contexto já estiver claro.

## Exemplos

```text
$yabook discuss trocar a autenticação por login social
$yabook plan discuss dividir a versão 2 em duas entregas
$yabook discuss onde documentar as regras de deploy
```

- Avalia necessidade, alternativas e riscos de uma mudança de implementação.
- Discute uma decisão de planejamento usando o alias.
- Analisa a fonte de verdade e o risco de duplicar documentação.

## Relacionados

- `plan`: transforma a decisão em planejamento de versão ou roadmap.
- `issue`: registra a alteração concreta que saiu da discussão.
- `steps`: acompanha a discussão em etapas.
