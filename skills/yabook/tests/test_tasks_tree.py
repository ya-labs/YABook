import contextlib
import io
import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import yabook_tasks
from tasks_runtime import sheet
from tasks_runtime.batch import Capture
from tasks_runtime.commands import Tasks
from tasks_runtime.store import TaskStore, scaffold

DAY = "2026-11-11"


class TreeTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name) / "dados"
        scaffold(self.root)
        self.store = TaskStore(self.root)
        self.tasks = Tasks(self.store, dict(machine="trabalho"))

    def tearDown(self):
        self.tmp.cleanup()

    def data(self, identifier):
        return self.store.get(identifier)["data"]

    def windows(self, task, count, start=8):
        path = self.root / "horas" / "2026-11-trabalho.jsonl"
        with path.open("a", encoding="utf-8") as stream:
            for index in range(count):
                minute = start * 60 + 15 * index
                stream.write(json.dumps(dict(tipo="janela", data=DAY, janela="%02d:%02d" % (minute // 60, minute % 60),
                                             tarefa=task)) + "\n")

    def test_levels_are_inferred_and_validated(self):
        self.tasks.add("projeto", "Melhorias do aplicativo", projeto="5723", nivel="epico")
        self.tasks.add("issue", "Relatório de agenda", issue=["org/app#12"], pai="projeto-5723")
        self.assertEqual(self.data("issue-relatorio-de-agenda")["nivel"], "historia")
        self.tasks.add("tarefa", "Ajustar filtro", pai="issue-relatorio-de-agenda")
        self.assertEqual(self.data("tarefa-ajustar-filtro")["nivel"], "tarefa")
        cases = [
            dict(tipo="tarefa", titulo="Órfã", pai="inexistente"),
            dict(tipo="tarefa", titulo="Épico com pai", nivel="epico", pai="projeto-5723"),
            dict(tipo="tarefa", titulo="Nível errado", nivel="tarefa", pai="projeto-5723"),
            dict(tipo="tarefa", titulo="Quarto nível", pai="tarefa-ajustar-filtro"),
            dict(tipo="tarefa", titulo="Nível inválido", nivel="subtarefa"),
            dict(tipo="tarefa", titulo="Pessoal texto", pessoal="sim"),
        ]
        for case in cases:
            with self.subTest(case=case), self.assertRaises(ValueError):
                self.tasks.add(case.pop("tipo"), case.pop("titulo"), **case)
        question = self.tasks.ask("Qual layout?", about="projeto-5723")["id"]
        with self.assertRaises(ValueError):
            self.tasks.edit(question, dict(pai="projeto-5723"))
        with self.assertRaises(ValueError):  # rebaixar o épico invalida as histórias
            self.tasks.edit("projeto-5723", dict(nivel="historia"))
        with self.assertRaises(ValueError):
            self.tasks.edit("issue-relatorio-de-agenda", dict(pai="issue-relatorio-de-agenda"))

    def test_story_inherits_code_and_personal_is_manual_over_computed(self):
        self.tasks.add("projeto", "Melhorias do aplicativo", projeto="5723", nivel="epico")
        self.tasks.add("issue", "Relatório de agenda", issue=["org/app#12"], pai="projeto-5723")
        self.tasks.add("issue", "Implementar a V1 do YABook Tasks", issue=["org/yabook#156"], nivel="epico")
        self.tasks.add("issue", "Captura da conversa", issue=["org/yabook#167"], pai="issue-implementar-a-v1-do-yabook-tasks")
        self.tasks.add("tarefa", "Revisar layout recebido do trabalho")
        self.tasks.add("demanda", "Ajuste pontual", demanda="1001")
        self.windows("issue-relatorio-de-agenda", 8)
        self.windows("issue-captura-da-conversa", 4, start=10)
        self.windows("tarefa-revisar-layout-recebido-do-trabalho", 4, start=11)
        self.windows("demanda-1001", 4, start=12)
        result = sheet.day_sheet(self.store, DAY)
        keys = {(r["tipo"], r["codigo"]) for r in result["linhas"]}
        self.assertEqual(keys, {("projeto", "5723"), ("demanda", "1001")})
        self.assertEqual(sorted(e["tarefa"] for e in result["extras"]),
                         ["issue-captura-da-conversa", "tarefa-revisar-layout-recebido-do-trabalho"])
        self.tasks.edit("tarefa-revisar-layout-recebido-do-trabalho", dict(pessoal=False))
        self.tasks.edit("demanda-1001", dict(pessoal=True))
        result = sheet.day_sheet(self.store, DAY)
        rows = {r["tipo"]: r for r in result["linhas"]}
        self.assertEqual(set(rows), {"projeto", "trabalho"})
        self.assertEqual((rows["trabalho"]["codigo"], rows["trabalho"]["rotulo"]), ("", "Sem código"))
        self.assertIn("demanda-1001", [e["tarefa"] for e in result["extras"]])
        sheet.confirm(self.store, DAY)  # linha sem código pode ser confirmada e ajustada depois
        self.tasks.edit("tarefa-revisar-layout-recebido-do-trabalho", unset=["pessoal"])
        self.assertNotIn("trabalho", {r["tipo"] for r in sheet.day_sheet(self.store, DAY)["linhas"]})

    def test_specification_without_code_is_personal_by_default(self):
        self.tasks.add("especificacao", "Cliente leve para mensagens")
        self.tasks.add("especificacao", "Especificar relatório", demanda="3001")
        self.windows("especificacao-cliente-leve-para-mensagens", 4)
        self.windows("especificacao-3001", 4, start=10)
        result = sheet.day_sheet(self.store, DAY)
        self.assertEqual([(r["tipo"], r["codigo"]) for r in result["linhas"]], [("especificacao", "3001")])
        self.assertEqual([e["tarefa"] for e in result["extras"]], ["especificacao-cliente-leve-para-mensagens"])
        self.tasks.edit("especificacao-cliente-leve-para-mensagens", dict(pessoal=False))
        rows = {(r["tipo"], r["codigo"]) for r in sheet.day_sheet(self.store, DAY)["linhas"]}
        self.assertEqual(rows, {("especificacao", "3001"), ("trabalho", "")})

    def test_summary_shows_epics_with_progress_and_personal_code(self):
        self.tasks.add("issue", "Implementar a V1 do YABook Tasks", issue=["org/yabook#156"], nivel="epico", coluna="andamento")
        self.tasks.add("issue", "Comandos", issue=["org/yabook#158"], pai="issue-implementar-a-v1-do-yabook-tasks", coluna="concluido")
        self.tasks.add("issue", "Site", issue=["org/yabook#170"], pai="issue-implementar-a-v1-do-yabook-tasks")
        self.tasks.add("projeto", "Melhorias do aplicativo", projeto="5723", nivel="epico")
        self.tasks.add("issue", "Agenda", issue=["org/app#12"], pai="projeto-5723")
        epics = {e["id"]: e for e in self.tasks.summary()["epicos"]}
        personal = epics["issue-implementar-a-v1-do-yabook-tasks"]
        self.assertEqual((personal["historias"], personal["concluidas"]), (2, 1))
        self.assertEqual((personal["codigo"], personal["pessoal"]), ("org/yabook#156", True))
        self.assertNotIn("pessoal", epics["projeto-5723"])
        found = self.tasks.search("", projeto="5723")["tarefas"]
        self.assertEqual(sorted(t["id"] for t in found), ["issue-agenda", "projeto-5723"])
        self.assertEqual(next(t for t in found if t["id"] == "issue-agenda")["codigo"], "5723")
        self.assertEqual(self.tasks.search("", pai="projeto-5723")["total"], 1)

    def test_capture_builds_and_reorganizes_the_tree(self):
        self.tasks.add("projeto", "Melhorias do aplicativo", projeto="5723", coluna="andamento")
        self.tasks.add("issue", "Agenda", issue=["org/app#12"], projeto="5723")
        capture = Capture(self.store, dict(machine="trabalho"))
        batch = dict(itens=[
            dict(tipo="tarefa", titulo="Ajustar filtro", pai="agenda", chave="filtro"),
            dict(tipo="issue", titulo="Agenda", issue="org/app#12", pai="p", chave="agenda"),
            dict(tipo="projeto", titulo="Melhorias do aplicativo", projeto="5723", nivel="epico", chave="p"),
            dict(tipo="issue", titulo="Implementar a V1", issue="org/yabook#156", nivel="epico", chave="v1"),
            dict(tipo="issue", titulo="Captura", issue="org/yabook#167", pai="v1", estado="concluido"),
        ])
        plan = capture.plan(batch)
        order = [o["id"] for o in plan["operacoes"]]
        self.assertLess(order.index("projeto-5723"), order.index("issue-agenda"))
        self.assertLess(order.index("issue-agenda"), order.index("tarefa-ajustar-filtro"))
        actions = {o["id"]: (o["acao"], o["campos"]) for o in plan["operacoes"]}
        self.assertEqual(actions["projeto-5723"], ("atualizar", ["nivel"]))
        self.assertEqual(actions["issue-agenda"], ("atualizar", ["nivel", "pai"]))
        capture.apply(batch)
        self.assertEqual((self.data("issue-agenda")["pai"], self.data("issue-agenda")["nivel"]), ("projeto-5723", "historia"))
        self.assertEqual(self.data("tarefa-ajustar-filtro")["nivel"], "tarefa")
        self.assertEqual({o["acao"] for o in capture.plan(batch)["operacoes"]}, {"sem-alteracao"})
        bad = dict(itens=[dict(tipo="tarefa", titulo="Quarto nível", pai="tarefa-ajustar-filtro")])
        with self.assertRaises(ValueError) as error:
            capture.plan(bad)
        self.assertIn("Hierarquia", str(error.exception))

    def test_cli_flags(self):
        config = Path(self.tmp.name) / "cfg.json"
        config.write_text(json.dumps(dict(tasks=dict(root=str(self.root), machine="trabalho"))))

        def cli(*argv):
            out = io.StringIO()
            with contextlib.redirect_stdout(out):
                code = yabook_tasks.main(["--config", str(config), *argv])
            return code, json.loads(out.getvalue())

        self.assertEqual(cli("add", "--tipo", "issue", "--titulo", "Épico", "--nivel", "epico", "--issue", "org/r#1")[0], 0)
        code, added = cli("add", "--tipo", "tarefa", "--titulo", "Filha", "--pai", "issue-epico", "--pessoal", "nao")
        self.assertEqual(code, 0)
        self.assertEqual((self.data(added["id"])["nivel"], self.data(added["id"])["pessoal"]), ("historia", False))
        self.assertEqual(cli("edit", added["id"], "--unset", "pessoal")[0], 0)
        self.assertNotIn("pessoal", self.data(added["id"]))
        self.assertEqual(cli("search", "--nivel", "epico")[1]["total"], 1)


if __name__ == "__main__":
    unittest.main()
