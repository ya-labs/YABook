#!/usr/bin/env python3

import argparse
import importlib.util
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from urllib import error, request


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CONFIG = ".yabook/context-telemetry.json"
VALIDATOR = ROOT / "tests" / "check_context_runtime.py"
SPEC = importlib.util.spec_from_file_location("context_runtime", VALIDATOR)
context_runtime = importlib.util.module_from_spec(SPEC)
assert SPEC.loader
SPEC.loader.exec_module(context_runtime)


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def load_config(repo: Path, config_path: str) -> dict:
    config_file = (repo / config_path).resolve()
    if not config_file.exists():
        return {"enabled": False, "status": "absent"}

    config = load_json(config_file)
    config.setdefault("enabled", False)
    config.setdefault("timeout_seconds", 5)
    config["status"] = "present"
    return config


def measurement_payload(measurements: dict) -> dict:
    payload = {}
    for name, entry in measurements.items():
        item = {"quality": entry["quality"]}
        if entry["quality"] != "unavailable":
            item["value"] = entry["value"]
        payload[name] = item
    return payload


def aggregate_operations(operations: list[dict]) -> list[dict]:
    aggregated = {}
    for operation in operations:
        tool = str(operation.get("tool", "unknown"))
        bucket = aggregated.setdefault(tool, {"tool": tool, "commands": 0, "output_chars": 0})
        bucket["commands"] += int(operation.get("commands", 0))
        bucket["output_chars"] += int(operation.get("output_chars", 0))
    return list(aggregated.values())


def sanitize_report(report: dict) -> dict:
    measurements = report.get("measurements", {})
    brief = report.get("brief", {})
    cache = report.get("cache", {})

    return {
        "version": 1,
        "exported_at": datetime.now(timezone.utc).isoformat(),
        "scenario": report["scenario"],
        "route": report["route"],
        "class": report["class"],
        "measurements": measurement_payload(measurements),
        "operations": aggregate_operations(report.get("operations", [])),
        "summary": {
            "reused_facts_count": len(report.get("reused_facts", [])),
            "rediscovered_facts_count": len(report.get("rediscovered_facts", [])),
            "expansion_count": len(report.get("expansions", [])),
            "expansion_metrics": sorted(
                {
                    str(expansion.get("metric", "")).strip()
                    for expansion in report.get("expansions", [])
                    if str(expansion.get("metric", "")).strip()
                }
            ),
            "brief_available": bool(brief.get("available")),
            "brief_used": bool(brief.get("used")),
            "cache_available": bool(cache.get("available")),
            "cache_used": bool(cache.get("used")),
            "cache_status": cache.get("status", "unknown"),
        },
    }


def build_headers(config: dict) -> dict:
    headers = {
        "Content-Type": "application/json; charset=utf-8",
        "User-Agent": "yabook-context-telemetry/1",
    }
    headers.update(config.get("headers", {}))
    token_env = str(config.get("token_env", "")).strip()
    if token_env:
        token = os.getenv(token_env)
        if token:
            headers["Authorization"] = f"Bearer {token}"
    return headers


def send_payload(payload: dict, config: dict) -> dict:
    endpoint = str(config.get("endpoint", "")).strip()
    if not endpoint:
        raise ValueError("endpoint ausente na configuração de telemetria")

    body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    req = request.Request(
        endpoint,
        data=body,
        headers=build_headers(config),
        method="POST",
    )
    timeout = int(config.get("timeout_seconds", 5))
    with request.urlopen(req, timeout=timeout) as response:
        status = getattr(response, "status", None) or response.getcode()
    return {"status": status}


def export_report(
    repo: Path,
    report_path: str,
    config_path: str = DEFAULT_CONFIG,
    output_path: str | None = None,
    sender=send_payload,
) -> dict:
    report_file = (repo / report_path).resolve()
    report = load_json(report_file)
    errors, _ = context_runtime.validate_report(report)
    if errors:
        raise ValueError("; ".join(errors))

    payload = sanitize_report(report)
    if output_path:
        destination = (repo / output_path).resolve()
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )

    config = load_config(repo, config_path)
    if not config.get("enabled"):
        return {
            "mode": "disabled",
            "reason": "telemetria externa opt-in desativada",
            "payload": payload,
        }

    try:
        response = sender(payload, config)
    except (OSError, ValueError, error.URLError) as exc:
        return {
            "mode": "warning",
            "reason": f"envio não bloqueante falhou: {exc}",
            "payload": payload,
        }

    return {"mode": "sent", "response": response, "payload": payload}


def main(argv: list[str]) -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("report")
    parser.add_argument("--config", default=DEFAULT_CONFIG)
    parser.add_argument("--output")
    args = parser.parse_args(argv[1:])

    result = export_report(ROOT.parents[1], args.report, args.config, args.output)
    if result["mode"] == "sent":
        print("ENVIADO: telemetria externa publicada com sucesso")
        return
    if result["mode"] == "warning":
        print(f"AVISO: {result['reason']}")
        return
    print("DESATIVADO: telemetria externa opt-in não configurada")


if __name__ == "__main__":
    main(os.sys.argv)
