"""Prévia, execução e isolamento de autorização no protocolo de hooks."""
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import yabook_hook as hook
from memory_runtime.core import Vault


class CommandAuthorizationTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.memory = self.root / "memory"
        self.vault = Vault(self.memory)
        self.vault.bootstrap("test")
        env = patch.dict(os.environ, YABOOK_CONFIG=str(self.root / "config.json"),
                         YABOOK_STATE=str(self.root / "sessions"))
        env.start(); self.addCleanup(env.stop)
        hook.write_json(hook.config_path(), {"memory_root": str(self.memory), "learning": {"mode": "automatic"}})
        fake_git = patch.object(hook, "git", return_value="feature")
        fake_git.start(); self.addCleanup(fake_git.stop)

    def state(self, prompt, previous=None):
        return hook.prompt_grant(prompt, previous or {}, str(self.root))

    def denied(self, state, command="", name="Bash", args=None):
        result = hook.inspect_call({"tool_name": name, "tool_input": args or {"command": command}},
                                   state, str(self.root))
        return result.get("hookSpecificOutput", {}).get("permissionDecision") == "deny"

    def memory_call(self, service):
        return f"python3 -B yabook_memory.py --root {self.memory} {service}"

    def test_preview_overrides_auto_and_discards_old_grant(self):
        old = self.state("$yabook mode auto & do memory clean")
        for prefix in ("yabook", "$yabook", "/yabook:yabook", "[$yabook:yabook](/path/SKILL.md)"):
            state = self.state(prefix + " memory clean", dict(old))
            self.assertTrue(state["read_only"])
            self.assertIsNone(state["grant"])
            for operation in ("prepare --input x", "apply P-x --approval-hash x", "clean-done --batches 0",
                              "publish", "learn --input x --actor codex", "clean-check --save-before"):
                self.assertTrue(self.denied(state, self.memory_call(operation)), operation)
            self.assertFalse(self.denied(state, self.memory_call("clean-check")))

    def test_preview_blocks_edits_git_issues_tasks_and_graphql_mutations(self):
        state = self.state("$yabook issue")
        for command in ("git add x", "git commit -m x", "gh issue create --title x",
                        "gh api graphql -f 'query=mutation { createIssue }'",
                        "python3 yabook_tasks.py edit tarefa --titulo x"):
            self.assertTrue(self.denied(state, command), command)
        for name in ("apply_patch", "functions.apply_patch", "mcp__codex_apps__github_create_issue"):
            self.assertTrue(self.denied(state, name=name, args={"input": "patch"}), name)
        for command in ("rtk git status", "git diff", "git branch --show-current", "rg 'apply' yabook_memory.py",
                        "rg python3 yabook_memory.py --root /other apply", self.memory_call("retrieve apply"),
                        self.memory_call("apply --help"), "python3 yabook_tasks.py search edit",
                        "gh issue view 184", "gh api graphql -f 'query={ viewer { login } }'"):
            self.assertFalse(self.denied(state, command), command)

    def test_natural_execution_is_authorized_without_do(self):
        for prompt in ("crie uma issue sobre X", "Por favor, crie uma issue", "$yabook crie uma issue",
                       "faça a faxina da memória", "pode implementar a correção"):
            state = self.state(prompt, self.state("$yabook issue"))
            self.assertFalse(state["read_only"], prompt)
            self.assertFalse(self.denied(state, "gh issue create --title x"), prompt)
        for prompt in ("como criar uma issue?", 'se eu digitar "crie uma issue"',
                       '`$yabook do issue`', '```\n$yabook do issue\n```'):
            self.assertNotEqual((self.state(prompt).get("grant") or {}).get("kind"), "context", prompt)

    def test_memory_valid_hash_does_not_replace_permission(self):
        proposal = self.vault.prepare([{"collection": "groups", "id": "G", "value": {
            "title": "Grupo", "scope": ["Demo"], "kind": "topic", "members": []}}],
            {key: "test" for key in ("reason", "utility", "application", "evidence_status")} | {"verdict": "add"}, "test")
        command = self.memory_call(f"apply {proposal['id']} --approval-hash {proposal['approval_hash']}")
        self.assertTrue(self.denied({}, command))
        self.assertTrue(self.denied(self.state("$yabook memory clean"), command))
        self.assertFalse(self.denied(self.state("$yabook do memory clean"), command))
        self.assertFalse(self.denied(self.state("aplique a proposta de memória"), command))
        self.assertTrue(self.denied(self.state("$yabook do memory policy manual"), command))

    def test_natural_request_does_not_unlock_unrelated_git_risks(self):
        state = self.state('crie uma issue sobre "merge"')
        self.assertFalse(state.get("merge_requested", False))
        for command in ("git push --force-with-lease origin feature", "git push origin main", "git merge other"):
            self.assertTrue(self.denied(state, command), command)
        self.assertFalse(self.denied(self.state("pode fazer o merge da outra"), "git merge other"))

    def test_read_only_snapshot_uses_existing_shared_lock(self):
        import fcntl
        self.vault.snapshot()  # cria a trava antes da consulta
        with patch("fcntl.flock", wraps=fcntl.flock) as flock:
            self.assertEqual(self.vault.snapshot(read_only=True)["metadata"]["owner"], "test")
            self.assertEqual(flock.call_args.args[1], fcntl.LOCK_SH)
        hook.write_json(self.memory / ".yabook-local/transaction.json", {})
        with self.assertRaisesRegex(ValueError, "Transação interrompida"):
            self.vault.snapshot(read_only=True)

    def test_executive_chain_does_not_promote_other_preview(self):
        state = self.state("$yabook mode auto & do issue & memory clean")
        self.assertFalse(self.denied(state, "gh issue create --title x"))
        self.assertTrue(self.denied(state, self.memory_call("publish")))
        state = self.state("$yabook memory clean & do memory clean")
        self.assertFalse(self.denied(state, self.memory_call("clean-done --batches 0")))
        state = self.state("$yabook mode auto & do issue & pr")
        self.assertTrue(self.denied(state, name="mcp__codex_apps__github_create_pull_request"))

    def test_empty_invocation_is_a_preview(self):
        for prompt in ("$yabook", "yabook ", "[$yabook:yabook](/path/SKILL.md)"):
            state = self.state(prompt, self.state("$yabook do issue"))
            self.assertTrue(state["read_only"], prompt)
            self.assertIsNone(state["grant"], prompt)

    def test_dev_authorizes_issue_and_branch_preparation(self):
        state = self.state("$yabook dev", self.state("$yabook issue"))
        self.assertEqual(state["grant"]["kind"], "dev")
        self.assertFalse(self.denied(state, "gh issue create --title x"))
        self.assertFalse(self.denied(state, "git switch -c 184-ajuste"))
        self.assertFalse(self.denied(state, name="Edit", args={"file_path": "x.py"}))
        reference = (Path(__file__).resolve().parents[1] / "references/dev.md").read_text()
        for text in ("crie-a", "sem exigir `do issue`", "sem pedir `do branch`", "Reutilize issue existente"):
            self.assertIn(text, reference)
        self.assertIn("criar commit", reference)

    def test_preview_stop_skips_background_mutations(self):
        event = {"hook_event_name": "Stop", "session_id": "preview", "cwd": str(self.root)}
        hook.write_json(hook.state_path(event), {"project": "feature", "read_only": True, "auto": True})
        with patch.object(hook, "project", return_value="feature"), \
             patch.object(hook, "apply_learning_queue") as queue, \
             patch.object(hook, "publish_automatic") as publish, \
             patch.object(hook, "tasks_capture") as tasks:
            self.assertEqual(hook.run(event), {})
            queue.assert_not_called(); publish.assert_not_called(); tasks.assert_not_called()

    def test_clean_check_cli_leaves_base_unchanged(self):
        cli = Path(__file__).resolve().parents[1] / "scripts/yabook_memory.py"
        before = {p.relative_to(self.memory): p.read_bytes() for p in self.memory.rglob("*") if p.is_file()}
        call = [sys.executable, "-B", str(cli), "--root", str(self.memory), "clean-check"]
        result = subprocess.run(call, text=True, capture_output=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        json.loads(result.stdout)
        after = {p.relative_to(self.memory): p.read_bytes() for p in self.memory.rglob("*") if p.is_file()}
        self.assertEqual(before, after)
        result = subprocess.run(call + ["--save-before"], text=True, capture_output=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue((self.memory / ".yabook-local/clean-check.json").is_file())


if __name__ == "__main__":
    unittest.main()
