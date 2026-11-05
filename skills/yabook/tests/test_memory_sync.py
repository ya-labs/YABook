"""Incorporação curada: referências, conflitos, repetição e publicação segura."""
import copy
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from memory_runtime.core import Vault, digest, read_json, write_json
from memory_runtime.gitstore import git, publish, run
from memory_runtime.incorporation import value_of
from memory_runtime.sources import source_add, source_config, curation_plan, sync_apply, all_entries, sync


A = dict(verdict="add", reason="Descoberta comprovada no escopo compartilhado", utility="Evitar investigação repetida",
         application="Investigar falhas de sincronização", evidence_status="Contrato conferido no código")


def record(content="O envio ao supervisor passa por sync.p.", scope=None, **extra):
    return dict(title="Envio ao supervisor", scope=scope or ["Org", "App"], kind="knowledge", content=content,
                application="Quando o checklist não chega ao supervisor", state="confirmed",
                evidence=[dict(type="code", ref="sync.p", level="static")],
                triggers=["checklist não chega ao supervisor"], **extra)


class MemorySyncTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(); self.addCleanup(self.temp.cleanup)
        self.directory = Path(self.temp.name)
        self.v = Vault(self.directory / "own"); self.v.bootstrap("own")
        self.remote = Vault(self.directory / "external"); self.remote.bootstrap("external")
        source_add(self.v, dict(id="peer", remote="https://github.com/demo/memory", includes=[["Org"]], incorporate=True))
        self.edit(self.remote, "R1", record())
        self.receipt()

    def edit(self, vault, identifier, value, collection="records"):
        p = vault.prepare([dict(collection=collection, id=identifier, value=value)], A, "test")
        return vault.apply(p["id"], p["approval_hash"])

    def receipt(self, source="peer", entries=None, revision=None):
        entries = list(self.remote.entries(include_archived=True)) if entries is None else entries
        write_json(self.v.local / "sources" / source / "receipt.json", dict(
            vault_id=self.remote.snapshot()["metadata"]["vault_id"], revision=revision or digest(entries),
            entries=entries, policy_hash=digest(source_config(self.v)[source]), checked_at=0))

    def payload(self, choices=None):
        plan = curation_plan(self.v)
        decisions = []
        for c in plan["candidates"]:
            action, extra = (choices or {}).get(c["origin"]["id"], ("add", {}))
            decisions.append(dict(candidate=c["candidate"], action=action, reason="Curadoria comprovada para o projeto", **extra))
        return dict(base_hash=plan["base_hash"], candidates_hash=plan["candidates_hash"], assessment=A, decisions=decisions)

    def apply(self, choices=None): return sync_apply(self.v, self.payload(choices), "test-agent")

    def test_plan_is_read_only_and_incorporation_is_idempotent(self):
        before = self.v.snapshot()
        self.assertEqual(len(curation_plan(self.v)["candidates"]), 1)
        self.assertEqual(self.v.snapshot(), before)
        self.apply()
        self.assertEqual(curation_plan(self.v)["candidates"], [])
        self.assertEqual(len(self.v.snapshot()["records"]), 1)
        self.assertEqual(len(list((self.v.root / "history").glob("*.json"))), 1)

    def test_unchanged_local_can_follow_external_update(self):
        self.apply()
        value = value_of(self.remote.snapshot()["records"]["R1"])
        value["content"] += " A carga exige status confirmado."
        self.edit(self.remote, "R1", value); self.receipt()
        self.assertEqual(curation_plan(self.v)["candidates"][0]["status"], "updated")
        self.apply({"R1": ("update", {})})
        self.assertEqual(self.v.snapshot()["records"]["R1"]["content"], value["content"])

    def test_local_edit_and_source_update_conflict_without_overwrite(self):
        self.apply()
        local = value_of(self.v.snapshot()["records"]["R1"]); local["content"] += " Complemento local."
        self.edit(self.v, "R1", local)
        external = value_of(self.remote.snapshot()["records"]["R1"]); external["content"] += " Correção externa."
        self.edit(self.remote, "R1", external); self.receipt()
        self.assertEqual(curation_plan(self.v)["candidates"][0]["status"], "conflict")
        with self.assertRaises(ValueError): self.apply({"R1": ("update", {})})
        self.apply({"R1": ("pending", {})})
        self.assertEqual(self.v.snapshot()["records"]["R1"]["content"], local["content"])
        self.assertTrue(any(f["kind"] == "source_sync_pending" for f in self.v.review()))
        count = len(list((self.v.root / "history").glob("*.json")))
        self.assertEqual(self.apply({"R1": ("pending", {})})["status"], "unchanged")
        self.assertEqual(len(list((self.v.root / "history").glob("*.json"))), count)

    def test_merge_preserves_origin_and_requires_merge_on_next_revision(self):
        self.edit(self.v, "own-record", record("Complemento local sobre a mesma sincronização."))
        merged = record("Complemento local. O envio externo passa por sync.p.")
        self.apply({"R1": ("merge", dict(target="own-record", value=merged))})
        self.assertEqual(self.v.snapshot()["records"]["own-record"]["origin"]["vault_id"], self.v.snapshot()["metadata"]["vault_id"])
        self.assertEqual(len(all_entries(self.v)), 1)
        self.assertNotIn("origin_updates", all_entries(self.v)[0])
        external = value_of(self.remote.snapshot()["records"]["R1"]); external["content"] += " Novo diagnóstico."
        self.edit(self.remote, "R1", external); self.receipt()
        self.assertEqual(curation_plan(self.v)["candidates"][0]["status"], "conflict")
        with self.assertRaises(ValueError): self.apply({"R1": ("update", {})})
        self.assertEqual(self.v.snapshot()["records"]["own-record"]["content"], merged["content"])

    def test_removal_and_invalidation_remain_pending(self):
        self.apply()
        self.receipt(entries=[])
        self.assertEqual(curation_plan(self.v)["candidates"][0]["status"], "removed")
        self.apply({"R1": ("pending", {})})
        self.assertIn("R1", self.v.snapshot()["records"])
        archived = value_of(self.remote.snapshot()["records"]["R1"]); archived["state"] = "archived"
        self.edit(self.remote, "R1", archived); self.receipt()
        self.assertEqual(curation_plan(self.v)["candidates"][0]["status"], "invalidated")
        with self.assertRaises(ValueError): self.apply({"R1": ("update", {})})
        self.apply({"R1": ("ignore", {})})
        self.assertEqual(curation_plan(self.v)["candidates"], [])
        self.assertEqual(self.v.snapshot()["records"]["R1"]["state"], "confirmed")

    def test_ignore_resurfaces_only_when_external_content_changes(self):
        self.apply({"R1": ("ignore", {})})
        self.assertEqual(curation_plan(self.v)["candidates"], [])
        external = value_of(self.remote.snapshot()["records"]["R1"]); external["content"] += " Novidade útil."
        self.edit(self.remote, "R1", external); self.receipt()
        self.assertEqual(len(curation_plan(self.v)["candidates"]), 1)

    def test_policy_change_and_stale_receipt_prevent_application(self):
        payload = self.payload()
        source_add(self.v, dict(id="peer", remote="https://github.com/demo/memory", includes=[["Org"]], branch="other", incorporate=True))
        with self.assertRaises(ValueError): sync_apply(self.v, payload, "test")
        self.assertEqual(curation_plan(self.v)["candidates"], [])
        self.assertTrue(curation_plan(self.v)["skipped_sources"])

    def test_agent_can_normalize_taxonomy_within_approved_scope(self):
        normalized = record(scope=["Org", "Apps comerciais", "Promotor"])
        self.apply({"R1": ("add", dict(value=normalized))})
        self.assertEqual(self.v.snapshot()["records"]["R1"]["scope"], normalized["scope"])
        self.assertEqual(curation_plan(self.v)["candidates"], [])

    def test_scope_outside_policy_is_rejected(self):
        with self.assertRaises(ValueError):
            self.apply({"R1": ("add", dict(value=record(scope=["Pessoa"])))})
        self.assertFalse(self.v.snapshot()["records"])

    def test_unapproved_legacy_sources_are_consulted_without_incorporation(self):
        config = source_config(self.v)
        config["peer"].pop("incorporate")
        write_json(self.v.local / "sources.json", config); (self.v.root / "sources.json").unlink()
        self.assertEqual(curation_plan(self.v)["candidates"], [])
        self.assertEqual(len(all_entries(self.v)), 1)
        with patch("memory_runtime.gitstore.settle", return_value=None), \
             patch("memory_runtime.gitstore.reconcile", return_value=dict(status="unchanged")), \
             patch("memory_runtime.sources.refresh", return_value=[]):
            sync(self.v)
        self.assertTrue((self.v.root / "sources.json").exists())
        self.assertNotIn("incorporate", source_config(self.v)["peer"])

    def test_returned_origin_and_third_party_copy_do_not_duplicate(self):
        self.apply()
        source_add(self.v, dict(id="third", remote="https://github.com/demo/third", includes=[["Org"]], incorporate=True))
        self.receipt(source="third", entries=list(self.v.entries()))
        self.assertEqual(curation_plan(self.v)["candidates"], [])
        self.assertEqual(len(all_entries(self.v)), 1)

    def test_own_discovery_returned_by_peer_does_not_create_candidate(self):
        self.edit(self.v, "own-discovery", record("Conhecimento originalmente meu."))
        self.receipt(entries=list(self.v.entries()))
        self.assertEqual(curation_plan(self.v)["candidates"], [])
        self.assertEqual(len(all_entries(self.v)), 1)

    def test_collision_remaps_groups_projects_entities_and_episodes(self):
        self.edit(self.v, "R1", record("Outro conhecimento já existente.", scope=["Other"]))
        self.edit(self.v, "P1", dict(title="Projeto local", scope=["Other"], kind="project", members=[]), "groups")
        project = dict(title="Projeto remoto", scope=["Org"], kind="project", members=["R1", "E1", "EP1"])
        entity = dict(title="sync.p", scope=["Org", "App"], relations=[dict(type="handled_by", target="R1")])
        episode = dict(title="Diagnóstico", scope=["Org", "App"], state="confirmed", objective="Localizar rotina",
            context="Checklist não chega", outcome="Rotina encontrada", actions=["Inspeção"], validation=["Leitura"],
            evidence=[dict(type="code", ref="sync.p", level="static")], learnings=["R1"])
        changes = [dict(collection="groups", id="P1", value=project), dict(collection="entities", id="E1", value=entity),
                   dict(collection="episodes", id="EP1", value=episode),
                   dict(collection="records", id="R1", value=record(project_id="P1", entities=["E1"], episodes=["EP1"]))]
        p = self.remote.prepare(changes, A, "test"); self.remote.apply(p["id"], p["approval_hash"]); self.receipt()
        self.apply()
        snapshot = self.v.snapshot()
        imported = next(e for i, e in snapshot["records"].items() if i != "R1")
        self.assertNotEqual(imported["project_id"], "P1")
        self.assertIn(imported["id"], snapshot["groups"][imported["project_id"]]["members"])
        self.assertEqual(snapshot["episodes"]["EP1"]["learnings"], [imported["id"]])
        self.assertEqual(snapshot["entities"]["E1"]["relations"][0]["target"], imported["id"])

    def test_remote_summary_cannot_confirm_pending_member_revision(self):
        self.apply()
        local = value_of(self.v.snapshot()["records"]["R1"]); local["content"] += " Local."
        self.edit(self.v, "R1", local)
        external = value_of(self.remote.snapshot()["records"]["R1"]); external["content"] += " Externo."
        self.edit(self.remote, "R1", external)
        self.edit(self.remote, "G1", dict(title="Resumo", scope=["Org"], kind="topic", members=["R1"],
            summary="Resumo da revisão externa não incorporada", summary_sources={"R1": 2}), "groups")
        self.edit(self.remote, "G2", dict(title="Resumo ancestral", scope=["Org"], kind="collection", members=["G1"],
            summary="Também contém a revisão externa não incorporada", summary_sources={"G1": 1}), "groups")
        self.receipt()
        self.apply({"R1": ("pending", {})})
        self.assertNotIn("summary", self.v.snapshot()["groups"]["G1"])
        self.assertNotIn("summary", self.v.snapshot()["groups"]["G2"])

    def test_same_batch_cannot_add_equivalent_origins_twice(self):
        self.edit(self.remote, "R2", record()); self.receipt()
        with self.assertRaises(ValueError): self.apply()
        self.assertEqual(self.v.snapshot()["records"], {})

    def test_offline_sync_keeps_usable_cache_without_claiming_fetch_success(self):
        with patch("memory_runtime.gitstore.settle", return_value=None), \
             patch("memory_runtime.gitstore.reconcile", return_value=dict(status="unchanged")), \
             patch("memory_runtime.sources.refresh", return_value=[dict(source="peer", status="offline_or_invalid", cached=True)]):
            report = sync(self.v)
        self.assertEqual(report["sources"][0]["status"], "offline_or_invalid")
        self.assertEqual(len(report["curation"]["candidates"]), 1)
        self.assertEqual(self.v.snapshot()["records"], {})


class SourcePublicationTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(); self.addCleanup(self.temp.cleanup)
        self.directory = Path(self.temp.name); self.v = Vault(self.directory / "own"); self.v.bootstrap("own")
        git(self.v.root, "init", "-b", "main"); git(self.v.root, "config", "user.name", "Test")
        git(self.v.root, "config", "user.email", "test@example.com")
        git(self.v.root, "add", "."); git(self.v.root, "commit", "-m", "initial")
        self.remote = self.directory / "remote.git"; run("git", "init", "--bare", str(self.remote))
        git(self.v.root, "remote", "add", "origin", str(self.remote)); git(self.v.root, "push", "-u", "origin", "main")
        self.source = dict(id="peer", remote="https://github.com/demo/memory", includes=[["Org"]], incorporate=True)

    def test_registry_is_committed_and_cloned_without_cache(self):
        result = source_add(self.v, self.source)
        self.assertEqual(result["publication"]["status"], "published")
        self.assertFalse(git(self.v.root, "status", "--porcelain").stdout.strip())
        clone = self.directory / "clone"; run("git", "clone", "--branch", "main", str(self.remote), str(clone))
        self.assertEqual(source_config(Vault(clone))["peer"]["includes"], [["Org"]])
        self.assertFalse((clone / ".yabook-local").exists())
        self.assertNotIn(".yabook-local", git(self.v.root, "ls-files").stdout)

    def test_pending_publication_blocks_registry_without_dirtying_it(self):
        value = record(); p = self.v.prepare([dict(collection="records", id="R1", value=value)], A, "test")
        applied = self.v.apply(p["id"], p["approval_hash"])
        with patch("memory_runtime.gitstore.git", wraps=git) as tool:
            original = git
            def fail_push(root, *args, **kwargs):
                if args and args[0] == "push":
                    from subprocess import CompletedProcess
                    return CompletedProcess(args, 1, "", "offline")
                return original(root, *args, **kwargs)
            tool.side_effect = fail_push
            result = publish(self.v, applied["paths"], "record")
        self.assertEqual(result["status"], "pending_push")
        with self.assertRaises(ValueError): source_add(self.v, self.source)
        self.assertFalse((self.v.root / "sources.json").exists())
        self.assertFalse(git(self.v.root, "status", "--porcelain").stdout.strip())

    def test_registry_journal_recovers_failure_before_publication(self):
        with patch("memory_runtime.sources.publish", side_effect=OSError("interrupted")):
            with self.assertRaises(OSError): source_add(self.v, self.source)
        self.assertTrue((self.v.local / "source-config.json").exists())
        result = source_add(self.v, self.source)
        self.assertEqual(result["publication"]["status"], "published")
        self.assertFalse((self.v.local / "source-config.json").exists())
        self.assertFalse(git(self.v.root, "status", "--porcelain").stdout.strip())


if __name__ == "__main__": unittest.main()
