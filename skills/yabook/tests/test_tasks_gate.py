import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import yabook_hook as hook
from tasks_runtime import capture, issueflow
from tasks_runtime.commands import Tasks
from tasks_runtime.store import TaskStore, atomic_write, scaffold
from test_tasks_store import GIT_ENV


class TasksGateTest(unittest.TestCase):
    """#319: sem tarefa escolhida na sessão, edições no projeto são barradas, inclusive em auto."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(); self.addCleanup(self.tmp.cleanup)
        self.base = Path(self.tmp.name)
        self.env = patch.dict(os.environ, dict(GIT_ENV, YABOOK_CONFIG=str(self.base / "config.json"),
                                               YABOOK_STATE=str(self.base / "sessions"), YABOOK_QUEUE=str(self.base / "queue")))
        self.env.start(); self.addCleanup(self.env.stop)
        self.data_root = self.base / "dados"
        scaffold(self.data_root)
        self.cfg = dict(root=str(self.data_root), machine="trabalho")
        hook.write_json(hook.config_path(), dict(tasks=self.cfg, learning={"edit_commands": ["edita.py"]}))
        self.store = TaskStore(self.data_root)
        self.tasks = Tasks(self.store, self.cfg)
        self.tasks.add("issue", "Agenda", issue=["Org/App#12"])
        self.repo = self.base / "app"; self.repo.mkdir()
        for args in (["init", "-q", "-b", "main"], ["remote", "add", "origin", "git@github.com:org/app.git"],
                     ["commit", "-q", "--allow-empty", "-m", "inicio"], ["switch", "-q", "-c", "trabalho"]):
            subprocess.run(["git", "-C", str(self.repo), *args], check=True, capture_output=True)
        self.event = dict(session_id="s1", cwd=str(self.repo))
        self.session = hook.state_path(self.event).stem

    def tool(self, stage, name, **args):
        return hook.run(dict(self.event, hook_event_name=stage, tool_name=name, tool_input=args))

    def denied(self, result):
        return result.get("hookSpecificOutput", {}).get("permissionDecision") == "deny"

    def test_edit_in_project_needs_a_session_task_even_in_auto(self):
        hook.run(dict(self.event, hook_event_name="UserPromptSubmit", prompt="$yabook mode: auto implemente"))
        result = self.tool("PreToolUse", "Edit", file_path=str(self.repo / "a.txt"))
        self.assertTrue(self.denied(result))
        self.assertIn("start --sem-tarefa", result["hookSpecificOutput"]["permissionDecisionReason"])
        self.assertFalse(self.denied(self.tool("PreToolUse", "Write", file_path=str(self.base / "fora.txt"))))
        self.assertTrue(self.denied(self.tool("PreToolUse", "Bash", command="python3 edita.py x.p --tag t")))
        self.assertFalse(self.denied(self.tool("PreToolUse", "Bash", command="ls")))

    def test_chained_start_with_path_in_variable_binds_the_session(self):
        command = 'T=/opt/yabook_tasks.py; python3 "$T" start issue-agenda && echo ok'
        self.tool("PreToolUse", "Bash", command=command)
        self.tasks.start("issue-agenda", self.data_root / "local" / "ativa.json")  # o que a CLI faria
        result = self.tool("PostToolUse", "Bash", command=command)
        self.assertIn("issue-agenda", json.dumps(result, ensure_ascii=False))
        self.assertTrue(capture.session_resolved(self.store, self.session))
        self.assertFalse(self.denied(self.tool("PreToolUse", "Edit", file_path=str(self.repo / "a.txt"))))

    def test_start_by_another_command_does_not_bind(self):
        self.tool("PreToolUse", "Bash", command="ls")
        self.tasks.start("issue-agenda", self.data_root / "local" / "ativa.json")  # outra conversa da máquina
        self.tool("PostToolUse", "Bash", command="ls")
        self.assertFalse(capture.session_resolved(self.store, self.session))

    def test_explicit_no_task_releases_edits(self):
        command = "python3 $T start --sem-tarefa"
        self.tool("PreToolUse", "Bash", command=command)
        atomic_write(self.data_root / "local" / "sem-tarefa.json", '{"desde": "agora"}\n')
        self.tool("PostToolUse", "Bash", command=command)
        self.assertFalse(self.denied(self.tool("PreToolUse", "Edit", file_path=str(self.repo / "a.txt"))))

    def test_branch_of_issue_without_task_creates_it_under_the_epic(self):
        self.tasks.add("issue", "Épico", issue=["org/app#10"], nivel="epico")
        epic = issueflow.find(self.store, "org/app#10")["data"]["id"]
        replies = {"view": dict(title="Nova tela", body="## Resumo rápido\n\n- Tarefa: fazer\n"),
                   "api": dict(data=dict(repository=dict(issue=dict(parent=dict(number=10)))))}
        subprocess.run(["git", "-C", str(self.repo), "switch", "-q", "-c", "13-nova-tela"], check=True)
        with patch.object(issueflow, "_gh_json", side_effect=lambda args, **_: replies[args[1] if args[0] == "issue" else "api"]), \
                patch.object(hook, "spawn_background"):
            result = self.tool("PostToolUse", "Bash", command="git switch -c 13-nova-tela")
        task = issueflow.find(self.store, "org/app#13")["data"]
        self.assertEqual((task["titulo"], task["nivel"], task["pai"]), ("Nova tela", "historia", epic))
        self.assertNotIn("projeto", task)  # projeto é código da empresa; issue pessoal não usa
        self.assertIn("- **Tarefa** — fazer", self.store.get(task["id"])["data"]["descricao"])
        self.assertEqual(capture.active(self.store, self.session), task["id"])
        self.assertIn("criada a partir da issue", json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    unittest.main()
