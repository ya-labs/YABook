import contextlib
import io
import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import yabook_tasks
from tasks_runtime import editing
from tasks_runtime.commands import Tasks
from tasks_runtime.store import TaskStore, scaffold


class DescriptionTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name) / "dados"
        scaffold(self.root)
        (self.root / "quadro.yml").write_text((self.root / "quadro.yml").read_text().replace(
            "  - {id: testes, nome: Testes, papel: validacao}\n",
            "  - {id: testes, nome: Testes, papel: validacao}\n  - {id: qa, nome: Validação QA, papel: validacao}\n"))
        self.store = TaskStore(self.root)
        self.tasks = Tasks(self.store, dict(machine="trabalho"))

    def tearDown(self):
        self.tmp.cleanup()

    def test_description_in_cli_brief_and_site_editing(self):
        config = Path(self.tmp.name) / "cfg.json"
        config.write_text(json.dumps(dict(tasks=dict(root=str(self.root), machine="trabalho"))))
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            yabook_tasks.main(["--config", str(config), "add", "--tipo", "tarefa", "--titulo", "Bloquear pedidos",
                               "--descricao", "Bloquear pedidos por dia da semana no app.", "--size", "1"])
        identifier = json.loads(out.getvalue())["id"]
        self.assertEqual(self.tasks.search("")["tarefas"][0]["descricao"], "Bloquear pedidos por dia da semana no app.")
        revision = self.store.get(identifier)["revision"]
        editing.save(self.store, dict(machine="trabalho"), dict(tarefas=[dict(id=identifier, revision=revision, campos=dict(descricao="Nova"))]))
        self.assertEqual(self.store.get(identifier)["data"]["descricao"], "Nova")

    def test_cli_add_refuses_missing_fields(self):
        config = Path(self.tmp.name) / "cfg.json"
        config.write_text(json.dumps(dict(tasks=dict(root=str(self.root), machine="trabalho"))))
        cases = [(("--size", "1"), "descricao"), (("--size", "1", "--descricao", "  "), "descricao"),
                 (("--descricao", "Escopo"), "size")]
        for flags, field in cases:
            with self.subTest(flags=flags), contextlib.redirect_stdout(io.StringIO()) as out:
                code = yabook_tasks.main(["--config", str(config), "add", "--tipo", "tarefa", "--titulo", "Nova", *flags])
                self.assertEqual(code, 1)
                self.assertIn(field + ":", json.loads(out.getvalue())["error"])
        self.assertEqual(self.store.list(), [])

    def test_review_lists_only_open_work_items_without_description(self):
        self.tasks.add("tarefa", "Legada")
        self.tasks.add("tarefa", "Com descrição", descricao="Descrever o escopo")
        self.tasks.add("tarefa", "Encerrada", coluna="concluido")
        self.tasks.ask("Uma pergunta?")
        self.assertEqual([task["id"] for task in self.tasks.review()["sem_descricao"]], ["tarefa-legada"])
        self.tasks.edit("tarefa-legada", dict(descricao="Escopo recuperado"))
        self.assertEqual(self.tasks.review()["sem_descricao"], [])

    def test_entering_validation_clears_qa_wait_only(self):
        self.tasks.add("tarefa", "A", coluna="andamento", aguardando="validação de QA")
        self.tasks.add("tarefa", "B", coluna="andamento", aguardando="versão de homologação da área comercial")
        self.tasks.edit("tarefa-a", dict(coluna="qa"))
        self.tasks.edit("tarefa-b", dict(coluna="qa"))
        self.assertNotIn("aguardando", self.store.get("tarefa-a")["data"])
        self.assertEqual(self.store.get("tarefa-b")["data"]["aguardando"], "versão de homologação da área comercial")
        self.tasks.add("tarefa", "C", coluna="testes")
        self.tasks.edit("tarefa-c", dict(aguardando="QA"))  # já em validação: espera marcada à mão permanece
        self.assertEqual(self.store.get("tarefa-c")["data"]["aguardando"], "QA")


if __name__ == "__main__":
    unittest.main()
