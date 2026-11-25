import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from tasks_runtime import issueflow
from tasks_runtime.commands import Tasks
from tasks_runtime.store import TaskStore, scaffold
from test_tasks_store import GIT_ENV


class ParentProgressTest(unittest.TestCase):
    """#339: item que entra em andamento leva a história e o épico acima, sem recuar nem concluir o pai."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(); self.addCleanup(self.tmp.cleanup)
        self.env = patch.dict(os.environ, GIT_ENV); self.env.start(); self.addCleanup(self.env.stop)
        root = Path(self.tmp.name) / "dados"
        scaffold(root)
        self.cfg = dict(root=str(root), machine="trabalho")
        self.store = TaskStore(root)
        self.tasks = Tasks(self.store, self.cfg)
        self.epic = self.tasks.add("issue", "Épico", nivel="epico")["id"]
        self.story = self.tasks.add("issue", "História", nivel="historia", pai=self.epic, issue=["org/app#13"])["id"]
        self.task = self.tasks.add("tarefa", "Tarefa", nivel="tarefa", pai=self.story)["id"]
        self.state = root / "local" / "ativa.json"

    def role(self, identifier):
        return self.tasks.roles().get(self.store.get(identifier)["data"]["coluna"])

    def test_start_moves_story_and_epic_with_log(self):
        self.assertEqual((self.role(self.epic), self.role(self.story)), ("entrada", "entrada"))
        self.tasks.start(self.task, self.state)
        self.assertEqual((self.role(self.task), self.role(self.story), self.role(self.epic)), ("ativo", "ativo", "ativo"))
        self.assertIn("Em andamento:", self.store.get(self.story)["body"])
        self.assertIn("Em andamento:", self.store.get(self.epic)["body"])

    def test_issue_flow_and_column_edit_also_propagate(self):
        issueflow.advance(self.store, self.cfg, "org/app#13", "inicio", branch="13-historia")
        self.assertEqual((self.role(self.story), self.role(self.epic)), ("ativo", "ativo"))
        other = self.tasks.add("issue", "Outro épico", nivel="epico")["id"]
        child = self.tasks.add("tarefa", "Filha", pai=other)["id"]
        self.tasks.edit(child, dict(coluna=self.tasks.first_column("ativo")))
        self.assertEqual(self.role(other), "ativo")

    def test_parent_ahead_is_not_moved_back_and_done_children_do_not_close_epic(self):
        self.tasks.edit(self.epic, dict(coluna=self.tasks.first_column("validacao")))
        self.tasks.start(self.task, self.state)
        self.assertEqual(self.role(self.epic), "validacao")  # pai adiante não recua
        self.tasks.merge_confirmed = True  # como no fluxo de PR integrado; sem rede no teste
        self.tasks.edit(self.story, dict(coluna=self.tasks.first_column("concluido")))
        self.tasks.edit(self.task, dict(coluna=self.tasks.first_column("concluido")))
        self.assertEqual(self.role(self.epic), "validacao")  # concluir filhos não conclui o épico

    def test_item_without_parent_and_reentry_do_not_touch_others(self):
        alone = self.tasks.add("tarefa", "Solta")["id"]
        self.tasks.start(alone, self.state)
        self.assertEqual((self.role(self.epic), self.role(self.story)), ("entrada", "entrada"))
        self.tasks.start(self.task, self.state)
        log = self.store.get(self.epic)["body"]
        self.tasks.edit(self.task, dict(proximo_passo="seguir"))  # continua em andamento: sem novo registro
        self.assertEqual(self.store.get(self.epic)["body"], log)


if __name__ == "__main__":
    unittest.main()
