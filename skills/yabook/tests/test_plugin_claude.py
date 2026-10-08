import shutil
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from host_claude import marketplace_root, sync_claude
from host_directory import MARKER
from memory_runtime.core import read_json
from plugin_sync import sync_plugin
from yabook_plugin import build


class ClaudeAdapterTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.home = Path(self.temp.name)
        self.source = build(self.home / "source")
        self.installed = marketplace_root(self.home) / "plugins/yabook"
        self.calls = []

    def runner(self, arguments):
        self.calls.append(arguments[:2])
        return ""

    def test_fresh_install_registers_marketplace_and_plugin(self):
        self.assertEqual(sync_claude(self.source, self.installed, self.home)["status"], "not_installed")
        result = sync_claude(self.source, self.installed, self.home, apply=True, runner=self.runner)
        self.assertEqual((result["status"], result["registration"]), ("updated", "installed"))
        self.assertEqual(self.calls, [["marketplace", "add"], ["install", "yabook@yabook-local"]])
        manifest = read_json(marketplace_root(self.home) / ".claude-plugin/marketplace.json")
        self.assertEqual(manifest["plugins"][0]["source"], "./plugins/yabook")
        self.assertTrue((self.installed / MARKER).exists())

    def test_adopts_manual_install_updates_and_noop(self):
        sync_claude(self.source, self.installed, self.home, apply=True, runner=self.runner)
        (self.installed / MARKER).unlink()  # instalação manual anterior ao adaptador
        self.calls.clear()
        (self.source / "assets/yabook-icon.png").write_bytes(b"novo")
        self.assertEqual(sync_plugin(self.source, self.installed, self.home)["status"], "outdated")
        result = sync_claude(self.source, self.installed, self.home, apply=True, runner=self.runner)
        self.assertEqual((result["status"], result["adopted"], result["registration"]), ("updated", True, "updated"))
        self.assertEqual(self.calls, [["marketplace", "update"], ["update", "yabook@yabook-local"]])
        self.calls.clear()
        result = sync_claude(self.source, self.installed, self.home, apply=True, runner=self.runner)
        self.assertEqual((result["status"], self.calls), ("synchronized", []))

    def test_missing_claude_still_updates_package(self):
        def missing(arguments): raise FileNotFoundError("Claude Code não encontrado")
        result = sync_claude(self.source, self.installed, self.home, apply=True, runner=missing)
        self.assertEqual(result["status"], "updated")
        self.assertIn("nova sessão", result["registration"])

    def test_rejects_other_destination_and_foreign_marketplace(self):
        with self.assertRaisesRegex(ValueError, "marketplace local"):
            sync_claude(self.source, self.home / "outro", self.home, apply=True, runner=self.runner)
        manifest = marketplace_root(self.home) / ".claude-plugin/marketplace.json"
        manifest.parent.mkdir(parents=True)
        manifest.write_text('{"name": "outro"}')
        with self.assertRaisesRegex(ValueError, "outro instalador"):
            sync_claude(self.source, self.installed, self.home, apply=True, runner=self.runner)


if __name__ == "__main__":
    unittest.main()
