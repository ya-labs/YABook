"""Regressões de sincronização entre lotes, recuperação e decisões locais."""
import copy
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from memory_runtime.core import Vault, digest, write_json
from memory_runtime.sources import all_entries, curation_plan, source_add, source_config, sync_apply


ASSESSMENT = dict(verdict="add", reason="Descoberta comprovada e reutilizável",
                  utility="Evitar investigação repetida", application="Investigar sincronização",
                  evidence_status="Contrato conferido no código")


def record(content="A rotina sync.p envia os checklists ao supervisor."):
    return dict(title="Envio dos checklists", scope=["Org", "App"], kind="knowledge",
                content=content, application="Quando o checklist não chega ao supervisor",
                state="confirmed", triggers=["checklist não chega ao supervisor"],
                evidence=[dict(type="code", ref="sync.p", level="static")])


class SyncRegressionsTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        root = Path(self.temp.name)
        self.own = Vault(root / "own")
        self.own.bootstrap("recipient")
        self.peer = Vault(root / "peer")
        self.peer.bootstrap("colleague")
        source_add(self.own, dict(id="peer", remote="https://github.com/demo/memory",
                                 includes=[["Org"]], incorporate=True))

    def edit(self, vault, collection, identifier, value=None, delete=False):
        change = dict(collection=collection, id=identifier)
        change.update(delete=True) if delete else change.update(value=value)
        proposal = vault.prepare([change], ASSESSMENT, "fixture")
        vault.apply(proposal["id"], proposal["approval_hash"])

    def refresh_cache(self):
        entries = list(self.peer.entries(include_archived=True))
        write_json(self.own.local / "sources/peer/receipt.json", dict(
            vault_id=self.peer.snapshot()["metadata"]["vault_id"], revision=digest(entries),
            policy_hash=digest(source_config(self.own)["peer"]), entries=entries))

    def incorporate(self):
        plan = curation_plan(self.own)
        return sync_apply(self.own, dict(
            base_hash=plan["base_hash"], candidates_hash=plan["candidates_hash"],
            assessment=ASSESSMENT, decisions=[dict(candidate=c["candidate"], action="add",
                reason="Conhecimento confirmado e útil ao projeto") for c in plan["candidates"]]), "test-agent")

    def test_interrupted_incorporation_recovers_record_and_ledger_together(self):
        self.edit(self.peer, "records", "sync-record", record())
        self.refresh_cache()
        failed = False

        def interrupted_write(path, value):
            nonlocal failed
            if Path(path) == self.own.path("records", "sync-record") and not failed:
                failed = True
                raise OSError("Simulação de interrupção ao gravar o registro")
            return write_json(path, value)

        with patch("memory_runtime.core.write_json", side_effect=interrupted_write):
            with self.assertRaises(OSError):
                self.incorporate()
        with self.assertRaisesRegex(ValueError, "Transação interrompida"):
            self.own.snapshot()

        self.own.recover()
        snapshot = self.own.snapshot()
        self.assertIn("sync-record", snapshot["records"])
        ledger = list(snapshot["metadata"]["source_sync"]["entries"].values())
        self.assertEqual(len(ledger), 1)
        self.assertEqual(ledger[0]["target"], "sync-record")
        self.assertEqual(curation_plan(self.own)["candidates"], [])
        self.assertEqual(len(list((self.own.root / "history").glob("*.json"))), 1)

    def test_later_group_preserves_dependency_with_renamed_source_identity(self):
        identifier = "renamed-in-peer"
        self.edit(self.own, "records", identifier, record("Conhecimento local sobre outro contrato."))
        external = record()
        external["origin"] = dict(vault_id="original-vault", id="original-id")
        self.edit(self.peer, "records", identifier, external)
        self.refresh_cache()
        target = self.incorporate()["incorporated"][0]
        self.assertNotEqual(target, identifier)

        self.edit(self.peer, "groups", "sync-topic", dict(
            title="Sincronização", scope=["Org", "App"], kind="topic", members=[identifier],
            summary="A rotina sync.p envia os checklists ao supervisor.", summary_sources={identifier: 1}))
        self.refresh_cache()
        self.assertEqual([c["entry"]["id"] for c in curation_plan(self.own)["candidates"]], ["sync-topic"])
        self.incorporate()
        group = self.own.snapshot()["groups"]["sync-topic"]
        self.assertEqual(group["members"], [target])
        self.assertEqual(group["summary_sources"], {target: 1})

    def test_inactive_or_deleted_local_knowledge_is_not_reactivated_by_external_cache(self):
        self.edit(self.peer, "records", "sync-record", record())
        self.refresh_cache()
        self.incorporate()
        value = copy.deepcopy(self.own.snapshot()["records"]["sync-record"])
        value["state"] = "archived"
        self.edit(self.own, "records", "sync-record", value)
        self.assertEqual(all_entries(self.own), [])

        self.edit(self.own, "records", "sync-record", delete=True)
        self.assertEqual(all_entries(self.own), [])


if __name__ == "__main__":
    unittest.main()
