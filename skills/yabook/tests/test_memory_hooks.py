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

    def test_quoted_command_is_not_grant(self):
        state = hook.prompt_grant('```\n$yabook mode: auto\n```', {}, self.tmp.name)
        self.assertFalse(state.get("auto", False))

    def test_protected_edit_and_bypass(self):
        event = dict(self.event, hook_event_name="PreToolUse", tool_name="apply_patch", tool_input={})
        self.assertEqual(hook.run(event)["hookSpecificOutput"]["permissionDecision"], "deny")
        hook.run(dict(self.event, hook_event_name="UserPromptSubmit", prompt="$yabook bypass corrigir texto"))
        self.assertNotIn("permissionDecision", hook.run(event)["hookSpecificOutput"])


if __name__ == "__main__": unittest.main()
