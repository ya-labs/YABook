import contextlib
import io
import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import yabook_tasks
from tasks_runtime import sheet, tree
from tasks_runtime.batch import Capture
from tasks_runtime.commands import Tasks
from tasks_runtime.store import TaskStore, scaffold


class OwnTypeCodeTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name) / "dados"
        scaffold(self.root)
        self.store = TaskStore(self.root)
        self.tasks = Tasks(self.store, dict(machine="trabalho"))
        self.tasks.add("projeto", "Melhorias", projeto="1000", demanda="2000", nivel="epico")
        self.tasks.add("issue", "Agenda", demanda="2000", pai="projeto-1000")
        self.tasks.add("tarefa", "Ajustar filtro", pai="issue-agenda")
        self.tasks.add("projeto", "Outro projeto", projeto="1001", nivel="epico")
        self.tasks.add("tarefa", "Sem código", pai="projeto-1001", nivel="historia")
        self.tasks.add("demanda", "Chamado com projeto", demanda="3000", projeto="1000")

    def tearDown(self):
        self.tmp.cleanup()

    def check(self, identifier):
        index = tree.index_of(self.store.list())
        data = index[identifier]
        return tree.code(data, index), sheet.attribution(data, index)

    def test_own_type_then_nearest_ancestor(self):
        self.assertEqual(self.check("projeto-1000"), ("1000", ("projeto", "1000")))
        self.assertEqual(self.check("issue-agenda"), ("2000", ("demanda", "2000")))
        self.assertEqual(self.check("tarefa-ajustar-filtro"), ("2000", ("demanda", "2000")))
        self.assertEqual(self.check("tarefa-sem-codigo"), ("1001", ("projeto", "1001")))
        self.assertEqual(self.check("demanda-3000"), ("3000", ("demanda", "3000")))

    def test_personal_and_specification_keep_behavior(self):
        self.tasks.add("issue", "Pessoal", issue=["org/repo#1"])
        self.tasks.add("especificacao", "Especificar", projeto="1000")
        self.assertEqual(self.check("issue-pessoal"), ("org/repo#1", None))
        self.assertEqual(self.check("especificacao-1000")[1], ("especificacao", "1000"))

    def test_mixed_codes_warn_in_capture_and_add(self):
        plan = Capture(self.store, dict(machine="trabalho")).plan(dict(itens=[
            dict(tipo="projeto", titulo="Novo", projeto="1002", demanda="4000"),
            dict(tipo="issue", titulo="Normal", demanda="4000")]))
        self.assertEqual(len(plan["avisos"]), 1)
        self.assertIn("projeto 1002", plan["avisos"][0])
        config = Path(self.tmp.name) / "cfg.json"
        config.write_text(json.dumps(dict(tasks=dict(root=str(self.root), machine="trabalho"))))
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            code = yabook_tasks.main(["--config", str(config), "add", "--tipo", "demanda", "--titulo", "X",
                                      "--demanda", "5000", "--projeto", "1000"])
        self.assertEqual(code, 0)
        self.assertIn("demanda 5000", json.loads(out.getvalue())["aviso"])


if __name__ == "__main__":
    unittest.main()
