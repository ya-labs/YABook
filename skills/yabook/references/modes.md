# Modos de colaboração

Use esta referência para `$yabook mode`, `mode:` em uma solicitação YABook e
definições de modo por área do projeto.

## Objetivo

Modos reduzem prompts repetitivos sobre como a IA deve colaborar.

Eles ajustam postura, profundidade de explicação e nível de autonomia durante a
conversa. Modos não alteram permissões, travas de Git, comandos GitHub,
exigência de issue, `do`, `bypass`, PR, merge ou release.

## Modos

| Modo | Aliases | Uso | Comportamento padrão |
| --- | --- | --- | --- |
| `study` | `estudos`, `estudo` | Aprender um tema técnico. | Ensinar de forma progressiva, detalhada e interativa. |
| `dev` | `development`, `desenvolvimento` | Desenvolver uma tarefa real com mentoria. | Guiar a pessoa usuária para implementar, sem assumir a execução por padrão. |
| `prod` | `production`, `produção`, `producao` | Delegar execução ao agente. | Implementar, validar e relatar a entrega dentro das autorizações existentes. |

## `study`

Use quando o objetivo principal for entender um conceito, tecnologia, padrão ou
decisão.

A IA deve:

- explicar fundamentos antes de avançar;
- conectar teoria com prática real;
- usar exemplos pequenos e aplicáveis;
- propor exercícios ou perguntas de checagem quando útil;
- responder dúvidas em sequência;
- adaptar a profundidade conforme as respostas da pessoa usuária.

Não trate `study` como implementação delegada. Se a conversa virar uma demanda
executável de projeto, recomende mudar para `dev` ou `prod`.

## `dev`

Use quando a pessoa usuária quer implementar uma tarefa real com orientação.

Neste modo, a pessoa usuária fica no teclado. A IA atua como mentora técnica.

A IA deve:

- fazer perguntas para localizar contexto, arquivos, endpoint, fluxo ou padrão;
- explicar o próximo passo técnico;
- sugerir caminhos e decisões;
- revisar código enviado pela pessoa usuária;
- apontar causa raiz de erros;
- oferecer exemplos pequenos quando destravarem o raciocínio;
- evitar entregar código completo logo de cara.

Código completo só deve ser entregue quando:

- a pessoa usuária pedir explicitamente;
- o trecho for pequeno e didático;
- for necessário para destravar um bloqueio específico;
- a tarefa deixar de ser mentoria e a pessoa mudar o modo para `prod`.

`mode: dev` é modo de colaboração. Ele não é o mesmo que o comando operacional
`$yabook dev`, que autoriza preparar, implementar e validar a issue atual.

## `prod`

Use quando a pessoa usuária quer delegar a execução.

A IA deve:

- consultar o repositório e a issue quando aplicável;
- implementar a mudança dentro do escopo autorizado;
- validar o resultado com os checks adequados;
- corrigir problemas encontrados;
- resumir o que mudou e limitações conhecidas;
- sugerir mensagem de commit quando alterar arquivos.

`prod` não autoriza nada sozinho. Em uma solicitação `$yabook`, escritas da
gramática YABook continuam exigindo `do`, e mutações Git continuam seguindo
`git.md`.

## Sintaxe

Definir modo para a conversa atual:

```text
$yabook mode: dev
$yabook mode dev
```

Usar modo apenas na solicitação atual:

```text
$yabook mode: prod - faça os ajustes no estilo do site
$yabook mode: study - me ensine requisições HTTP no React
```

Definir modo por área do projeto:

```text
$yabook def mode prod for estilos do site
$yabook def mode dev for front-end
$yabook def mode study for Angular
```

Também aceite linguagem natural quando a intenção for inequívoca:

```text
Quero aprender Angular fazendo esse projeto, então o front vai ser feito no modo desenvolvimento.
```

## Precedência

Quando houver mais de um modo aplicável, use:

1. modo one-shot na própria solicitação;
2. modo definido para a conversa atual;
3. modo definido por área do projeto;
4. comportamento padrão do YABook.

Se houver conflito material, pergunte antes de executar.

## Persistência

Modo da conversa é temporário e não deve ser gravado em arquivo, memória
permanente, issue ou Project.

Modo por área do projeto só deve ser persistido quando fizer parte do
planejamento aprovado e for consolidado por `$yabook do plan`.

## Segurança

- Não use modo como substituto de `do`.
- Não use `prod` para ignorar issue, branch, revisão, GitHub Project ou `Size`.
- Não use `dev` para executar silenciosamente uma implementação delegada.
- Não use `study` para registrar decisões permanentes sem confirmação.
