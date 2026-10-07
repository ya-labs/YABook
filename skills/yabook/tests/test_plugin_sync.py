import shutil
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from memory_runtime.core import read_json, write_json
from plugin_sync import compare, sync_codex, validate_package
from yabook_plugin import build, register_codex


class PluginSyncTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.home = Path(self.temp.name)
        self.source = build(self.home / "source")
        registered = register_codex(self.home, source=self.source)
        self.old = Path(registered["path"])
        self.installed = self.home / "cache"
        shutil.copytree(self.old, self.installed)
        self.registry = self.home / ".agents/plugins/marketplace.json"
        data = read_json(self.registry)
        data["plugins"].append(dict(name="other", source={}))
        write_json(self.registry, data)
        self.calls = []

    def host(self, arguments):
        self.calls.append(arguments)
        if arguments[0] == "remove":
            shutil.rmtree(self.installed)
        else:
            data = read_json(self.registry)
            entry = next(p for p in data["plugins"] if p["name"] == "yabook")
            shutil.copytree(self.home / entry["source"]["path"], self.installed)

    def change(self):
        (self.source / "assets/yabook-icon.png").write_bytes(b"new icon")

    def test_preview_compares_entire_plugin_without_writes(self):
        self.change()
        before = self.registry.read_bytes()
        result = sync_codex(self.source, self.installed, self.home, runner=self.host)
        self.assertEqual(result["changed"], ["assets/yabook-icon.png"])
        self.assertEqual(before, self.registry.read_bytes())
        self.assertEqual(self.calls, [])

    def test_update_then_noop_preserves_other_plugins_and_old_package(self):
        self.change()
        self.assertEqual(sync_codex(self.source, self.installed, self.home, True, self.host)["status"], "updated")
        self.assertEqual(compare(self.source, self.installed)["status"], "synchronized")
        self.assertTrue(self.old.exists())
        self.assertEqual(read_json(self.registry)["plugins"][-1]["name"], "other")
        calls = list(self.calls)
        sync_codex(self.source, self.installed, self.home, True, self.host)
        self.assertEqual(calls, self.calls)

    def test_failed_install_restores_old_package_and_registry(self):
        self.change()
        failed = False

        def flaky(arguments):
            nonlocal failed
            if arguments[0] == "add" and not failed:
                failed = True
                raise RuntimeError("host failure")
            self.host(arguments)

        with self.assertRaisesRegex(RuntimeError, "origem anterior restaurada"):
            sync_codex(self.source, self.installed, self.home, True, flaky)
        self.assertEqual(compare(self.old, self.installed)["status"], "synchronized")
        entry = next(p for p in read_json(self.registry)["plugins"] if p["name"] == "yabook")
        self.assertEqual((self.home / entry["source"]["path"]).resolve(), self.old)

    def test_incomplete_source_cannot_touch_installation(self):
        (self.source / "hooks/hooks.json").unlink()
        before = self.registry.read_bytes()
        with self.assertRaises(ValueError):
            sync_codex(self.source, self.installed, self.home, True, self.host)
        self.assertEqual(self.registry.read_bytes(), before)
        self.assertEqual(self.calls, [])

    def test_host_content_mismatch_triggers_verified_recovery(self):
        self.change()
        corrupt = True

        def wrong_package(arguments):
            nonlocal corrupt
            self.host(arguments)
            if arguments[0] == "add" and corrupt:
                corrupt = False
                (self.installed / "hooks/hooks.json").write_text("{}")

        with self.assertRaisesRegex(RuntimeError, "origem anterior restaurada"):
            sync_codex(self.source, self.installed, self.home, True, wrong_package)
        self.assertEqual(compare(self.old, self.installed)["status"], "synchronized")

    def test_recovery_failure_is_reported_explicitly(self):
        self.change()

        def unavailable(arguments):
            if arguments[0] == "add":
                raise RuntimeError("host unavailable")
            self.host(arguments)

        with self.assertRaisesRegex(RuntimeError, "recuperação pelo host falhou"):
            sync_codex(self.source, self.installed, self.home, True, unavailable)
        self.assertTrue(self.old.exists())

    def test_symlink_is_rejected(self):
        (self.source / "assets/external").symlink_to(self.registry)
        with self.assertRaisesRegex(ValueError, "Link simbólico"):
            validate_package(self.source)
