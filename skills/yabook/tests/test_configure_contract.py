#!/usr/bin/env python3

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class ConfigureContractTest(unittest.TestCase):
    def setUp(self) -> None:
        self.configure = (ROOT / "references" / "configure.md").read_text(encoding="utf-8")
        self.workspace = (ROOT / "references" / "workspace.md").read_text(encoding="utf-8")
        self.skill = (ROOT / "SKILL.md").read_text(encoding="utf-8")

    def test_configuracao_ausente_e_opcional(self) -> None:
        self.assertIn("ausência não é erro", self.workspace)

    def test_configuracao_existente_e_carregada_em_rota_local(self) -> None:
        self.assertIn("Em rotas de repositório", self.workspace)
        self.assertIn(".yabook/AGENTS.md", self.workspace)
        self.assertIn("Regra local aplicada:", self.configure)

    def test_comando_local_valido_tem_contrato_executavel(self) -> None:
        for section in (
            "Sintaxe:",
            "Pré-condições:",
            "Sem `do`:",
            "Com `do`:",
            "Validações esperadas:",
            "Limites e riscos:",
        ):
            self.assertIn(section, self.configure)
        self.assertIn("### `apk homolog`", self.configure)

    def test_comando_local_inseguro_e_bloqueado(self) -> None:
        self.assertIn("pode remover a exigência de `do`", self.configure)
        self.assertIn("autorizar Git ou GitHub", self.configure)
        self.assertIn("implicitamente", self.configure)
        self.assertIn("Campo inválido", self.configure)
        self.assertIn(".yabook/AGENTS.md", self.skill)


if __name__ == "__main__":
    unittest.main()
