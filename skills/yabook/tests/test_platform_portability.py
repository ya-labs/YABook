import os
import shutil
import sys
import tempfile
import threading
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from memory_runtime.core import file_lock
from plugin_sync import ROOTS, validate_package
import yabook_hook as hook

SOURCE = Path(__file__).resolve().parents[3]


class PlatformTest(unittest.TestCase):
    def copy_package(self, target):
        for item in ROOTS:
            shutil.copytree(SOURCE / item, target / item, ignore=shutil.ignore_patterns("__pycache__", "*.pyc", "tests"))

    def test_crlf_checkout_is_a_valid_package(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self.copy_package(root)
            skill = root / "skills/yabook/SKILL.md"
            skill.write_bytes(skill.read_bytes().replace(b"\r\n", b"\n").replace(b"\n", b"\r\n"))
            validate_package(root)

    def test_file_lock_is_exclusive(self):
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / "lock"
            events = []
            with open(path, "a") as first, file_lock(first):
                def contender():
                    with open(path, "a") as second, file_lock(second):
                        events.append("second")
                worker = threading.Thread(target=contender)
                worker.start()
                worker.join(0.3)
                events.append("first")
            worker.join(15)
            self.assertEqual(events, ["first", "second"])

    @unittest.skipUnless(os.name == "nt", "caminhos com barra invertida só no Windows")
    def test_windows_paths_survive_command_parsing(self):
        parts = hook.command_parts(r'python C:\x\yabook_memory.py learn --root "C:\Users\a b\memory"')
        self.assertEqual(parts[1], r"C:\x\yabook_memory.py")
        self.assertEqual(parts[-1], r"C:\Users\a b\memory")


if __name__ == "__main__": unittest.main()
