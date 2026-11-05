"""Contrato público do sync: curadoria explícita, persistência e retomada via CLI."""
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))
from memory_runtime.core import Vault, digest, read_json, write_json
from memory_runtime.sources import source_add, sync


ASSESSMENT = dict(verdict="add", reason="Descoberta comprovada e aplicável ao projeto.",
                  utility="Evitar nova investigação da sincronização.",
                  application="Ao investigar checklist que não chega ao supervisor.",
                  evidence_status="Contrato da rotina conferido no código.")


class SyncCliTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.vault = Vault(self.root / "own")
        self.vault.bootstrap("recipient")
        self.source = source_add(self.vault, dict(id="colleague",
            remote="https://github.com/demo/YABook-memory-demo", includes=[["Org"]], incorporate=True))
        remote = Vault(self.root / "external")
        remote.bootstrap("colleague")
        record = dict(title="Envio dos checklists", scope=["Org", "App"], kind="knowledge",
            content="O envio ao supervisor é tratado na rotina de sincronização.",
            application="Rastrear o checklist que não chega ao supervisor.", state="confirmed",
            triggers=["checklist não chega ao supervisor"],
            evidence=[dict(type="code", ref="src/sync.p", level="static")])
        proposal = remote.prepare([dict(collection="records", id="checklist-sync", value=record)], ASSESSMENT, "test")
        remote.apply(proposal["id"], proposal["approval_hash"])
        write_json(self.vault.local / "sources/colleague/receipt.json", dict(
            vault_id=remote.snapshot()["metadata"]["vault_id"], revision="a" * 40,
            policy_hash=digest({k: v for k, v in self.source.items() if k != "publication"}),
            checked_at=0, entries=list(remote.entries()), report=dict(status="updated")))

    def plan(self):
        with patch("memory_runtime.gitstore.settle", return_value=None), \
             patch("memory_runtime.gitstore.reconcile", return_value=dict(status="unchanged")), \
             patch("memory_runtime.sources.refresh", return_value=[dict(source="colleague", status="updated")]):
            return sync(self.vault)["curation"]

    def cli(self, *args):
        result = subprocess.run([sys.executable, str(SCRIPTS / "yabook_memory.py"),
            "--root", str(self.vault.root), *args], capture_output=True, text=True)
        return result, json.loads(result.stdout if result.returncode == 0 else result.stderr)

    def payload(self, plan):
        return dict(base_hash=plan["base_hash"], candidates_hash=plan["candidates_hash"],
            assessment=ASSESSMENT, decisions=[dict(candidate=plan["candidates"][0]["candidate"],
                action="add", reason="Conhecimento novo com evidência e aplicação no escopo compartilhado.")])

    def test_cli_incorporates_once_and_exposes_own_searchable_knowledge(self):
        path = self.root / "curated.json"
        write_json(path, self.payload(self.plan()))
        result, report = self.cli("sync-apply", "--input", str(path), "--actor", "test-agent")
        self.assertEqual(result.returncode, 0, report)
        records = self.vault.snapshot()["records"]
        self.assertEqual(len(records), 1)
        self.assertEqual(next(iter(records.values()))["origin"]["id"], "checklist-sync")
        self.assertEqual(self.plan()["candidates"], [])
        result, found = self.cli("retrieve", "checklist supervisor", "--scope", "Org", "--budget", "2000")
        self.assertEqual(result.returncode, 0, found)
        self.assertIn("rotina de sincronização", json.dumps(found, ensure_ascii=False))
        self.assertEqual(len(list((self.vault.root / "history").glob("*.json"))), 1)

    def test_cli_rejects_curated_batch_when_own_base_changed(self):
        payload = self.payload(self.plan())
        proposal = self.vault.prepare([dict(collection="records", id="other", value=dict(
            title="Outra descoberta", scope=["Org"], content="Contexto local novo.",
            application="Consulta", state="hypothesis"))], ASSESSMENT, "other-agent")
        self.vault.apply(proposal["id"], proposal["approval_hash"])
        path = self.root / "curated.json"
        write_json(path, payload)
        result, report = self.cli("sync-apply", "--input", str(path), "--actor", "test-agent")
        self.assertNotEqual(result.returncode, 0, report)
        self.assertEqual(set(self.vault.snapshot()["records"]), {"other"})

    def test_pending_conflict_remains_visible_when_retrieving_own_knowledge(self):
        path = self.root / "curated.json"
        write_json(path, self.payload(self.plan()))
        result, report = self.cli("sync-apply", "--input", str(path), "--actor", "test-agent")
        self.assertEqual(result.returncode, 0, report)
        record = self.vault.snapshot()["records"]["checklist-sync"]
        record["content"] += " Complemento comprovado na máquina local."
        proposal = self.vault.prepare([dict(collection="records", id=record["id"], value=record)], ASSESSMENT, "test")
        self.vault.apply(proposal["id"], proposal["approval_hash"])
        cache = self.vault.local / "sources/colleague/receipt.json"
        receipt = read_json(cache)
        receipt["revision"] = "b" * 40
        receipt["entries"][0].update(content="O checklist tem outra condição de envio ao supervisor.", revision=2)
        write_json(cache, receipt)
        payload = self.payload(self.plan())
        payload["decisions"][0].update(action="pending", reason="Duas versões divergentes precisam de verificação.")
        write_json(path, payload)
        result, report = self.cli("sync-apply", "--input", str(path), "--actor", "test-agent")
        self.assertEqual(result.returncode, 0, report)
        result, found = self.cli("retrieve", "checklist supervisor", "--scope", "Org", "--budget", "3000")
        self.assertEqual(result.returncode, 0, found)
        self.assertIn("Duas versões divergentes", json.dumps(found, ensure_ascii=False))


if __name__ == "__main__":
    unittest.main()
