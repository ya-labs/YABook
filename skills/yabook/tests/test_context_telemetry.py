#!/usr/bin/env python3

import importlib.util
import sys
import unittest
from pathlib import Path


sys.dont_write_bytecode = True
SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "export_context_telemetry.py"
SPEC = importlib.util.spec_from_file_location("context_telemetry", SCRIPT)
context_telemetry = importlib.util.module_from_spec(SPEC)
assert SPEC.loader
SPEC.loader.exec_module(context_telemetry)


class ContextTelemetryTest(unittest.TestCase):
    def base_report(self) -> dict:
        return {
            "scenario": "dev_ready",
            "route": "dev",
            "class": "C3",
            "references": [
                "references/dev.md",
                "references/git/checkpoint.md",
            ],
            "consulted_files": [
                "skills/yabook/tests/context-runtime.md",
                "skills/yabook/tests/runtime-report.example.json",
            ],
            "operations": [
                {"tool": "terminal", "commands": 4, "output_chars": 1200},
                {"tool": "search", "commands": 1, "output_chars": 1800},
            ],
            "rounds": 5,
            "directed_searches": [
                {
                    "tool": "rg",
                    "query": "runtime observabilidade orçamento",
                    "reason": "localizar o cenário",
                }
            ],
            "measurements": {
                "references": {"quality": "exact", "value": 2},
                "consulted_files": {"quality": "exact", "value": 2},
                "commands": {"quality": "exact", "value": 5},
                "output_chars": {"quality": "exact", "value": 3000},
                "rounds": {"quality": "exact", "value": 5},
                "directed_searches": {"quality": "exact", "value": 1},
                "rediscovered_facts": {"quality": "exact", "value": 0},
                "tokens": {"quality": "unavailable", "note": "sem token real"},
            },
            "brief": {"available": True, "used": False},
            "cache": {"available": True, "used": True, "status": "valid"},
            "reused_facts": ["workspace", "issue", "branch"],
            "rediscovered_facts": [],
            "expansions": [{"metric": "commands", "reason": "falha inicial de validação"}],
        }

    def test_sanitiza_payload_sem_conteudo_sensivel(self) -> None:
        payload = context_telemetry.sanitize_report(self.base_report())
        self.assertNotIn("references", payload)
        self.assertNotIn("consulted_files", payload)
        serialized = str(payload)
        self.assertNotIn("runtime observabilidade orçamento", serialized)
        self.assertNotIn("references/dev.md", serialized)
        self.assertEqual(payload["summary"]["expansion_metrics"], ["commands"])

    def test_preserva_metricas_indisponiveis_sem_inventar_valor(self) -> None:
        payload = context_telemetry.sanitize_report(self.base_report())
        self.assertEqual(payload["measurements"]["tokens"], {"quality": "unavailable"})

    def test_falha_de_envio_nao_bloqueia(self) -> None:
        repo = Path(__file__).resolve().parents[3]
        report_path = "skills/yabook/tests/runtime-report.example.json"
        config_path = "skills/yabook/tests/context-telemetry-config.example.json"

        def failing_sender(payload: dict, config: dict) -> dict:
            raise OSError("sem rede")

        result = context_telemetry.export_report(
            repo,
            report_path,
            config_path,
            sender=failing_sender,
        )
        self.assertEqual(result["mode"], "warning")
        self.assertIn("não bloqueante", result["reason"])

    def test_telemetria_desativada_por_padrao(self) -> None:
        repo = Path(__file__).resolve().parents[3]
        result = context_telemetry.export_report(
            repo,
            "skills/yabook/tests/runtime-report.example.json",
            "skills/yabook/tests/arquivo-inexistente.json",
        )
        self.assertEqual(result["mode"], "disabled")


if __name__ == "__main__":
    unittest.main()
