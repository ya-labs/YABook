import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from memory_runtime.contract import removed_terms, review
from memory_runtime.core import Vault

EVIDENCE = [dict(type="code", ref="fixture", level="static")]


class ContractReviewTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.repo = Path(self.temp.name) / "repo"
        self.repo.mkdir()
        self.git("init", "-q", "-b", "main")
        (self.repo / "regras.md").write_text("Commit exige `$yabook do commit`.\nForce usa `push --force-with-lease`.\n"
                                             "Exemplo: `$yabook do commit` cria o commit.\n")
        self.git("add", "-A"); self.git("-c", "user.name=a", "-c", "user.email=a@x", "commit", "-q", "-m", "base")
        (self.repo / "regras.md").write_text("Commit segue o pedido da pessoa.\nExemplo: `$yabook do commit` cria o commit.\n")
        self.git("-c", "user.name=a", "-c", "user.email=a@x", "commit", "-q", "-am", "muda contrato")

    def git(self, *args):
        subprocess.run(["git", "-C", str(self.repo), *args], check=True, capture_output=True)

    def test_terms_removed_from_contract_point_to_contradicting_records(self):
        terms = removed_terms(self.repo, "HEAD~1")
        self.assertEqual(terms, dict(gone=["push --force-with-lease"], changed=["$yabook do commit"]))
        vault = Vault(Path(self.temp.name) / "v"); vault.bootstrap("demo")
        base = dict(scope=["Org"], kind="knowledge", state="confirmed", evidence=EVIDENCE, application="Aplicar")
        changes = [dict(collection="records", id="OBSOLETO", value=dict(base, title="Commit exige comando",
                        content="Commit ainda exige `$yabook do commit`; force com `push --force-with-lease`.")),
                   dict(collection="records", id="ATUAL", value=dict(base, title="Pedido da pessoa", content="Commit pelo pedido."))]
        assessment = dict(verdict="add", reason="t", utility="t", application="t", evidence_status="t")
        proposal = vault.prepare(changes, assessment, "test"); vault.apply(proposal["id"], proposal["approval_hash"])
        result = review(vault, terms["gone"], terms["changed"])
        self.assertEqual([c["id"] for c in result["candidates"]], ["OBSOLETO"])
        self.assertEqual(result["candidates"][0]["gone"], ["push --force-with-lease"])


if __name__ == "__main__":
    unittest.main()
