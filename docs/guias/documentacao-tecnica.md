# Documentação técnica

Este guia define como a YA LABS organiza documentação técnica nos projetos.

O objetivo é manter documentos úteis para desenvolvimento real, sem transformar a documentação em burocracia difícil de manter.

## Princípios

- Documente decisões e contratos que ajudam outra pessoa a continuar o trabalho.
- Escreva em português claro, com acentos e UTF-8.
- Use Markdown simples.
- Prefira exemplos reais do projeto.
- Não invente arquitetura, endpoint ou fluxo que ainda não existe.
- Atualize a documentação quando uma mudança alterar comportamento, contrato ou processo.

## O que documentar no projeto

Cada projeto deve manter sua própria documentação específica.

Exemplos:

- visão, problema, público e escopo do produto;
- stack e setup local;
- arquitetura real;
- requisitos e fluxos de uso;
- contratos de API, eventos, arquivos, comandos ou integrações;
- variáveis de ambiente e deploy;
- decisões técnicas importantes;
- provas técnicas e critérios de pronto.

## Estrutura recomendada

```text
docs/
|-- README.md
|-- produto/
|-- arquitetura/
|-- requisitos/
|-- fluxos/
|-- interface/
|-- contratos/
|-- processos/
|-- adrs/
|-- rfcs/
|-- prototipos/
|-- release/
|-- uso/
`-- planejamento/
```

Essa estrutura pode ser adaptada conforme o tamanho do projeto.

Projetos pequenos não precisam criar pastas vazias sem uso imediato.

## Uso recomendado das pastas

| Pasta | Uso |
| --- | --- |
| `docs/produto/` | Visão, problema, público, escopo inicial e alternativas. |
| `docs/arquitetura/` | Arquitetura conceitual, módulos e responsabilidades. |
| `docs/requisitos/` | Capacidades esperadas e requisitos funcionais ou não funcionais. |
| `docs/fluxos/` | Jornadas e sequências de uso. |
| `docs/interface/` | Diretrizes visuais, estados de tela e critérios de UX. |
| `docs/contratos/` | APIs, eventos, arquivos, comandos, entradas e saídas. |
| `docs/processos/` | Regras locais que complementam o YABook. |
| `docs/adrs/` | Decisões técnicas aceitas. |
| `docs/rfcs/` | Propostas ainda em discussão. |
| `docs/prototipos/` | Provas técnicas, experimentos e validações. |
| `docs/release/` | Critérios de pronto, release e riscos aceitos. |
| `docs/uso/` | Manuais e trilhas da pessoa usuária. |
| `docs/planejamento/` | Etapas macro estáticas, sem status operacional. |

## Markdown e GitHub

Markdown deve guardar conhecimento estável do projeto.

GitHub deve guardar trabalho executável, como backlog, responsáveis, Project, milestones, épicos, issues, Pull Requests e progresso.

Não use Markdown para acompanhar status de cards, próxima issue operacional ou lista detalhada de tarefas em andamento.

## Contratos de API

Quando documentar uma API, inclua:

- método HTTP;
- rota;
- parâmetros;
- exemplo de request, quando existir;
- exemplo de response;
- estados de sucesso;
- estados de erro;
- estados vazios esperados.

Exemplo:

````md
## Buscar perfil

GET /users/{id}

### Parâmetros

- `id`: identificador do usuário.

### Response de sucesso

```json
{
  "id": "123",
  "name": "Nícolas"
}
```

### Estados tratados

- `200`: usuário encontrado.
- `404`: usuário não encontrado.
````

## Decisões técnicas

Registre decisões quando elas ajudarem o time a entender por que uma solução foi escolhida.

Uma decisão técnica deve responder:

- qual problema estava sendo resolvido;
- quais opções foram consideradas;
- qual decisão foi tomada;
- quais impactos ou limitações existem.

Use ADR para decisão aceita e RFC para proposta ainda aberta.

## Provas técnicas

Use provas técnicas para validar riscos antes de transformar uma ideia em contrato final.

Uma prova técnica deve deixar claro:

- objetivo da validação;
- relação com requisito, etapa ou decisão;
- pré-condições;
- cenários executados;
- resultado observado;
- limites do que não foi validado.

## Regra prática

Documentação boa é aquela que reduz dúvida na hora de implementar, revisar, testar ou dar manutenção.

Se o documento não ajuda ninguém a tomar decisão ou executar trabalho real, simplifique.
