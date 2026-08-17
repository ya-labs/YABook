#!/usr/bin/env python3

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class GuardrailsContractTest(unittest.TestCase):
    def setUp(self) -> None:
        self.reference = (ROOT / "references" / "guardrails.md").read_text(encoding="utf-8")

    def test_preserva_o_contrato_comportamental_do_yabook(self) -> None:
        for text in (
            "fluxo YABook",
            "checkpoint",
            "mutações Git sem `$yabook do <ação>`",
            "$yabook bypass <ação>",
            "Próxima etapa",
            "tipo: descrição curta",
        ):
            self.assertIn(text, self.reference)

    def test_instalacao_e_remocao_sao_delimitadas(self) -> None:
        for text in (
            "$yabook do guardrails install",
            "$yabook do guardrails remove",
            "YABOOK-GUARDRAILS:START",
            "YABOOK-GUARDRAILS:END",
            "Preserve instruções pessoais",
        ):
            self.assertIn(text, self.reference)


if __name__ == "__main__":
    unittest.main()
