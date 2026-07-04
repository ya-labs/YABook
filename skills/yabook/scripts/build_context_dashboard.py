#!/usr/bin/env python3

import argparse
import json
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REGRESSION_METRICS = (
    "commands",
    "output_chars",
    "rounds",
    "directed_searches",
    "rediscovered_facts",
)

INDICATOR_CATALOG = [
    {
        "indicator": "Execuções por rota",
        "source": "payload.route",
        "reliability": "exact",
        "meaning": "Quantidade de execuções agrupadas por rota oficial.",
    },
    {
        "indicator": "Classe observada",
        "source": "payload.class",
        "reliability": "exact",
        "meaning": "Classe C0 a C4 registrada pelo relatório exportado.",
    },
    {
        "indicator": "Ampliações",
        "source": "payload.summary.expansion_count / expansion_metrics",
        "reliability": "exact",
        "meaning": "Mostra quantas ampliações ocorreram e quais métricas exigiram expansão.",
    },
    {
        "indicator": "Redescoberta",
        "source": "payload.measurements.rediscovered_facts / payload.summary.rediscovered_facts_count",
        "reliability": "exact",
        "meaning": "Indica redescobertas de fatos que já eram conhecidos no contexto.",
    },
    {
        "indicator": "Tokens",
        "source": "payload.measurements.tokens",
        "reliability": "unavailable",
        "meaning": "Permanece indisponível quando o runtime não expõe o valor real.",
    },
]


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def validate_payload(payload: dict, source: Path) -> list[str]:
    errors = []
    required_top_level = {"version", "exported_at", "route", "class", "measurements", "operations", "summary"}
    missing = required_top_level - set(payload)
    if missing:
        errors.append(f"{source.name}: faltam campos obrigatórios: {', '.join(sorted(missing))}")

    if payload.get("version") != 1:
        errors.append(f"{source.name}: versão de contrato inválida")

    for forbidden in ("references", "consulted_files", "directed_searches", "expansions", "reused_facts"):
        if forbidden in payload:
            errors.append(f"{source.name}: payload bruto não é aceito no dashboard ({forbidden})")

    if not isinstance(payload.get("measurements"), dict):
        errors.append(f"{source.name}: measurements precisa ser objeto")

    if not isinstance(payload.get("summary"), dict):
        errors.append(f"{source.name}: summary precisa ser objeto")

    if not isinstance(payload.get("operations"), list):
        errors.append(f"{source.name}: operations precisa ser lista")

    return errors


def parse_exported_at(value: str) -> datetime:
    normalized = value.replace("Z", "+00:00")
    return datetime.fromisoformat(normalized)


def measurement_value(payload: dict, name: str) -> int | None:
    entry = payload.get("measurements", {}).get(name, {})
    if entry.get("quality") == "unavailable":
        return None
    value = entry.get("value")
    if isinstance(value, (int, float)):
        return int(value)
    return None


def measurement_quality(payload: dict, name: str) -> str:
    entry = payload.get("measurements", {}).get(name, {})
    return str(entry.get("quality", "unavailable"))


def summarize_operations(runs: list[dict]) -> list[dict]:
    aggregated: dict[str, dict] = {}
    for run in runs:
        for operation in run.get("operations", []):
            tool = str(operation.get("tool", "unknown"))
            bucket = aggregated.setdefault(tool, {"tool": tool, "commands": 0, "output_chars": 0})
            bucket["commands"] += int(operation.get("commands", 0))
            bucket["output_chars"] += int(operation.get("output_chars", 0))
    return sorted(aggregated.values(), key=lambda item: (-item["commands"], item["tool"]))


def summarize_quality(runs: list[dict]) -> list[dict]:
    metric_names = sorted({name for run in runs for name in run.get("measurements", {}).keys()})
    rows = []
    for metric in metric_names:
        counts = Counter(measurement_quality(run, metric) for run in runs)
        rows.append(
            {
                "metric": metric,
                "exact": counts.get("exact", 0),
                "approx": counts.get("approx", 0),
                "unavailable": counts.get("unavailable", 0),
                "source": f"payload.measurements.{metric}",
            }
        )
    return rows


def summarize_classes(runs: list[dict]) -> list[dict]:
    counts = Counter(str(run.get("class", "unknown")) for run in runs)
    return [{"class": label, "runs": counts[label]} for label in sorted(counts)]


def summarize_expansions(runs: list[dict]) -> list[dict]:
    counts = Counter()
    for run in runs:
        for metric in run.get("summary", {}).get("expansion_metrics", []):
            counts[str(metric)] += 1
    return [{"metric": metric, "runs": counts[metric]} for metric in sorted(counts)]


def summarize_routes(runs: list[dict]) -> list[dict]:
    grouped: dict[str, list[dict]] = defaultdict(list)
    for run in runs:
        grouped[str(run.get("route", "unknown"))].append(run)

    rows = []
    for route, route_runs in grouped.items():
        ordered = sorted(route_runs, key=lambda item: parse_exported_at(item["exported_at"]))
        latest = ordered[-1]
        previous = ordered[-2] if len(ordered) > 1 else None
        regressions = []
        if previous:
            for metric in REGRESSION_METRICS:
                current_value = measurement_value(latest, metric)
                previous_value = measurement_value(previous, metric)
                if current_value is None or previous_value is None:
                    continue
                if current_value > previous_value:
                    regressions.append(
                        {
                            "metric": metric,
                            "previous": previous_value,
                            "current": current_value,
                            "delta": current_value - previous_value,
                        }
                    )

        rows.append(
            {
                "route": route,
                "runs": len(ordered),
                "latest_class": latest.get("class"),
                "latest_exported_at": latest.get("exported_at"),
                "latest_expansions": int(latest.get("summary", {}).get("expansion_count", 0)),
                "latest_rediscovered_facts": int(latest.get("summary", {}).get("rediscovered_facts_count", 0)),
                "latest_commands": measurement_value(latest, "commands"),
                "latest_output_chars": measurement_value(latest, "output_chars"),
                "regressions": regressions,
                "regression_count": len(regressions),
            }
        )

    return sorted(rows, key=lambda item: (-item["regression_count"], item["route"]))


def build_dataset(payloads: list[dict]) -> dict:
    ordered_runs = sorted(payloads, key=lambda item: parse_exported_at(item["exported_at"]))
    routes = summarize_routes(ordered_runs)
    regressions = sum(route["regression_count"] for route in routes)
    return {
        "version": 1,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "source_contract_version": 1,
        "dashboard_kind": "context_telemetry",
        "read_only": True,
        "notes": [
            "Este dashboard consome somente o payload oficial exportado pela telemetria externa opt-in.",
            "Indicadores indisponíveis permanecem sem valor inventado.",
            "A visualização é somente leitura e não coleta novos dados.",
        ],
        "overview": {
            "total_runs": len(ordered_runs),
            "routes": len({run.get('route') for run in ordered_runs}),
            "regressions": regressions,
            "runs_with_expansion": sum(1 for run in ordered_runs if run.get("summary", {}).get("expansion_count", 0) > 0),
            "runs_with_rediscovery": sum(
                1 for run in ordered_runs if run.get("summary", {}).get("rediscovered_facts_count", 0) > 0
            ),
        },
        "indicator_catalog": INDICATOR_CATALOG,
        "routes": routes,
        "classes": summarize_classes(ordered_runs),
        "quality": summarize_quality(ordered_runs),
        "expansion_metrics": summarize_expansions(ordered_runs),
        "operations": summarize_operations(ordered_runs),
        "runs": ordered_runs,
    }


def build_dashboard(repo: Path, inputs: list[str], output: str | None = None) -> dict:
    payloads = []
    errors = []
    for raw_path in inputs:
        file_path = (repo / raw_path).resolve()
        payload = load_json(file_path)
        errors.extend(validate_payload(payload, file_path))
        payloads.append(payload)

    if errors:
        raise ValueError("; ".join(errors))

    dataset = build_dataset(payloads)
    if output:
        destination = (repo / output).resolve()
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(json.dumps(dataset, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return dataset


def main(argv: list[str]) -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("inputs", nargs="+")
    parser.add_argument("--output")
    args = parser.parse_args(argv[1:])

    build_dashboard(ROOT.parents[1], args.inputs, args.output)
    print("OK: dashboard de contexto gerado")


if __name__ == "__main__":
    main(__import__("os").sys.argv)
