import json
import sys
import tempfile
import unittest
import uuid
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from tasks_runtime import editing, sheet
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

    def entry(self, **fields):
        return dict(dict(id=str(uuid.uuid4()), data=DAY, codigo="9001", minutos=20,
                         descricao="Atendimento sem código próprio"), **fields)

    def save(self, entries, **changes):
        with patch.object(editing, "_commit", return_value=(None, None)):
            return editing.save(self.store, dict(machine="teste"), dict(apontamentos=entries, **changes))

    def test_captured_and_distributed_are_separate(self):
        self.window("issue-chamado")
        result = sheet.day_sheet(self.store, DAY)
        row = result["linhas"][0]
        self.assertEqual((row["capturado"], row["informado"], row["registrado"], row["total"]), (.25, 0, .25, 8))
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

    def test_epic_allocation_does_not_become_direct_capture_on_story(self):
        self.window("projeto-1001")
        with patch.object(sheet, "touches", return_value={"issue-chamado": 3}):
            result = sheet.day_sheet(self.store, DAY)
        rows = {r["codigo"]: r for r in result["linhas"]}
        self.assertEqual((rows["2001"]["capturado"], rows["2001"]["total"]), (0, 8))
        self.assertEqual((rows["1001"]["capturado"], rows["1001"]["total"]), (.25, 0))
        self.assertEqual(result["registrado_ficha"], .25)

    def test_free_entry_keeps_20_minutes_without_filling_the_day(self):
        entry = self.entry()
        self.assertEqual(sheet.day_sheet(self.store, DAY)["apontamentos"], [])
        self.save([entry])
        result = sheet.day_sheet(self.store, DAY)
        row = result["linhas"][0]
        self.assertEqual(row["codigo"], "9001")
        for key in ("total", "informado", "registrado"):
            self.assertAlmostEqual(row[key], 1 / 3, places=6)
        self.assertIn(entry["descricao"], row["observacao"])
        self.assertAlmostEqual(result["falta"], 8 - 1 / 3, places=6)
        self.assertEqual(result["capturado_total"], 0)

    def test_resend_and_duplicate_payload_do_not_double_count(self):
        entry = self.entry()
        self.save([entry, entry])
        self.save([entry])
        self.assertEqual(len(sheet.free_entries(self.root)), 1)
        self.assertAlmostEqual(sheet.day_sheet(self.store, DAY)["informado_total"], 1 / 3, places=6)
        with self.assertRaises(ValueError):
            self.save([dict(entry, minutos=40)])

    def test_invalid_free_entry_prevents_all_other_changes(self):
        task = self.store.get("issue-chamado")
        changes = dict(tarefas=[dict(id="issue-chamado", revision=task["revision"], campos=dict(titulo="Alterado"))])
        for fields in (dict(minutos=0), dict(minutos=True), dict(minutos=1.5), dict(codigo="../x"), dict(descricao=" "), dict(data="2026-02-30")):
            with self.subTest(fields=fields), self.assertRaises(ValueError):
                self.save([self.entry(), self.entry(**fields)], **changes)
            self.assertEqual(self.store.get("issue-chamado")["revision"], task["revision"])
            self.assertEqual(sheet.free_entries(self.root), [])

    def test_confidential_description_is_rejected_before_writing(self):
        with patch.object(Tasks, "_check_text", side_effect=ValueError("Termo confidencial")):
            with self.assertRaises(ValueError):
                self.save([self.entry()])
        self.assertEqual(sheet.free_entries(self.root), [])

    def test_manual_time_is_fixed_while_remaining_hours_are_distributed(self):
        self.window("issue-chamado")
        self.save([self.entry()])
        result = sheet.day_sheet(self.store, DAY)
        rows = {r["codigo"]: r for r in result["linhas"]}
        self.assertAlmostEqual(rows["9001"]["total"], 1 / 3, places=6)
        self.assertAlmostEqual(rows["2001"]["total"], 8 - 1 / 3, places=6)
        self.assertEqual(result["total"], 8)
        self.assertAlmostEqual(result["registrado_ficha"], .25 + 1 / 3, places=6)

    def test_free_entries_are_scoped_to_the_day_and_limited_to_24_hours(self):
        self.save([self.entry(minutos=1440)])
        with self.assertRaises(ValueError):
            self.save([self.entry(minutos=1)])
        other = sheet.day_sheet(self.store, "2026-11-12")
        self.assertEqual((other["informado_total"], other["apontamentos"]), (0, []))

    def test_existing_manual_logs_are_shown_without_changing_the_rateio_contract(self):
        self.tasks.log("issue-chamado", .5, day=DAY)
        result = sheet.day_sheet(self.store, DAY)
        self.assertEqual((result["capturado_total"], result["informado_total"], result["registrado_ficha"], result["total"]), (0, .5, .5, 8))

    def test_board_uses_local_free_code_configuration(self):
        from tasks_runtime.server import Board
        board = Board(self.store, dict(codigo_ficha_livre="9001"))
        self.assertEqual(board.sheet(DAY)["codigo_livre"], "9001")

    def test_extra_time_is_not_rounded_up_in_the_registered_total(self):
        self.window("tarefa-pessoal")
        result = sheet.day_sheet(self.store, DAY)
        self.assertEqual((result["capturado_total"], result["extras_registrado"], result["registrado_ficha"]), (.25, .25, 0))


if __name__ == "__main__":
    unittest.main()
