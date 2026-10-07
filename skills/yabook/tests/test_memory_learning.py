import copy
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from memory_runtime.core import Vault, write_json
from memory_runtime.gitstore import git
from memory_runtime.learning import learn, recent, set_policy


class LearningTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.vault = Vault(self.root / "memory")
        self.vault.bootstrap("demo")
        self.cfg = self.root / "config.json"
        self.config = {"memory_root": str(self.vault.root), "projects": {str(self.root): ["Demo"]}, "learning": {"mode": "automatic"}}
        write_json(self.cfg, self.config)
        self.payload = {
            "learning": {"source": "development", "conflicts": []},
            "assessment": dict(verdict="add", reason="Responsabilidade rastreada", utility="Evitar investigação repetida",
                               application="Investigar sincronização", evidence_status="Código examinado"),
            "changes": [dict(collection="records", id="R-sync", value=dict(
                title="Responsabilidade", kind="knowledge", scope=["Demo"], content="Operação recebe dados",
                application="Investigar recebimento", state="confirmed", evidence=[dict(type="code", ref="fixture:source@revision", level="static")]))]}

    def run_learning(self, payload=None):
        return learn(self.vault, payload or self.payload, "test-agent", self.cfg, self.root)

    def test_confirmed_learning_history_views_and_idempotence(self):
        result = self.run_learning()
        self.assertEqual(result["status"], "memory_updated")
        self.assertEqual(result["publication"]["status"], "local_only")
        self.assertTrue((self.vault.root / "views/MEMORY.md").exists())
        history = recent(self.vault)
        self.assertEqual(history[0]["assessment"]["learning"]["mode"], "automatic")
        self.assertNotIn("snapshot", history[0])
        self.assertEqual(self.run_learning()["status"], "unchanged")
        self.assertEqual(len(recent(self.vault)), 1)

    def test_hypothesis_conflict_and_wrong_scope_do_not_change_base(self):
        baseline = self.vault.snapshot()
        for field, value in (("state", "hypothesis"), ("scope", ["Another"])):
            payload = copy.deepcopy(self.payload)
            payload["changes"][0]["value"][field] = value
            result = self.run_learning(payload)
            self.assertEqual(result["status"], "pending_review")
            self.assertEqual(self.vault.snapshot(), baseline)
        payload = copy.deepcopy(self.payload)
        payload["changes"][0]["value"]["evidence"] = []
        with self.assertRaisesRegex(ValueError, "evidência"):
            self.run_learning(payload)
        self.assertEqual(self.vault.snapshot(), baseline)
        payload = copy.deepcopy(self.payload)
        payload["learning"]["conflicts"] = ["Diverge do contrato atual"]
        self.assertEqual(self.run_learning(payload)["status"], "pending_review")
        self.assertEqual(self.vault.snapshot(), baseline)
        self.assertTrue(any(item["kind"] == "pending_proposal" for item in self.vault.review()))

    def test_duplicate_and_external_origin_remain_pending(self):
        self.run_learning()
        payload = copy.deepcopy(self.payload)
        payload["changes"][0]["id"] = "R-duplicate"
        self.assertEqual(self.run_learning(payload)["status"], "pending_review")
        payload["changes"][0]["value"]["content"] = "Conhecimento externo"
        payload["changes"][0]["value"]["origin"] = dict(vault_id="other-vault", id="external", revision=1)
        self.assertEqual(self.run_learning(payload)["status"], "pending_review")
        self.assertNotIn("R-duplicate", self.vault.snapshot()["records"])

    def test_preferences_require_user_statement_and_explicit_authority(self):
        payload = copy.deepcopy(self.payload)
        entry = payload["changes"][0]["value"]
        entry.update(kind="preference", scope=["Pessoa"], authority="inferred", activation="conditional")
        payload["learning"]["source"] = "user_statement"
        self.assertEqual(self.run_learning(payload)["status"], "pending_review")
        entry.update(authority="explicit", activation="always")
        self.assertEqual(self.run_learning(payload)["status"], "memory_updated")

    def test_delete_is_pending_and_legacy_policy_is_manual(self):
        self.run_learning()
        payload = copy.deepcopy(self.payload)
        payload["assessment"]["verdict"] = "delete"
        payload["changes"] = [dict(collection="records", id="R-sync", delete=True)]
        self.assertEqual(self.run_learning(payload)["status"], "pending_review")
        self.assertIn("R-sync", self.vault.snapshot()["records"])
        self.config.pop("learning")
        write_json(self.cfg, self.config)
        payload = copy.deepcopy(self.payload)
        payload["changes"][0]["value"]["content"] = "Complemento comprovado"
        self.assertEqual(self.run_learning(payload)["status"], "pending_review")
        set_policy(self.cfg, self.vault.root, "automatic")
        self.assertEqual(self.run_learning(payload)["status"], "memory_updated")

    def test_git_checkpoint_one_commit_for_batch_and_dirty_blocks(self):
        git(self.vault.root, "init", "-b", "main")
        git(self.vault.root, "config", "user.name", "Demo")
        git(self.vault.root, "config", "user.email", "demo@example.invalid")
        git(self.vault.root, "add", ".")
        git(self.vault.root, "commit", "-m", "docs: base")
        remote = self.root / "remote.git"
        git(self.root, "init", "--bare", str(remote))
        git(self.vault.root, "remote", "add", "origin", str(remote))
        second = copy.deepcopy(self.payload["changes"][0])
        second["id"] = "R-second"
        second["value"]["content"] = "Outra responsabilidade comprovada"
        self.payload["changes"].append(second)
        result = self.run_learning()
        self.assertEqual(result["publication"]["status"], "published")
        self.assertEqual(git(self.vault.root, "rev-list", "--count", "HEAD").stdout.strip(), "2")
        self.assertFalse(git(self.vault.root, "status", "--porcelain").stdout.strip())
        (self.vault.root / "unrelated.txt").write_text("preservar")
        self.payload["changes"][0]["value"]["content"] = "Novo complemento"
        with self.assertRaisesRegex(ValueError, "Alterações independentes"):
            self.run_learning()

    def test_sandbox_batches_accumulate_until_publication_outside(self):
        from memory_runtime.gitstore import publish
        git(self.vault.root, "init", "-b", "main")
        git(self.vault.root, "config", "user.name", "Demo")
        git(self.vault.root, "config", "user.email", "demo@example.invalid")
        git(self.vault.root, "add", ".")
        git(self.vault.root, "commit", "-m", "docs: base")
        remote = self.root / "remote.git"
        git(self.root, "init", "--bare", str(remote))
        git(self.vault.root, "remote", "add", "origin", str(remote))
        lock = self.vault.root / ".git/index.lock"
        lock.write_text("")  # .git protegido como no sandbox do agente
        first = self.run_learning()
        self.assertEqual((first["status"], first["publication"]["status"]), ("memory_updated", "pending_commit"))
        payload = copy.deepcopy(self.payload)
        payload["changes"][0]["id"] = "R-second"
        payload["changes"][0]["value"]["content"] = "Outra responsabilidade comprovada"
        second = self.run_learning(payload)
        self.assertEqual(second["publication"]["status"], "pending_commit")
        lock.unlink()
        self.assertEqual(publish(self.vault)["status"], "published")
        self.assertEqual(git(self.vault.root, "rev-list", "--count", "HEAD").stdout.strip(), "2")
        self.assertFalse(git(self.vault.root, "status", "--porcelain").stdout.strip())
        self.assertIn("R-second", self.vault.snapshot()["records"])


if __name__ == "__main__":
    unittest.main()
