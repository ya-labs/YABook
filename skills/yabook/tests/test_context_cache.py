#!/usr/bin/env python3

import importlib.util
import sys
import unittest
from pathlib import Path


sys.dont_write_bytecode = True
SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "check_context_cache.py"
SPEC = importlib.util.spec_from_file_location("context_cache", SCRIPT)
context_cache = importlib.util.module_from_spec(SPEC)
assert SPEC.loader
SPEC.loader.exec_module(context_cache)


class ContextCacheTest(unittest.TestCase):
    def setUp(self) -> None:
        self.repo = Path(__file__).parent / "fixtures" / "context-cache"
        self.cache = self.repo / "inexistente.md"
        self.state = {
            "branch": "main",
            "remote": "https://github.com/ya-labs/teste.git",
            "reference_is_ancestor": True,
        }

    def metadata(self, **overrides: str) -> dict[str, str]:
        values = {
            "version": "1",
            "branch": "main",
            "remote": "https://github.com/ya-labs/teste.git",
            "reference": "a" * 40,
            "rules_sources": "AGENTS.md",
            "rules_fingerprint": context_cache.fingerprint(
                self.repo, "AGENTS.md"
            ),
            "planning_sources": "docs/planejamento",
            "planning_fingerprint": context_cache.fingerprint(
                self.repo, "docs/planejamento"
            ),
        }
        values.update(overrides)
        return values

    def cache_text(
        self,
        metadata: dict[str, str],
        body: str = "# Contexto\n",
    ) -> str:
        header = "\n".join(f"{key}: {value}" for key, value in metadata.items())
        return f"---\n{header}\n---\n{body}"

    def test_cache_ausente_e_opcional(self) -> None:
        self.assertEqual(context_cache.validate(self.repo, self.cache, self.state), [])

    def test_cache_valido(self) -> None:
        text = self.cache_text(self.metadata())
        self.assertEqual(context_cache.validate_text(self.repo, text, self.state), [])

    def test_invalida_branch_remote_reference_regras_e_planejamento(self) -> None:
        cases = {
            "branch": {"branch": "outra"},
            "remote": {"remote": "https://example.com/outro.git"},
            "reference": {},
            "rules": {"rules_fingerprint": "0" * 64},
            "planning": {"planning_fingerprint": "0" * 64},
        }
        for expected, overrides in cases.items():
            with self.subTest(expected=expected):
                state = dict(self.state)
                if expected == "reference":
                    state["reference_is_ancestor"] = False
                text = self.cache_text(self.metadata(**overrides))
                errors = context_cache.validate_text(self.repo, text, state)
                self.assertTrue(any(expected in error for error in errors), errors)

    def test_invalida_cache_acima_do_limite(self) -> None:
        text = self.cache_text(self.metadata(), "x" * 3001)
        errors = context_cache.validate_text(self.repo, text, self.state)
        self.assertTrue(any("máximo" in error for error in errors), errors)


if __name__ == "__main__":
    unittest.main()
