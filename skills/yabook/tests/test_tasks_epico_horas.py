import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from tasks_runtime import capture, sheet
from tasks_runtime.commands import Tasks
from tasks_runtime.store import TaskStore, scaffold

DAY = "2026-11-05"


class EpicHoursTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name) / "dados"
        scaffold(self.root)
        self.store = TaskStore(self.root)
        self.tasks = Tasks(self.store, dict(machine="trabalho"))
        with patch("tasks_runtime.store.now", lambda: "2026-11-01T10:00:00-03:00"):
            self.tasks.add("projeto", "Melhorias", projeto="5000", nivel="epico", coluna="andamento")
            self.tasks.add("issue", "Agenda", demanda="111", pai="projeto-5000")
            self.tasks.add("issue", "Boletos", demanda="222", pai="projeto-5000")
            self.tasks.add("issue", "Sem toque", demanda="333", pai="projeto-5000")
            self.tasks.add("issue", "Sem chamado", pai="projeto-5000")

    def tearDown(self):
        self.tmp.cleanup()

    def windows(self, task, count, start=8):
        path = self.root / "horas" / "2026-11-trabalho.jsonl"
        with path.open("a", encoding="utf-8") as stream:
            for index in range(count):
                minute = start * 60 + 15 * index
                stream.write(json.dumps(dict(tipo="janela", data=DAY, janela="%02d:%02d" % (minute // 60, minute % 60), tarefa=task)) + "\n")

    def touch(self, identifier, times=1):
        for n in range(times):
            with patch("tasks_runtime.store.now", lambda: DAY + "T1%d:00:00-03:00" % n), \
                 patch("tasks_runtime.events.datetime") as clock:
                import datetime
                clock.datetime.now.return_value = datetime.datetime(2026, 11, 5, 10 + n, tzinfo=datetime.timezone(datetime.timedelta(hours=-3)))
                self.tasks.edit(identifier, append="toque %d" % n)

    def test_epic_hours_go_to_touched_demands(self):
        self.windows("projeto-5000", 16)  # 4h no épico
        self.touch("issue-agenda", 3)
        self.touch("issue-boletos", 1)
        self.touch("issue-sem-chamado", 1)  # sem demanda: não recebe a divisão
        result = sheet.day_sheet(self.store, DAY)
        totals = {(r["tipo"], r["codigo"]): r["total"] for r in result["linhas"] if r["total"]}
        self.assertEqual(totals, {("demanda", "111"): 6, ("demanda", "222"): 2})
        self.assertTrue(all(r["observacao"] == "" for r in result["linhas"] if r["tipo"] == "demanda"))
        project = next(r for r in result["linhas"] if r["tipo"] == "projeto")
        self.assertEqual((project["capturado"], project["total"]), (4, 0))
        self.assertEqual(result["registrado_ficha"], 4)
        self.assertEqual(result["divididas"], {"projeto-5000": ["issue-agenda", "issue-boletos"]})

    def test_without_touched_demands_epic_stays_on_project(self):
        self.windows("projeto-5000", 8)
        result = sheet.day_sheet(self.store, DAY)
        row = result["linhas"][0]
        self.assertEqual((row["tipo"], row["codigo"]), ("projeto", "5000"))
        self.assertTrue(row["observacao"].startswith("Desenvolvimento"))
        self.assertEqual(result["divididas"], {})

    def test_personal_epic_is_not_spread_and_session_warns(self):
        self.tasks.edit("projeto-5000", dict(pessoal=True))
        self.windows("projeto-5000", 8)
        self.touch("issue-agenda")
        self.assertEqual(sheet.day_sheet(self.store, DAY)["divididas"], {})
        self.tasks.edit("projeto-5000", unset=["pessoal"])
        self.tasks.start("projeto-5000", self.root / "local" / "ativa.json")
        text = capture.session_start(dict(tasks=dict(root=str(self.root), machine="trabalho")), "s1")
        self.assertIn("A tarefa ativa é um épico com histórias abertas", text)


if __name__ == "__main__":
    unittest.main()
