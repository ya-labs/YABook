import contextlib
import io
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import yabook_tasks
from tasks_runtime import editing, issueflow
from tasks_runtime.batch import Capture
from tasks_runtime.commands import Tasks
from tasks_runtime.store import TaskStore, scaffold


class SizeTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name) / "dados"
        scaffold(self.root)
        self.store = TaskStore(self.root)
        self.cfg = dict(machine="trabalho")
        self.tasks = Tasks(self.store, self.cfg)

    def tearDown(self):
        self.tmp.cleanup()

    def test_size_is_validated_and_listed_by_review(self):
        self.tasks.add("tarefa", "Com tamanho", size=2)
        self.tasks.add("tarefa", "Sem tamanho")
        with self.assertRaises(ValueError):
            self.tasks.add("tarefa", "Inválida", size=6)
        review = self.tasks.review()
        self.assertEqual([t["titulo"] for t in review["sem_size"]], ["Sem tamanho"])
        self.assertEqual(self.tasks.brief(self.store.get("tarefa-com-tamanho"))["size"], 2)

    def test_cli_accepts_size(self):
        config = Path(self.tmp.name) / "cfg.json"
        config.write_text(json.dumps(dict(tasks=dict(root=str(self.root), machine="trabalho"))))
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            yabook_tasks.main(["--config", str(config), "add", "--tipo", "tarefa", "--titulo", "Pela CLI", "--size", "3"])
        self.assertEqual(self.store.get(json.loads(out.getvalue())["id"])["data"]["size"], 3)

    def test_board_size_is_manual_and_wins_over_issue(self):
        self.tasks.add("issue", "Da issue", issue=["dono/repo#7"], size=1)
        revision = self.store.get("issue-da-issue")["revision"]
        editing.save(self.store, self.cfg, dict(tarefas=[dict(id="issue-da-issue", revision=revision, campos=dict(size="4"))]))
        data = self.store.get("issue-da-issue")["data"]
        self.assertEqual((data["size"], data["size_manual"]), (4, True))
        self.assertFalse(issueflow.sync_size(self.store, self.cfg, "dono/repo#7", size=2)["alterada"])
        self.tasks.edit("issue-da-issue", unset=["size"])
        self.assertNotIn("size_manual", self.store.get("issue-da-issue")["data"])

    def test_issue_size_is_copied_to_task(self):
        self.tasks.add("issue", "Copiar", issue=["dono/repo#8"])
        graphql = json.dumps(dict(data=dict(repository=dict(issue=dict(projectItems=dict(
            nodes=[dict(fieldValueByName=None), dict(fieldValueByName=dict(name="3"))]))))))
        with mock.patch("subprocess.run", return_value=mock.Mock(returncode=0, stdout=graphql)):
            result = issueflow.sync_size(self.store, self.cfg, "dono/repo#8")
        task = self.store.get("issue-copiar")
        self.assertEqual((result["alterada"], task["data"]["size"]), (True, 3))
        self.assertIn("Size 3 copiado da issue dono/repo#8.", task["body"])

    def test_capture_rejects_invalid_size(self):
        capture = Capture(self.store, self.cfg)
        with self.assertRaises(ValueError):
            capture.plan(dict(itens=[dict(tipo="tarefa", titulo="Lote", size=9)]))
        plan = capture.plan(dict(itens=[dict(tipo="tarefa", titulo="Lote", size=2)]))
        capture.apply(dict(itens=[dict(tipo="tarefa", titulo="Lote", size=2)]), plan.get("approval_hash"))
        self.assertEqual(self.tasks.search("Lote")["tarefas"][0]["size"], 2)


if __name__ == "__main__":
    unittest.main()
