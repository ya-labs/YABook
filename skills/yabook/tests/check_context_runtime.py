#!/usr/bin/env python3

import json
import sys
from pathlib import Path


TESTS = Path(__file__).resolve().parent
BUDGETS = json.loads(
    (TESTS / "context-runtime-budgets.json").read_text(encoding="utf-8")
)
MAX_OUTPUT_PER_OPERATION = 4000
MEASUREMENT_QUALITIES = {"exact", "approx", "unavailable"}
DERIVED_METRICS = {
    "references": lambda report: len(set(report.get("references", []))),
    "consulted_files": lambda report: len(set(report.get("consulted_files", []))),
    "commands": lambda report: sum(
        operation.get("commands", 0) for operation in report.get("operations", [])
    ),
    "output_chars": lambda report: sum(
        operation.get("output_chars", 0) for operation in report.get("operations", [])
    ),
    "rounds": lambda report: report.get("rounds", 0),
    "directed_searches": lambda report: len(report.get("directed_searches", [])),
    "rediscovered_facts": lambda report: len(report.get("rediscovered_facts", [])),
}


def fail(message: str) -> None:
    raise SystemExit(f"FALHOU: {message}")


def plural(value: int, singular: str, plural_form: str) -> str:
    return singular if value == 1 else plural_form


def validate_measurements(report: dict) -> list[str]:
    errors = []
    measurements = report.get("measurements")
    if not isinstance(measurements, dict):
        return ["measurements ausente ou inválido"]

    for name, entry in measurements.items():
        if not isinstance(entry, dict):
            errors.append(f"measurement inválido: {name}")
            continue

        quality = entry.get("quality")
        if quality not in MEASUREMENT_QUALITIES:
            errors.append(f"measurement {name} com quality inválido: {quality!r}")
            continue

        value = entry.get("value")
        if quality == "unavailable":
            if value is not None:
                errors.append(f"measurement {name} indisponível não pode informar valor")
            if not str(entry.get("note", "")).strip():
                errors.append(f"measurement {name} indisponível exige note")
            continue

        if not isinstance(value, int) or value < 0:
            errors.append(f"measurement {name} exige value inteiro não negativo")
            continue

    for name, derive in DERIVED_METRICS.items():
        entry = measurements.get(name)
        if not isinstance(entry, dict):
            errors.append(f"measurement ausente: {name}")
            continue

        if entry.get("quality") == "unavailable":
            errors.append(f"measurement {name} não pode ser indisponível")
            continue

        value = entry.get("value")
        derived = derive(report)
        if value != derived:
            errors.append(f"measurement {name}={value} difere do observado {derived}")

    return errors


def validate_report(report: dict) -> tuple[list[str], dict[str, int]]:
    scenario = report.get("scenario")
    if scenario not in BUDGETS:
        return ([f"cenário desconhecido: {scenario}"], {})

    budget = BUDGETS[scenario]
    route = str(report.get("route", "")).strip()
    cost_class = report.get("class")
    references = set(report.get("references", []))
    consulted_files = set(report.get("consulted_files", []))
    operations = report.get("operations", [])
    rounds = report.get("rounds", 0)
    rediscovered = report.get("rediscovered_facts", [])
    expansions = report.get("expansions", [])
    directed_searches = report.get("directed_searches", [])
    observed = {
        "references": len(references),
        "consulted_files": len(consulted_files),
        "commands": sum(operation.get("commands", 0) for operation in operations),
        "output_chars": sum(
            operation.get("output_chars", 0) for operation in operations
        ),
        "rounds": rounds,
        "directed_searches": len(directed_searches),
    }
    violations = []

    if not route:
        violations.append(("route", "route ausente ou vazia"))
    if cost_class != budget["class"]:
        violations.append((
            "class",
            f"classe observada {cost_class!r} difere de {budget['class']!r}",
        ))
    if "references/contexto.md" in references:
        violations.append(("contexto", "contexto.md carregado em rota explícita"))
    if observed["references"] > budget["max_references"]:
        violations.append((
            "references",
            f"{observed['references']} referências > {budget['max_references']}",
        ))
    if observed["consulted_files"] > budget["max_consulted_files"]:
        violations.append((
            "consulted_files",
            f"{observed['consulted_files']} arquivos consultados > "
            f"{budget['max_consulted_files']}",
        ))
    if observed["commands"] > budget["max_commands"]:
        violations.append((
            "commands",
            f"{observed['commands']} comandos > {budget['max_commands']}",
        ))
    if observed["output_chars"] > budget["max_output_chars"]:
        violations.append((
            "output_chars",
            f"{observed['output_chars']} caracteres > {budget['max_output_chars']}",
        ))
    if observed["rounds"] > budget["max_rounds"]:
        violations.append((
            "rounds",
            f"{observed['rounds']} rodadas > {budget['max_rounds']}",
        ))
    if observed["directed_searches"] > budget["max_directed_searches"]:
        violations.append((
            "directed_searches",
            f"{observed['directed_searches']} buscas direcionadas > "
            f"{budget['max_directed_searches']}",
        ))
    if rediscovered:
        violations.append((
            "rediscovered_facts",
            "fatos redescobertos sem mudança: " + ", ".join(rediscovered),
        ))

    for metric in ("references", "consulted_files", "commands", "output_chars", "rounds"):
        if not any(expansion.get("metric") == metric for expansion in expansions):
            continue

    for index, operation in enumerate(operations, start=1):
        size = operation.get("output_chars", 0)
        if size > MAX_OUTPUT_PER_OPERATION:
            violations.append((
                "output_per_operation",
                f"operação {index}: {size} caracteres > {MAX_OUTPUT_PER_OPERATION}",
            ))

    for index, expansion in enumerate(expansions, start=1):
        metric = str(expansion.get("metric", "")).strip()
        reason = str(expansion.get("reason", "")).strip()
        if not metric:
            violations.append((f"expansion_{index}", f"expansão {index} sem metric"))
        if not reason:
            violations.append((
                f"expansion_{index}",
                f"expansão {index} sem justificativa",
            ))

    violations.extend(
        ("measurement", error) for error in validate_measurements(report)
    )

    if violations:
        justified = {
            expansion.get("metric")
            for expansion in expansions
            if str(expansion.get("reason", "")).strip()
        }
        pending = [
            message
            for metric, message in violations
            if cost_class == "C0"
            or metric not in justified
            or metric
            in {"class", "contexto", "rediscovered_facts", "route", "measurement"}
            or str(metric).startswith("expansion_")
        ]
        if pending:
            return (pending, observed)

    return ([], observed)


def main(argv: list[str]) -> None:
    if len(argv) != 2:
        fail("uso: check_context_runtime.py <relatorio.json>")

    report = json.loads(Path(argv[1]).read_text(encoding="utf-8"))
    errors, observed = validate_report(report)
    if errors:
        fail("; ".join(errors))

    print(
        f"OK: {report['scenario']} {report['route']} [{report['class']}] — "
        f"{observed['references']} referências, "
        f"{observed['consulted_files']} arquivos consultados, "
        f"{observed['commands']} comandos, "
        f"{observed['output_chars']} caracteres, "
        f"{observed['rounds']} rodadas, "
        f"{observed['directed_searches']} "
        f"{plural(observed['directed_searches'], 'busca direcionada', 'buscas direcionadas')}"
    )


if __name__ == "__main__":
    main(sys.argv)
