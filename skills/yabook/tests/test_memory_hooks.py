import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import yabook_hook as hook


class HooksTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(); self.addCleanup(self.tmp.cleanup)
        self.env = patch.dict(os.environ, YABOOK_CONFIG=self.tmp.name + "/config.json", YABOOK_STATE=self.tmp.name + "/sessions",
                              YABOOK_QUEUE=self.tmp.name + "/queue")
        self.env.start(); self.addCleanup(self.env.stop)
        self.head = "c1"
        self.git = patch.object(hook, "git", side_effect=lambda cwd, *args: "main" if args == ("branch", "--show-current")
                                else self.head if args == ("rev-parse", "HEAD") else "")
        self.git.start(); self.addCleanup(self.git.stop)
        self.event = dict(session_id="session1", cwd=self.tmp.name)

    def test_start_resets_authorization(self):
        hook.run(dict(self.event, hook_event_name="UserPromptSubmit", prompt="$yabook mode: auto objetivo"))
        result = hook.run(dict(self.event, hook_event_name="SessionStart", source="startup"))
        self.assertIn("YABook ativo", result["hookSpecificOutput"]["additionalContext"])
        state = hook.read_json(hook.state_path(self.event)); self.assertFalse(state["auto"])

    def test_git_without_grant_denied(self):
        result = hook.run(dict(self.event, hook_event_name="PreToolUse", tool_name="Bash", tool_input={"command":"rtk git push"}))
        self.assertEqual(result["hookSpecificOutput"]["permissionDecision"], "deny")

    def test_explicit_auto_and_merge_limit(self):
        hook.run(dict(self.event, hook_event_name="UserPromptSubmit", prompt="$yabook mode: auto objetivo"))
        result = hook.run(dict(self.event, hook_event_name="PreToolUse", tool_name="Bash", tool_input={"command":"git merge branch"}))
        self.assertEqual(result["hookSpecificOutput"]["permissionDecision"], "deny")
        state = hook.prompt_grant("não faça merge; apenas prepare a revisão", {"auto": True}, self.tmp.name)
        self.assertFalse(state.get("merge_requested", False))

    def test_quoted_command_is_not_grant(self):
        state = hook.prompt_grant('```\n$yabook mode: auto\n```', {}, self.tmp.name)
        self.assertFalse(state.get("auto", False))

    def test_selected_skill_and_chain_register_auto_and_commit(self):
        selected = "[$yabook:yabook](/home/user/.codex/plugins/yabook/skills/yabook/SKILL.md)"
        state = hook.prompt_grant(selected + " mode: auto & do commit", {}, self.tmp.name)
        self.assertTrue(state["auto"])
        self.assertEqual(state["goal"], "")
        self.assertEqual(state["grant"], {"kind": "commit", "root": self.tmp.name})
        hook.run(dict(self.event, hook_event_name="UserPromptSubmit", prompt=selected + " do commit"))
        for command in ("rtk git add example.md", "rtk git commit -m 'fix: exemplo'"):
            result = hook.run(dict(self.event, hook_event_name="PreToolUse", tool_name="Bash", tool_input={"command":command}))
            self.assertNotEqual(result.get("hookSpecificOutput", {}).get("permissionDecision"), "deny")
        result = hook.run(dict(self.event, hook_event_name="PreToolUse", tool_name="Bash", tool_input={"command":"rtk git push"}))
        self.assertEqual(result["hookSpecificOutput"]["permissionDecision"], "deny")

    def test_chains_are_processed_in_order_and_keep_merge_protection(self):
        state = hook.prompt_grant("$yabook mode: auto & mode: work & do commit", {}, self.tmp.name)
        self.assertFalse(state["auto"])
        self.assertEqual(state["grant"]["kind"], "commit")
        state = hook.prompt_grant("/yabook:yabook mode: auto & /yabook do commit", {}, self.tmp.name)
        self.assertTrue(state["auto"])
        self.assertEqual(state["grant"]["kind"], "commit")
        result = hook.inspect_call(dict(tool_name="Bash",tool_input={"command":"git merge other"}), state, self.tmp.name)
        self.assertEqual(result["hookSpecificOutput"]["permissionDecision"], "deny")
        state = hook.prompt_grant("$yabook mode: auto & do merge", {}, self.tmp.name)
        result=hook.inspect_call(dict(tool_name="Bash",tool_input={"command":"git merge other"}),state,self.tmp.name)
        self.assertNotEqual(result.get("hookSpecificOutput",{}).get("permissionDecision"),"deny")

    def test_command_aliases_and_selected_skill_paths(self):
        for prefix in ("$yabook", "$yabook:yabook", "/yabook", "/yabook:yabook",
                       "[$yabook](/path/SKILL.md)", "[$yabook:yabook](</path with spaces/SKILL.md>)"):
            with self.subTest(prefix=prefix):
                state=hook.prompt_grant(prefix+" do commit",{},self.tmp.name)
                self.assertEqual(state["grant"]["kind"],"commit")

    def test_commit_followed_by_mode_auto_without_colon(self):
        for mode in ("mode auto", "mode: auto", "mode:auto"):
            with self.subTest(mode=mode):
                state=hook.prompt_grant("[$yabook:yabook](/path/SKILL.md) do commit & "+mode,{},self.tmp.name)
                self.assertTrue(state["auto"])
                self.assertEqual(state["goal"],"")
                result=hook.inspect_call(dict(tool_name="Bash",tool_input={"command":"rtk git add example.md"}),state,self.tmp.name)
                self.assertNotEqual(result.get("hookSpecificOutput",{}).get("permissionDecision"),"deny")
                result=hook.inspect_call(dict(tool_name="Bash",tool_input={"command":"rtk git merge other"}),state,self.tmp.name)
                self.assertEqual(result["hookSpecificOutput"]["permissionDecision"],"deny")

    def test_selected_skill_examples_and_open_fences_never_grant(self):
        selected="[$yabook:yabook](/path/SKILL.md) mode: auto & do commit"
        for text in ("> "+selected, "```text\n"+selected+"\n```", "~~~\n"+selected+"\n~~~",
                     "```\n"+selected, "    "+selected, "\t"+selected, "`"+selected+"`",
                     "Exemplo: "+selected, "[outra-skill](/path/SKILL.md) do commit", "$yabook:outra do commit"):
            with self.subTest(text=text):
                state=hook.prompt_grant(text,{},self.tmp.name)
                self.assertFalse(state.get("auto",False))
                self.assertFalse(state.get("grant"))

    def test_ampersands_inside_goal_are_not_commands(self):
        for goal in ('"revisar & do push"', "'revisar & do push'", "`revisar & do push`", r"revisar \& do push"):
            state=hook.prompt_grant("$yabook mode: auto "+goal,{},self.tmp.name)
            self.assertTrue(state["auto"])
            self.assertEqual(state["goal"],goal)
            self.assertIsNone(state["grant"])

    def test_selected_skill_memory_chain_uses_exact_administrative_grant(self):
        hook.write_json(hook.config_path(), {"memory_root":self.tmp.name})
        state=hook.prompt_grant("[$yabook:yabook](/path/SKILL.md) mode: auto & do memory sync",{},self.tmp.name)
        self.assertTrue(state["auto"])
        self.assertEqual(state["grant"]["kind"],"memory_sync")

    def commit(self, head):
        call = dict(self.event, tool_name="Bash", tool_input={"command": "rtk git commit -m 'fix: x'"})
        hook.run(dict(call, hook_event_name="PreToolUse"))
        self.head = head
        hook.run(dict(call, hook_event_name="PostToolUse"))

    def test_claude_namespace_and_stop_does_not_loop(self):
        state = hook.prompt_grant("/yabook:yabook mode: auto objetivo", {}, self.tmp.name)
        self.assertTrue(state["auto"])
        state = hook.prompt_grant("$yabook mode: automatico", {}, self.tmp.name)
        self.assertFalse(state.get("auto", False))
        hook.write_json(hook.config_path(), {"memory_root": self.tmp.name, "learning": {"checkpoint": "hook"}})
        hook.run(dict(self.event, hook_event_name="SessionStart", source="startup"))
        hook.run(dict(self.event,hook_event_name="PostToolUse",tool_name="Edit"))
        event = dict(self.event,hook_event_name="Stop",stop_hook_active=False)
        self.commit("c2")
        self.assertEqual(hook.run(event)["decision"],"block")
        self.assertEqual(hook.run(event),{})

    def test_git_state_injected_only_when_changed_and_stats_recorded(self):
        event = dict(self.event, hook_event_name="PreToolUse", tool_name="Bash", tool_input={"command": "ls"})
        self.git.stop()
        status = {"value": ""}
        with patch.object(hook, "git", side_effect=lambda cwd, *args: "feature" if args == ("branch", "--show-current")
                          else status["value"] if args == ("status", "--short") else ""):
            self.assertIn("additionalContext", hook.run(event)["hookSpecificOutput"])
            self.assertEqual(hook.run(event), {})
            status["value"] = " M app.js"
            self.assertIn("app.js", hook.run(event)["hookSpecificOutput"]["additionalContext"])
            hook.run(dict(self.event, hook_event_name="SessionStart", source="compact"))
            self.assertIn("additionalContext", hook.run(event)["hookSpecificOutput"])
        self.git.start()
        stats = (Path(self.tmp.name) / "hook-stats.jsonl").read_text().splitlines()
        self.assertTrue(any('"PreToolUse"' in line for line in stats))

    def test_short_continuation_skips_memory_lookup(self):
        self.assertFalse(hook.needs_memory("pode implementar"))
        self.assertFalse(hook.needs_memory("certo, prossiga"))
        self.assertTrue(hook.needs_memory("o checklist não chega no supervisor"))

    def test_git_mutation_in_compound_command_is_guarded(self):
        def call(command):
            result = hook.run(dict(self.event, hook_event_name="PreToolUse", tool_name="Bash", tool_input={"command": command}))
            return result.get("hookSpecificOutput", {}).get("permissionDecision") == "deny"
        for command in ("cd /repo && git add x && git commit -m 'y'", "cd /repo&&git push", "echo ok; rtk git commit -m z",
                        "ls | git stash"):
            self.assertTrue(call(command), command)
        for command in ("cd /repo && git status && git log -1", "git diff --stat; git branch --show-current"):
            self.assertFalse(call(command), command)
        hook.run(dict(self.event, hook_event_name="UserPromptSubmit", prompt="$yabook do commit"))
        self.assertFalse(call("cd /repo && git add x && git commit -m 'y'"))
        self.assertTrue(call("cd /repo && git commit -m y && git push"))

    def test_svn_mutations_need_grant_and_reads_stay_free(self):
        def call(command):
            return hook.run(dict(self.event, hook_event_name="PreToolUse", tool_name="Bash", tool_input={"command": command}))
        def denied(result):
            return result.get("hookSpecificOutput", {}).get("permissionDecision") == "deny"
        for command in ("svn status", "rtk proxy svn diff node_modules", "svn propget svn:ignore node_modules", "svn log -l 5"):
            self.assertFalse(denied(call(command)), command)
        for command in ("svn propset svn:ignore '*' node_modules", "cd /x && svn ps svn:ignore '*' nm",
                        "svn commit -m x", "svn revert --depth=empty node_modules", "svn update --set-depth=empty nm"):
            self.assertTrue(denied(call(command)), command)
        hook.run(dict(self.event, hook_event_name="UserPromptSubmit", prompt="$yabook do commit"))
        self.assertFalse(denied(call("svn commit -m 'fix: x'")))
        self.assertTrue(denied(call("svn revert file.js")))
        hook.run(dict(self.event, hook_event_name="UserPromptSubmit", prompt="$yabook mode: auto objetivo"))
        self.assertFalse(denied(call("svn revert file.js")))

    def test_protected_branch_allows_edits_outside_repository(self):
        patch_text = "*** Begin Patch\n*** Add File: /tmp/lote.json\n+{}\n*** End Patch"
        event = dict(self.event, hook_event_name="PreToolUse", tool_name="apply_patch", tool_input={"command": patch_text})
        self.assertNotIn("permissionDecision", hook.run(event).get("hookSpecificOutput", {}))
        inside = patch_text.replace("/tmp/lote.json", "src/app.js")
        event = dict(event, tool_input={"command": inside})
        self.assertEqual(hook.run(event)["hookSpecificOutput"]["permissionDecision"], "deny")
        event = dict(event, tool_name="Write", tool_input={"file_path": "/tmp/x.json", "content": "{}"})
        self.assertNotIn("permissionDecision", hook.run(event).get("hookSpecificOutput", {}))

    def test_protected_edit_and_bypass(self):
        event = dict(self.event, hook_event_name="PreToolUse", tool_name="apply_patch", tool_input={})
        self.assertEqual(hook.run(event)["hookSpecificOutput"]["permissionDecision"], "deny")
        hook.run(dict(self.event, hook_event_name="UserPromptSubmit", prompt="$yabook bypass corrigir texto"))
        self.assertNotIn("permissionDecision", hook.run(event)["hookSpecificOutput"])

    def test_administration_is_not_a_record_identifier(self):
        hook.write_json(hook.config_path(), {"memory_root": self.tmp.name})
        for command, service in (("sync", "sync"), ("publish", "publish"),
                                 ("recover", "recover"), ("source add marco", "source-add")):
            hook.run(dict(self.event, hook_event_name="UserPromptSubmit", prompt="$yabook do memory " + command))
            result = hook.run(dict(self.event, hook_event_name="PreToolUse", tool_name="Bash",
                tool_input={"command": "python3 yabook_memory.py --root " + self.tmp.name + " " + service}))
            self.assertNotIn("permissionDecision", result.get("hookSpecificOutput", {}))
        result = hook.run(dict(self.event, hook_event_name="PreToolUse", tool_name="Bash",
            tool_input={"command": "python3 yabook_memory.py --root " + self.tmp.name + " sync"}))
        self.assertEqual(result["hookSpecificOutput"]["permissionDecision"], "deny")

    def test_first_initialization_without_existing_configuration(self):
        plan = Path(self.tmp.name) / "plan.json"
        hook.write_json(plan, {"root": self.tmp.name})
        hook.run(dict(self.event, hook_event_name="UserPromptSubmit", prompt="$yabook do memory init"))
        result = hook.run(dict(self.event, hook_event_name="PreToolUse", tool_name="Bash", tool_input={
            "command": "python3 yabook_memory.py --root " + self.tmp.name + " init-apply --plan " + str(plan)}))
        self.assertNotIn("permissionDecision", result.get("hookSpecificOutput", {}))

    def test_memory_guard_expands_home(self):
        hook.write_json(hook.config_path(), {"memory_root": str(Path.home() / ".yabook-teste-base")})
        result = hook.run(dict(self.event, hook_event_name="PreToolUse", tool_name="Bash",
                               tool_input={"command": "python3 yabook_memory.py --root ~/.yabook-teste-base learn --input x.json --actor a"}))
        self.assertNotIn("permissionDecision", result.get("hookSpecificOutput", {}))

    def test_learn_triggers_is_limited_to_configured_base(self):
        hook.write_json(hook.config_path(), {"memory_root": self.tmp.name})
        def inspect(command):
            return hook.run(dict(self.event, hook_event_name="PreToolUse", tool_name="Bash", tool_input={"command": command}))
        ok = inspect("python3 yabook_memory.py --root " + self.tmp.name + " learn-triggers --id R --phrase x --actor a")
        self.assertNotIn("permissionDecision", ok.get("hookSpecificOutput", {}))
        other = inspect("python3 yabook_memory.py --root /outra learn-triggers --id R --phrase x --actor a")
        self.assertEqual(other["hookSpecificOutput"]["permissionDecision"], "deny")

    def test_learning_without_grant_and_policy_requires_grant(self):
        hook.write_json(hook.config_path(), {"memory_root": self.tmp.name, "learning": {"mode": "automatic"}})
        def inspect(command):
            return hook.run(dict(self.event, hook_event_name="PreToolUse", tool_name="Bash",
                                 tool_input={"command": "python3 yabook_memory.py --root " + self.tmp.name + " " + command}))
        self.assertNotIn("permissionDecision", inspect("learn --input data.json --actor demo").get("hookSpecificOutput", {}))
        self.assertEqual(inspect("apply P-example --approval-hash hash")["hookSpecificOutput"]["permissionDecision"], "deny")
        self.assertEqual(inspect("learning-policy --mode automatic")["hookSpecificOutput"]["permissionDecision"], "deny")
        self.assertEqual(inspect("learn --config /other/config.json --input data.json --actor demo")["hookSpecificOutput"]["permissionDecision"], "deny")
        hook.run(dict(self.event, hook_event_name="UserPromptSubmit", prompt="$yabook do memory policy manual"))
        self.assertNotIn("permissionDecision", inspect("learning-policy --mode manual").get("hookSpecificOutput", {}))

    def test_automatic_checkpoint_once_and_unconfigured_skips(self):
        event = dict(self.event, hook_event_name="Stop", stop_hook_active=False)
        hook.run(dict(self.event, hook_event_name="SessionStart", source="startup"))
        hook.run(dict(self.event, hook_event_name="PostToolUse", tool_name="Edit"))
        self.commit("c2")
        self.assertEqual(hook.run(event), {})
        hook.write_json(hook.config_path(), {"memory_root": self.tmp.name, "learning": {"mode": "automatic", "checkpoint": "hook"}})
        hook.run(dict(self.event, hook_event_name="PostToolUse", tool_name="Edit"))
        self.commit("c3")
        self.assertIn("Não peça do memory", hook.run(event)["reason"])
        self.assertEqual(hook.run(event), {})

    def test_checkpoint_requires_consolidated_delivery(self):
        hook.write_json(hook.config_path(), {"memory_root": self.tmp.name, "learning": {"mode": "automatic", "checkpoint": "hook"}})
        hook.run(dict(self.event, hook_event_name="SessionStart", source="startup"))
        event = dict(self.event, hook_event_name="Stop", stop_hook_active=False)
        for _ in range(3):
            hook.run(dict(self.event, hook_event_name="PostToolUse", tool_name="Edit"))
            self.assertEqual(hook.run(event), {})
        # HEAD movido por outro agente no mesmo checkout não é entrega desta sessão.
        self.head = "c2"
        self.assertEqual(hook.run(event), {})
        self.commit("c3")
        self.assertEqual(hook.run(event)["decision"], "block")
        self.assertEqual(hook.run(event), {})

    def test_checkpoint_ignores_patch_text_failed_commit_learned_turn_and_agent_mode(self):
        hook.write_json(hook.config_path(), {"memory_root": self.tmp.name, "learning": {"mode": "automatic", "checkpoint": "hook"}})
        hook.run(dict(self.event, hook_event_name="SessionStart", source="startup"))
        stop = dict(self.event, hook_event_name="Stop", stop_hook_active=False)
        hook.run(dict(self.event, hook_event_name="PostToolUse", tool_name="apply_patch",
                      tool_input={"command": "+ rtk git commit -m 'exemplo em teste'"}))
        self.head = "c2"
        self.assertEqual(hook.run(stop), {})  # texto de patch não é commit
        hook.run(dict(self.event, hook_event_name="PreToolUse", tool_name="Bash", tool_input={"command": "git commit -m x"}))
        hook.run(dict(self.event, hook_event_name="PostToolUse", tool_name="Bash", tool_input={"command": "git commit -m x"}))
        self.assertEqual(hook.run(stop), {})  # HEAD inalterado: commit falhou ou foi bloqueado
        hook.run(dict(self.event, hook_event_name="UserPromptSubmit", prompt="continue"))
        hook.run(dict(self.event, hook_event_name="PostToolUse", tool_name="Edit"))
        self.commit("c3")
        hook.run(dict(self.event, hook_event_name="PostToolUse", tool_name="Bash",
                      tool_input={"command": "python3 scripts/yabook_memory.py --root /m learn --input x.json"}))
        self.assertEqual(hook.run(stop), {})  # learn já chamado no turno
        hook.write_json(hook.config_path(), {"memory_root": self.tmp.name, "learning": {"mode": "automatic"}})
        hook.run(dict(self.event, hook_event_name="UserPromptSubmit", prompt="continue"))
        hook.run(dict(self.event, hook_event_name="PostToolUse", tool_name="Edit"))
        self.commit("c4")
        self.assertEqual(hook.run(stop), {})  # padrão agent: sem pedido

    def test_checkpoint_without_git_uses_configured_edit_commands_and_cooldown(self):
        hook.write_json(hook.config_path(), {"memory_root": self.tmp.name, "learning": {
            "mode": "automatic", "checkpoint": "hook", "edit_commands": ["edita.py"]}})
        self.head = ""  # workspace sem Git, como um controle de fontes próprio
        hook.run(dict(self.event, hook_event_name="SessionStart", source="startup"))
        stop = dict(self.event, hook_event_name="Stop", stop_hook_active=False)
        bash = lambda command: hook.run(dict(self.event, hook_event_name="PostToolUse", tool_name="Bash",
                                             tool_input={"command": command}))
        bash("ls backup/")
        self.assertEqual(hook.run(stop), {})  # sem edição, sem pedido
        bash("python3 ~/.claude/edita.py wad821c03.p --anchor x")
        self.assertEqual(hook.run(stop)["decision"], "block")
        bash("python3 ~/.claude/edita.py wad821c04.p --anchor y")
        self.assertEqual(hook.run(stop), {})  # dentro do intervalo
        with patch.object(hook.time, "time", return_value=hook.time.time() + 31 * 60):
            self.assertEqual(hook.run(stop)["decision"], "block")

    def test_memory_failure_degrades_but_authorization_still_denies(self):
        hook.write_json(hook.config_path(), {"memory_root": self.tmp.name})
        import sqlite3
        with patch("memory_runtime.retrieval.retrieve", side_effect=sqlite3.OperationalError("locked")), \
             patch("memory_runtime.views.session_context", side_effect=sqlite3.OperationalError("locked")):
            result = hook.run(dict(self.event, hook_event_name="UserPromptSubmit", prompt="checklist do supervisor"))
            self.assertIn("indisponível", result["hookSpecificOutput"]["additionalContext"])
            result = hook.run(dict(self.event, hook_event_name="SessionStart", source="startup"))
            self.assertIn("indisponível", result["hookSpecificOutput"]["additionalContext"])
            result = hook.run(dict(self.event, hook_event_name="PreToolUse", tool_name="Bash", tool_input={"command": "git push"}))
            self.assertEqual(result["hookSpecificOutput"]["permissionDecision"], "deny")


if __name__ == "__main__": unittest.main()
