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
from tasks_runtime.store import TaskStore, scaffold
from test_tasks_store import GIT_ENV


class IssueFlowTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.base = Path(self.tmp.name)
        self.env = patch.dict(os.environ, dict(GIT_ENV, YABOOK_CONFIG=str(self.base / "config.json"),
                                               YABOOK_STATE=str(self.base / "sessions"), YABOOK_QUEUE=str(self.base / "queue")))
        self.env.start()
        self.root = self.base / "dados"
        scaffold(self.root)
        self.cfg = dict(root=str(self.root), machine="trabalho")
        hook.write_json(hook.config_path(), dict(tasks=self.cfg))
        self.store = TaskStore(self.root)
        self.tasks = Tasks(self.store, self.cfg)
        self.tasks.add("issue", "Agenda", issue=["Org/App#12"], aguardando="retorno")
        self.repo = self.base / "app"
        self.repo.mkdir()
        for args in (["init", "-q", "-b", "main"], ["remote", "add", "origin", "git@github.com:org/app.git"],
                     ["commit", "-q", "--allow-empty", "-m", "inicio"]):
            subprocess.run(["git", "-C", str(self.repo), *args], check=True, capture_output=True)

    def tearDown(self):
        self.env.stop()
        self.tmp.cleanup()

    def data(self):
        return self.store.get("issue-agenda")

    def test_phases_move_forward_once_and_never_back(self):
        result = issueflow.advance(self.store, self.cfg, "org/app#12", "inicio", branch="12-agenda", session="s1")
        self.assertEqual((result["coluna"], result["movida"]), ("andamento", True))
        self.assertEqual(capture.active(self.store, "s1"), "issue-agenda")
        issueflow.advance(self.store, self.cfg, "org/app#12", "inicio", branch="12-agenda")
        self.assertEqual(self.data()["body"].count("Desenvolvimento iniciado"), 1)
        issueflow.advance(self.store, self.cfg, "org/app#12", "revisao", pr="https://github.com/org/app/pull/30")
        self.assertEqual(self.data()["data"]["coluna"], "testes")
        self.assertEqual(self.data()["data"]["proximo_passo"], "Revisar e integrar o PR")
        issueflow.advance(self.store, self.cfg, "org/app#12", "inicio", branch="12-agenda")
        self.assertEqual(self.data()["data"]["coluna"], "testes")  # não recua
        issueflow.advance(self.store, self.cfg, "org/app#12", "integrado", pr="#30")
        data = self.data()["data"]
        self.assertEqual(data["coluna"], "concluido")
        self.assertNotIn("proximo_passo", data)
        self.assertNotIn("aguardando", data)
        self.assertIn("Integrado no PR #30", self.data()["body"])
        self.assertIsNone(issueflow.advance(self.store, self.cfg, "org/app#99", "inicio"))
        with self.assertRaises(ValueError):
            issueflow.advance(self.store, self.cfg, "org/app#12", "outra")

    def test_ref_from_branch_and_remote(self):
        subprocess.run(["git", "-C", str(self.repo), "switch", "-q", "-c", "12-agenda"], check=True)
        self.assertEqual(issueflow.ref_from_branch(self.repo), "org/app#12")
        self.assertIsNone(issueflow.ref_from_branch(self.repo, "main"))

    def run_hook(self, command, stdout=""):
        event = dict(session_id="sessao", cwd=str(self.repo), hook_event_name="PostToolUse", tool_name="Bash",
                     tool_input=dict(command=command), tool_response=dict(stdout=stdout))
        hook.run(event)
        return hook.state_path(event).stem

    def test_hook_moves_task_on_branch_pr_and_merge(self):
        subprocess.run(["git", "-C", str(self.repo), "switch", "-q", "-c", "12-agenda"], check=True)
        session = self.run_hook("git switch -c 12-agenda")
        self.assertEqual(self.data()["data"]["coluna"], "andamento")
        self.assertEqual(capture.active(self.store, session), "issue-agenda")
        self.run_hook("gh pr create --base main --title X", "https://github.com/org/app/pull/30\n")
        self.assertEqual(self.data()["data"]["coluna"], "testes")
        with patch.object(hook, "spawn_background") as popen:
            self.run_hook("gh pr merge 30 --squash")
        args = popen.call_args[0][0]
        self.assertEqual(args[args.index("--pr") + 1], "30")
        with patch("tasks_runtime.issueflow.subprocess.run") as run:
            run.return_value = subprocess.CompletedProcess([], 0, json.dumps(dict(state="MERGED", headRefName="12-agenda", url="u")), "")
            with patch("tasks_runtime.issueflow.repo_of", return_value="org/app"):
                self.assertEqual(issueflow.merged_pr(self.repo, 30), ("org/app#12", "u"))
            run.return_value = subprocess.CompletedProcess([], 0, json.dumps(dict(state="OPEN", headRefName="12-agenda")), "")
            self.assertIsNone(issueflow.merged_pr(self.repo, 30))

    def test_hook_ignores_other_branches_and_missing_config(self):
        self.run_hook("git switch main")
        self.assertEqual(self.data()["data"]["coluna"], "backlog")
        hook.write_json(hook.config_path(), {})
        subprocess.run(["git", "-C", str(self.repo), "switch", "-q", "-c", "12-agenda"], check=True)
        self.run_hook("git switch -c 12-agenda")
        self.assertEqual(self.data()["data"]["coluna"], "backlog")


if __name__ == "__main__":
    unittest.main()
