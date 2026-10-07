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
        self.git = patch.object(hook, "git", side_effect=lambda cwd, *args: "main" if args == ("branch", "--show-current") else "")
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

    def test_claude_namespace_and_stop_does_not_loop(self):
        state = hook.prompt_grant("/yabook:yabook mode: auto objetivo", {}, self.tmp.name)
        self.assertTrue(state["auto"])
        state = hook.prompt_grant("$yabook mode: automatico", {}, self.tmp.name)
        self.assertFalse(state.get("auto", False))
        hook.run(dict(self.event,hook_event_name="PostToolUse",tool_name="Edit"))
        event = dict(self.event,hook_event_name="Stop",stop_hook_active=False)
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


if __name__ == "__main__": unittest.main()
