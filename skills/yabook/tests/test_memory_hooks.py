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
        self.env = patch.dict(os.environ, YABOOK_CONFIG=self.tmp.name + "/config.json", YABOOK_STATE=self.tmp.name + "/sessions")
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

    def commit(self):
        hook.run(dict(self.event, hook_event_name="PostToolUse", tool_name="Bash",
                      tool_input={"command": "rtk git commit -m 'fix: x'"}))

    def test_claude_namespace_and_stop_does_not_loop(self):
        state = hook.prompt_grant("/yabook:yabook mode: auto objetivo", {}, self.tmp.name)
        self.assertTrue(state["auto"])
        state = hook.prompt_grant("$yabook mode: automatico", {}, self.tmp.name)
        self.assertFalse(state.get("auto", False))
        hook.write_json(hook.config_path(), {"memory_root": self.tmp.name})
        hook.run(dict(self.event, hook_event_name="SessionStart", source="startup"))
        hook.run(dict(self.event,hook_event_name="PostToolUse",tool_name="Edit"))
        event = dict(self.event,hook_event_name="Stop",stop_hook_active=False)
        self.commit()
        self.head = "c2"
        self.assertEqual(hook.run(event)["decision"],"block")
        self.assertEqual(hook.run(event),{})

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
        self.commit()
        self.head = "c2"
        self.assertEqual(hook.run(event), {})
        hook.write_json(hook.config_path(), {"memory_root": self.tmp.name, "learning": {"mode": "automatic"}})
        hook.run(dict(self.event, hook_event_name="PostToolUse", tool_name="Edit"))
        self.commit()
        self.head = "c3"
        self.assertIn("Não peça do memory", hook.run(event)["reason"])
        self.assertEqual(hook.run(event), {})

    def test_checkpoint_requires_consolidated_delivery(self):
        hook.write_json(hook.config_path(), {"memory_root": self.tmp.name, "learning": {"mode": "automatic"}})
        hook.run(dict(self.event, hook_event_name="SessionStart", source="startup"))
        event = dict(self.event, hook_event_name="Stop", stop_hook_active=False)
        for _ in range(3):
            hook.run(dict(self.event, hook_event_name="PostToolUse", tool_name="Edit"))
            self.assertEqual(hook.run(event), {})
        # HEAD movido por outro agente no mesmo checkout não é entrega desta sessão.
        self.head = "c2"
        self.assertEqual(hook.run(event), {})
        self.commit()
        self.head = "c3"
        self.assertEqual(hook.run(event)["decision"], "block")
        self.assertEqual(hook.run(event), {})

    def test_memory_failure_degrades_but_authorization_still_denies(self):
        hook.write_json(hook.config_path(), {"memory_root": self.tmp.name})
        import sqlite3
        with patch("memory_runtime.retrieval.retrieve", side_effect=sqlite3.OperationalError("locked")), \
             patch("memory_runtime.views.session_context", side_effect=sqlite3.OperationalError("locked")):
            result = hook.run(dict(self.event, hook_event_name="UserPromptSubmit", prompt="checklist"))
            self.assertIn("indisponível", result["hookSpecificOutput"]["additionalContext"])
            result = hook.run(dict(self.event, hook_event_name="SessionStart", source="startup"))
            self.assertIn("indisponível", result["hookSpecificOutput"]["additionalContext"])
            result = hook.run(dict(self.event, hook_event_name="PreToolUse", tool_name="Bash", tool_input={"command": "git push"}))
            self.assertEqual(result["hookSpecificOutput"]["permissionDecision"], "deny")


if __name__ == "__main__": unittest.main()
