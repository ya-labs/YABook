import contextlib
import io
import json
import os
import sys
import tempfile
import time
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import yabook_diff
import yabook_hook as hook
from diff_runtime import compare, store
from diff_runtime.capture import chat_titles as capture_titles


class DiffCaptureTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(); self.addCleanup(self.tmp.cleanup)
        self.home = Path(self.tmp.name)
        self.root = self.home / "projeto"; self.root.mkdir()
        self.env = patch.dict(os.environ, YABOOK_CONFIG=str(self.home / "config.json"),
                              YABOOK_STATE=str(self.home / "sessions"), YABOOK_QUEUE=str(self.home / "queue"))
        self.env.start(); self.addCleanup(self.env.stop)
        self.git = patch.object(hook, "git", side_effect=lambda cwd, *args: "feature" if args == ("branch", "--show-current") else "")
        self.git.start(); self.addCleanup(self.git.stop)
        self.event = dict(session_id="s1", cwd=str(self.root))
        hook.write_json(hook.config_path(), {"learning": {"edit_commands": ["edita.py"]}})

    def tool(self, stage, name, **args):
        return hook.run(dict(self.event, hook_event_name=stage, tool_name=name, tool_input=args))

    def session(self):
        found = store.sessions(store.settings(hook.config())["base"], str(self.root))
        self.assertEqual(len(found), 1)
        return found[0]

    def test_edit_keeps_version_before_first_edit_only(self):
        source = self.root / "src" / "tela.p"; source.parent.mkdir(); source.write_bytes("original ação\n".encode("latin-1"))
        self.tool("PreToolUse", "Edit", file_path=str(source))
        source.write_bytes("primeira ação\n".encode("latin-1"))
        self.tool("PreToolUse", "Edit", file_path=str(source))
        source.write_bytes("segunda ação\n".encode("latin-1"))
        folder, data = self.session()
        self.assertEqual([i["caminho"] for i in data["arquivos"]], ["src/tela.p"])
        before = folder / data["arquivos"][0]["antes"]
        self.assertEqual(before.suffix, ".p")  # mesma extensão: VS Code aplica a associação ABL
        self.assertEqual(before.read_bytes(), "original ação\n".encode("latin-1"))
        [change] = compare.changes(folder, data)
        self.assertEqual((change["estado"], change["adicionadas"], change["removidas"]), ("alterado", 1, 1))
        self.assertIn("+segunda ação", compare.unified(change))

    def test_new_file_and_unchanged_file(self):
        new, same = self.root / "novo.md", self.root / "igual.txt"
        same.write_text("x\n")
        self.tool("PreToolUse", "Write", file_path=str(new))
        self.tool("PreToolUse", "Edit", file_path=str(same))
        new.write_text("conteúdo\n")
        folder, data = self.session()
        self.assertTrue(next(i for i in data["arquivos"] if i["caminho"] == "novo.md")["novo"])
        self.assertEqual([(c["caminho"], c["estado"]) for c in compare.changes(folder, data)], [("novo.md", "novo")])

    def test_session_is_named_after_the_chat(self):
        transcript = self.home / "chat.jsonl"
        entries = [{"type": "user", "message": "oi"}, {"type": "ai-title", "aiTitle": "Título automático"},
                   {"type": "custom-title", "customTitle": "Chamado 123 - renomeado"}]
        transcript.write_text("".join(json.dumps(e) + "\n" for e in entries))
        source = self.root / "a.txt"; source.write_text("um\n")
        hook.run(dict(self.event, hook_event_name="UserPromptSubmit", prompt="ajusta", transcript_path=str(transcript)))
        self.tool("PreToolUse", "Edit", file_path=str(source)); source.write_text("dois\n")
        self.assertEqual(self.session()[1]["titulo"], "Chamado 123 - renomeado")  # renomeado vence o automático
        # O renomeado sai do trecho lido no fim do arquivo: o último título conhecido continua valendo.
        with transcript.open("a") as stream:
            stream.write(json.dumps({"type": "user", "message": "x" * 300_000}) + "\n")
            stream.write(json.dumps({"type": "ai-title", "aiTitle": "Outro automático"}) + "\n")
        hook.run(dict(self.event, hook_event_name="UserPromptSubmit", prompt="de novo", transcript_path=str(transcript)))
        self.tool("PreToolUse", "Edit", file_path=str(self.root / "b.txt"))
        self.assertEqual(self.session()[1]["titulo"], "Chamado 123 - renomeado")
        self.assertEqual(capture_titles(transcript)["ai"], "Outro automático")

    def test_session_without_chat_title_uses_first_message(self):
        source = self.root / "a.txt"; source.write_text("um\n")
        hook.run(dict(self.event, hook_event_name="UserPromptSubmit", prompt="primeiro pedido com edição"))
        self.tool("PreToolUse", "Edit", file_path=str(source))
        folder, data = self.session()
        self.assertNotIn("titulo", data)
        self.assertEqual(store.session_title(data), "primeiro pedido com edição")

    def test_edit_command_uses_backup_written_by_the_command(self):
        source = self.root / "fontes" / "x.p"; source.parent.mkdir(); source.write_text("antes\n")
        command = "python3 edita.py fontes/x.p --tag filtro <<'FIM'"
        self.tool("PreToolUse", "Bash", command=command)
        backup = self.root / "backup" / "fontes" / "x.p.bak-20261124-101500-filtro"
        backup.parent.mkdir(parents=True); backup.write_text("antes\n"); source.write_text("depois\n")
        self.tool("PostToolUse", "Bash", command=command)
        folder, data = self.session()
        [item] = data["arquivos"]
        self.assertEqual((item["caminho"], item["origem"]), ("fontes/x.p", "backup"))
        self.assertEqual((folder / item["antes"]).read_text(), "antes\n")
        state = hook.read_json(hook.state_path(self.event))
        self.assertNotIn("diff_command_started", state)

    def test_old_backups_and_other_commands_are_ignored(self):
        old = self.root / "backup" / "y.p.bak-20200101-000000-velho"
        old.parent.mkdir(); old.write_text("velho\n"); os.utime(old, (time.time() - 3600,) * 2)
        self.tool("PreToolUse", "Bash", command="ls backup")
        self.tool("PostToolUse", "Bash", command="ls backup")
        self.tool("PreToolUse", "Bash", command="python3 edita.py y.p --tag t")
        self.tool("PostToolUse", "Bash", command="python3 edita.py y.p --tag t")
        self.assertEqual(store.sessions(store.settings(hook.config())["base"], str(self.root)), [])

    def test_capture_failure_never_blocks_tool(self):
        source = self.root / "a.txt"; source.write_text("a\n")
        with patch.object(hook.diff_capture, "before_edit", side_effect=OSError("disco cheio")):
            result = self.tool("PreToolUse", "Edit", file_path=str(source))
        self.assertNotEqual(result.get("hookSpecificOutput", {}).get("permissionDecision"), "deny")

    def test_disabled_capture(self):
        hook.write_json(hook.config_path(), {"diff": {"enabled": False}})
        source = self.root / "a.txt"; source.write_text("a\n")
        self.tool("PreToolUse", "Edit", file_path=str(source))
        self.assertEqual(store.sessions(store.settings(hook.config())["base"], str(self.root)), [])

    def test_prune_removes_sessions_past_retention(self):
        base = self.home / "diffs"
        old = store.Session(base, self.root, "antiga"); old.record(self.root / "n.txt")
        manifest = old.folder / "manifest.json"; os.utime(manifest, (time.time() - 20 * 86400,) * 2)
        recent = store.Session(base, self.root, "recente"); recent.record(self.root / "m.txt")
        self.assertEqual(store.prune(base, 14), 1)
        self.assertEqual([d["sessao"] for _, d in store.sessions(base, self.root)], ["recente"])

    def test_cli_show_and_patch(self):
        source = self.root / "a.txt"; source.write_text("um\n")
        self.tool("PreToolUse", "Edit", file_path=str(source))
        source.write_text("dois\n")
        out = io.StringIO()
        with patch.object(yabook_diff, "project_root", return_value=str(self.root)), contextlib.redirect_stdout(out):
            yabook_diff.main(["show", "--json"])
            payload = json.loads(out.getvalue())
            self.assertEqual(payload["arquivos"][0]["caminho"], "a.txt")
            out.truncate(0); out.seek(0)
            yabook_diff.main(["patch"])
        patch_file = Path(out.getvalue().strip())
        self.assertIn("-um\n+dois\n", patch_file.read_text(encoding="utf-8"))

    def prompt(self, text):
        hook.run(dict(self.event, hook_event_name="UserPromptSubmit", prompt=text))

    def view(self, *args):
        out = io.StringIO()
        with patch.object(yabook_diff, "project_root", return_value=str(self.root)), contextlib.redirect_stdout(out):
            yabook_diff.main(["show", "--json", *args])
        result = json.loads(out.getvalue())
        return result["visao"], {f["caminho"]: (f["adicionadas"], f["removidas"]) for f in result["arquivos"]}

    def test_rounds_split_changes_per_message(self):
        a, b = self.root / "a.txt", self.root / "b.txt"
        a.write_text("um\n")
        self.prompt("<ide_opened_file>x</ide_opened_file> ajusta o a")
        self.tool("PreToolUse", "Edit", file_path=str(a)); a.write_text("dois\n")
        self.prompt("só uma pergunta")  # sem edição: não vira rodada
        self.prompt("agora mexe no a e cria o b")
        self.tool("PreToolUse", "Edit", file_path=str(a)); a.write_text("tres\n")
        self.tool("PreToolUse", "Write", file_path=str(b)); b.write_text("novo\n")
        folder, data = self.session()
        self.assertEqual([(r["numero"], r["pedido"]) for r in data["rodadas"]],
                         [(1, "ajusta o a"), (2, "agora mexe no a e cria o b")])
        self.assertEqual(self.view(), ("rodada-2", {"a.txt": (1, 1), "b.txt": (1, 0)}))
        self.assertEqual(self.view("--inteira"), ("sessao", {"a.txt": (1, 1), "b.txt": (1, 0)}))
        round_one = compare.changes(folder, data, 1)
        self.assertEqual((round_one[0]["caminho"], Path(round_one[0]["depois"]).read_text()), ("a.txt", "dois\n"))
        self.assertIn("+dois", compare.unified(round_one[0]))  # rodada 1 termina onde a 2 começou

    def test_round_uses_backup_of_edit_command(self):
        source = self.root / "x.p"; source.write_text("v1\n")
        self.prompt("primeira")
        self.tool("PreToolUse", "Edit", file_path=str(source)); source.write_text("v2\n")
        self.prompt("segunda via edita")
        command = "python3 edita.py x.p --tag t"
        self.tool("PreToolUse", "Bash", command=command)
        backup = self.root / "backup" / "x.p.bak-20261125-101500-t"; backup.parent.mkdir(); backup.write_text("v2\n")
        source.write_text("v3\n")
        self.tool("PostToolUse", "Bash", command=command)
        folder, data = self.session()
        self.assertEqual(data["rodadas"][1]["arquivos"][0]["origem"], "backup")
        self.assertEqual(self.view(), ("rodada-2", {"x.p": (1, 1)}))
        self.assertIn("-v2\n+v3", compare.unified(compare.changes(folder, data, "ultima")[0]))

    def test_cli_open_uses_extension_or_falls_back_to_code_diff(self):
        source = self.root / "a.txt"; source.write_text("um\n")
        self.tool("PreToolUse", "Edit", file_path=str(source))
        source.write_text("dois\n")
        calls = []

        def fake_run(args, **kwargs):
            calls.append(args)
            listing = "yalabs.yabook\n" if installed else "ms-python.python\n"
            return mock_result(listing if "--list-extensions" in args else "")

        def mock_result(stdout):
            return type("R", (), {"stdout": stdout, "returncode": 0})()

        def run_open():
            out = io.StringIO()
            with patch.object(yabook_diff, "project_root", return_value=str(self.root)), \
                    patch.object(yabook_diff.shutil, "which", return_value="/bin/code"), \
                    patch.object(yabook_diff.subprocess, "run", side_effect=fake_run), contextlib.redirect_stdout(out):
                yabook_diff.main(["open", "--json"])
            return json.loads(out.getvalue())

        installed = True
        result = run_open()
        self.assertEqual(result["editor"]["modo"], "extensao")
        url = calls[-1][-1]
        self.assertEqual(calls[-1][1], "--open-url")
        self.assertTrue(url.startswith("vscode://yalabs.yabook/diff?manifest="))
        self.assertTrue(Path(result["patch"]).exists())

        installed, calls[:] = False, []
        result = run_open()
        self.assertEqual(result["editor"]["modo"], "code --diff")
        self.assertEqual(calls[-1][:2], ["/bin/code", "--diff"])
        self.assertTrue(calls[-1][3].endswith("a.txt"))

        with patch.object(yabook_diff, "project_root", return_value=str(self.root)), \
                patch.object(yabook_diff.shutil, "which", return_value=None), contextlib.redirect_stdout(io.StringIO()) as out:
            yabook_diff.main(["open", "--json"])
        self.assertEqual(json.loads(out.getvalue())["editor"]["modo"], "nenhum")


if __name__ == "__main__":
    unittest.main()
