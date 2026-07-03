# Cenários do cache compacto

Confirme que `.yabook/context-cache.md`:

- é opcional e limitado a 3.000 caracteres;
- não é criado ou atualizado por `load`;
- aceita `reference` ancestral quando os fingerprints continuam válidos;
- é invalidado por branch, remote, regras ou planejamento divergentes;
- rejeita fontes ausentes ou fora da raiz;
- não bloqueia rotas quando ausente ou inválido;
- não substitui fontes reais em decisão crítica, conflito ou risco;
- pode ser removido sem afetar o fluxo principal.

Execute:

```text
python -m unittest skills/yabook/tests/test_context_cache.py
```
