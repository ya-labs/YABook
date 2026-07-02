#!/usr/bin/env python3

import json
import sys
from pathlib import Path


TESTS = Path(__file__).resolve().parent
BUDGETS = json.loads(
    (TESTS / "context-runtime-budgets.json").read_text(encoding="utf-8")
)
MAX_OUTPUT_PER_OPERATION = 4000


def fail(message: str) -> None:
    raise SystemExit(f"FALHOU: {message}")


if len(sys.argv) != 2:
    fail("uso: check_context_runtime.py <relatorio.json>")

report = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
scenario = report.get("scenario")
if scenario not in BUDGETS:
    fail(f"cenário desconhecido: {scenario}")

budget = BUDGETS[scenario]
references = set(report.get("references", []))
operations = report.get("operations", [])
commands = sum(operation.get("commands", 0) for operation in operations)
output_chars = sum(operation.get("output_chars", 0) for operation in operations)
rounds = report.get("rounds", 0)
rediscovered = report.get("rediscovered_facts", [])
expansions = report.get("expansions", [])

violations = []
if "references/contexto.md" in references:
    violations.append(("contexto", "contexto.md carregado em rota explícita"))
if len(references) > budget["max_references"]:
    violations.append((
        "references",
        f"{len(references)} referências > {budget['max_references']}",
    ))
if commands > budget["max_commands"]:
    violations.append(("commands", f"{commands} comandos > {budget['max_commands']}"))
if output_chars > budget["max_output_chars"]:
    violations.append((
        "output_chars",
        f"{output_chars} caracteres > {budget['max_output_chars']}",
    ))
if rounds > budget["max_rounds"]:
    violations.append(("rounds", f"{rounds} rodadas > {budget['max_rounds']}"))
if rediscovered:
    violations.append((
        "rediscovered_facts",
        "fatos redescobertos sem mudança: " + ", ".join(rediscovered),
    ))

for index, operation in enumerate(operations, start=1):
    size = operation.get("output_chars", 0)
    if size > MAX_OUTPUT_PER_OPERATION:
        violations.append((
            "output_per_operation",
            f"operação {index}: {size} caracteres > {MAX_OUTPUT_PER_OPERATION}",
        ))

if violations:
    justified = {
        expansion.get("metric")
        for expansion in expansions
        if str(expansion.get("reason", "")).strip()
    }
    pending = [
        message
        for metric, message in violations
        if metric not in justified or metric in {"contexto", "rediscovered_facts"}
    ]
    if pending:
        fail("; ".join(pending))

print(
    f"OK: {scenario} — {len(references)} referências, {commands} comandos, "
    f"{output_chars} caracteres, {rounds} rodadas"
)
