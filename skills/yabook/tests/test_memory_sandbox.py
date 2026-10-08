import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from memory_runtime.core import Vault, write_json
from memory_runtime.learning import learn
from memory_runtime.sandbox import codex_blocks, read_codex_sandbox
import yabook_hook as hook


class SandboxTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.toml = self.root / "config.toml"
        env = patch.dict(os.environ, YABOOK_QUEUE=str(self.root / "queue"))
        env.start(); self.addCleanup(env.stop)

    def test_reads_writable_roots_and_permission_profiles(self):
        self.toml.write_text('model = "x"\n[plugins."a"]\nenabled = true\n\n[sandbox_workspace_write]\n'
                             'writable_roots = [\n  "/data/memory",\n  "~/outro",\n]\n')
        settings = read_codex_sandbox(self.toml)
        self.assertEqual(settings, dict(default_permissions=False, writable_roots=["/data/memory", "~/outro"]))
        self.assertIsNone(codex_blocks("/data/memory/sub", settings))
        blocked = codex_blocks("/data/outra-base", settings)
        self.assertIn('writable_roots = ["/data/outra-base"]', blocked["suggestion"])
        self.toml.write_text('default_permissions = "dev"\n[permissions.dev]\nextends = ":workspace"\n')
        self.assertIn("perfil", codex_blocks("/data/memory", read_codex_sandbox(self.toml))["suggestion"])
        self.assertIsNone(read_codex_sandbox(self.root / "ausente.toml"))

    def test_learn_queues_and_hook_applies_outside_sandbox(self):
        from memory_runtime.queue import apply_queue, pending_notices
        vault, config, payload = self.read_only_setup()
        result = learn(vault, payload, "test", config, self.root)
        self.assertEqual((result["status"], result["changed"]), ("queued", False))
        self.assertEqual(vault.snapshot()["records"], {})
        vault.local.chmod(0o755)
        applied = apply_queue(config)
        self.assertEqual([r["status"] for r in applied], ["memory_updated"])
        self.assertIn("R", vault.snapshot()["records"])
        self.assertEqual(list((self.root / "queue").glob("*.json")), [])
        self.assertEqual(pending_notices(), [])

    def test_queue_rejects_other_base_and_tampering(self):
        from memory_runtime.queue import apply_queue, enqueue, pending_notices
        vault, config, payload = self.read_only_setup()
        vault.local.chmod(0o755)
        other = enqueue(self.root / "outra", payload, "test", config, self.root)
        tampered = enqueue(vault.root, payload, "test", config, self.root)
        text = tampered.read_text().replace('"test"', '"intruso"', 1); tampered.write_text(text)
        results = apply_queue(config)
        self.assertEqual([r["status"] for r in results], ["failed", "failed"])
        self.assertEqual(vault.snapshot()["records"], {})
        self.assertEqual(len(pending_notices()), 2)
        self.assertFalse(other.exists())

    def test_invalid_batch_is_rejected_before_queue_and_notices_stay_per_project(self):
        from memory_runtime.queue import apply_queue, enqueue, pending_notices
        vault, config, payload = self.read_only_setup()
        payload["changes"][0]["value"]["evidence"] = ["texto livre"]
        with self.assertRaisesRegex(ValueError, "type e level"):
            learn(vault, payload, "test", config, self.root)
        self.assertFalse(list((self.root / "queue").glob("*.json")) if (self.root / "queue").exists() else [])
        vault.local.chmod(0o755)
        enqueue(self.root / "outra", payload, "test", config, "/projeto/a")
        enqueue(self.root / "outra", payload, "test", config, "/projeto/b")
        apply_queue(config)
        self.assertEqual([n["workspace"] for n in pending_notices("/projeto/b")], ["/projeto/b"])
        self.assertEqual([n["workspace"] for n in pending_notices("/projeto/a")], ["/projeto/a"])
        self.assertEqual(pending_notices("/projeto/a"), [])

    def read_only_setup(self):
        vault = Vault(self.root / "memory"); vault.bootstrap("demo")
        config = self.root / "yabook.json"
        write_json(config, {"memory_root": str(vault.root), "projects": {str(self.root): ["Demo"]},
                            "learning": {"mode": "automatic"}})
        vault.local.mkdir(exist_ok=True)
        vault.local.chmod(0o555)
        self.addCleanup(vault.local.chmod, 0o755)
        payload = {"learning": {"source": "development", "conflicts": []},
                   "assessment": dict(verdict="add", reason="r", utility="u", application="a", evidence_status="e"),
                   "changes": [dict(collection="records", id="R", value=dict(
                       title="T", kind="knowledge", scope=["Demo"], content="c", application="a", state="confirmed",
                       evidence=[dict(type="code", ref="x", level="static")], triggers=["dado não aparece"]))]}
        return vault, config, payload

    def test_learn_reports_read_only_sandbox_without_changing_base(self):
        vault = Vault(self.root / "memory"); vault.bootstrap("demo")
        config = self.root / "yabook.json"
        write_json(config, {"memory_root": str(vault.root), "projects": {str(self.root): ["Demo"]},
                            "learning": {"mode": "automatic"}})
        vault.local.mkdir(exist_ok=True)
        vault.local.chmod(0o555)
        self.addCleanup(vault.local.chmod, 0o755)
        payload = {"learning": {"source": "development", "conflicts": []},
                   "assessment": dict(verdict="add", reason="r", utility="u", application="a", evidence_status="e"),
                   "changes": [dict(collection="records", id="R", value=dict(
                       title="T", kind="knowledge", scope=["Demo"], content="c", application="a", state="confirmed",
                       evidence=[dict(type="code", ref="x", level="static")], triggers=["dado não aparece"]))]}
        (self.root / "queue").write_text("")  # fila indisponível, como no modo somente leitura
        with patch("memory_runtime.sandbox.read_codex_sandbox", return_value={"default_permissions": False, "writable_roots": []}):
            result = learn(vault, payload, "test", config, self.root)
        self.assertEqual((result["status"], result["changed"]), ("sandbox_read_only", False))
        self.assertIn(str(vault.root), result["hint"]["suggestion"])
        self.assertEqual(vault.snapshot()["records"], {})

    def test_session_start_warns_only_when_codex_blocks_memory(self):
        self.toml.write_text('model = "x"\n')
        cfg = self.root / "yabook.json"
        write_json(cfg, {"memory_root": str(self.root / "memory"), "learning": {"mode": "automatic"}})
        env = dict(YABOOK_CONFIG=str(cfg), YABOOK_STATE=str(self.root / "s"), CODEX_HOME=str(self.root))
        event = dict(session_id="s", hook_event_name="SessionStart", source="startup", cwd=self.tmp.name)
        with patch.dict(os.environ, env), patch.object(hook, "git", return_value=""):
            text = hook.run(event)["hookSpecificOutput"]["additionalContext"]
            self.assertIn("não grava no sandbox do Codex", text)
            self.toml.write_text('[sandbox_workspace_write]\nwritable_roots = ["%s"]\n' % (self.root / "memory"))
            text = hook.run(event)["hookSpecificOutput"]["additionalContext"]
            self.assertNotIn("não grava no sandbox do Codex", text)


if __name__ == "__main__":
    unittest.main()
