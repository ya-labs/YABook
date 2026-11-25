import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import yabook_hook as hook
from diff_runtime import capture, compare, store
from test_tasks_store import GIT_ENV


class DiffShellTest(unittest.TestCase):
    """#335: edições feitas por comandos de shell em repositório Git entram no diff da sessão e da rodada."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(); self.addCleanup(self.tmp.cleanup)
        home = Path(self.tmp.name)
        self.env = patch.dict(os.environ, dict(GIT_ENV, YABOOK_CONFIG=str(home / "config.json"),
                                               YABOOK_STATE=str(home / "sessions"), YABOOK_QUEUE=str(home / "queue")))
        self.env.start(); self.addCleanup(self.env.stop)
        self.repo = home / "repo"; self.repo.mkdir()
        self.git("init", "-q", "-b", "main")
        (self.repo / "a.txt").write_text("um\n"); (self.repo / "b.txt").write_text("apagar\n")
        (self.repo / ".gitignore").write_text("build/\n")
        self.git("add", "-A"); self.git("commit", "-q", "-m", "inicio"); self.git("switch", "-q", "-c", "trabalho")
        self.event = dict(session_id="s1", cwd=str(self.repo))

    def git(self, *args):
        subprocess.run(["git", "-C", str(self.repo), *args], check=True, capture_output=True)

    def run_shell(self, command, change):
        hook.run(dict(self.event, hook_event_name="UserPromptSubmit", prompt="ajuste por script"))
        hook.run(dict(self.event, hook_event_name="PreToolUse", tool_name="Bash", tool_input={"command": command}))
        change()
        hook.run(dict(self.event, hook_event_name="PostToolUse", tool_name="Bash", tool_input={"command": command}))

    def sessions(self):
        return store.sessions(store.settings(hook.config())["base"], str(self.repo))

    def test_script_changes_are_recorded_with_state_before_the_command(self):
        (self.repo / "a.txt").write_text("dois\n")  # já alterado antes do comando

        def change():
            (self.repo / "a.txt").write_text("tres\n")
            (self.repo / "novo.txt").write_text("novo\n")
            (self.repo / "b.txt").unlink()
            (self.repo / "build").mkdir(); (self.repo / "build" / "saida.js").write_text("ignorado\n")

        self.run_shell("python3 gerar.py", change)
        [(folder, data)] = self.sessions()
        states = {c["caminho"]: c["estado"] for c in compare.changes(folder, data, "ultima")}
        self.assertEqual(states, {"a.txt": "alterado", "novo.txt": "novo", "b.txt": "removido"})
        item = next(i for i in data["rodadas"][0]["arquivos"] if i["caminho"] == "a.txt")
        self.assertEqual(((folder / item["antes"]).read_text(), item["origem"]), ("dois\n", "shell"))
        self.assertEqual((folder / next(i for i in data["arquivos"] if i["caminho"] == "b.txt")["antes"]).read_text(),
                         "apagar\n")
        self.assertEqual(subprocess.run(["git", "-C", str(self.repo), "stash", "list"], capture_output=True,
                                        text=True).stdout, "")  # retrato não usa o stash
        status = subprocess.run(["git", "-C", str(self.repo), "diff", "--cached", "--name-only"],
                                capture_output=True, text=True).stdout
        self.assertEqual(status, "")  # nem o índice real

    def test_git_worktree_commands_and_no_change_are_ignored(self):
        self.run_shell("git switch -c outra", lambda: (self.repo / "a.txt").write_text("troca de branch\n"))
        self.run_shell("ls -la", lambda: None)
        self.assertEqual(self.sessions(), [])

    def test_shell_capture_can_be_disabled_and_is_noop_outside_git(self):
        hook.write_json(hook.config_path(), {"diff": {"shell": False}})
        self.run_shell("python3 gerar.py", lambda: (self.repo / "a.txt").write_text("x\n"))
        self.assertEqual(self.sessions(), [])
        self.assertIsNone(capture.git_snapshot(Path(self.tmp.name)))


if __name__ == "__main__":
    unittest.main()
