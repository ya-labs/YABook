#!/usr/bin/env python3

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class GuardrailsContractTest(unittest.TestCase):
    def setUp(self) -> None:
        self.reference = (ROOT / "references" / "guardrails.md").read_text(encoding="utf-8")
        self.skill = (ROOT / "SKILL.md").read_text(encoding="utf-8")

    def test_comandos_e_marcadores_sao_definidos(self) -> None:
        for text in (
            "$yabook guardrails",
            "$yabook do guardrails install",
            "$yabook do guardrails remove",
            "YABOOK-GUARDRAILS:START",
            "YABOOK-GUARDRAILS:END",
        ):
            self.assertIn(text, self.reference)
        self.assertIn("guardrails", self.skill)

    def test_preserva_conteudo_e_bloqueia_estado_ambiguo(self) -> None:
        self.assertIn("Preserve todo conteúdo", self.reference)
        self.assertIn("bloco duplicado", self.reference)
        self.assertIn("marcador incompleto", self.reference)

    def test_bypass_libera_edicao_sem_liberar_git(self) -> None:
        self.assertIn("bloqueie edição direta por padrão", self.reference)
        self.assertIn("não substitui `$yabook do`", self.reference)
        self.assertIn("Mutações Git locais ou remotas exigem", self.reference)


if __name__ == "__main__":
    unittest.main()
