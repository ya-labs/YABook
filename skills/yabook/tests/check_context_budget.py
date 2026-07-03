#!/usr/bin/env python3

import argparse
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
VALID_CLASSES = {"C0", "C1", "C2", "C3", "C4"}

# Referências iniciais, orçamento aproximado e quantidade máxima de arquivos.
ROUTES = {
    "help": ("C0", ["references/help.md"], 2000, 1),
    "help plan": ("C0", ["references/help.md", "references/help/plan.md"], 2400, 2),
    "mode study": ("C0", ["references/modes.md", "references/modes/study.md"], 2200, 2),
    "mode work": ("C0", ["references/modes.md", "references/modes/work.md"], 2200, 2),
    "mode prod": ("C0", ["references/modes.md", "references/modes/prod.md"], 2200, 2),
    "steps": ("C0", ["references/steps.md"], 2000, 1),
    "discuss": ("C0", ["references/discuss.md"], 2200, 1),
    "bypass": ("C1", ["references/bypass.md"], 2000, 1),
    "load": ("C1", ["references/session-minimo.md", "references/workspace.md"], 2800, 2),
    "status": ("C1", ["references/workspace.md", "references/git/leitura.md"], 2800, 2),
    "branch": ("C1", ["references/roteamento.md", "references/artefatos/branch-commit.md"], 2600, 2),
    "commit message": ("C1", ["references/roteamento.md", "references/artefatos/branch-commit.md"], 2600, 2),
    "apk": ("C1", ["references/apk.md", "references/workspace.md"], 3200, 2),
    "issue": ("C2", ["references/artefatos/issue.md"], 2200, 1),
    "pr": ("C2", ["references/artefatos/pr-release.md"], 2200, 1),
    "release": ("C2", ["references/artefatos/pr-release.md"], 2200, 1),
    "docs": ("C2", ["references/documentacao.md"], 2800, 1),
    "check": ("C2", ["references/quality.md"], 2200, 1),
    "review": ("C2", ["references/quality.md"], 2200, 1),
    "init": ("C2", ["references/init.md", "references/workspace.md"], 3200, 2),
    "sync": ("C2", ["references/sync.md"], 2800, 1),
    "diagnose": ("C2", ["references/planejamento/diagnose.md"], 2400, 1),
    "plan start": ("C2", ["references/planejamento/start.md"], 2200, 1),
    "plan status": ("C2", ["references/planejamento/status-next.md"], 2200, 1),
    "plan review": ("C2", ["references/planejamento/review.md"], 2200, 1),
    "plan roadmap": ("C2", ["references/planejamento/roadmap.md"], 2200, 1),
    "dev quick": ("C3", ["references/dev.md", "references/git/checkpoint.md"], 3600, 2),
    "dev": ("C3", ["references/dev.md", "references/git/checkpoint.md"], 3600, 2),
    "do plan": ("C3", ["references/planejamento/persistencia.md", "references/git/checkpoint.md"], 3200, 2),
    "do apk": ("C3", ["references/apk.md", "references/git/checkpoint.md", "references/git/mutacoes.md"], 4200, 3),
    "do issue": ("C3", ["references/artefatos/issue.md", "references/github/issues-projects.md"], 2800, 2),
    "do branch": ("C3", ["references/artefatos/branch-commit.md", "references/github/branches.md", "references/git/mutacoes.md"], 3200, 3),
    "do pr": ("C3", ["references/artefatos/pr-release.md", "references/github/pr-release.md", "references/git/checkpoint.md", "references/git/mutacoes.md"], 4200, 4),
    "diagnose full": ("C4", ["references/planejamento/diagnose.md"], 2400, 1),
    "check full": ("C4", ["references/quality.md"], 2200, 1),
    "review full": ("C4", ["references/quality.md"], 2200, 1),
    "dev full": ("C4", ["references/dev.md", "references/git/checkpoint.md"], 3600, 2),
}


def approximate_tokens(paths: list[str]) -> int:
    characters = len((ROOT / "SKILL.md").read_text(encoding="utf-8"))
    characters += sum(len((ROOT / path).read_text(encoding="utf-8")) for path in paths)
    return (characters + 3) // 4


parser = argparse.ArgumentParser()
parser.add_argument("--verbose", action="store_true")
args = parser.parse_args()

failures = []
for route, (cost_class, paths, budget, max_references) in ROUTES.items():
    tokens = approximate_tokens(paths)
    reasons = []

    if cost_class not in VALID_CLASSES:
        reasons.append(f"classe inválida: {cost_class}")
    if "references/contexto.md" in paths:
        reasons.append("contexto.md não pode ser referência inicial")
    if len(paths) > max_references:
        reasons.append(f"{len(paths)} referências > {max_references}")
    if tokens > budget:
        reasons.append(f"{tokens} tokens > {budget}")

    if args.verbose or reasons:
        status = "FALHOU" if reasons else "OK"
        print(
            f"{status:6} {cost_class} {route:16} {tokens:4}/{budget} tokens "
            f"{len(paths)}/{max_references} referências"
        )
    failures.extend(f"{route}: {reason}" for reason in reasons)

if failures:
    raise SystemExit("\n".join(failures))

print(f"OK: {len(ROUTES)} rotas dentro do orçamento")
