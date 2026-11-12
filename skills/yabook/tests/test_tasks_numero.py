import contextlib
import io
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import yabook_tasks
from tasks_runtime.commands import Tasks
from tasks_runtime.store import TaskStore, scaffold


class NumberTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name) / "dados"
        scaffold(self.root)
        self.store = TaskStore(self.root)
        self.tasks = Tasks(self.store, dict(machine="trabalho"))
        self.config = Path(self.tmp.name) / "cfg.json"
        self.config.write_text(json.dumps(dict(tasks=dict(root=str(self.root), machine="trabalho"))))

    def tearDown(self):
        self.tmp.cleanup()

    def cli(self, *argv):
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            code = yabook_tasks.main(["--config", str(self.config), *argv])
        return code, json.loads(out.getvalue())

    def test_new_tasks_get_next_number_and_resolve_by_at(self):
        self.tasks.add("tarefa", "Primeira")
        self.tasks.add("tarefa", "Segunda")
        self.assertEqual(self.store.get("tarefa-segunda")["data"]["numero"], 2)
        self.assertEqual(self.store.get("@1")["data"]["id"], "tarefa-primeira")
        self.tasks.edit("tarefa-primeira", dict(proximo_passo="x"))
        self.assertEqual(self.store.get("tarefa-primeira")["data"]["numero"], 1)  # edição não renumera
        code, shown = self.cli("show", "@2")
        self.assertEqual((code, shown["data"]["id"]), (0, "tarefa-segunda"))
        self.assertEqual(self.cli("edit", "@1", "--proximo-passo", "y")[1]["id"], "tarefa-primeira")
        self.assertEqual(self.cli("show", "@9")[0], 1)
        self.assertEqual(self.tasks.search("")["tarefas"][0]["numero"], 1)

    def test_backfill_by_creation_and_fix_duplicates(self):
        for title, stamp in (("Antiga", "2026-11-01"), ("Nova", "2026-11-03"), ("Meio", "2026-11-02")):
            with patch("tasks_runtime.store.now", lambda s=stamp: s + "T10:00:00-03:00"):
                self.tasks.add("tarefa", title)
        for task in self.store.list():  # simula tarefas anteriores ao campo
            data = dict(task["data"]); data.pop("numero")
            (self.root / "tarefas" / (data["id"] + ".md")).write_text(self.store.render(data, task["body"]), encoding="utf-8")
        before = {t["data"]["id"]: t["data"]["atualizada"] for t in self.store.list()}
        code, result = self.cli("numerar")
        self.assertEqual({t["data"]["id"]: t["data"]["atualizada"] for t in self.store.list()}, before)  # numerar não altera a data
        self.assertEqual([r["id"] for r in result["numeradas"]], ["tarefa-antiga", "tarefa-meio", "tarefa-nova"])
        self.assertEqual(self.cli("numerar")[1]["numeradas"], [])  # idempotente
        nova = self.store.get("tarefa-nova")
        self.store.save(dict(nova["data"], numero=1), nova["body"], nova["revision"])  # repetido vindo de outra máquina
        self.assertEqual(self.cli("validate")[1]["numeros_repetidos"], {"1": ["tarefa-antiga", "tarefa-nova"]})
        stamp = self.store.get("tarefa-nova")["data"]["atualizada"]
        fixed = self.cli("numerar", "--corrigir")[1]["numeradas"]
        self.assertEqual(self.store.get("tarefa-nova")["data"]["atualizada"], stamp)
        self.assertEqual(fixed, [dict(id="tarefa-nova", numero=3)])
        self.assertEqual(self.store.duplicate_numbers(), {})
        self.assertEqual(self.store.get("tarefa-antiga")["data"]["numero"], 1)


if __name__ == "__main__":
    unittest.main()
