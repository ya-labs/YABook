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

    def test_auto_tem_excecao_explicita_nas_travas_globais(self) -> None:
        self.assertIn("Fora de `mode: auto`", self.reference)
        self.assertIn("explicitamente ativado", self.reference)
        self.assertIn("merge exige pedido explícito", self.reference)
        self.assertIn("Outro modo, projeto ou sessão encerra `auto`", self.reference)

    def test_bypass_exige_sugestao_completa_e_pacote_preserva_corpos(self) -> None:
        self.assertIn("`Mensagem` e `Descrição` em blocos separados", self.reference)
        self.assertIn("sem validações na descrição", self.reference)
        self.assertIn("PR por merge commit", self.reference)


if __name__ == "__main__":
    unittest.main()
