import json
import sys
import tempfile
import threading
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from memory_runtime.core import Vault, write_json
from memory_runtime.retrieval import delivered_levels, retrieve
from memory_runtime.search import search

EVIDENCE = [dict(type="code", ref="fixture/fonte.p@abc", level="static", date="2026-01-15")]


class StabilityTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.v = Vault(Path(self.tmp.name) / "vault")
        self.v.bootstrap("demo")
        self.assessment = dict(verdict="add", reason="Evitar redescoberta", utility="Investigação",
                               application="Sincronização", evidence_status="Código examinado")

    def record(self, identifier="R1", **extra):
        return dict(dict(title="Recebimento do checklist " + identifier, scope=["Org", "App"], kind="knowledge",
                         content="Operação recebe checklist do supervisor " + identifier, application="Investigar recebimento",
                         state="confirmed", evidence=EVIDENCE, keywords=["checklist"]), **extra)

    def apply(self, changes):
        p = self.v.prepare(changes, self.assessment, "test")
        return self.v.apply(p["id"], p["approval_hash"])

    def save(self, value, identifier="R1", **change):
        return self.apply([dict(collection="records", id=identifier, value=value, **change)])

    def test_history_is_proportional_to_changed_items(self):
        self.apply([dict(collection="records", id="K%d" % i, value=self.record("K%d" % i, content="texto " * 80))
                    for i in range(40)])
        self.save(self.record("R1"))
        self.save(self.record("R1", content="Complemento comprovado"))
        receipts = sorted((self.v.root / "history").glob("*.json"), key=lambda p: p.stat().st_size)
        small = json.loads(receipts[0].read_text())
        self.assertNotIn("snapshot", small)
        self.assertLess(receipts[0].stat().st_size, receipts[-1].stat().st_size / 10)
        update = next(json.loads(p.read_text()) for p in receipts
                      if json.loads(p.read_text())["changes"][0].get("before"))
        self.assertEqual(update["changes"][0]["before"]["revision"], 1)
        self.assertEqual(update["changes"][0]["after"]["content"], "Complemento comprovado")

    def test_recover_keeps_full_journal(self):
        p = self.v.prepare([dict(collection="records", id="R1", value=self.record())], self.assessment, "test")
        self.assertIn("result", p)
        write_json(self.v.local / "transaction.json", p)
        self.v.recover()
        receipt = json.loads(next((self.v.root / "history").glob("*.json")).read_text())
        self.assertIsNone(receipt["changes"][0]["before"])

    def test_omitted_field_requires_explicit_removal(self):
        self.save(self.record())
        value = self.record(); value.pop("keywords")
        with self.assertRaisesRegex(ValueError, "keywords"):
            self.save(value)
        with self.assertRaisesRegex(ValueError, "continua"):
            self.save(self.record(), remove_fields=["keywords"])
        with self.assertRaisesRegex(ValueError, "não existe"):
            self.save(value, remove_fields=["keywords", "aliases"])
        self.save(value, remove_fields=["keywords"])
        self.assertNotIn("keywords", self.v.snapshot()["records"]["R1"])

    def test_structured_evidence_and_provenance(self):
        for evidence in (["fixture:code"], [dict(type="code", ref="x")], [dict(type="code", ref="x", level="certo")],
                         [dict(type="code", ref="x", level="static", date="15/01/2026")]):
            with self.assertRaises(ValueError):
                self.save(self.record(evidence=evidence))
        with self.assertRaisesRegex(ValueError, "hash"):
            self.save(self.record(provenance=[dict(agent="codex", file="MEMORY.md", hash="abc")]))
        self.save(self.record(provenance=[dict(agent="codex", file="MEMORY.md", lines="10-24", hash="a" * 64)]))

    def test_legacy_evidence_remains_readable(self):
        legacy = dict(self.record("L1"), id="L1", revision=1, evidence=["fixture:code"])
        write_json(self.v.root / "records/L1.json", legacy)
        self.assertEqual([e["id"] for e in self.v.entries()], ["L1"])
        self.save(self.record("R1"))
        with self.assertRaisesRegex(ValueError, "type e level"):
            self.save(legacy, "L1")

    def test_stale_summaries_are_reported(self):
        self.save(self.record())
        group = dict(title="Checklist", scope=["Org", "App"], kind="topic", members=["R1"],
                     summary="Resumo", summary_sources={"R1": 1})
        self.apply([dict(collection="groups", id="G1", value=group)])
        result = self.save(self.record(content="Complemento comprovado"))
        self.assertEqual(result["stale_summaries"], ["G1"])
        refreshed = dict(group, summary_sources={"R1": 3})
        both = self.apply([dict(collection="records", id="R1", value=self.record(content="Outro complemento")),
                           dict(collection="groups", id="G1", value=refreshed)])
        self.assertEqual(both["stale_summaries"], [])

    def test_concurrent_searches_do_not_fail(self):
        self.save(self.record())
        errors = []
        def run():
            try:
                for _ in range(15): search(Vault(self.v.root), "checklist supervisor")
            except Exception as exc:
                errors.append(repr(exc))
        threads = [threading.Thread(target=run) for _ in range(4)]
        for thread in threads: thread.start()
        for thread in threads: thread.join()
        self.assertEqual(errors, [])

    def test_delivered_levels_skip_repeated_content_only(self):
        self.save(self.record())
        self.apply([dict(collection="groups", id="G1", value=dict(title="Checklist", scope=["Org", "App"],
                                                                     kind="topic", members=["R1"]))])
        first = retrieve(self.v, "checklist", [["Org"]])
        self.assertEqual({k["id"] for k in first["knowledge"]}, {"R1"})
        delivered = {k: sorted(v) for k, v in delivered_levels(first).items()}
        second = retrieve(self.v, "checklist", [["Org"]], delivered=delivered)
        self.assertEqual((second["knowledge"], second["topics"]), ([], []))
        self.assertEqual(second["already_delivered"], 2)
        index_only = {k: ["index"] for k in delivered}
        third = retrieve(self.v, "checklist", [["Org"]], delivered=index_only)
        self.assertEqual([k["id"] for k in third["knowledge"]], ["R1"])
        self.assertEqual(third["topics"], [])
        self.save(self.record(content="Complemento comprovado"))
        fourth = retrieve(self.v, "checklist", [["Org"]], delivered=delivered)
        self.assertEqual([k["id"] for k in fourth["knowledge"]], ["R1"])


if __name__ == "__main__":
    unittest.main()
