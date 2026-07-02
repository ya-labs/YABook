#!/usr/bin/env python3

import argparse
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

# Referências iniciais, orçamento aproximado e quantidade máxima de arquivos.
ROUTES = {
    "help": (["references/help.md"], 1800, 1),
    "help plan": (["references/help.md", "references/help/plan.md"], 2200, 2),
    "mode study": (["references/modes.md", "references/modes/study.md"], 2000, 2),
    "mode dev": (["references/modes.md", "references/modes/dev.md"], 2000, 2),
    "mode prod": (["references/modes.md", "references/modes/prod.md"], 2000, 2),
    "steps": (["references/steps.md"], 1800, 1),
    "discuss": (["references/discuss.md"], 2000, 1),
    "bypass": (["references/bypass.md"], 1800, 1),
    "load": (["references/session-minimo.md", "references/workspace.md"], 2500, 2),
    "status": (["references/workspace.md", "references/git/leitura.md"], 2500, 2),
    "branch": (["references/roteamento.md", "references/artefatos/branch-commit.md"], 2200, 2),
    "commit message": (["references/roteamento.md", "references/artefatos/branch-commit.md"], 2200, 2),
    "issue": (["references/artefatos/issue.md"], 1800, 1),
    "pr": (["references/artefatos/pr-release.md"], 1800, 1),
    "release": (["references/artefatos/pr-release.md"], 1800, 1),
    "docs": (["references/documentacao.md"], 2500, 1),
    "init": (["references/init.md", "references/workspace.md"], 3000, 2),
    "sync": (["references/sync.md"], 2500, 1),
    "apk": (["references/apk.md", "references/workspace.md"], 3000, 2),
    "diagnose": (["references/planejamento/diagnose.md"], 2000, 1),
    "plan start": (["references/planejamento/start.md"], 1800, 1),
    "plan status": (["references/planejamento/status-next.md"], 1800, 1),
    "plan review": (["references/planejamento/review.md"], 1800, 1),
    "plan roadmap": (["references/planejamento/roadmap.md"], 1800, 1),
    "do plan": (["references/planejamento/persistencia.md", "references/git/checkpoint.md"], 3000, 2),
    "dev": (["references/dev.md", "references/git/checkpoint.md"], 3200, 2),
    "do apk": (["references/apk.md", "references/git/checkpoint.md", "references/git/mutacoes.md"], 4000, 3),
    "do issue": (["references/artefatos/issue.md", "references/github/issues-projects.md"], 2500, 2),
    "do branch": (["references/artefatos/branch-commit.md", "references/github/branches.md", "references/git/mutacoes.md"], 3000, 3),
    "do pr": (["references/artefatos/pr-release.md", "references/github/pr-release.md", "references/git/checkpoint.md", "references/git/mutacoes.md"], 4000, 4),
}


def approximate_tokens(paths: list[str]) -> int:
    characters = len((ROOT / "SKILL.md").read_text(encoding="utf-8"))
    characters += sum(len((ROOT / path).read_text(encoding="utf-8")) for path in paths)
    return (characters + 3) // 4


parser = argparse.ArgumentParser()
parser.add_argument("--verbose", action="store_true")
args = parser.parse_args()

failures = []
for route, (paths, budget, max_references) in ROUTES.items():
    tokens = approximate_tokens(paths)
    reasons = []

    if "references/contexto.md" in paths:
        reasons.append("contexto.md não pode ser referência inicial")
    if len(paths) > max_references:
        reasons.append(f"{len(paths)} referências > {max_references}")
    if tokens > budget:
        reasons.append(f"{tokens} tokens > {budget}")

    if args.verbose or reasons:
        status = "FALHOU" if reasons else "OK"
        print(
            f"{status:6} {route:16} {tokens:4}/{budget} tokens "
            f"{len(paths)}/{max_references} referências"
        )
    failures.extend(f"{route}: {reason}" for reason in reasons)

if failures:
    raise SystemExit("\n".join(failures))

print(f"OK: {len(ROUTES)} rotas dentro do orçamento")
