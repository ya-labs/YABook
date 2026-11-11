import contextlib
import datetime
import io
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import yabook_tasks
from tasks_runtime import commands
from tasks_runtime.commands import Tasks, parse_date, sync
from tasks_runtime.store import Conflict, TaskStore, scaffold
from test_tasks_store import GIT_ENV

BASE = datetime.date(2026, 11, 11)  # quarta-feira


class DateTest(unittest.TestCase):
    def test_relative_and_absolute(self):
        cases = {"2026-11-14": "2026-11-14", "14/11": "2026-11-14", "05/01": "2027-01-05", "14/11/27": "2027-11-14",
                 "hoje": "2026-11-11", "amanhã": "2026-11-12", "+3d": "2026-11-14", "sexta": "2026-11-13",
                 "sexta-feira": "2026-11-13", "próxima quarta": "2026-11-18", "Segunda": "2026-11-16"}
        for text, expected in cases.items():
            self.assertEqual(parse_date(text, BASE), expected, text)
        for text in ("semana que vem", "31/02", "ontem"):
            with self.assertRaises(ValueError, msg=text):
                parse_date(text, BASE)


class CommandsTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name) / "dados"
        scaffold(self.root)
        self.confidential = Path(self.tmp.name) / "confidencial"
        self.tasks = Tasks(TaskStore(self.root), dict(machine="trabalho", confidential=str(self.confidential)))
        self.today = patch.object(commands, "today", lambda: BASE)
        self.today.start()

    def tearDown(self):
        self.today.stop()
        self.tmp.cleanup()

    def test_add_edit_move_and_forget(self):
        first = self.tasks.add("demanda", "Ajustar limite", demanda="1001", projeto="2001", prazo="sexta",
                               issue=["org/repo#3"])
        self.assertEqual(first["id"], "demanda-1001")
        self.assertEqual(first["coluna"], "backlog")
        second = self.tasks.add("tarefa", "Revisar documentação")
        self.assertEqual(self.tasks.store.get(second["id"])["data"]["ordem"], 2)
        self.tasks.edit("demanda-1001", dict(proximo_passo="Validar no aparelho", coluna="testes"),
                        append="ajuste aplicado")
        data = self.tasks.store.get("demanda-1001")
        self.assertEqual((data["data"]["coluna"], data["data"]["ordem"], data["data"]["prazo"]), ("testes", 1, "2026-11-13"))
        self.assertIn("## Registro", data["body"])
        self.assertIn("ajuste aplicado", data["body"])
        self.tasks.edit("demanda-1001", unset=("prazo",))
        self.assertNotIn("prazo", self.tasks.store.get("demanda-1001")["data"])
        with self.assertRaises(Conflict):
            self.tasks.edit("demanda-1001", dict(titulo="x"), expected_revision=first["revision"])
        with self.assertRaises(ValueError):
            self.tasks.edit("demanda-1001", dict(criada="x"))
        self.tasks.forget("demanda-1001", "duplicada")
        archived = self.tasks.store.get("demanda-1001")
        self.assertEqual(archived["data"]["coluna"], "arquivado")
        self.assertIn("Arquivada: duplicada", archived["body"])

    def test_start_moves_to_active_and_rejects_closed(self):
        self.tasks.add("tarefa", "Implementar", coluna="pronto")
        state = self.root / "local" / "ativa.json"
        result = self.tasks.start("tarefa-implementar", state)
        self.assertEqual(result["movida_para"], "andamento")
        self.assertEqual(json.loads(state.read_text())["id"], "tarefa-implementar")
        self.assertIsNone(self.tasks.start("tarefa-implementar", state)["movida_para"])
        self.tasks.add("tarefa", "Antiga", coluna="concluido")
        with self.assertRaises(ValueError):
            self.tasks.start("tarefa-antiga", state)

    def test_questions_and_review(self):
        self.tasks.add("demanda", "Atrasada", demanda="1", prazo="2026-11-10", coluna="andamento")
        self.tasks.add("demanda", "Próxima", demanda="2", prazo="2026-11-13")
        self.tasks.add("demanda", "Distante", demanda="3", prazo="2026-12-30")
        self.tasks.add("tarefa", "Sem prazo")
        self.tasks.add("tarefa", "Feita", coluna="concluido")
        question = self.tasks.ask("Qual coluna usar para revisão?", about="demanda-1")
        review = self.tasks.review()
        self.assertEqual([t["id"] for t in review["atrasadas"]], ["demanda-1"])
        self.assertEqual([t["id"] for t in review["proximas"]], ["demanda-2"])
        self.assertEqual([t["id"] for t in review["sem_prazo"]], ["tarefa-sem-prazo"])
        self.assertEqual([t["id"] for t in review["perguntas"]], [question["id"]])
        with self.assertRaises(ValueError):
            self.tasks.answer("demanda-1", "x")
        self.tasks.answer(question["id"], "Testes")
        self.assertEqual(self.tasks.review()["perguntas"], [])
        summary = self.tasks.summary()
        self.assertEqual([t["id"] for t in summary["ativas"]], ["demanda-1"])
        self.assertEqual(summary["colunas"]["concluido"]["total"], 1)

    def test_stale_tasks_are_reported(self):
        self.tasks.add("tarefa", "Parada", coluna="andamento")
        later = patch.object(commands, "today", lambda: BASE + datetime.timedelta(days=10))
        with later:
            self.assertEqual([t["id"] for t in self.tasks.review()["paradas"]], ["tarefa-parada"])

    def test_search_show_and_complement(self):
        stamps = iter(["2026-11-11T10:00:00-03:00", "2026-11-11T11:00:00-03:00"])
        with patch("tasks_runtime.store.now", lambda: next(stamps)):
            self.tasks.add("demanda", "Limite de desconto", demanda="1001", projeto="2001")
            self.tasks.add("tarefa", "Outra coisa")
        self.assertEqual(self.tasks.search("desconto")["total"], 1)
        self.assertEqual(self.tasks.search(projeto="2001")["tarefas"][0]["id"], "demanda-1001")
        self.assertNotIn("complemento", self.tasks.show("demanda-1001"))
        (self.confidential / "tarefas").mkdir(parents=True)
        (self.confidential / "tarefas" / "demanda-1001.md").write_text("dado sensível", encoding="utf-8")
        self.assertEqual(self.tasks.show("demanda-1001")["complemento"], "dado sensível")
        self.assertEqual(self.tasks.recent(1)[0]["id"], "tarefa-outra-coisa")

    def test_manual_hours(self):
        self.tasks.add("tarefa", "Reunião")
        entry = self.tasks.log("tarefa-reuniao", "1,5h", "alinhamento", day="hoje")
        self.assertEqual(entry["horas"], 1.5)
        lines = (self.root / "horas" / "2026-11-trabalho.jsonl").read_text().splitlines()
        self.assertEqual(json.loads(lines[0])["data"], "2026-11-11")
        for hours in ("0", "25", "x"):
            with self.assertRaises(ValueError):
                self.tasks.log("tarefa-reuniao", hours)

    def test_terms_also_block_log_and_append(self):
        tasks = Tasks(TaskStore(self.root, terms=["Segredo"]), {})
        tasks.add("tarefa", "Genérica")
        with self.assertRaises(ValueError):
            tasks.log("tarefa-generica", 1, "visita ao segredo")
        with self.assertRaises(ValueError):
            tasks.edit("tarefa-generica", append="falar com SEGREDO")

    def test_clean_reports_duplicates_and_archives_old(self):
        self.tasks.add("tarefa", "Revisar fluxo", coluna="concluido")
        self.tasks.add("tarefa", "Revisar  Fluxo", id="tarefa-revisar-fluxo-b")
        with patch.object(commands, "today", lambda: BASE + datetime.timedelta(days=40)):
            preview = self.tasks.clean()
            self.assertEqual(preview["concluidas_antigas"], ["tarefa-revisar-fluxo"])
            self.assertEqual(preview["arquivadas"], [])
            self.assertEqual(len(preview["duplicatas"]), 1)
            self.assertEqual(self.tasks.clean(apply=True)["arquivadas"], ["tarefa-revisar-fluxo"])
        self.assertEqual(self.tasks.store.get("tarefa-revisar-fluxo")["data"]["coluna"], "arquivado")


class CliAndSyncTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.base = Path(self.tmp.name)
        self.env = patch.dict(os.environ, GIT_ENV)
        self.env.start()
        self.bare = self.base / "remoto.git"
        subprocess.run(["git", "init", "-q", "--bare", "-b", "main", str(self.bare)], check=True)
        self.work = self.clone("trabalho")
        scaffold(self.work)
        self.git(self.work, "add", "-A")
        self.git(self.work, "commit", "-q", "-m", "inicio")
        self.git(self.work, "push", "-q", "-u", "origin", "main")
        self.home = self.clone("casa")

    def tearDown(self):
        self.env.stop()
        self.tmp.cleanup()

    def git(self, root, *args):
        return subprocess.run(["git", "-C", str(root), *args], capture_output=True, text=True, check=True)

    def clone(self, name):
        path = self.base / name
        subprocess.run(["git", "clone", "-q", str(self.bare), str(path)], check=True, capture_output=True)
        return path

    def cli(self, root, *argv):
        config = self.base / ("cfg-" + root.name + ".json")
        config.write_text(json.dumps(dict(tasks=dict(root=str(root), machine=root.name))), encoding="utf-8")
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            code = yabook_tasks.main(["--config", str(config), *argv])
        return code, json.loads(out.getvalue())

    def test_cli_flow_and_sync_between_machines(self):
        code, added = self.cli(self.work, "add", "--tipo", "demanda", "--titulo", "Ajustar limite",
                               "--demanda", "1001", "--prazo", "2026-11-14", "--issue", "org/repo#1")
        self.assertEqual((code, added["id"]), (0, "demanda-1001"))
        code, edited = self.cli(self.work, "edit", "demanda-1001", "--issue", "org/repo#2", "--append", "nota")
        self.assertEqual(code, 0)
        self.assertEqual(self.cli(self.work, "show", "demanda-1001")[1]["data"]["issue"], ["org/repo#1", "org/repo#2"])
        code, error = self.cli(self.work, "edit", "demanda-1001", "--prazo", "ontem")
        self.assertEqual(code, 1)
        self.assertIn("Prazo", error["error"])
        self.cli(self.work, "log", "demanda-1001", "2")
        self.assertTrue(sync(self.work)["pushed"])
        code, result = self.cli(self.home, "ask", "Qual o prazo?")
        self.assertEqual(code, 0)
        synced = sync(self.home)
        self.assertTrue(synced["pulled"] and synced["pushed"])
        self.assertEqual(self.cli(self.home, "show", "demanda-1001")[1]["data"]["demanda"], "1001")
        sync(self.work)
        self.assertEqual(len(self.cli(self.work, "review")[1]["perguntas"]), 1)
        self.assertEqual(self.cli(self.work, "validate")[1]["ok"], True)

    def test_policy_requires_configuration(self):
        config = self.base / "vazio.json"
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            code = yabook_tasks.main(["--config", str(config), "policy", "manual"])
        self.assertEqual(code, 1)
        code, result = self.cli(self.work, "policy", "manual")
        self.assertEqual(result, dict(policy="manual"))


if __name__ == "__main__":
    unittest.main()
