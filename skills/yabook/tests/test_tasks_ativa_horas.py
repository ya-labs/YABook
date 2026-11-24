import datetime
import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from tasks_runtime import capture, sheet
from tasks_runtime.commands import Tasks
from tasks_runtime.store import TaskStore, scaffold

DAY = "2026-11-17"


class ActiveAndHoursTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name) / "dados"
        scaffold(self.root)
        self.store = TaskStore(self.root)
        self.cfg = dict(machine="trabalho")
        self.tasks = Tasks(self.store, self.cfg)
        self.tasks.add("projeto", "Épico", projeto="5723", nivel="epico", coluna="andamento")
        self.tasks.add("demanda", "História", demanda="320321", pai="projeto-5723", coluna="pronto")
        self.tasks.add("tarefa", "Outra", coluna="andamento")
        capture.set_active(self.store, "s1", "projeto-5723")

    def tearDown(self):
        self.tmp.cleanup()

    def windows(self, task, starts):
        with (self.root / "horas" / "2026-11-trabalho.jsonl").open("a", encoding="utf-8") as handle:
            for start in starts:
                handle.write(json.dumps(dict(tipo="janela", data=DAY, janela=start, tarefa=task)) + "\n")

    def test_recording_on_story_below_active_epic_switches_active(self):
        story = next(t["data"]["id"] for t in self.store.list() if t["data"]["titulo"] == "História")
        message = capture.follow_edit(self.store, self.cfg, "s1", story)
        self.assertIn("trocada de projeto-5723 para " + story, message)
        self.assertEqual(capture.active(self.store, "s1"), story)
        self.assertEqual(self.store.get(story)["data"]["coluna"], "andamento")  # start leva pronto ao papel ativo
        self.assertEqual(capture.follow_edit(self.store, self.cfg, "s1", "projeto-5723"), "")  # resumo no épico não troca

    def test_unrelated_task_only_warns(self):
        message = capture.follow_edit(self.store, self.cfg, "s1", "tarefa-outra")
        self.assertIn("aviso: a tarefa ativa da sessão é projeto-5723", message)
        self.assertEqual(capture.active(self.store, "s1"), "projeto-5723")

    def test_move_windows_keeps_total_and_can_be_undone(self):
        story = next(t["data"]["id"] for t in self.store.list() if t["data"]["titulo"] == "História")
        self.windows("projeto-5723", ["09:00", "09:15", "09:30", "09:45"])
        self.windows(story, ["09:30"])  # a mesma janela já capturada na história não pode somar duas vezes
        before = sum(sheet.activity(self.root, DAY)[0].values())
        result = sheet.move_windows(self.store, "trabalho", DAY, "projeto-5723", story)
        self.assertEqual(result["janelas"], ["09:00", "09:15", "09:30", "09:45"])  # 09:30 movida some na leitura
        hours = sheet.activity(self.root, DAY)[0]
        self.assertEqual(hours.get(story), 1.0)
        self.assertNotIn("projeto-5723", hours)
        self.assertLessEqual(sum(hours.values()), before)
        moved = next(r for r in sheet.window_records(self.root, DAY)[0] if r["janela"] == "09:00")
        self.assertEqual((moved["tarefa"], moved["origem"]), (story, "projeto-5723"))
        sheet.correct_windows(self.store, "trabalho", DAY, [dict(janela="09:00", tarefa=story, para="projeto-5723")])
        self.assertEqual(sheet.activity(self.root, DAY)[0].get("projeto-5723"), 0.25)  # desfazer devolve à origem

    def test_mixed_durations_share_only_the_overlapping_time(self):
        story = "demanda-320321"
        self.windows("projeto-5723", ["09:00", "09:15"])
        when = datetime.datetime.fromisoformat(DAY + "T09:12:00")
        capture.mark(self.store, "trabalho", story, when)
        capture.mark(self.store, "trabalho", story, when, minutes=15)
        capture.mark(self.store, "trabalho", "projeto-5723", when.replace(hour=10))
        windows, manual, _, _ = sheet.window_records(self.root, DAY)
        self.assertEqual(sheet.captured_activity(windows), {"projeto-5723": .75, story: .25})
        self.assertEqual(sheet.accumulated_activity(windows, manual), {"projeto-5723": 1., story: .5})
        # A correção de uma janela antiga alcança seus 15 minutos, e não toda a meia hora.
        sheet.correct_windows(self.store, "trabalho", DAY,
                              [dict(janela="09:15", tarefa="projeto-5723", ignorar=True)])
        day = sheet.day_sheet(self.store, DAY)
        self.assertEqual(day["capturado_total"], 1.)
        self.assertEqual(sheet.captured_activity(day["janelas"]), {"projeto-5723": .625, story: .375})
        self.assertEqual(sheet.activity(self.root, DAY)[0]["projeto-5723"], .75)

    def test_moving_longer_window_to_legacy_window_keeps_coverage(self):
        story = "demanda-320321"
        self.windows(story, ["09:00"])
        capture.mark(self.store, "trabalho", "projeto-5723", datetime.datetime.fromisoformat(DAY + "T09:05:00"))
        sheet.move_windows(self.store, "trabalho", DAY, "projeto-5723", story)
        self.assertEqual(sheet.activity(self.root, DAY)[0], {story: .5})
        sheet.correct_windows(self.store, "trabalho", DAY, [dict(janela="09:00", tarefa=story, para="projeto-5723")])
        self.assertEqual(sheet.activity(self.root, DAY)[0], {story: .25, "projeto-5723": .5})

    def test_move_rejects_missing_windows_and_same_task(self):
        with self.assertRaises(ValueError):
            sheet.move_windows(self.store, "trabalho", DAY, "projeto-5723", "tarefa-outra")
        with self.assertRaises(ValueError):
            sheet.move_windows(self.store, "trabalho", DAY, "tarefa-outra", "tarefa-outra")


if __name__ == "__main__":
    unittest.main()
