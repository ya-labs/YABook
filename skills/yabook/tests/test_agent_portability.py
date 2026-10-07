import json
import os
import shutil
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from host_directory import sync_directory
from memory_runtime.gitstore import inventory
from plugin_sync import compare, sync_plugin
from yabook_hook import normalize_event, event_response, run, state_path
from yabook_plugin import build


class PortabilityTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.home = Path(self.temp.name)
        self.source = build(self.home / "source")
        self.installed = self.home / "plugin"

    def test_install_update_and_noop_without_codex(self):
        with patch("subprocess.run", side_effect=AssertionError("Host CLI forbidden")):
            sync_directory(self.source, self.installed, True)
            before = (self.installed / ".codex-plugin/plugin.json").stat().st_mtime_ns
            self.assertEqual(sync_plugin(self.source, self.installed, self.home, True)["status"], "synchronized")
            self.assertEqual(before, (self.installed / ".codex-plugin/plugin.json").stat().st_mtime_ns)
            (self.source / "assets/yabook-icon.png").write_bytes(b"new")
            preview = sync_directory(self.source, self.installed)
            self.assertEqual(preview["changed"], ["assets/yabook-icon.png"])
            result = sync_directory(self.source, self.installed, True)
        self.assertEqual(compare(self.source, self.installed)["status"], "synchronized")
        self.assertTrue(Path(result["previous"]).is_dir())

    def test_unmanaged_destination_and_nested_source_are_preserved(self):
        self.installed.mkdir()
        personal = self.installed / "notes.txt"
        personal.write_text("personal")
        with self.assertRaisesRegex(ValueError, "não gerenciado"):
            sync_directory(self.source, self.installed, True)
        self.assertEqual(personal.read_text(), "personal")
        with self.assertRaisesRegex(ValueError, "independentes"):
            sync_directory(self.source, self.source / "plugin", True)

    def test_failed_replacement_restores_old_package(self):
        sync_directory(self.source, self.installed, True)
        old = (self.installed / "assets/yabook-icon.png").read_bytes()
        (self.source / "assets/yabook-icon.png").write_bytes(b"new")
        original = Path.rename

        def fail_candidate(path, destination):
            if path.name == "candidate":
                raise OSError("replacement failed")
            return original(path, destination)

        with patch.object(Path, "rename", fail_candidate):
            with self.assertRaises(OSError):
                sync_directory(self.source, self.installed, True)
        self.assertEqual((self.installed / "assets/yabook-icon.png").read_bytes(), old)

    def test_preparation_failure_preserves_existing_installation(self):
        sync_directory(self.source, self.installed, True)
        old = (self.installed / "assets/yabook-icon.png").read_bytes()
        (self.source / "assets/yabook-icon.png").write_bytes(b"new")
        with patch("yabook_plugin.build", side_effect=OSError("preparation failed")):
            with self.assertRaises(OSError):
                sync_directory(self.source, self.installed, True)
        self.assertEqual((self.installed / "assets/yabook-icon.png").read_bytes(), old)

    def test_any_agent_inventory_supports_exported_file(self):
        source = self.home / "export.txt"
        source.write_text("A useful fact")
        result = inventory("another-agent", source)
        self.assertEqual(result["agent"], "another-agent")
        self.assertEqual(len(result["files"]), 1)
        self.assertEqual(result["files"][0]["status"], "candidate")

    def test_generic_events_inject_context_and_isolate_authorization(self):
        settings = {"YABOOK_CONFIG": str(self.home / "config.json"), "YABOOK_STATE": str(self.home / "sessions")}
        payload = dict(event="session.start", session="same", agent="agent-a", workspace=str(self.home))
        with patch.dict(os.environ, settings):
            event = normalize_event(payload, "generic")
            response = event_response(run(event), "generic")
            self.assertIn("YABook ativo", response["context"])
            granted = normalize_event(dict(payload, event="user.prompt", message="$yabook mode: auto"), "generic")
            run(granted)
            self.assertTrue(json.loads(state_path(granted).read_text())["auto"])
            other = normalize_event(dict(payload, agent="agent-b"), "generic")
            run(other)
            self.assertFalse(json.loads(state_path(other).read_text())["auto"])
            run(event)
            self.assertFalse(json.loads(state_path(event).read_text())["auto"])

    def test_generic_edit_mapping_and_deny_translation(self):
        event = normalize_event(dict(event="tool.before", session="s", agent="a",
                                      tool=dict(kind="edit", input={})), "generic")
        self.assertEqual(event["tool_name"], "Edit")
        response = event_response({"hookSpecificOutput": {"permissionDecision": "deny", "permissionDecisionReason": "blocked"}}, "generic")
        self.assertEqual(response["decision"], "deny")
        self.assertEqual(response["reason"], "blocked")

    def test_generic_protected_edit_is_denied_by_runtime(self):
        event = normalize_event(dict(event="tool.before", agent="agent-c", session="s",
                                     workspace=str(self.home), tool=dict(kind="edit", input={})), "generic")
        settings = {"YABOOK_STATE": str(self.home / "sessions")}

        def git_result(cwd, *arguments):
            if arguments == ("rev-parse", "--show-toplevel"): return str(self.home)
            if arguments == ("branch", "--show-current"): return "main"
            return ""

        with patch.dict(os.environ, settings), patch("yabook_hook.git", git_result):
            self.assertEqual(event_response(run(event), "generic")["decision"], "deny")
