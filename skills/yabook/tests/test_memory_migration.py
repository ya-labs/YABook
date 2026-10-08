import json
import subprocess
import shutil
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from memory_runtime.core import Vault, digest, read_json, write_json
from memory_runtime.gitstore import init_plan, init_apply
from memory_runtime.migration import start, block, checkpoint, coverage, validate_targets


class MigrationTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.source = self.root / "native"
        self.source.mkdir()
        (self.source / "MEMORY.md").write_text("linha 1\nlinha 2\nlinha 3\nlinha 4\nlinha 5\n")
        self.state = self.root / "checkpoint.json"
        start("any-agent", self.source, self.state, 2)

    def review(self, identifier, decision="discarded", targets=None):
        state = read_json(self.state)
        return checkpoint(self.state, dict(checkpoint_hash=digest(state), reviews=[dict(
            id=identifier, decision=decision, reason="Avaliação explícita", targets=targets or [])]))

    def test_reads_every_line_and_resumes_without_repeating_review(self):
        state = read_json(self.state)
        text = "".join(block(state, b["id"])["text"] for b in state["blocks"])
        self.assertEqual(text, (self.source / "MEMORY.md").read_text())
        self.review(state["blocks"][0]["id"])
        report = start("any-agent", self.source, self.state, 2)
        self.assertEqual(report["counts"]["discarded"], 1)
        self.assertEqual(block(read_json(self.state))["first"], 3)
        self.assertFalse(report["complete"])

    def test_source_changes_invalidate_only_changed_files(self):
        second = self.source / "other.md"
        second.write_text("outra memória")
        start("any-agent", self.source, self.state, 2)
        state = read_json(self.state)
        for b in state["blocks"]:
            self.review(b["id"])
        (self.source / "MEMORY.md").write_text("alterada")
        with self.assertRaisesRegex(ValueError, "Origem mudou"):
            coverage(read_json(self.state))
        report = start("any-agent", self.source, self.state, 2)
        self.assertEqual(report["counts"]["discarded"], 1)
        self.assertEqual(report["counts"]["unreviewed"], 1)

    def test_secret_is_never_returned_and_requires_exclusion(self):
        (self.source / "secret.md").write_text("sk-" + "x" * 30)
        start("any-agent", self.source, self.state, 2)
        state = read_json(self.state)
        secret = next(b for b in state["blocks"] if b["status"] == "sensitive")
        self.assertEqual(block(state, secret["id"])["text"], "")
        with self.assertRaises(ValueError):
            self.review(secret["id"], "migrated", [dict(collection="records", id="R1")])
        self.review(secret["id"])

    def test_stale_checkpoint_and_pending_cannot_finish(self):
        state = read_json(self.state)
        stale = dict(checkpoint_hash=digest(state), reviews=[dict(id=state["blocks"][0]["id"],
                     decision="discarded", reason="Duplicada")])
        self.review(state["blocks"][1]["id"], "pending")
        with self.assertRaisesRegex(ValueError, "Checkpoint mudou"):
            checkpoint(self.state, stale)
        self.assertFalse(coverage(read_json(self.state))["complete"])

    def test_targets_require_existing_items_and_exact_provenance(self):
        state = read_json(self.state)
        b = state["blocks"][0]
        self.review(b["id"], "migrated", [dict(collection="records", id="R1")])
        state = read_json(self.state)
        curated = dict(changes=[])
        with self.assertRaisesRegex(ValueError, "ausente"):
            validate_targets(state, curated)
        curated["changes"] = [dict(collection="records", id="R1", value={})]
        with self.assertRaisesRegex(ValueError, "procedência"):
            validate_targets(state, curated)
        curated["changes"][0]["value"]["provenance"] = [dict(
            agent="any-agent", file=b["path"], hash=b["hash"], lines="1-2")]
        validate_targets(state, curated)

    def test_state_cannot_pollute_origin_and_large_files_are_not_skipped(self):
        with self.assertRaises(ValueError):
            start("any-agent", self.source, self.source / "progress.json")
        (self.source / "large.md").write_text("x" * 1_000_001)
        report = start("any-agent", self.source, self.state, 2)
        state = read_json(self.state)
        large = next(b for b in state["blocks"] if b["path"].endswith("large.md"))
        self.assertEqual(len(block(state, large["id"])["text"]), 1_000_001)
        self.assertEqual(report["files"], 2)

    def gh(self, *args, **kwargs):
        body = {"login": "home-login"} if args == ("gh", "api", "user") else {"private": True}
        return subprocess.CompletedProcess(args, 0, json.dumps(body), "")

    def test_explicit_existing_repository_preserves_vault_owner_and_baseline(self):
        v = Vault(self.root / "vault")
        v.bootstrap("work-login")
        def local_git(root, *args, **kwargs):
            value = "https://github.com/work-login/Personal-memory.git" if args[0] == "remote" else (
                "main" if args[0] == "branch" else "abc" if args[0] == "rev-parse" and args[1] == "HEAD" else str(v.root) if args[0] == "rev-parse" else "")
            return subprocess.CompletedProcess(args, 0, value + "\n", "")
        def gh(*args, **kwargs):
            if "/commits/" in args[-1]:
                return subprocess.CompletedProcess(args, 0, '{"sha":"abc"}', "")
            return self.gh(*args, **kwargs)
        (v.root / ".git").mkdir()
        with patch("memory_runtime.gitstore.run", side_effect=gh), patch("memory_runtime.gitstore.git", side_effect=local_git):
            plan = init_plan(v.root, "any-agent", self.source, repository="work-login/Personal-memory")
        self.assertEqual(plan["repository"], "work-login/Personal-memory")
        self.assertEqual(plan["baseline"]["metadata"]["owner"], "work-login")
        self.assertEqual(plan["base_hash"], digest(v.snapshot()))

    def test_final_plan_requires_complete_checkpoint(self):
        with self.assertRaisesRegex(ValueError, "checkpoint"):
            init_plan(self.root / "vault", "any-agent", self.source, curated={"changes": []})
        with patch("memory_runtime.gitstore.run", side_effect=self.gh):
            with self.assertRaisesRegex(ValueError, "incompleta"):
                init_plan(self.root / "vault", "any-agent", self.source, curated={"changes": []}, migration=read_json(self.state))

    def test_changed_baseline_rejected_before_publication(self):
        v = Vault(self.root / "vault"); v.bootstrap("home-login")
        plan = dict(owner="home-login", repository="home-login/custom", root=str(v.root), existing=True,
                    inventory=dict(agent="any-agent", files=[]), curated_hash=digest({"changes": []}), base_hash="old")
        plan["approval_hash"] = digest(plan)
        with patch("memory_runtime.gitstore.run", side_effect=self.gh), patch("memory_runtime.gitstore.clean"):
            with self.assertRaisesRegex(ValueError, "Base mudou"):
                init_apply(plan, plan["approval_hash"], {"changes": []}, self.root / "config.json")

    def test_changed_remote_rejected_before_cloning(self):
        plan = dict(owner="home-login", repository="home-login/custom", root=str(self.root / "vault"),
                    existing=True, inventory=dict(agent="any-agent", files=[]),
                    curated_hash=digest({"changes": []}), remote_revision="approved", branch="main")
        plan["approval_hash"] = digest(plan)
        def gh(*args, **kwargs):
            if "/commits/" in args[-1]:
                return subprocess.CompletedProcess(args, 0, '{"sha":"changed"}', "")
            return self.gh(*args, **kwargs)
        with patch("memory_runtime.gitstore.run", side_effect=gh):
            with self.assertRaisesRegex(ValueError, "Remoto mudou"):
                init_apply(plan, plan["approval_hash"], {"changes": []}, self.root / "config.json")
        self.assertFalse((self.root / "vault").exists())

    def test_preview_clones_existing_base_only_into_temporary_directory(self):
        def gh(*args, **kwargs):
            if args[:3] == ("gh", "repo", "clone"):
                Vault(args[-1]).bootstrap("work-login")
                return subprocess.CompletedProcess(args, 0, "", "")
            return self.gh(*args, **kwargs)
        def local_git(root, *args, **kwargs):
            return subprocess.CompletedProcess(args, 0, "main" if args[0] == "branch" else "abc", "")
        with patch("memory_runtime.gitstore.run", side_effect=gh), patch("memory_runtime.gitstore.git", side_effect=local_git):
            plan = init_plan(self.root / "vault", "any-agent", self.source, repository="work-login/Personal-memory")
        self.assertFalse((self.root / "vault").exists())
        self.assertEqual(plan["baseline"]["metadata"]["owner"], "work-login")
        self.assertEqual(plan["remote_revision"], "abc")

    def test_approved_clone_keeps_identity_when_authenticated_account_differs(self):
        original = Vault(self.root / "remote-base"); original.bootstrap("work-login")
        (original.root / ".git").mkdir()
        target = self.root / "home-base"
        curated = {"changes": []}
        plan = dict(owner="home-login", repository="work-login/custom", root=str(target), existing=True,
                    inventory=dict(agent="any-agent", files=[]), curated_hash=digest(curated),
                    base_hash=digest(original.snapshot()), remote_revision="abc", branch="main")
        plan["approval_hash"] = digest(plan)
        def gh(*args, **kwargs):
            if args[:3] == ("gh", "repo", "clone"):
                shutil.copytree(original.root, args[-1])
                return subprocess.CompletedProcess(args, 0, "", "")
            if "/commits/" in args[-1]:
                return subprocess.CompletedProcess(args, 0, '{"sha":"abc"}', "")
            return self.gh(*args, **kwargs)
        def local_git(root, *args, **kwargs):
            if args[0] == "remote": value = "https://github.com/work-login/custom.git"
            elif args[0] == "branch": value = "main"
            elif args[:2] == ("rev-parse", "--show-toplevel"): value = str(target)
            elif args[0] == "rev-parse": value = "abc"
            else: value = ""
            return subprocess.CompletedProcess(args, 0, value, "")
        with patch("memory_runtime.gitstore.run", side_effect=gh), patch("memory_runtime.gitstore.git", side_effect=local_git):
            result = init_apply(plan, plan["approval_hash"], curated, self.root / "config.json")
        self.assertEqual(result["status"], "unchanged")
        self.assertEqual(read_json(target / "memory.json"), read_json(original.root / "memory.json"))
        self.assertEqual(read_json(self.root / "config.json")["repository"], "work-login/custom")


if __name__ == "__main__":
    unittest.main()
