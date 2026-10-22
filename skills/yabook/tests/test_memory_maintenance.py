import copy
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from memory_runtime import maintenance
from memory_runtime.core import Vault, read_json, write_json
from memory_runtime.learning import learn

EVIDENCE = [dict(type="code", ref="fixture", level="static")]
ASSESSMENT = dict(verdict="add", reason="t", utility="t", application="t", evidence_status="t")


class MaintenanceTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.vault = Vault(self.root / "memory")
        self.vault.bootstrap("demo")
        self.cfg_path = self.root / "config.json"
        self.cfg = {"memory_root": str(self.vault.root), "projects": {str(self.root): ["Demo"]},
                    "learning": {"mode": "automatic", "cleanup": {"days": 14, "changes": 2, "problems": 3, "max_days": 30}}}
        write_json(self.cfg_path, self.cfg)
        record = dict(title="Fila", kind="knowledge", scope=["Demo"], content="Fila grava antes.", application="Investigar",
                      state="confirmed", evidence=EVIDENCE, triggers=["fila não grava"])
        self.apply([dict(collection="records", id="R1", value=record),
                    dict(collection="groups", id="G", value=dict(title="Fila", scope=["Demo"], kind="topic", members=["R1"],
                                                                 summary="Fila de envio.", summary_sources={"R1": 1}))])

    def apply(self, changes):
        proposal = self.vault.prepare(changes, ASSESSMENT, "test")
        return self.vault.apply(proposal["id"], proposal["approval_hash"])

    def test_recommendation_by_time_volume_and_problems_then_registered(self):
        from datetime import timedelta
        self.assertFalse(maintenance.status(self.vault, self.cfg)["due"])
        metadata = read_json(self.vault.root / "memory.json")
        metadata["created_at"] = (maintenance.now() - timedelta(days=20)).isoformat()
        write_json(self.vault.root / "memory.json", metadata)
        self.apply([dict(collection="records", id="R2", value=dict(read_json(self.vault.root / "records/R1.json"),
                         title="Outra fila", content="Outra fila grava depois."))])
        status = maintenance.status(self.vault, self.cfg)
        self.assertTrue(status["due"]); self.assertEqual(status["orphans"], 1)
        self.assertIn("lotes", status["reasons"][0])
        before = maintenance.check(self.vault, self.cfg)["totals"]
        for invalid in (-1, 3):  # negativo ou mais lotes que os aplicados (2) desde a criação
            with self.assertRaisesRegex(ValueError, "não batem"):
                maintenance.done_change(self.vault, invalid)
        with self.assertRaisesRegex(ValueError, "pendências mecânicas"):
            maintenance.done_change(self.vault, 0)  # ainda há registro sem grupo
        self.apply([maintenance.done_change(self.vault, 2, "teste")])
        record = read_json(self.vault.root / "memory.json")["maintenance"]
        self.assertEqual((record["batches"], record["before"], record["after"]["orphans"]), (2, before, 1))
        status = maintenance.status(self.vault, self.cfg)
        self.assertFalse(status["due"]); self.assertEqual((status["days"], status["changes"]), (0, 0))
        with self.assertRaisesRegex(ValueError, "maintenance"):
            self.vault.prepare([dict(collection="metadata", id="memory", value=dict(owner="outro"))], ASSESSMENT, "test")

    def test_session_start_recommends_cleanup_once_when_due(self):
        import os
        from datetime import timedelta
        from unittest.mock import patch
        import yabook_hook as hook
        write_json(self.cfg_path, dict(self.cfg, learning=dict(self.cfg["learning"], cleanup=dict(problems=1))))
        self.apply([dict(collection="records", id="SOLTO", value=dict(read_json(self.vault.root / "records/R1.json"),
                         title="Solto", content="Registro sem grupo."))])
        environment = dict(YABOOK_CONFIG=str(self.cfg_path), YABOOK_STATE=str(self.root / "sessions"), YABOOK_QUEUE=str(self.root / "q"))
        with patch.dict(os.environ, environment), patch.object(hook, "git", return_value=""):
            text = hook.run(dict(session_id="s", cwd=str(self.root), hook_event_name="SessionStart", source="startup"))
        context = text["hookSpecificOutput"]["additionalContext"]
        self.assertIn("Faxina da memória recomendada (1 problema acumulado)", context)
        self.assertIn("memory clean", context)

    def test_portable_evidence_summary_is_validated_and_clears_diagnosis(self):
        base = read_json(self.vault.root / "records/R1.json")
        elsewhere = dict(type="session", level="reported", ref="rollout_summaries/x.md",
                         available="fora desta máquina; provável memória nativa do Codex no Windows")
        value = {k: v for k, v in base.items() if k not in ("id", "revision", "origin")}
        value["evidence"] = EVIDENCE + [elsewhere]
        self.apply([dict(collection="records", id="R1", value=value)])
        self.assertEqual(maintenance.diagnose(self.vault, self.cfg)["judgment"]["evidence_elsewhere"], ["R1"])
        with self.assertRaisesRegex(ValueError, "400"):
            self.vault.prepare([dict(collection="records", id="R1", value=dict(value, evidence=[dict(elsewhere, summary="x" * 401)]))],
                               ASSESSMENT, "test")
        self.apply([dict(collection="records", id="R1", value=dict(value, evidence=EVIDENCE + [dict(elsewhere, summary="Teste passou; APK pendente.")]))])
        self.assertEqual(maintenance.diagnose(self.vault, self.cfg)["judgment"]["evidence_elsewhere"], [])
        # Sem depender do texto de disponibilidade: relato de sessão ou caminho local sem resumo não é portátil.
        for ref in ("~/.codex/sessions/2026/x.jsonl", "/home/x/relato.md", "rollout_summaries/y.md"):
            self.assertFalse(maintenance.portable(dict(type="session", level="reported", ref=ref)), ref)
        self.assertTrue(maintenance.portable(dict(type="code", level="static", ref="skills/yabook/scripts/x.py:10")))

    def test_diagnose_separates_mechanical_from_judgment(self):
        self.apply([dict(collection="records", id="H", value=dict(title="Hipótese velha", kind="knowledge", scope=["Demo"],
                         content="Talvez.", application="Ver", state="hypothesis", triggers=["fila"],
                         evidence=[dict(type="code", ref="x", level="static", date="2026-01-01")]))])
        report = maintenance.diagnose(self.vault, self.cfg)
        self.assertEqual(report["mechanical"]["orphans"], ["H"])
        self.assertEqual(report["judgment"]["old_hypotheses"], ["H"])
        self.assertEqual(report["judgment"]["single_word_triggers"], ["H"])

    def test_learn_joins_indicated_group_and_keeps_summary_current(self):
        payload = dict(learning=dict(source="development", conflicts=[]), assessment=ASSESSMENT, changes=[dict(
            collection="records", id="R3", group="G", value=dict(title="Fila reenvia", kind="knowledge", scope=["Demo"],
            content="Fila reenvia após falha.", application="Investigar", state="confirmed", evidence=EVIDENCE,
            triggers=["fila não reenvia"]))])
        self.assertEqual(learn(self.vault, payload, "test", self.cfg_path, self.root)["status"], "memory_updated")
        group = read_json(self.vault.root / "groups/G.json")
        self.assertEqual((group["members"], group["summary_sources"]), (["R1", "R3"], {"R1": 1, "R3": 1}))
        enriched = read_json(self.vault.root / "records/R1.json")
        enriched["keywords"] = ["fila", "envio"]
        payload = dict(payload, changes=[dict(collection="records", id="R1", value={k: v for k, v in enriched.items()
                                                                                    if k not in ("id", "revision", "origin")})])
        learn(self.vault, payload, "test", self.cfg_path, self.root)
        self.assertEqual(read_json(self.vault.root / "groups/G.json")["summary_sources"]["R1"], 2)
        self.assertEqual(maintenance.problems(self.vault.snapshot()), dict(stale_summaries=[], orphans=[]))


if __name__ == "__main__":
    unittest.main()
