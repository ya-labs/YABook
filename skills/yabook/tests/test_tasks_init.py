import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from tasks_runtime import init, remote
from tasks_runtime.store import TaskStore, is_data_repo
from test_tasks_store import GIT_ENV


class FakeGitHub:
    """Repositórios bare locais no lugar do GitHub."""

    def __init__(self, base, login="alice"):
        self.base, self.login = Path(base), login
        self.private = {}

    def bare(self, repository):
        return self.base / (repository.replace("/", "__") + ".git")

    def info(self, repository):
        return dict(private=self.private[repository]) if repository in self.private else None

    def create(self, repository, private=True):
        subprocess.run(["git", "init", "-q", "--bare", "-b", "main", str(self.bare(repository))], check=True)
        self.private[repository] = private

    def clone(self, repository, destination):
        subprocess.run(["git", "clone", "-q", str(self.bare(repository)), str(destination)], check=True)

    def patches(self):
        return [patch.object(remote, "whoami", lambda: self.login), patch.object(remote, "info", self.info),
                patch.object(remote, "create", self.create), patch.object(remote, "clone", self.clone),
                patch.object(remote, "url", lambda r: str(self.bare(r))),
                patch.object(remote, "accepted_urls", lambda r: {str(self.bare(r))})]


class InitTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.base = Path(self.tmp.name)
        self.github = FakeGitHub(self.base)
        self.active = [patch.dict(os.environ, GIT_ENV)] + self.github.patches()
        for item in self.active:
            item.start()

    def tearDown(self):
        for item in reversed(self.active):
            item.stop()
        self.tmp.cleanup()

    def machine(self, name):
        return self.base / (name + ".json"), self.base / name / "tasks"

    def init(self, name, **options):
        config, root = self.machine(name)
        plan = init.init_plan(config, root=root, machine=name, **options)
        return plan, init.init_apply(plan, plan["approval_hash"], config)

    def test_first_machine_creates_and_second_connects(self):
        terms = self.base / "termos.txt"
        terms.write_text("Segredo\n", encoding="utf-8")
        plan, result = self.init("trabalho", terms=terms, confidential=self.base)
        self.assertEqual(plan["repository"], "alice/YABook-task-alice")
        self.assertIn("create-private-repository", plan["operations"])
        self.assertTrue(result["created"] and result["pushed"])
        self.assertTrue(self.github.private["alice/YABook-task-alice"])
        config, root = self.machine("trabalho")
        cfg = json.loads(config.read_text(encoding="utf-8"))["tasks"]
        self.assertEqual(cfg["machine"], "trabalho")
        self.assertEqual(cfg["terms"], str(terms.resolve()))
        self.assertTrue(is_data_repo(root))
        hooks = subprocess.run(["git", "-C", str(root), "config", "core.hooksPath"], capture_output=True, text=True)
        self.assertEqual(hooks.stdout.strip(), ".githooks")
        tracked = subprocess.run(["git", "-C", str(root), "ls-files"], capture_output=True, text=True).stdout
        self.assertNotIn("local/", tracked)
        self.assertIn(".githooks/pre-commit", tracked)

        plan, result = self.init("casa")
        self.assertEqual(plan["operations"][0], "clone-existing")
        self.assertIn("warn-no-terms", plan["operations"])
        self.assertFalse(result["created"] or result["pushed"])
        self.assertEqual(len(self.github.private), 1)
        TaskStore(self.machine("casa")[1]).config()

    def test_rerun_reuses_local_clone(self):
        self.init("trabalho")
        plan, result = self.init("trabalho")
        self.assertEqual(plan["operations"][0], "reuse-local")
        self.assertIsNone(result["commit"])

    def test_other_account_must_exist(self):
        config, root = self.machine("trabalho")
        with self.assertRaises(ValueError):
            init.init_plan(config, repository="bob/YABook-task-bob", root=root)
        self.github.create("bob/publico", private=False)
        with self.assertRaises(ValueError):
            init.init_plan(config, repository="bob/publico", root=root)

    def test_configured_repository_is_not_replaced(self):
        self.init("trabalho")
        config, root = self.machine("trabalho")
        with self.assertRaises(ValueError):
            init.init_plan(config, repository="alice/outro", root=root)

    def test_altered_plan_and_changed_state_are_refused(self):
        config, root = self.machine("trabalho")
        plan = init.init_plan(config, root=root)
        with self.assertRaises(ValueError):
            init.init_apply(dict(plan, root=str(self.base / "outro")), plan["approval_hash"], config)
        self.github.create("alice/YABook-task-alice")
        with self.assertRaises(ValueError):
            init.init_apply(plan, plan["approval_hash"], config)
        self.assertFalse(config.exists())

    def test_occupied_folder_is_refused(self):
        config, root = self.machine("trabalho")
        root.mkdir(parents=True)
        (root / "arquivo.txt").write_text("x", encoding="utf-8")
        with self.assertRaises(ValueError):
            init.init_plan(config, root=root)


if __name__ == "__main__":
    unittest.main()
