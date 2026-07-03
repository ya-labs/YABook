# Briefs reutilizáveis

Use para `issue brief`, `plan brief` e `pr brief`. Briefs são artefatos `C2`,
somente textuais, com até 1.200 caracteres.

## Contrato comum

```md
## Brief

Objetivo:
Escopo:
Fora do escopo:
Critérios de aceite:
Validação mínima:
Riscos:
```

Preencha somente fatos sustentados pela conversa e pelas fontes já válidas.
Omita campo sem utilidade; não invente resposta para completar o modelo.

## Variações

- `issue brief`: condensa a demanda antes de gerar ou desenvolver a issue;
- `plan brief`: registra decisões, dependências, pendências e próxima etapa;
- `pr brief`: resume issue, mudança real, validações e riscos de revisão.

O brief não escreve arquivos ou GitHub. `do` continua obrigatório para
persistência.

## Validade e consumo

O brief vale na conversa enquanto objetivo, escopo e fonte permanecerem
compatíveis. `pr brief` também perde validade quando o diff ou os commits mudam.

Rotas posteriores usam primeiro o brief válido e consultam a fonte longa somente
quando faltar evidência, houver conflito, risco ou mudança. Ao invalidar, informe
o fato que mudou; não reutilize conteúdo stale.
