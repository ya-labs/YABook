import contextlib
import datetime
import io
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import yabook_tasks
from tasks_runtime import capture, editing
from tasks_runtime.commands import Tasks
from tasks_runtime.store import TaskStore, scaffold

TZ = datetime.timezone(datetime.timedelta(hours=-3))


def stamp(day):
    return lambda: day + "T10:00:00-03:00"


class WaitingTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name) / "dados"
        scaffold(self.root)
        self.terms = Path(self.tmp.name) / "termos.txt"
        self.terms.write_text("ClienteSecreto\n", encoding="utf-8")
        self.store = TaskStore(self.root, str(self.terms))
        self.tasks = Tasks(self.store, dict(machine="trabalho"))
        self.tasks.add("issue", "Consultar clientes em atraso", projeto="2001", coluna="testes")

    def tearDown(self):
        self.tmp.cleanup()

    def data(self):
        return self.store.get("issue-consultar-clientes-em-atraso")["data"]

    def test_since_is_set_kept_restarted_and_cleared(self):
        with patch("tasks_runtime.store.now", stamp("2026-11-10")):
            self.tasks.edit("issue-consultar-clientes-em-atraso", dict(aguardando="validação de QA"))
        self.assertEqual(self.data()["aguardando_desde"], "2026-11-10")
        with patch("tasks_runtime.store.now", stamp("2026-11-11")):
            self.tasks.edit("issue-consultar-clientes-em-atraso", dict(proximo_passo="Mergear após QA"))
        self.assertEqual(self.data()["aguardando_desde"], "2026-11-10")  # outra edição não reinicia
        with patch("tasks_runtime.store.now", stamp("2026-11-12")):
            self.tasks.edit("issue-consultar-clientes-em-atraso", dict(aguardando="retorno da área comercial"))
        self.assertEqual(self.data()["aguardando_desde"], "2026-11-12")  # texto novo reinicia
        self.tasks.edit("issue-consultar-clientes-em-atraso", unset=["aguardando"])
        self.assertNotIn("aguardando", self.data())
        self.assertNotIn("aguardando_desde", self.data())
        with self.assertRaises(ValueError):
            self.tasks.edit("issue-consultar-clientes-em-atraso", dict(aguardando="base do ClienteSecreto"))

    def test_review_and_session_start_list_waiting_tasks(self):
        with patch("tasks_runtime.store.now", stamp("2026-11-09")):
            self.tasks.edit("issue-consultar-clientes-em-atraso", dict(aguardando="validação de QA"))
        self.tasks.add("tarefa", "Concluída esperando", coluna="concluido", aguardando="nada")
        with patch("tasks_runtime.commands.today", lambda: datetime.date(2026, 11, 12)):
            review = self.tasks.review()
            self.assertEqual([(t["id"], t["dias"]) for t in review["aguardando"]], [("issue-consultar-clientes-em-atraso", 3)])
            text = capture.session_start(dict(tasks=dict(root=str(self.root), machine="trabalho")), "s1")
        self.assertIn("Aguardando terceiros: issue-consultar-clientes-em-atraso", text)
        self.assertIn("validação de QA, 3d", text)
        self.assertIn("--aguardando", text)

    def test_cli_site_and_capture_accept_the_field(self):
        config = Path(self.tmp.name) / "cfg.json"
        config.write_text(json.dumps(dict(tasks=dict(root=str(self.root), machine="trabalho"))))

        def cli(*argv):
            out = io.StringIO()
            with contextlib.redirect_stdout(out):
                return yabook_tasks.main(["--config", str(config), *argv]), json.loads(out.getvalue())

        self.assertEqual(cli("edit", "issue-consultar-clientes-em-atraso", "--aguardando", "validação de QA")[0], 0)
        self.assertEqual(self.data()["aguardando"], "validação de QA")
        self.assertEqual(cli("edit", "issue-consultar-clientes-em-atraso", "--unset", "aguardando")[0], 0)
        self.assertNotIn("aguardando", self.data())
        revision = self.store.get("issue-consultar-clientes-em-atraso")["revision"]
        editing.save(self.store, dict(machine="trabalho"), dict(tarefas=[dict(
            id="issue-consultar-clientes-em-atraso", revision=revision, campos=dict(aguardando="retorno do suporte"))]))
        self.assertEqual(self.data()["aguardando"], "retorno do suporte")
        revision = self.store.get("issue-consultar-clientes-em-atraso")["revision"]
        with self.assertRaises(editing.TermsFound):
            editing.save(self.store, dict(machine="trabalho"), dict(tarefas=[dict(
                id="issue-consultar-clientes-em-atraso", revision=revision, campos=dict(aguardando="ClienteSecreto"))]))
        brief = Tasks(self.store).search("consultar")["tarefas"][0]
        self.assertEqual(brief["aguardando"], "retorno do suporte")
        self.assertIn("aguardando_desde", brief)


if __name__ == "__main__":
    unittest.main()
