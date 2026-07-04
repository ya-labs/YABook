# Eficiência de contexto da YABook Skill

## Problema

A issue #39 reduziu o tamanho das referências, mas comandos simples ainda podem
carregar contexto, memória, GitHub, documentação e saídas de terminal além do
necessário para executar a demanda.

## Resultado esperado

Cada comando deve começar com o menor contexto seguro e ampliar a descoberta
somente diante de ambiguidade, erro, risco ou informação ausente.

## Escopo

- auditar todos os comandos e suas dependências;
- definir contexto mínimo e gatilhos de ampliação por rota;
- criar um caminho rápido para comandos explícitos e demandas delimitadas;
- limitar inspeções, repetições e volume das saídas;
- definir testes e orçamento aproximado contra regressões.

## Fora de escopo

- controlar o histórico, as instruções globais ou a contabilização da plataforma;
- remover validações obrigatórias de segurança;
- reduzir profundidade de comandos complexos quando o escopo exigir análise.

## Critérios de pronto

- cada comando possui contexto mínimo e gatilhos de ampliação documentados;
- comandos explícitos evitam a matriz geral quando ela não altera o roteamento;
- demandas pequenas usam uma inspeção inicial e uma validação final por padrão;
- memória, GitHub e documentação ampla são consultados apenas com necessidade;
- cenários automatizáveis registram o orçamento esperado por classe de comando.

## Desdobramento aprovado

O aprofundamento dessa capacidade foi estruturado no épico #46, com quatro
frentes complementares:

- classes de custo e profundidade explícita por rota;
- briefs reutilizáveis para condensar contexto válido;
- cache compacto opcional para fatos estáveis do projeto;
- observabilidade local com relatórios e testes de orçamento.

A sessão de planejamento correspondente está em
`docs/planejamento/sessoes/2026-07-02-aprofundar-engenharia-de-custo-yabook.md`.
