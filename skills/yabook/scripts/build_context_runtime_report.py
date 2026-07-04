#!/usr/bin/env python3

import argparse
import importlib.util
import json
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = SKILL_ROOT.parents[1]
VALIDATOR = SKILL_ROOT / "tests" / "check_context_runtime.py"
SPEC = importlib.util.spec_from_file_location("context_runtime", VALIDATOR)
context_runtime = importlib.util.module_from_spec(SPEC)
assert SPEC.loader
SPEC.loader.exec_module(context_runtime)


DEFAULT_UNAVAILABLE_NOTE = "o runtime local não expõe tokens reais por operação"


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def measurement_block(capture: dict) -> dict:
    draft = capture.get("measurements", {})
    measurements = {}

    for name, derive in context_runtime.DERIVED_METRICS.items():
        entry = draft.get(name, {})
        measurements[name] = {
            "quality": entry.get("quality", "exact"),
            "value": derive(capture),
        }

    tokens_entry = draft.get("tokens", {})
    quality = tokens_entry.get("quality", "unavailable")
    if quality == "unavailable":
        measurements["tokens"] = {
            "quality": "unavailable",
            "note": str(tokens_entry.get("note", DEFAULT_UNAVAILABLE_NOTE)).strip()
            or DEFAULT_UNAVAILABLE_NOTE,
        }
    else:
        value = tokens_entry.get("value")
        if not isinstance(value, int) or value < 0:
            raise ValueError("tokens disponível exige value inteiro não negativo")
        measurements["tokens"] = {"quality": quality, "value": value}

    return measurements


def normalize_capture(capture: dict) -> dict:
    scenario = str(capture.get("scenario", "")).strip()
    if not scenario:
        raise ValueError("scenario ausente")

    route = str(capture.get("route", "")).strip()
    if not route:
        raise ValueError("route ausente")

    budget = context_runtime.BUDGETS.get(scenario)
    if not budget:
        raise ValueError(f"cenário desconhecido: {scenario}")

    report = {
        "scenario": scenario,
        "route": route,
        "class": capture.get("class", budget["class"]),
        "references": capture.get("references", []),
        "consulted_files": capture.get("consulted_files", []),
        "operations": capture.get("operations", []),
        "rounds": capture.get("rounds", 0),
        "directed_searches": capture.get("directed_searches", []),
        "reused_facts": capture.get("reused_facts", []),
        "rediscovered_facts": capture.get("rediscovered_facts", []),
        "brief": capture.get("brief", {"available": False, "used": False}),
        "cache": capture.get(
            "cache",
            {"available": False, "used": False, "status": "absent"},
        ),
        "expansions": capture.get("expansions", []),
    }
    report["measurements"] = measurement_block(report | {"measurements": capture.get("measurements", {})})
    return report


def build_report(repo: Path, capture_path: str, output_path: str | None = None) -> dict:
    capture_file = (repo / capture_path).resolve()
    capture = load_json(capture_file)
    report = normalize_capture(capture)
    errors, _ = context_runtime.validate_report(report)
    if errors:
        raise ValueError("; ".join(errors))

    if output_path:
        destination = (repo / output_path).resolve()
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(
            json.dumps(report, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
    return report


def main(argv: list[str]) -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("capture")
    parser.add_argument("--output")
    args = parser.parse_args(argv[1:])

    build_report(REPO_ROOT, args.capture, args.output)
    print("OK: relatório de runtime gerado")


if __name__ == "__main__":
    main(__import__("os").sys.argv)
