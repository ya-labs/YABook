import datetime
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
from tasks_runtime import capture, events, sheet
from tasks_runtime.commands import Tasks
from tasks_runtime.store import TaskStore, scaffold
from test_tasks_store import GIT_ENV

WHEN = datetime.datetime(2026, 11, 11, 14, 37, tzinfo=datetime.timezone(datetime.timedelta(hours=-3)))


class CaptureTest(unittest.TestCase):
    def setUp(self):
        offline = patch("tasks_runtime.merge_check.can_conclude", return_value=True)  # sem consulta ao GitHub
        offline.start(); self.addCleanup(offline.stop)
        self.tmp = tempfile.TemporaryDirectory()
        self.base = Path(self.tmp.name)
        self.env = patch.dict(os.environ, GIT_ENV)
        self.env.start()
        self.root = self.base / "dados"
        scaffold(self.root)
        self.git("init", "-q", "-b", "main")
        self.git("add", "-A")
        self.git("commit", "-q", "-m", "inicio")
        self.cfg = dict(tasks=dict(root=str(self.root), machine="trabalho"))
        self.store = TaskStore(self.root)
        self.tasks = Tasks(self.store, self.cfg["tasks"])

    def tearDown(self):
        self.env.stop()
        self.tmp.cleanup()

    def git(self, *args):
        return subprocess.run(["git", "-C", str(self.root), *args], capture_output=True, text=True, check=True)

    def hours(self):
        path = self.root / "horas" / "2026-11-trabalho.jsonl"
        return [json.loads(line) for line in path.read_text().splitlines()] if path.exists() else []

    def focus_fixture(self):
        self.tasks.add("projeto", "Geral", projeto="9001", coluna="andamento", nivel="epico")
        self.tasks.add("demanda", "Primeira", demanda="1001", coluna="andamento", issue=["org/repo#10"])
        self.tasks.add("demanda", "Segunda", demanda="1002", coluna="pronto")
        capture.set_active(self.store, "s1", "projeto-9001")

    def test_work_request_switches_before_mark_and_preserves_other_sessions(self):
        self.focus_fixture()
        capture.set_active(self.store, "s2", "projeto-9001")
        capture.prompt(self.cfg, "s1", WHEN, "corrija o chamado 1001")
        self.assertEqual(self.hours()[0]["tarefa"], "demanda-1001")
        self.assertEqual(capture.active(self.store, "s2"), "projeto-9001")
        capture.prompt(self.cfg, "s1", WHEN + datetime.timedelta(minutes=15), "teste org/repo#10")
        capture.prompt(self.cfg, "s1", WHEN + datetime.timedelta(minutes=30), "retome o projeto 9001")
        self.assertEqual([h["tarefa"] for h in self.hours()], ["demanda-1001", "demanda-1001", "projeto-9001"])

    def test_ambiguous_missing_closed_and_unconfirmed_do_not_capture(self):
        self.focus_fixture()
        for text in ("corrija o chamado 1001 e o chamado 1002", "corrija o chamado 9999"):
            self.assertIn("não foi capturada", capture.prompt(self.cfg, "s1", WHEN, text))
        self.tasks.move("demanda-1001", "concluido")
        capture.prompt(self.cfg, "s1", WHEN, "corrija o chamado 1001")
        capture.prompt(self.cfg, "nova", WHEN, "corrija o chamado 1002")
        capture.set_active(self.store, "s3", "demanda-1001")
        capture.prompt(self.cfg, "s3", WHEN, "continuar")
        self.assertEqual(self.hours(), [])
        self.assertEqual(capture.active(self.store, "s1"), "projeto-9001")

    def test_incidental_references_do_not_switch_and_number_is_supported(self):
        self.focus_fixture()
        for text in ("mostre as tarefas do chamado 1001", 'ele disse "corrija o chamado 1001"',
                     "corrija o código, como feito no chamado 1001"):
            capture.prompt(self.cfg, "s1", WHEN, text)
            self.assertEqual(capture.active(self.store, "s1"), "projeto-9001")
        number = self.store.get("demanda-1002")["data"]["numero"]
        capture.prompt(self.cfg, "s1", WHEN + datetime.timedelta(minutes=15), "teste @%s" % number)
        self.assertEqual(self.hours()[-1]["tarefa"], "demanda-1002")

    def test_issue_number_requires_unique_owner(self):
        self.focus_fixture()
        self.tasks.add("issue", "Outra", issue=["other/repo#10"])
        self.assertEqual(capture.prompt_focus(self.store, "teste issue #10"), (None, True))
        self.assertEqual(capture.prompt_focus(self.store, "teste org/repo#10"), ("demanda-1001", False))

    def test_session_start_lists_suggestion_questions_deadlines_and_events(self):
        self.tasks.add("demanda", "Ajustar limite", demanda="1001", coluna="andamento", prazo="hoje")
        self.tasks.ask("Qual coluna usar?")
        for index in range(12):
            events.record(self.root, "casa", "quadro", "mover", tarefa="demanda-1001", de="backlog", para="andamento")
        text = capture.session_start(self.cfg, "s1")
        self.assertIn("Tarefa ativa sugerida: demanda-1001", text)
        self.assertIn("Perguntas abertas", text)
        self.assertIn("Prazos: demanda-1001", text)
        self.assertIn("(+2)", text)
        self.assertLessEqual(len(text), 1500)
        self.assertEqual(capture.prompt(self.cfg, "s1", WHEN), "")
        events.record(self.root, "casa", "quadro", "renomear-coluna", coluna="testes")
        self.assertIn("1 nova(s)", capture.prompt(self.cfg, "s1", WHEN))
        self.assertEqual(capture.prompt(self.cfg, "s1", WHEN), "")

    def test_without_active_task_asks_once(self):
        self.assertIn("Sem tarefa ativa", capture.session_start(self.cfg, "s1"))

    def test_window_marks_are_idempotent_per_window_and_task(self):
        self.tasks.add("tarefa", "Implementar", coluna="pronto")
        capture.set_active(self.store, "s1", "tarefa-implementar")
        for _ in range(3):
            capture.prompt(self.cfg, "s1", WHEN)
        capture.prompt(self.cfg, "s1", WHEN + datetime.timedelta(minutes=10))
        self.assertEqual([(h["janela"], h["tarefa"]) for h in self.hours()], [("14:30", "tarefa-implementar"), ("14:45", "tarefa-implementar")])
        self.tasks.add("tarefa", "Outra", coluna="pronto")
        capture.set_active(self.store, "s2", "tarefa-outra")
        capture.prompt(self.cfg, "s2", WHEN)
        self.assertEqual(len(self.hours()), 3)
        capture.prompt(self.cfg, "sem-escolha", WHEN)
        self.assertEqual(len(self.hours()), 3)

    def test_admin_and_inherited_task_do_not_create_windows(self):
        self.tasks.add("tarefa", "A", coluna="pronto")
        self.tasks.start("tarefa-a", self.root / "local" / "ativa.json")
        capture.prompt(self.cfg, "nova", WHEN, "corrija o código")
        self.assertEqual(self.hours(), [])  # tarefa antiga ainda não escolhida nesta sessão
        capture.set_active(self.store, "nova", "tarefa-a")
        for text in ("$yabook commit msg", "$yabook task review", "$yabook task add corrigir tela", "registre envio à QA", "mostre o quadro"):
            capture.prompt(self.cfg, "nova", WHEN, text)
        self.assertEqual(self.hours(), [])
        capture.prompt(self.cfg, "nova", WHEN, "corrija o código e atualize a tarefa")
        self.assertEqual(len(self.hours()), 1)

    def test_session_choice_overrides_machine_choice(self):
        self.tasks.add("tarefa", "A", coluna="pronto")
        self.tasks.add("tarefa", "B", coluna="pronto")
        self.tasks.start("tarefa-a", self.root / "local" / "ativa.json")
        self.assertEqual(capture.active(self.store, "nova"), "tarefa-a")
        capture.set_active(self.store, "nova", "tarefa-b")
        self.assertEqual(capture.active(self.store, "nova"), "tarefa-b")

    def test_first_choice_attributes_only_its_own_pending_windows(self):
        self.tasks.add("demanda", "A", demanda="1001")
        self.tasks.add("tarefa", "B")
        self.tasks.start("tarefa-b", self.root / "local" / "ativa.json")
        today = WHEN.replace(hour=14, minute=0)
        capture.prompt(self.cfg, "s1", today - datetime.timedelta(days=1), "trabalho de ontem")
        capture.prompt(self.cfg, "s1", today, "corrigir tela")
        capture.prompt(self.cfg, "s1", today + datetime.timedelta(minutes=1), "continuação")
        capture.prompt(self.cfg, "s1", today + datetime.timedelta(minutes=15), "$yabook task review")
        capture.prompt(self.cfg, "s1", today + datetime.timedelta(minutes=30), "validar alterações")
        capture.prompt(self.cfg, "s2", today + datetime.timedelta(minutes=15), "outra sessão")
        self.assertEqual(self.hours(), [])
        notice = capture.set_active(self.store, "s1", "demanda-1001", self.cfg["tasks"], when=WHEN)
        self.assertIn("2 janela(s)", notice)
        self.assertIn("14:00–14:30", notice)
        self.assertIn("demanda-1001", notice)
        capture.set_active(self.store, "s1", "demanda-1001", self.cfg["tasks"], when=WHEN)
        capture.set_active(self.store, "s1", "tarefa-b", self.cfg["tasks"], when=WHEN)
        self.assertEqual([(h["janela"], h["tarefa"], h["tipo"]) for h in self.hours()],
                         [("14:00", "demanda-1001", "janela"), ("14:30", "demanda-1001", "janela")])
        windows, manual, _ = sheet.window_records(self.root, WHEN.date().isoformat())
        self.assertEqual(len(windows), 2)
        self.assertEqual(manual, {})
        other = capture._read(capture._session_file(self.store, "s2"), {})
        self.assertEqual(other["pendentes"], [[WHEN.date().isoformat(), "14:15"]])
        self.assertNotIn("ativa", other)

    def test_old_or_disabled_pending_windows_are_not_attributed(self):
        self.tasks.add("tarefa", "A")
        capture.prompt(self.cfg, "s1", WHEN, "trabalho de ontem")
        notice = capture.set_active(self.store, "s1", "tarefa-a", self.cfg["tasks"],
                                    when=WHEN + datetime.timedelta(days=1))
        self.assertEqual(notice, "")
        disabled = dict(self.cfg["tasks"], retroativo=False)
        capture.prompt(dict(tasks=disabled), "s2", WHEN, "continuar trabalho")
        self.assertNotIn("pendentes", capture._read(capture._session_file(self.store, "s2"), {}))
        self.assertEqual(capture.set_active(self.store, "s2", "tarefa-a", disabled, when=WHEN), "")
        self.assertEqual(self.hours(), [])

    def test_manual_approval_keeps_first_task_after_switch(self):
        self.tasks.add("tarefa", "A")
        self.tasks.add("tarefa", "B")
        cfg = dict(self.cfg["tasks"], policy="manual")
        capture.prompt(dict(tasks=cfg), "s1", WHEN, "corrigir tela")
        notice = capture.set_active(self.store, "s1", "tarefa-a", cfg, when=WHEN)
        self.assertIn("do task retroativo", notice)
        self.assertEqual(self.hours(), [])
        plan = capture.retroactive(self.store, cfg, "s1", when=WHEN)
        self.assertEqual((plan["tarefa"], plan["janelas"]), ("tarefa-a", ["14:30"]))
        for approval, match in ((None, "Política manual"), ("inválido", "Prévia desatualizada")):
            with self.assertRaisesRegex(ValueError, match):
                capture.retroactive(self.store, cfg, "s1", apply=True, approval_hash=approval, when=WHEN)
        with self.assertRaisesRegex(ValueError, "Prévia desatualizada"):
            capture.retroactive(self.store, cfg, "s1", apply=True, approval_hash=plan["approval_hash"],
                                when=WHEN + datetime.timedelta(days=1))
        self.assertEqual(self.hours(), [])
        capture.set_active(self.store, "s1", "tarefa-b", cfg, when=WHEN)
        result = capture.retroactive(self.store, cfg, "s1", apply=True, approval_hash=plan["approval_hash"], when=WHEN)
        self.assertEqual(result["atribuidas"], ["14:30"])
        self.assertEqual(capture.active(self.store, "s1"), "tarefa-b")
        self.assertEqual([h["tarefa"] for h in self.hours()], ["tarefa-a"])
        self.assertEqual(capture.retroactive(self.store, cfg, "s1", when=WHEN)["janelas"], [])

    def test_retry_after_partial_transfer_does_not_duplicate_or_change_destination(self):
        self.tasks.add("tarefa", "A")
        self.tasks.add("tarefa", "B")
        capture.prompt(self.cfg, "s1", WHEN - datetime.timedelta(minutes=15), "corrigir tela")
        capture.prompt(self.cfg, "s1", WHEN, "validar")
        mark = capture.mark

        def interrupted(store, machine, identifier, when):
            if when.minute == 30:
                raise OSError("Interrompido após a primeira janela")
            return mark(store, machine, identifier, when)

        with patch.object(capture, "mark", side_effect=interrupted), self.assertRaises(OSError):
            capture.set_active(self.store, "s1", "tarefa-a", self.cfg["tasks"], when=WHEN)
        capture.set_active(self.store, "s1", "tarefa-b", self.cfg["tasks"], when=WHEN)
        notice = capture.prompt(self.cfg, "s1", WHEN + datetime.timedelta(minutes=15), "continuar na segunda tarefa")
        self.assertIn("atribuída(s) a tarefa-a", notice)
        self.assertEqual([(h["janela"], h["tarefa"]) for h in self.hours()],
                         [("14:15", "tarefa-a"), ("14:30", "tarefa-a"), ("14:45", "tarefa-b")])

    def test_pending_events_and_analysis_across_machines(self):
        self.tasks.add("tarefa", "A")
        self.assertEqual(events.pending(self.root), [])  # ação do agente nasce analisada
        moved = events.record(self.root, "casa", "quadro", "mover", tarefa="tarefa-a", de="backlog", para="testes")
        self.assertEqual([e["id"] for e in events.pending(self.root)], [moved["id"]])
        events.analyze(self.root, "trabalho", [moved["id"]], "próximo passo atualizado")
        self.assertEqual(events.pending(self.root), [])
        with self.assertRaises(ValueError):
            events.analyze(self.root, "trabalho", ["ev-inexistente"], "x")
        files = sorted(p.name for p in (self.root / "eventos").glob("*.jsonl"))
        self.assertEqual(len(files), 2)

    def test_stop_commits_once_and_schedules_push_only_when_due(self):
        self.assertIsNone(capture.stop(self.cfg, spawn=False)["commit"])
        self.tasks.add("tarefa", "Nova")
        first = capture.stop(self.cfg, spawn=False)
        self.assertTrue(first["commit"])
        self.assertIsNone(capture.stop(self.cfg, spawn=False)["commit"])
        log = self.git("log", "--format=%s").stdout.splitlines()
        self.assertEqual(log[0], capture.COMMIT_MESSAGE)
        self.assertNotIn("local/", self.git("ls-files").stdout)

    def test_prompt_capture_latency(self):
        for index in range(300):
            self.store.save(dict(id="tarefa-%d" % index, tipo="tarefa", titulo="Tarefa %d" % index, coluna="backlog"))
        for index in range(200):
            events.record(self.root, "casa", "quadro", "mover", tarefa="tarefa-1", de="backlog", para="testes")
        capture.set_active(self.store, "s1", "tarefa-1")
        capture.prompt(self.cfg, "s1", WHEN)
        samples = []
        for minute in range(5):
            started = time.perf_counter()
            capture.prompt(self.cfg, "s1", WHEN + datetime.timedelta(minutes=15 * (minute + 1)))
            samples.append((time.perf_counter() - started) * 1000)
        self.assertLess(statistics.median(samples), 100, samples)


class HookIntegrationTest(unittest.TestCase):
    def setUp(self):
        offline = patch("tasks_runtime.merge_check.can_conclude", return_value=True)  # sem consulta ao GitHub
        offline.start(); self.addCleanup(offline.stop)
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
        Tasks(TaskStore(self.root), dict(machine="trabalho")).add("tarefa", "Implementar", coluna="pronto")

    def tearDown(self):
        self.env.stop()
        self.tmp.cleanup()

    def context(self, result):
        return result.get("hookSpecificOutput", {}).get("additionalContext", "")

    def test_events_flow_through_hook(self):
        start = hook.run(dict(self.event, hook_event_name="SessionStart", source="startup"))
        self.assertIn("YABook Tasks:", self.context(start))
        self.assertIn("tarefa-implementar", self.context(start))
        script = str(Path(hook.__file__).with_name("yabook_tasks.py"))
        command = "python3 %s --config %s start tarefa-implementar" % (script, hook.config_path())
        completed = subprocess.run(command.split(), check=True, capture_output=True, text=True)
        hook.run(dict(self.event, hook_event_name="PostToolUse", tool_name="Bash", tool_input=dict(command=command),
                      tool_response=dict(stdout=completed.stdout)))
        session = hook.state_path(self.event).stem
        self.assertEqual(capture.active(TaskStore(self.root), session), "tarefa-implementar")
        hook.run(dict(self.event, hook_event_name="UserPromptSubmit", prompt="continuar a implementação"))
        marks = (self.root / "horas").glob("*.jsonl")
        self.assertTrue(any("tarefa-implementar" in p.read_text() for p in marks))
        self.assertEqual(hook.run(dict(self.event, hook_event_name="Stop")), {})
        log = subprocess.run(["git", "-C", str(self.root), "log", "--format=%s"], capture_output=True, text=True).stdout
        self.assertIn(capture.COMMIT_MESSAGE, log)

    def test_add_after_prompt_uses_task_from_tool_result(self):
        hook.run(dict(self.event, hook_event_name="UserPromptSubmit", prompt="corrigir tela"))
        script = str(Path(hook.__file__).with_name("yabook_tasks.py"))
        command = "%s %s --config %s add --tipo demanda --titulo Ajuste --demanda 1234 --descricao Ajustar --size 1" % (
            sys.executable, script, hook.config_path())
        event = dict(self.event, hook_event_name="PostToolUse", tool_name="Bash", tool_input=dict(command=command))
        completed = subprocess.run(command.split(), check=True, capture_output=True, text=True)
        response = dict(stdout=completed.stdout, exit_code=1)
        self.assertEqual(hook.run(dict(event, tool_response=response)), {})
        response = dict(stdout=completed.stdout)
        notice = self.context(hook.run(dict(event, tool_response=response)))
        self.assertIn("atribuída(s) a demanda-1234", notice)
        session = hook.state_path(self.event).stem
        self.assertEqual(capture.active(TaskStore(self.root), session), "demanda-1234")
        self.assertEqual(hook.run(dict(event, tool_response=response)), {})
        prompt = dict(self.event, hook_event_name="UserPromptSubmit", prompt="corrigir outra tela")
        hook.run(prompt)
        rows = [json.loads(line) for path in (self.root / "horas").glob("*.jsonl")
                for line in path.read_text().splitlines()]
        self.assertEqual({(row["tipo"], row["tarefa"]) for row in rows}, {("janela", "demanda-1234")})
        after = command.replace("1234", "5678")
        completed = subprocess.run(after.split(), check=True, capture_output=True, text=True)
        hook.run(dict(event, tool_input=dict(command=after), tool_response=dict(output=completed.stdout, exit_code=0)))
        self.assertEqual(capture.active(TaskStore(self.root), session), "demanda-1234")

    def test_broken_task_repository_never_blocks(self):
        hook.write_json(hook.config_path(), dict(tasks=dict(root=str(self.base / "inexistente"))))
        self.assertIn("YABook ativo", self.context(hook.run(dict(self.event, hook_event_name="SessionStart", source="startup"))))
        (self.root / "quadro.yml").write_text("colunas: [", encoding="utf-8")
        hook.write_json(hook.config_path(), dict(tasks=dict(root=str(self.root))))
        result = hook.run(dict(self.event, hook_event_name="UserPromptSubmit", prompt="oi"))
        self.assertIn("Estado operacional", self.context(result))
        stats = (self.base / "hook-stats.jsonl").read_text()
        self.assertIn('"tasks.prompt"', stats)


if __name__ == "__main__":
    unittest.main()
