import sys
import tempfile
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from yabook_plugin import register_codex
from memory_runtime.core import read_json, write_json


class PluginTest(unittest.TestCase):
    def test_idempotent_registration_preserves_other_plugins(self):
        with tempfile.TemporaryDirectory() as d:
            registry = Path(d) / ".agents/plugins/marketplace.json"
            write_json(registry, dict(name="personal",plugins=[dict(name="other",source={})],extra="preserve"))
            first = register_codex(d); second = register_codex(d)
            self.assertEqual(first, second)
            data = read_json(registry)
            self.assertEqual(len(data["plugins"]),2)
            self.assertEqual(data["extra"],"preserve")
            register_codex(d,remove=True); register_codex(d,remove=True)
            self.assertEqual(read_json(registry)["plugins"],[dict(name="other",source={})])
            self.assertTrue(Path(first["path"]).exists())

    def test_existing_unmanaged_entry_is_preserved(self):
        with tempfile.TemporaryDirectory() as d:
            registry = Path(d) / ".agents/plugins/marketplace.json"
            data = dict(name="personal",plugins=[dict(name="yabook",source=dict(source="git",url="external"))])
            write_json(registry,data)
            with self.assertRaises(ValueError): register_codex(d)
            self.assertEqual(read_json(registry),data)
