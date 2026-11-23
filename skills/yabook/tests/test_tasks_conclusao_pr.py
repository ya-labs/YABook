import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from tasks_runtime import issueflow
from tasks_runtime.commands import Tasks
from tasks_runtime.merge_check import evaluate
from tasks_runtime.store import TaskStore, scaffold


class EvaluateTest(unittest.TestCase):
    def issue(self, branches=0, closing=(), timeline=()):
        return dict(linkedBranches=dict(totalCount=branches),
                    closedByPullRequestsReferences=dict(nodes=[dict(merged=m) for m in closing]),
                    timelineItems=dict(nodes=list(timeline)))

    def test_rules(self):
        self.assertTrue(evaluate(self.issue()))  # sem branch e sem PR: não passa por código
        self.assertFalse(evaluate(self.issue(branches=1)))  # branch sem PR
        self.assertFalse(evaluate(self.issue(closing=[False])))  # PR aberto
        self.assertTrue(evaluate(self.issue(branches=1, closing=[False, True])))  # um PR integrado basta
        self.assertTrue(evaluate(self.issue(timeline=[dict(subject=dict(merged=True))])))  # PR ligado e integrado
        self.assertTrue(evaluate(self.issue(timeline=[dict(source=dict())])))  # citada só por outra issue


class ConclusionRuleTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name) / "dados"
        scaffold(self.root)
        self.store = TaskStore(self.root)
        self.answers = {}
        self.tasks = Tasks(self.store, dict(machine="trabalho"), merge_checker=lambda ref: self.answers.get(ref))
        self.tasks.add("issue", "Com PR", issue=["dono/repo#1"], coluna="testes")
        self.tasks.add("tarefa", "Sem issue", coluna="testes")

    def tearDown(self):
        self.tmp.cleanup()

    def test_blocks_without_merged_pr_and_when_unconfirmed(self):
        self.answers["dono/repo#1"] = False
        with self.assertRaisesRegex(ValueError, "sem merge"):
            self.tasks.edit("issue-com-pr", dict(coluna="concluido"))
        self.answers["dono/repo#1"] = None
        with self.assertRaisesRegex(ValueError, "não foi possível confirmar"):
            self.tasks.edit("issue-com-pr", dict(coluna="concluido"))
        self.assertEqual(self.store.get("issue-com-pr")["data"]["coluna"], "testes")

    def test_allows_merged_pr_tasks_without_issue_and_other_moves(self):
        self.tasks.edit("tarefa-sem-issue", dict(coluna="concluido"))
        self.tasks.edit("issue-com-pr", dict(coluna="andamento"))  # outras colunas não consultam o GitHub
        self.answers["dono/repo#1"] = True
        self.tasks.edit("issue-com-pr", dict(coluna="concluido"))
        self.assertEqual(self.store.get("issue-com-pr")["data"]["coluna"], "concluido")

    def test_epics_with_issues_conclude_without_checking_github(self):
        from unittest.mock import Mock, patch
        from tasks_runtime import editing

        cli = self.tasks.add("issue", "Épico na CLI", nivel="epico", issue=["dono/repo#2"], coluna="testes")["id"]
        web = self.tasks.add("issue", "Épico no quadro", nivel="epico", issue=["dono/repo#3"], coluna="testes")
        checker = Mock(side_effect=AssertionError("Épico não deve consultar o GitHub"))
        self.tasks.merge_checker = checker
        self.tasks.edit(cli, dict(coluna="concluido"))
        with patch("tasks_runtime.merge_check.can_conclude", checker):
            editing.save(self.store, dict(machine="trabalho"),
                         dict(tarefas=[dict(id=web["id"], revision=web["revision"], campos=dict(coluna="concluido"))]))
        checker.assert_not_called()
        self.assertEqual(self.store.get(cli)["data"]["coluna"], "concluido")
        self.assertEqual(self.store.get(web["id"])["data"]["coluna"], "concluido")

    def test_site_save_refuses_before_writing_anything(self):
        from unittest.mock import patch
        from tasks_runtime import editing
        self.tasks.add("tarefa", "Outra", coluna="testes")
        changes = [dict(id="tarefa-outra", revision=self.store.get("tarefa-outra")["revision"], campos=dict(coluna="andamento")),
                   dict(id="issue-com-pr", revision=self.store.get("issue-com-pr")["revision"], campos=dict(coluna="concluido"))]
        with patch("tasks_runtime.merge_check.can_conclude", return_value=False):
            with self.assertRaisesRegex(ValueError, "sem merge"):
                editing.save(self.store, dict(machine="trabalho"), dict(tarefas=changes))
        self.assertEqual(self.store.get("tarefa-outra")["data"]["coluna"], "testes")  # nada gravado

    def test_issue_flow_after_merge_does_not_query_again(self):
        self.answers["dono/repo#1"] = False  # o fluxo integrado já conferiu o merge
        original = Tasks.__init__

        def init(this, *args, **kwargs):
            kwargs.setdefault("merge_checker", lambda ref: False)
            original(this, *args, **kwargs)
        Tasks.__init__ = init
        try:
            issueflow.advance(self.store, dict(machine="trabalho"), "dono/repo#1", "integrado", pr="#9")
        finally:
            Tasks.__init__ = original
        self.assertEqual(self.store.get("issue-com-pr")["data"]["coluna"], "concluido")


if __name__ == "__main__":
    unittest.main()
