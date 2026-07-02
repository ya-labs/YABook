#!/usr/bin/env python3

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

# Orçamentos aproximados por caracteres / 4. Incluem SKILL.md e somente as
# referências iniciais da rota; fontes do projeto e histórico ficam de fora.
ROUTES = {
    "help": (["references/help.md"], 3000),
    "mode": (["references/modes.md"], 3000),
    "steps": (["references/steps.md"], 3000),
    "discuss": (["references/discuss.md"], 2000),
    "bypass": (["references/bypass.md"], 1800),
    "load": (["references/session-minimo.md", "references/workspace.md"], 2500),
    "status": (["references/workspace.md"], 2200),
    "branch": (["references/roteamento.md", "references/artefatos/branch-commit.md"], 2200),
    "commit message": (["references/roteamento.md", "references/artefatos/branch-commit.md"], 2200),
    "issue": (["references/artefatos/issue.md"], 1800),
    "pr": (["references/artefatos/pr-release.md"], 1800),
    "release": (["references/artefatos/pr-release.md"], 1800),
    "docs": (["references/documentacao.md"], 2500),
    "init": (["references/init.md", "references/workspace.md"], 3000),
    "sync": (["references/sync.md"], 2500),
    "apk": (["references/apk.md", "references/workspace.md"], 3000),
    "diagnose": (["references/planejamento/diagnose.md"], 2000),
    "plan start": (["references/planejamento/start.md"], 1800),
    "plan status": (["references/planejamento/status-next.md"], 1800),
    "plan review": (["references/planejamento/review.md"], 1800),
    "plan roadmap": (["references/planejamento/roadmap.md"], 1800),
    "do plan": (["references/planejamento/persistencia.md", "references/git.md"], 3500),
    "dev": (["references/dev.md", "references/git.md"], 4000),
    "do apk": (["references/apk.md", "references/git.md"], 4000),
    "do issue": (["references/artefatos/issue.md", "references/github.md"], 4000),
    "do pr": (["references/artefatos/pr-release.md", "references/git.md", "references/github.md"], 5000),
}


def approximate_tokens(paths: list[str]) -> int:
    characters = len((ROOT / "SKILL.md").read_text(encoding="utf-8"))
    characters += sum(len((ROOT / path).read_text(encoding="utf-8")) for path in paths)
    return (characters + 3) // 4


failures = []
for route, (paths, budget) in ROUTES.items():
    if "references/contexto.md" in paths:
        failures.append(f"{route}: contexto.md não pode ser referência inicial")
        continue

    tokens = approximate_tokens(paths)
    status = "OK" if tokens <= budget else "FALHOU"
    print(f"{status:6} {route:16} {tokens:4}/{budget} tokens aproximados")
    if tokens > budget:
        failures.append(f"{route}: {tokens} > {budget}")

if failures:
    raise SystemExit("\n".join(failures))
