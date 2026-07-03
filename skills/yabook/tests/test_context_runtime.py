#!/usr/bin/env python3

import importlib.util
import sys
import unittest
from pathlib import Path


sys.dont_write_bytecode = True
SCRIPT = Path(__file__).resolve().parent / "check_context_runtime.py"
SPEC = importlib.util.spec_from_file_location("context_runtime", SCRIPT)
context_runtime = importlib.util.module_from_spec(SPEC)
assert SPEC.loader
SPEC.loader.exec_module(context_runtime)


class ContextRuntimeTest(unittest.TestCase):
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
            "measurements": {
                "references": {"quality": "exact", "value": 2},
                "consulted_files": {"quality": "exact", "value": 2},
                "commands": {"quality": "exact", "value": 8},
                "output_chars": {"quality": "exact", "value": 4600},
                "rounds": {"quality": "exact", "value": 5},
                "directed_searches": {"quality": "exact", "value": 1},
                "rediscovered_facts": {"quality": "exact", "value": 0},
                "tokens": {
                    "quality": "unavailable",
                    "note": "runtime sem métrica de tokens",
                },
            },
            "reused_facts": ["workspace", "issue", "branch", "objective"],
            "rediscovered_facts": [],
            "brief": {"available": True, "used": True},
            "cache": {"available": True, "used": True, "status": "valid"},
            "expansions": [],
        }

    def test_relatorio_valido(self) -> None:
        errors, observed = context_runtime.validate_report(self.base_report())
        self.assertEqual(errors, [])
        self.assertEqual(observed["commands"], 8)
        self.assertEqual(observed["consulted_files"], 2)

    def test_ampliacao_sem_justificativa_falha(self) -> None:
        report = self.base_report()
        report["expansions"] = [{"metric": "commands", "reason": ""}]
        errors, _ = context_runtime.validate_report(report)
        self.assertTrue(any("sem justificativa" in error for error in errors), errors)

    def test_releitura_desnecessaria_falha(self) -> None:
        report = self.base_report()
        report["rediscovered_facts"] = ["branch"]
        report["measurements"]["rediscovered_facts"]["value"] = 1
        errors, _ = context_runtime.validate_report(report)
        self.assertTrue(any("redescobertos" in error for error in errors), errors)

    def test_metrica_indisponivel_nao_pode_inventar_valor(self) -> None:
        report = self.base_report()
        report["measurements"]["tokens"]["value"] = 123
        errors, _ = context_runtime.validate_report(report)
        self.assertTrue(any("indisponível" in error for error in errors), errors)


if __name__ == "__main__":
    unittest.main()
