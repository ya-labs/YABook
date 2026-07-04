#!/usr/bin/env python3

import importlib.util
import json
import time
import sys
import unittest
from pathlib import Path


sys.dont_write_bytecode = True
SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "build_context_runtime_report.py"
SPEC = importlib.util.spec_from_file_location("context_runtime_builder", SCRIPT)
context_runtime_builder = importlib.util.module_from_spec(SPEC)
assert SPEC.loader
SPEC.loader.exec_module(context_runtime_builder)


class ContextRuntimeBuilderTest(unittest.TestCase):
    def capture(self) -> dict:
        return {
            "scenario": "dev_ready",
            "route": "dev",
            "references": [
                "references/dev.md",
                "references/git/checkpoint.md",
            ],
            "consulted_files": [
                "skills/yabook/tests/context-runtime.md",
                "skills/yabook/tests/context-runtime-budgets.json",
            ],
            "operations": [
                {"tool": "terminal", "commands": 4, "output_chars": 1200},
                {"tool": "search", "commands": 1, "output_chars": 1800},
                {"tool": "terminal", "commands": 3, "output_chars": 1600},
            ],
            "rounds": 5,
            "directed_searches": [
                {"tool": "rg", "query": "runtime orçamento", "reason": "achar o teste"}
            ],
            "reused_facts": ["workspace", "issue", "branch", "objective"],
            "rediscovered_facts": [],
            "brief": {"available": True, "used": True},
            "cache": {"available": True, "used": True, "status": "valid"},
            "expansions": [],
            "measurements": {
                "tokens": {
                    "quality": "unavailable",
                    "note": "runtime sem métrica de tokens",
                }
            },
        }

    def test_gera_measurements_e_classe_automaticamente(self) -> None:
        report = context_runtime_builder.normalize_capture(self.capture())
        self.assertEqual(report["class"], "C3")
        self.assertEqual(report["measurements"]["commands"]["value"], 8)
        self.assertEqual(report["measurements"]["consulted_files"]["value"], 2)
        self.assertEqual(report["measurements"]["tokens"]["quality"], "unavailable")

    def test_permte_tokens_disponivel_quando_informado(self) -> None:
        capture = self.capture()
        capture["measurements"]["tokens"] = {"quality": "approx", "value": 1200}
        report = context_runtime_builder.normalize_capture(capture)
        self.assertEqual(report["measurements"]["tokens"], {"quality": "approx", "value": 1200})

    def test_falha_com_capture_invalido(self) -> None:
        capture = self.capture()
        capture["rediscovered_facts"] = ["branch"]
        report = context_runtime_builder.normalize_capture(capture)
        errors, _ = context_runtime_builder.context_runtime.validate_report(report)
        self.assertTrue(any("redescobertos" in error for error in errors), errors)

    def test_gera_arquivo_final_valido(self) -> None:
        root = Path(__file__).resolve().parents[3]
        capture_path = root / "tmp" / "runtime-capture-test.json"
        output_path = root / "tmp" / "runtime-report-test.json"
        capture_path.parent.mkdir(parents=True, exist_ok=True)
        try:
            capture_path.write_text(json.dumps(self.capture(), ensure_ascii=False), encoding="utf-8")
            report = context_runtime_builder.build_report(
                root,
                "tmp/runtime-capture-test.json",
                "tmp/runtime-report-test.json",
            )
            self.assertTrue(output_path.exists())
            self.assertEqual(report["measurements"]["rounds"]["value"], 5)
        finally:
            for path in (capture_path, output_path):
                for _ in range(3):
                    if not path.exists():
                        break
                    try:
                        path.unlink()
                        break
                    except PermissionError:
                        time.sleep(0.1)


if __name__ == "__main__":
    unittest.main()
