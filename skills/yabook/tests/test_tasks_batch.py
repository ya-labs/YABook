import contextlib
import datetime
import io
import json
import os
import statistics
import subprocess
import sys
import tempfile
import time
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import yabook_hook as hook
import yabook_tasks
from tasks_runtime import capture, events
from tasks_runtime.batch import Capture
from tasks_runtime.commands import Tasks
from tasks_runtime.store import Conflict, TaskStore, scaffold
from test_tasks_store import GIT_ENV

WHEN = datetime.datetime(2026, 11, 11, 14, 37, tzinfo=datetime.timezone(datetime.timedelta(hours=-3)))


def conversation():
    return dict(
        itens=[
            dict(chave="p", tipo="projeto", titulo="Melhorias do aplicativo de vendas", projeto="5723", estado="ativo",
                 registro="Levantamento dos itens concluído"),
            dict(chave="a", tipo="demanda", titulo="Restrição de horário", demanda="1001", projeto="5723",
                 issue="org/app#10", estado="concluido", registro="Publicado e validado"),
            dict(chave="b", tipo="demanda", titulo="Boletos em PDF", demanda="1002", projeto="5723",
                 estado="validacao", proximo_passo="Aguardar retorno do teste", complemento="Base de homologação X"),
            dict(chave="c", tipo="issue", titulo="Relatório de agenda", projeto="5723", issue=["org/app#12"],
                 estado="pronto", prazo="2026-11-27"),
        ],
        perguntas=[dict(texto="Qual layout usar no relatório de agenda?", sobre="c")],
        ativa="b",
        horas=[dict(tarefa="b", data="2026-11-10", horas=3, obs="testes")],
    )


class BatchTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.base = Path(self.tmp.name)
        self.root = self.base / "dados"
        scaffold(self.root)
        self.terms = self.base / "termos.txt"
        self.terms.write_text("ClienteSecreto\nhostsecreto\n", encoding="utf-8")
        self.confidential = self.base / "confidencial"
        self.cfg = dict(machine="trabalho", confidential=str(self.confidential))
        self.store = TaskStore(self.root, str(self.terms))
        self.capture = Capture(self.store, self.cfg)

    def tearDown(self):
        self.tmp.cleanup()

    def ids(self):
        return sorted(t["data"]["id"] for t in self.store.list())

    def test_plan_writes_nothing_and_apply_records_everything(self):
        plan = self.capture.plan(conversation())
        self.assertEqual([o["acao"] for o in plan["operacoes"]], ["criar"] * 4)
        self.assertEqual(self.ids(), [])
        result = self.capture.apply(conversation(), plan["approval_hash"])
        self.assertEqual(result["criadas"], ["projeto-5723", "demanda-1001", "demanda-1002", "issue-relatorio-de-agenda"])
        self.assertEqual(len(result["perguntas"]), 1)
        cols = {t["data"]["id"]: t["data"]["coluna"] for t in self.store.list()}
        self.assertEqual((cols["projeto-5723"], cols["demanda-1001"], cols["demanda-1002"], cols["issue-relatorio-de-agenda"]),
                         ("andamento", "concluido", "testes", "pronto"))
        question = next(t for t in self.store.list() if t["data"]["tipo"] == "pergunta")
        self.assertEqual(question["data"]["sobre"], "issue-relatorio-de-agenda")
        self.assertIn("Publicado e validado", self.store.get("demanda-1001")["body"])
        self.assertIn("Base de homologação X", (self.confidential / "tarefas" / "demanda-1002.md").read_text())
        self.assertNotIn("homologação X", self.store.get("demanda-1002")["body"])
        self.assertEqual(json.loads((self.root / "local" / "ativa.json").read_text())["id"], "demanda-1002")
        hours = [json.loads(l) for l in (self.root / "horas" / "2026-11-trabalho.jsonl").read_text().splitlines()]
        self.assertEqual((hours[0]["tarefa"], hours[0]["horas"], hours[0]["data"]), ("demanda-1002", 3.0, "2026-11-10"))
        captured = [e for e in events.read_all(self.root) if e["acao"] == "capturar"]
        self.assertEqual(len(captured), 1)
        self.assertTrue(captured[0]["analisado"])

    def test_repeating_the_batch_does_not_duplicate(self):
        self.capture.apply(conversation())
        before = self.ids()
        plan = self.capture.plan(conversation())
        self.assertEqual({o["acao"] for o in plan["operacoes"]}, {"sem-alteracao"})
        self.assertTrue(plan["perguntas"][0]["existente"])
        self.capture.apply(conversation())
        self.assertEqual(self.ids(), before)
        self.assertEqual(self.store.get("demanda-1001")["body"].count("Publicado e validado"), 1)
        self.assertEqual((self.confidential / "tarefas" / "demanda-1002.md").read_text().count("homologação X"), 1)

    def test_matches_existing_tasks_by_issue_code_and_title(self):
        tasks = Tasks(self.store, self.cfg)
        tasks.add("issue", "Nome antigo", issue=["org/app#12"])
        tasks.add("demanda", "Restrição", demanda="1001")
        tasks.add("tarefa", "Evoluir o painel")
        batch = dict(itens=[dict(tipo="issue", titulo="Relatório de agenda", issue="org/app#12", estado="ativo"),
                            dict(tipo="demanda", titulo="Restrição de horário", demanda="1001", projeto="5723"),
                            dict(tipo="tarefa", titulo="evoluir  o PAINEL", registro="Primeira versão")])
        plan = self.capture.plan(batch)
        self.assertEqual([(o["acao"], o["id"]) for o in plan["operacoes"]],
                         [("atualizar", "issue-nome-antigo"), ("atualizar", "demanda-1001"), ("atualizar", "tarefa-evoluir-o-painel")])
        self.assertEqual(plan["operacoes"][1]["campos"], ["projeto", "titulo"])
        self.capture.apply(batch)
        self.assertEqual(self.store.get("issue-nome-antigo")["data"]["coluna"], "andamento")
        self.assertEqual(len(self.ids()), 3)

    def test_same_role_keeps_custom_column(self):
        Tasks(self.store, self.cfg).add("demanda", "Ajuste", demanda="1001", coluna="testes")
        plan = self.capture.plan(dict(itens=[dict(tipo="demanda", titulo="Ajuste", demanda="1001", estado="validacao")]))
        self.assertEqual(plan["operacoes"][0]["acao"], "sem-alteracao")

    def test_confidential_term_rejects_whole_batch_naming_the_field(self):
        batch = conversation()
        batch["itens"][2]["proximo_passo"] = "Validar na base do ClienteSecreto"
        batch["perguntas"][0]["texto"] = "Acesso ao hostsecreto?"
        with self.assertRaises(ValueError) as error:
            self.capture.apply(batch)
        self.assertIn("itens[2].proximo_passo: ClienteSecreto", str(error.exception))
        self.assertIn("perguntas[0].texto: hostsecreto", str(error.exception))
        self.assertEqual(self.ids(), [])
        batch = conversation()
        batch["itens"][2]["complemento"] = "Base do ClienteSecreto"
        self.capture.apply(batch)  # complemento é local e não versionado

    def test_invalid_batches(self):
        cases = [
            dict(),
            dict(itens=[dict(tipo="pergunta", titulo="x")]),
            dict(itens=[dict(tipo="tarefa")]),
            dict(itens=[dict(tipo="tarefa", titulo="x", estado="inexistente")]),
            dict(itens=[dict(tipo="tarefa", titulo="x", proximoPasso="y")]),
            dict(itens=[dict(tipo="tarefa", titulo="x")], ativa="nada"),
            dict(itens=[dict(tipo="tarefa", titulo="x", chave="t", estado="concluido")], ativa="t"),
            dict(itens=[dict(tipo="tarefa", titulo="x", chave="t")], horas=[dict(tarefa="t", horas=2)]),
            dict(itens=[dict(tipo="demanda", titulo="a", demanda="1"), dict(tipo="demanda", titulo="b", demanda="1")]),
            dict(itens=[dict(tipo="demanda", titulo="a", demanda="9"), dict(tipo="demanda", titulo="b", demanda="9")]),
            dict(itens=[dict(tipo="tarefa", titulo="Igual"), dict(tipo="tarefa", titulo="igual")]),
            dict(chamados=[]),
        ]
        Tasks(self.store, self.cfg).add("demanda", "Existente", demanda="1")
        for batch in cases:
            with self.subTest(batch=batch), self.assertRaises(ValueError):
                self.capture.plan(batch)
        home = Capture(self.store, dict(machine="casa"))
        with self.assertRaises(ValueError):
            home.plan(dict(itens=[dict(tipo="tarefa", titulo="x", complemento="y")]))

    def test_stale_plan_is_refused(self):
        plan = self.capture.plan(conversation())
        Tasks(self.store, self.cfg).add("demanda", "Criada em paralelo", demanda="1001")
        with self.assertRaises(Conflict):
            self.capture.apply(conversation(), plan["approval_hash"])
        self.assertEqual(self.ids(), ["demanda-1001"])


class CaptureCliTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.base = Path(self.tmp.name)
        self.root = self.base / "dados"
        scaffold(self.root)
        self.config = self.base / "cfg.json"
        self.batch = self.base / "lote.json"
        self.batch.write_text(json.dumps(dict(itens=[dict(tipo="tarefa", titulo="Nova", chave="n")], ativa="n")))

    def tearDown(self):
        self.tmp.cleanup()

    def cli(self, policy, *argv):
        self.config.write_text(json.dumps(dict(tasks=dict(root=str(self.root), machine="trabalho", policy=policy))))
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            code = yabook_tasks.main(["--config", str(self.config), *argv])
        return code, json.loads(out.getvalue())

    def test_manual_policy_requires_the_previewed_hash(self):
        code, plan = self.cli("manual", "capture", "--input", str(self.batch))
        self.assertEqual((code, plan["politica"], plan["operacoes"][0]["acao"]), (0, "manual", "criar"))
        code, refused = self.cli("manual", "capture", "--input", str(self.batch), "--apply")
        self.assertEqual(code, 1)
        self.assertIn("do task capture", refused["error"])
        self.assertFalse(list((self.root / "tarefas").glob("*.md")))
        code, done = self.cli("manual", "capture", "--input", str(self.batch), "--apply", "--approval-hash", plan["approval_hash"])
        self.assertEqual((code, done["criadas"], done["ativa"]), (0, ["tarefa-nova"], "tarefa-nova"))

    def test_automatic_policy_applies_directly(self):
        code, done = self.cli("automatic", "capture", "--input", str(self.batch), "--apply")
        self.assertEqual((code, done["criadas"]), (0, ["tarefa-nova"]))


class ReinforcementTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name) / "dados"
        scaffold(self.root)
        self.cfg = dict(tasks=dict(root=str(self.root), machine="trabalho"))
        self.store = TaskStore(self.root)

    def tearDown(self):
        self.tmp.cleanup()

    def test_session_start_carries_the_rules(self):
        text = capture.session_start(self.cfg, "s1")
        self.assertIn("task edit --append", text)
        self.assertIn("task capture", text)

    def test_signal_reminder_once_per_window(self):
        Tasks(self.store).add("tarefa", "A", coluna="pronto")
        capture.set_active(self.store, "s1", "tarefa-a")
        self.assertEqual(capture.prompt(self.cfg, "s1", WHEN, "continuar a implementação"), "")
        self.assertIn("cita prazo", capture.prompt(self.cfg, "s1", WHEN, "terminei, o prazo é sexta"))
        self.assertEqual(capture.prompt(self.cfg, "s1", WHEN, "chamado 1001 ficou pendente"), "")
        later = WHEN + datetime.timedelta(minutes=15)
        self.assertIn("cita prazo", capture.prompt(self.cfg, "s1", later, "ver issue #12"))

    def test_reasks_once_without_active_task(self):
        texts = [capture.prompt(self.cfg, "s2", WHEN, "seguir") for _ in range(capture.REASK_AFTER + 3)]
        asked = [i for i, t in enumerate(texts) if "sem tarefa ativa" in t]
        self.assertEqual(asked, [capture.REASK_AFTER - 1])
        self.assertEqual(list((self.root / "horas").glob("*.jsonl")), [])

    def test_prompt_latency_with_signal(self):
        for index in range(300):
            self.store.save(dict(id="tarefa-%d" % index, tipo="tarefa", titulo="Tarefa %d" % index, coluna="backlog"))
        capture.set_active(self.store, "s1", "tarefa-1")
        samples = []
        for minute in range(5):
            started = time.perf_counter()
            capture.prompt(self.cfg, "s1", WHEN + datetime.timedelta(minutes=15 * minute), "terminei o chamado 1001, prazo sexta")
            samples.append((time.perf_counter() - started) * 1000)
        self.assertLess(statistics.median(samples), 100, samples)


class HookCaptureTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.base = Path(self.tmp.name)
        self.env = patch.dict(os.environ, dict(GIT_ENV, YABOOK_CONFIG=str(self.base / "config.json"),
                                               YABOOK_STATE=str(self.base / "sessions"), YABOOK_QUEUE=str(self.base / "queue")))
        self.env.start()
        self.root = self.base / "dados"
        scaffold(self.root)
        subprocess.run(["git", "-C", str(self.root), "init", "-q", "-b", "main"], check=True)
        hook.write_json(hook.config_path(), dict(tasks=dict(root=str(self.root), machine="trabalho")))
        self.event = dict(session_id="sessao", cwd=self.tmp.name)

    def tearDown(self):
        self.env.stop()
        self.tmp.cleanup()

    def test_capture_apply_binds_active_task_and_prompt_reaches_signal(self):
        batch = self.base / "lote.json"
        batch.write_text(json.dumps(dict(itens=[dict(tipo="demanda", titulo="Ajuste", demanda="1001", chave="d")], ativa="d")))
        script = str(Path(hook.__file__).with_name("yabook_tasks.py"))
        command = "python3 %s --config %s capture --input %s --apply" % (script, hook.config_path(), batch)
        subprocess.run(command.split(), check=True, capture_output=True)
        hook.run(dict(self.event, hook_event_name="PostToolUse", tool_name="Bash", tool_input=dict(command=command)))
        session = hook.state_path(self.event).stem
        self.assertEqual(capture.active(TaskStore(self.root), session), "demanda-1001")
        result = hook.run(dict(self.event, hook_event_name="UserPromptSubmit", prompt="terminei o ajuste"))
        self.assertIn("cita prazo", result["hookSpecificOutput"]["additionalContext"])


if __name__ == "__main__":
    unittest.main()
