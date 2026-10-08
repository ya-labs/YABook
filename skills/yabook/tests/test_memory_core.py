import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from memory_runtime.core import Vault


class MemoryCoreTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.v = Vault(Path(self.tmp.name) / "vault")
        self.v.bootstrap("demo")
        self.assessment = dict(verdict="add", reason="Evitar redescoberta", utility="Investigação",
                               application="Falhas de sincronização", evidence_status="Hipótese")

    def record(self, identifier="R1", scope=None):
        return dict(id=identifier, title="Retorno ao supervisor", scope=scope or ["Org", "App"],
                    content="Operação candidata recebe checklist", application="Investigar recebimento",
                    state="hypothesis", evidence=[])

    def save(self, value):
        p = self.v.prepare([dict(collection="records", id=value["id"], value=value)], self.assessment, "test")
        self.v.apply(p["id"], p["approval_hash"])

    def test_approval_and_stale_base(self):
        p = self.v.prepare([dict(collection="records", id="R1", value=self.record())], self.assessment, "test")
        with self.assertRaises(ValueError): self.v.apply(p["id"], "wrong")
        self.save(self.record("R2"))
        with self.assertRaises(ValueError): self.v.apply(p["id"], p["approval_hash"])
        self.assertEqual([r["id"] for r in self.v.entries()], ["R2"])

    def test_confirmed_requires_evidence(self):
        value = self.record(); value["state"] = "confirmed"
        with self.assertRaises(ValueError): self.save(value)

    def test_scope_and_archive(self):
        self.save(self.record())
        self.save(self.record("R2", ["Pessoa"]))
        self.assertEqual([r["id"] for r in self.v.entries([["Org"]])], ["R1"])
        value = self.record(); value["state"] = "archived"; self.save(value)
        self.assertEqual([r["id"] for r in self.v.entries()], ["R2"])

    def test_group_summary_invalidates(self):
        self.save(self.record())
        g = dict(id="G1", title="Sincronização", scope=["Org", "App"], members=["R1"],
                 summary="Hipótese", summary_sources={"R1": 1})
        p = self.v.prepare([dict(collection="groups", id="G1", value=g)], self.assessment, "test")
        self.v.apply(p["id"], p["approval_hash"])
        self.save(dict(self.record(), content="Hipótese corrigida"))
        group = next(x for x in self.v.entries() if x["id"] == "G1")
        self.assertTrue(group["summary_stale"]); self.assertNotIn("summary", group)

    def test_discard_removes_only_the_proposal(self):
        p = self.v.prepare([dict(collection="records", id="R1", value=self.record())], self.assessment, "test")
        self.assertEqual(self.v.discard(p["id"])["status"], "discarded")
        with self.assertRaises(Exception):
            self.v.proposal(p["id"])
        self.assertEqual(list(self.v.entries()), [])

    def test_ambiguous_and_path_traversal(self):
        for identifier in ("R1", "R2"):
            self.v.prepare([dict(collection="records", id=identifier, value=self.record(identifier))], self.assessment, "test")
        with self.assertRaises(ValueError): self.v.proposal()
        with self.assertRaises(ValueError): self.v.path("records", "../escape")

    def test_recovery(self):
        from memory_runtime.core import write_json
        p = self.v.prepare([dict(collection="records", id="R1", value=self.record())], self.assessment, "test")
        write_json(self.v.local / "transaction.json", p)
        self.v.recover()
        self.assertEqual(next(self.v.entries())["revision"], 1)


if __name__ == "__main__": unittest.main()
