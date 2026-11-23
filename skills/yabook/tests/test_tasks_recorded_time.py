import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from tasks_runtime import sheet
from tasks_runtime.server import Board
from tasks_runtime.commands import Tasks
from tasks_runtime.store import TaskStore, scaffold

DAY = "2026-11-13"


class RecordedTimeTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name) / "dados"
        scaffold(self.root)
        self.store = TaskStore(self.root)
        self.tasks = Tasks(self.store, dict(machine="teste"))
        self.tasks.add("projeto", "Projeto", projeto="1001", nivel="epico", size=1)
        self.tasks.add("issue", "Chamado", pai="projeto-1001", demanda="2001", size=1)
        self.tasks.add("tarefa", "Pessoal", size=1)

    def window(self, identifier, slot="08:00"):
        path = self.root / "horas/2026-11-teste.jsonl"
        with path.open("a") as stream:
            stream.write(json.dumps(dict(tipo="janela", data=DAY, tarefa=identifier, janela=slot)) + "\n")


    def test_captured_and_distributed_are_separate(self):
        self.window("issue-chamado")
        result = sheet.day_sheet(self.store, DAY)
        row = result["linhas"][0]
        self.assertEqual((row["capturado"], row["informado"], row["registrado"], row["total"]), (.25, 0, .25, .375))
        self.assertEqual((result["capturado_total"], result["registrado_ficha"], result["falta"]), (.25, .25, 7.75))

    def test_concurrent_windows_are_shared_without_multiplying_the_day(self):
        for task in ("issue-chamado", "tarefa-pessoal", "issue-chamado"):
            self.window(task)
        result = sheet.day_sheet(self.store, DAY)
        self.assertEqual(result["capturado_total"], .25)
        self.assertEqual(result["linhas"][0]["capturado"], .125)
        self.assertEqual(result["extras"][0]["registrado"], .125)
        self.assertEqual(result["extras_registrado"], .125)

    def test_ignored_window_is_not_counted(self):
        self.window("issue-chamado")
        sheet.correct_windows(self.store, "teste", DAY, [dict(janela="08:00", tarefa="issue-chamado", ignorar=True)])
        self.assertEqual(sheet.day_sheet(self.store, DAY)["capturado_total"], 0)

    def test_project_capture_stays_on_project_without_inventing_child_hours(self):
        self.window("projeto-1001")
        with patch("tasks_runtime.store.now", lambda: DAY + "T10:00:00-03:00"):
            self.tasks.edit("issue-chamado", append="atividade")
        result = sheet.day_sheet(self.store, DAY)
        rows = {r["codigo"]: r for r in result["linhas"]}
        self.assertEqual((rows["2001"]["capturado"], rows["2001"]["total"]), (0, 0))
        self.assertEqual((rows["1001"]["capturado"], rows["1001"]["total"]), (.25, .375))
        self.assertEqual(rows["2001"]["tarefas"], ["issue-chamado"])
        self.assertEqual(result["registrado_ficha"], .25)

    def test_week_and_sheet_agree_on_capture_and_expose_accumulated_fronts(self):
        for task in ("issue-chamado", "tarefa-pessoal"):
            self.window(task)
        self.tasks.log("issue-chamado", .5, day=DAY)
        board = Board(self.store, {})
        day = next(d for d in board.week(DAY)["dias"] if d["data"] == DAY)
        result = sheet.day_sheet(self.store, DAY)
        self.assertEqual(day["horas"], result["capturado_total"])
        self.assertEqual(day["acumulado"], result["acumulado_total"])
        self.assertEqual((day["horas"], day["informado"], day["acumulado"]), (.25, .5, 1))
        self.assertEqual(sum(t["horas"] for t in day["tarefas"]), .25)

    def test_task_detail_sums_captured_and_manual_hours_across_days(self):
        for task in ("issue-chamado", "tarefa-pessoal", "issue-chamado"):
            self.window(task)
        self.window("issue-chamado", "09:00")
        sheet.correct_windows(self.store, "teste", DAY, [dict(janela="09:00", tarefa="issue-chamado", ignorar=True)])
        self.tasks.log("issue-chamado", .5, day="2026-10-30", machine="outra")
        board = Board(self.store)
        self.assertEqual(board.task("issue-chamado")["horas"], dict(capturado=.125, informado=.5))
        self.assertEqual(board.task("tarefa-pessoal")["horas"], dict(capturado=.125, informado=0))
        self.assertEqual(board.task("projeto-1001")["horas"], {})

    def test_margin_caps_small_and_long_work_without_forcing_eight_hours(self):
        self.assertEqual(sheet.bounded_rateio(dict(short=.25, normal=1, long=3, unknown=0), 8),
                         dict(short=.375, normal=1.5, long=4, unknown=0))
        result = sheet.bounded_rateio(dict(a=4, b=3), 8)
        self.assertEqual(sum(result.values()), 8)
        self.assertTrue(all(result[k] - v <= min(v * .5, 1) for k, v in dict(a=4,b=3).items()))
        self.assertEqual(sheet.bounded_rateio(dict(a=9), 8), dict(a=9))
        self.assertEqual(sheet.bounded_rateio({}, 8), {})

    def test_margin_is_per_code_not_per_task_and_balance_remains_visible(self):
        self.tasks.add("issue", "Outra", demanda="2001", size=1)
        self.tasks.log("issue-chamado", 2, day=DAY)
        self.tasks.log("issue-outra", 2, day=DAY)
        result = sheet.day_sheet(self.store, DAY)
        self.assertEqual(len(result["linhas"]), 1)
        self.assertEqual(result["total"], 5)
        self.assertEqual(result["saldo_rateado"], 3)
        self.assertEqual(result["falta"], 4)

    def test_existing_manual_logs_are_shown_and_used_as_base(self):
        self.tasks.log("issue-chamado", .5, day=DAY)
        result = sheet.day_sheet(self.store, DAY)
        self.assertEqual((result["capturado_total"], result["informado_total"], result["registrado_ficha"], result["total"]), (0, .5, .5, .75))


    def test_extra_time_is_not_rounded_up_in_the_registered_total(self):
        self.window("tarefa-pessoal")
        result = sheet.day_sheet(self.store, DAY)
        self.assertEqual((result["capturado_total"], result["extras_registrado"], result["registrado_ficha"]), (.25, .25, 0))


if __name__ == "__main__":
    unittest.main()
