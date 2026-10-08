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
