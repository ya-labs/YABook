#!/usr/bin/env python3

import importlib.util
import json
import shutil
import sys
import unittest
from pathlib import Path


sys.dont_write_bytecode = True
SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "build_context_dashboard.py"
SPEC = importlib.util.spec_from_file_location("context_dashboard", SCRIPT)
context_dashboard = importlib.util.module_from_spec(SPEC)
assert SPEC.loader
SPEC.loader.exec_module(context_dashboard)


class ContextDashboardTest(unittest.TestCase):
    def payload(self, exported_at: str, route: str = "dev", commands: int = 7, output_chars: int = 4200) -> dict:
        return {
            "version": 1,
            "exported_at": exported_at,
            "scenario": "dev_ready",
            "route": route,
            "class": "C3" if route == "dev" else "C2",
            "measurements": {
                "references": {"quality": "exact", "value": 2},
                "consulted_files": {"quality": "exact", "value": 2},
                "commands": {"quality": "exact", "value": commands},
                "output_chars": {"quality": "exact", "value": output_chars},
                "rounds": {"quality": "exact", "value": 4},
                "directed_searches": {"quality": "exact", "value": 1},
                "rediscovered_facts": {"quality": "exact", "value": 0},
                "tokens": {"quality": "unavailable"},
            },
            "operations": [
                {"tool": "terminal", "commands": commands - 2, "output_chars": output_chars - 1200},
                {"tool": "search", "commands": 1, "output_chars": 1200},
            ],
            "summary": {
                "reused_facts_count": 3,
                "rediscovered_facts_count": 0,
                "expansion_count": 0,
                "expansion_metrics": [],
                "brief_available": False,
                "brief_used": False,
                "cache_available": False,
                "cache_used": False,
                "cache_status": "absent",
            },
        }

    def test_marca_regressao_por_rota(self) -> None:
        dataset = context_dashboard.build_dataset(
            [
                self.payload("2026-07-04T14:58:00+00:00", commands=7, output_chars=4200),
                self.payload("2026-07-04T16:11:27+00:00", commands=9, output_chars=5100),
            ]
        )
        route = dataset["routes"][0]
        self.assertEqual(route["route"], "dev")
        self.assertEqual(route["regression_count"], 2)
        self.assertEqual(route["regressions"][0]["metric"], "commands")

    def test_rejeita_relatorio_bruto(self) -> None:
        payload = self.payload("2026-07-04T14:58:00+00:00")
        payload["references"] = ["references/dev.md"]
        root = Path(__file__).resolve().parents[3] / "tmp" / "context-dashboard-test"
        if root.exists():
            shutil.rmtree(root, ignore_errors=True)
        root.mkdir(parents=True, exist_ok=True)
        try:
            file_path = root / "raw.json"
            file_path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "payload bruto"):
                context_dashboard.build_dashboard(root, ["raw.json"])
        finally:
            if root.exists():
                shutil.rmtree(root, ignore_errors=True)

    def test_resume_qualidade_sem_inventar_tokens(self) -> None:
        dataset = context_dashboard.build_dataset([self.payload("2026-07-04T14:58:00+00:00")])
        tokens = next(item for item in dataset["quality"] if item["metric"] == "tokens")
        self.assertEqual(tokens["unavailable"], 1)
        self.assertEqual(tokens["exact"], 0)


if __name__ == "__main__":
    unittest.main()
