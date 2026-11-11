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
from tasks_runtime import sheet
from tasks_runtime.commands import Tasks
from tasks_runtime.store import TaskStore, scaffold

DAY = "2026-11-11"


class DistributeTest(unittest.TestCase):
    def test_exact_total_by_largest_remainder(self):
        self.assertEqual(sheet.distribute(dict(a=3, b=1), 8, 1), dict(a=6, b=2))
        result = sheet.distribute(dict(a=1, b=1, c=1), 8, 1)
        self.assertEqual(sum(result.values()), 8)
        self.assertEqual(sorted(result.values()), [2, 3, 3])
        self.assertEqual(sheet.distribute(dict(a=1, b=2), 8, 0.5), dict(a=2.5, b=5.5))
        self.assertEqual(sheet.distribute(dict(a=10, b=0.01), 8, 1), dict(a=8))
        self.assertEqual(sheet.distribute({}, 8, 1), {})


class SheetTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name) / "dados"
        scaffold(self.root)
        self.store = TaskStore(self.root)
        self.tasks = Tasks(self.store, dict(machine="trabalho"))
        self.tasks.add("demanda", "Ajustar limite", demanda="1001", projeto="2001")
        self.tasks.add("projeto", "Melhorias do aplicativo", projeto="2001")
        self.tasks.add("issue", "Corrigir sincronização", projeto="2001", issue=["org/repo#5"])
        self.tasks.add("especificacao", "Especificar relatório", demanda="3001")
        self.tasks.add("tarefa", "Evoluir o YABook")

    def tearDown(self):
        self.tmp.cleanup()

    def windows(self, machine, task, count, start=8):
        path = self.root / "horas" / ("2026-11-%s.jsonl" % machine)
        with path.open("a", encoding="utf-8") as stream:
            for index in range(count):
                minute = (start * 60) + 15 * index
                stream.write(json.dumps(dict(tipo="janela", data=DAY, janela="%02d:%02d" % (minute // 60, minute % 60),
                                             tarefa=task)) + "\n")

    def test_day_sheet_counts_codes_and_keeps_extras_outside_total(self):
        self.windows("trabalho", "demanda-1001", 8)            # 2h
        self.windows("trabalho", "projeto-2001", 8, start=10)  # 2h
        self.windows("trabalho", "issue-corrigir-sincronizacao", 8, start=12)  # 2h no projeto 2001
        self.windows("casa", "demanda-1001", 8)                # mesmas janelas em outra máquina
        self.windows("trabalho", "tarefa-evoluir-o-yabook", 8, start=16)  # 2h extra
        with patch("tasks_runtime.commands.today", lambda: __import__("datetime").date(2026, 11, 11)):
            self.tasks.log("especificacao-3001", 2, "levantamento", day=DAY)
            self.tasks.edit("demanda-1001", append="ajuste aplicado")
        result = sheet.day_sheet(self.store, DAY)
        self.assertEqual(result["total"], 8)
        totals = {(r["tipo"], r["codigo"]): r["total"] for r in result["linhas"]}
        self.assertEqual(totals, {("projeto", "2001"): 4, ("demanda", "1001"): 2, ("especificacao", "3001"): 2})
        projeto = next(r for r in result["linhas"] if r["tipo"] == "projeto")
        self.assertEqual(sorted(projeto["tarefas"]), ["issue-corrigir-sincronizacao", "projeto-2001"])
        self.assertEqual(result["extras"], [dict(tarefa="tarefa-evoluir-o-yabook", titulo="Evoluir o YABook", horas=2)])
        espec = next(r for r in result["linhas"] if r["tipo"] == "especificacao")
        self.assertIn("levantamento", espec["observacao"])
        self.assertEqual(espec["rotulo"], "Especificação")
        self.assertIsNone(espec["inicio"])

    def test_observation_uses_complement_only_when_available(self):
        self.windows("trabalho", "demanda-1001", 4)
        plain = sheet.day_sheet(self.store, DAY)["linhas"][0]
        self.assertNotIn("complemento", plain)
        self.assertIn("Ajustar limite", plain["observacao"])
        local = sheet.day_sheet(self.store, DAY, lambda i: "detalhe local" if i == "demanda-1001" else None)
        self.assertEqual(local["linhas"][0]["complemento"], "detalhe local")

    def test_empty_day(self):
        result = sheet.day_sheet(self.store, DAY)
        self.assertEqual((result["total"], result["linhas"], result["extras"]), (0, [], []))

    def test_confirmation_latest_wins_and_week_uses_it(self):
        self.windows("trabalho", "demanda-1001", 4)
        sheet.confirm(self.store, DAY)
        sheet.confirm(self.store, DAY, [dict(tipo="demanda", codigo="1001", total=6), dict(tipo="projeto", codigo="2001", total=2)], [])
        self.assertEqual(sheet.confirmed_day(self.root, DAY)["linhas"][0]["total"], 6)
        week = sheet.week_sheet(self.store, DAY)
        self.assertEqual(week["inicio"], "2026-11-09")
        self.assertEqual(week["totais"], [dict(tipo="demanda", codigo="1001", total=6), dict(tipo="projeto", codigo="2001", total=2)])
        for row in (dict(tipo="tarefa", codigo="x", total=1), dict(tipo="demanda", codigo="", total=1),
                    dict(tipo="demanda", codigo="1", total=30)):
            with self.assertRaises(ValueError):
                sheet.confirm(self.store, DAY, [row], [])

    def test_cli(self):
        self.windows("trabalho", "demanda-1001", 4)
        config = Path(self.tmp.name) / "cfg.json"
        config.write_text(json.dumps(dict(tasks=dict(root=str(self.root), machine="trabalho"))), encoding="utf-8")

        def cli(*argv):
            out = io.StringIO()
            with contextlib.redirect_stdout(out):
                code = yabook_tasks.main(["--config", str(config), *argv])
            return code, json.loads(out.getvalue())

        code, day = cli("sheet", "--data", DAY)
        self.assertEqual((code, day["total"]), (0, 8))
        code, week = cli("sheet", "--data", DAY, "--semana")
        self.assertEqual(week["totais"][0]["total"], 8)
        code, entry = cli("sheet", "--data", DAY, "--confirm")
        self.assertEqual((code, entry["linhas"][0]["codigo"]), (0, "1001"))
        self.assertEqual(cli("sheet", "--semana", "--confirm")[0], 1)
        self.assertTrue(cli("sheet", "--data", DAY)[1]["confirmada"])


if __name__ == "__main__":
    unittest.main()
