import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from tasks_runtime.commands import Tasks
from tasks_runtime.store import TaskStore, fmt, scaffold


class OneIssueTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name) / "dados"
        scaffold(self.root)
        self.store = TaskStore(self.root)
        self.tasks = Tasks(self.store, dict(machine="trabalho"), merge_checker=lambda ref: True)

    def tearDown(self):
        self.tmp.cleanup()

    def legacy(self, identifier, issues, **extra):
        """Tarefa antiga com várias issues, escrita direto no arquivo (como antes da regra)."""
        data = dict(id=identifier, tipo="demanda", titulo="Chamado", coluna="testes", demanda="1001", issue=issues,
                    criada="2026-11-01T10:00:00-03:00", atualizada="2026-11-01T10:00:00-03:00", **extra)
        (self.root / "tarefas" / (identifier + ".md")).write_text(fmt.join_frontmatter(data, "", ()), encoding="utf-8")

    def test_saving_more_than_one_issue_is_refused_with_guidance(self):
        with self.assertRaisesRegex(ValueError, "Uma issue por tarefa"):
            self.tasks.add("issue", "Duas", issue=["dono/repo#1", "dono/repo#2"])
        self.tasks.add("issue", "Uma", issue=["dono/repo#1"])
        with self.assertRaisesRegex(ValueError, "task add --tipo issue --pai issue-uma"):
            self.tasks.edit("issue-uma", dict(issue=["dono/repo#1", "dono/repo#3"]))

    def test_split_creates_one_child_per_issue_and_keeps_parent_history(self):
        self.legacy("demanda-1001", ["dono/repo#1", "dono/repo#2", "dono/repo#3"])
        self.tasks.add("issue", "Já existe", issue=["dono/repo#3"])
        info = {"dono/repo#1": ("Primeira", 2), "dono/repo#2": ("Segunda", None)}
        preview = self.tasks.split_issues(issue_info=lambda ref: info[ref])
        self.assertEqual(preview["tarefas"], 1)
        self.assertNotIn("issue", self.store.get("demanda-1001")["data"].get("nada", {}))  # prévia não grava
        self.assertEqual(len(self.store.get("demanda-1001")["data"]["issue"]), 3)
        self.tasks.split_issues(apply=True, issue_info=lambda ref: info[ref])
        parent = self.store.get("demanda-1001")
        self.assertNotIn("issue", parent["data"])
        self.assertEqual(parent["data"]["nivel"], "historia")
        self.assertIn("Issues separadas em tarefas próprias", parent["body"])
        children = {tuple(t["data"]["issue"]): t["data"] for t in self.store.list()
                    if t["data"].get("pai") == "demanda-1001"}
        self.assertEqual(set(children), {("dono/repo#1",), ("dono/repo#2",)})
        first = children[("dono/repo#1",)]
        self.assertEqual((first["titulo"], first["size"], first["coluna"], first["nivel"]), ("Primeira", 2, "testes", "tarefa"))
        self.assertTrue(all(len(t["data"].get("issue") or []) <= 1 for t in self.store.list()))


if __name__ == "__main__":
    unittest.main()
