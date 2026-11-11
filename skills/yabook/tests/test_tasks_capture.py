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
from tasks_runtime import capture, events
from tasks_runtime.commands import Tasks
from tasks_runtime.store import TaskStore, scaffold
from test_tasks_store import GIT_ENV

WHEN = datetime.datetime(2026, 11, 11, 14, 37, tzinfo=datetime.timezone(datetime.timedelta(hours=-3)))


class CaptureTest(unittest.TestCase):
    def setUp(self):
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

    def test_session_choice_overrides_machine_choice(self):
        self.tasks.add("tarefa", "A", coluna="pronto")
        self.tasks.add("tarefa", "B", coluna="pronto")
        self.tasks.start("tarefa-a", self.root / "local" / "ativa.json")
        self.assertEqual(capture.active(self.store, "nova"), "tarefa-a")
        capture.set_active(self.store, "nova", "tarefa-b")
        self.assertEqual(capture.active(self.store, "nova"), "tarefa-b")

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
        subprocess.run(command.split(), check=True, capture_output=True)
        hook.run(dict(self.event, hook_event_name="PostToolUse", tool_name="Bash", tool_input=dict(command=command)))
        session = hook.state_path(self.event).stem
        self.assertEqual(capture.active(TaskStore(self.root), session), "tarefa-implementar")
        hook.run(dict(self.event, hook_event_name="UserPromptSubmit", prompt="continuar a implementação"))
        marks = (self.root / "horas").glob("*.jsonl")
        self.assertTrue(any("tarefa-implementar" in p.read_text() for p in marks))
        self.assertEqual(hook.run(dict(self.event, hook_event_name="Stop")), {})
        log = subprocess.run(["git", "-C", str(self.root), "log", "--format=%s"], capture_output=True, text=True).stdout
        self.assertIn(capture.COMMIT_MESSAGE, log)

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
