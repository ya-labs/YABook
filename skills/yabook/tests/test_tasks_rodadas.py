import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from tasks_runtime import mirror
from tasks_runtime.commands import Tasks
from tasks_runtime.store import TaskStore, scaffold

COLUMNS = ("  - {id: testes, nome: Testes, papel: validacao}\n  - {id: qa, nome: Validação QA, papel: validacao}\n"
           "  - {id: ajustes, nome: Ajustes, papel: ativo}\n")


class RoundTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name) / "dados"
        scaffold(self.root)
        quadro = self.root / "quadro.yml"
        quadro.write_text(quadro.read_text().replace("  - {id: testes, nome: Testes, papel: validacao}\n", COLUMNS))
        self.store = TaskStore(self.root)
        self.tasks = Tasks(self.store, dict(machine="trabalho"), merge_checker=lambda ref: True)
        self.tasks.add("tarefa", "Chamado", coluna="andamento")

    def tearDown(self):
        self.tmp.cleanup()

    def data(self):
        return self.store.get("tarefa-chamado")

    def test_each_return_from_validation_opens_a_round(self):
        self.tasks.edit("tarefa-chamado", dict(coluna="qa"))
        self.assertNotIn("rodada", self.data()["data"])  # primeira entrega: rodada 1 implícita
        self.tasks.edit("tarefa-chamado", dict(coluna="ajustes"))
        self.assertEqual(self.data()["data"]["rodada"], 2)
        self.assertIn("Rodada 2: retorno de Validação QA para Ajustes.", self.data()["body"])
        self.tasks.edit("tarefa-chamado", dict(coluna="qa"))
        self.tasks.edit("tarefa-chamado", dict(coluna="ajustes"))
        self.assertEqual(self.data()["data"]["rodada"], 3)

    def test_own_tests_also_count_and_other_moves_do_not(self):
        self.tasks.edit("tarefa-chamado", dict(coluna="testes"))
        self.tasks.edit("tarefa-chamado", dict(coluna="andamento"), append="Ajustar o filtro.")
        task = self.data()
        self.assertEqual(task["data"]["rodada"], 2)
        self.assertIn("Ajustar o filtro.", task["body"])
        self.assertIn("Rodada 2: retorno de Testes para Em andamento.", task["body"])
        self.tasks.edit("tarefa-chamado", dict(coluna="ajustes"))  # ativo -> ativo não conta
        self.tasks.edit("tarefa-chamado", dict(proximo_passo="Revisar"))
        self.assertEqual(self.data()["data"]["rodada"], 2)


class MirrorAdjustmentsTest(unittest.TestCase):
    OPTIONS = [dict(id=n, name=n) for n in ("Backlog", "Em andamento", "Validação interna", "Validação QA", "Ajustes", "Concluído")]

    def test_validation_to_adjustments_is_the_only_allowed_step_back(self):
        self.assertTrue(mirror.advances("Validação QA", "Ajustes", "ativo", self.OPTIONS))
        self.assertTrue(mirror.advances("Ajustes", "Validação QA", "validacao", self.OPTIONS))
        self.assertFalse(mirror.advances("Validação QA", "Em andamento", "ativo", self.OPTIONS))
        self.assertFalse(mirror.advances("Concluído", "Ajustes", "ativo", self.OPTIONS))
        self.assertEqual(mirror.status_option(self.OPTIONS, "ativo", "dono/repo", {}, "Ajustes", "ajustes")["name"], "Ajustes")


if __name__ == "__main__":
    unittest.main()
