# Documentação no padrão YABook

Use esta referência para decidir onde documentar e quando podar documentação.

## Regra principal

Markdown guarda conhecimento estável.

GitHub guarda trabalho executável: backlog, status, responsáveis, Project, milestones, issues, Pull Requests e progresso.

## Fonte única da estrutura

Em projetos que seguem o template YABook, use:

```text
docs/guia-da-documentacao.md
```

Esse guia define onde cada assunto deve ficar.

Não repita a matriz de pastas em vários documentos.

## O que documentar no projeto

- visão, problema, público e escopo do produto;
- stack e setup local;
- arquitetura real;
- requisitos e fluxos de uso;
- contratos de API, eventos, arquivos, comandos ou integrações;
- variáveis de ambiente e deploy;
- decisões técnicas importantes;
- provas técnicas e critérios de pronto.

## O que não documentar no YABook

Não coloque no YABook conteúdo específico de produto:

- endpoints reais;
- arquitetura específica de uma aplicação;
- variáveis de ambiente;
- deploy próprio de projeto;
- fluxo de negócio exclusivo;
- roadmap interno de produto.

## Antes de criar documento novo

Confirme:

- quem vai usar o documento;
- quando ele será consultado;
- qual decisão ou ação ele apoia;
- se o conteúdo cabe melhor em documento existente;
- se a informação é estável o bastante para Markdown.

## Poda

Remova, funda ou reescreva documentos que:

- repetem regra já documentada;
- não ajudam execução, revisão ou decisão;
- descrevem intenção sem orientar ação;
- misturam status operacional com conhecimento estável;
- parecem texto genérico gerado por IA.

## Templates mínimos

Para um projeto YA LABS, prefira manter:

- `README.md`;
- `AGENTS.md`;
- `docs/README.md`;
- `docs/guia-da-documentacao.md`;
- `docs/guia-de-documentacao-para-ia.md`.

Crie outras pastas apenas quando houver conteúdo real.
