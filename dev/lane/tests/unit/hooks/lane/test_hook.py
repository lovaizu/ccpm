"""What each hook's command runs: the event Claude Code hands on stdin read, the guard asked where
the event is of a subagent of the plugin, and its answer given in Claude Code's JSON output, a
break denied with its sentence, an error told the user too."""

import io
import json
import os
import runpy
import unittest
from unittest import mock

import helpers
from helpers import hook

RUN_BREAK = (
    f"changelog: {helpers.RUN}\nThe commands you may run, each word for word: `git log --oneline`."
)


class HookTest(helpers.PluginTest):
    def setUp(self) -> None:
        super().setUp()
        self.lay()

    def answered(self, given: object, argv: tuple = ("changelog",)) -> dict:
        """What the PreToolUse hook answers on stdout, given the event, as JSON or as the text
        itself, with the command's words."""
        text = given if isinstance(given, str) else json.dumps(given)
        out = io.StringIO()
        hook.main("PreToolUse", list(argv), io.StringIO(text), out, self.plugin)
        return helpers.answer(out.getvalue())


def denied(reason: str, user: str = "") -> dict:
    """The answer denying the call with the reason, telling the user where there is anything."""
    found = {
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "deny",
            "permissionDecisionReason": reason,
        }
    }
    return {"systemMessage": user, **found} if user else found


class TestAnswer(HookTest):
    def test_a_call_its_lanes_allow_is_answered_nothing(self):
        # Given: writer with the README's lanes laid
        # When: it runs git log --oneline
        # Then: the hook prints nothing, so the call goes on
        self.assertEqual(self.answered(self.bash("git log --oneline")), {})

    def test_a_break_is_denied_with_the_sentence_headed_by_the_plugins_name(self):
        # Given: writer with the README's lanes laid
        # When: it runs git commit
        # Then: the call is denied, the reason the sentence headed changelog:, the user told
        # nothing, as a break is the subagent's to put right
        self.assertEqual(self.answered(self.bash("git commit -m m")), denied(RUN_BREAK))

    def test_an_error_is_told_the_subagent_and_the_user(self):
        # Given: hooks/lanes.json removed
        os.remove(os.path.join(self.plugin, "hooks", "lanes.json"))
        # When: writer runs git log --oneline
        found = self.answered(self.bash("git log --oneline"))
        # Then: the call is denied, and the user told the same, headed changelog:
        reason = found["hookSpecificOutput"]["permissionDecisionReason"]
        self.assertTrue(reason.startswith("changelog: lane cannot check the lanes of writer:"))
        self.assertEqual(found, denied(reason, reason))

    def test_a_call_of_no_subagent_of_the_plugin_is_answered_nothing(self):
        for agent in (None, "other:writer", "changelog-x:writer", "general-purpose"):
            with self.subTest(agent=agent):
                # Given: writer with the README's lanes laid
                # When: the main conversation, a subagent of another plugin, one of a plugin
                # whose name begins with changelog, or a built-in subagent runs git commit
                # Then: the hook prints nothing, as lane checks this plugin's subagents alone
                self.assertEqual(self.answered(self.bash("git commit", agent)), {})


class TestEvent(HookTest):
    def test_an_event_out_of_its_documented_fields_is_an_error_for_claude_code(self):
        good = self.bash("ls")
        for event, wrong in (
            ({**good, "cwd": os.path.join(self.base, "gone")}, "$.cwd: expected a folder"),
            ({**good, "cwd": 1}, "$.cwd: expected a string"),
            ({**good, "tool_input": "ls"}, "$.tool_input: expected an object"),
            ({**good, "hook_event_name": "PostToolUse"}, "$.hook_event_name: expected"),
            ({k: v for k, v in good.items() if k != "tool_name"}, 'expected the key "tool_name"'),
        ):
            with self.subTest(wrong=wrong):
                # Given: writer's event with a folder not there, a folder not text, an input not
                # an object, another event's name, or no tool
                # When: the hook is handed it
                found = self.answered(event)
                # Then: the call is denied, telling what is wrong, for Claude Code to fix
                reason = found["hookSpecificOutput"]["permissionDecisionReason"]
                self.assertIn("the hook was handed no event as Claude Code hands it, ", reason)
                self.assertIn(wrong, reason)
                self.assertIn("`claude update`", reason)

    def test_text_that_is_no_json_object_is_an_error_naming_this_hook(self):
        for text in ("not json", "[1]"):
            with self.subTest(text=text):
                # Given: the hook handed no JSON, or JSON that is no object
                # When: it is run
                found = self.answered(text)
                # Then: the call is denied, as no subagent can be told from it, and the user told
                reason = found["hookSpecificOutput"]["permissionDecisionReason"]
                self.assertTrue(
                    reason.startswith(
                        "changelog: lane cannot check the lanes of this hook: it was handed no"
                        " JSON object."
                    ),
                    reason,
                )
                self.assertEqual(found["systemMessage"], reason)


class TestCommand(HookTest):
    def test_a_command_not_naming_the_plugin_stops_every_subagents_call(self):
        for argv in ((), ("changelog", "x"), ("change log",), ("a/b",)):
            with self.subTest(argv=argv):
                # Given: a hook's command giving no name, two words, or no name of a plugin
                # When: writer runs git log --oneline
                found = self.answered(self.bash("git log --oneline"), argv)
                # Then: the call is denied, headed lane:, as the plugin is not known
                reason = found["hookSpecificOutput"]["permissionDecisionReason"]
                self.assertTrue(
                    reason.startswith("lane: lane cannot check the lanes of this hook: its command")
                )
                self.assertIn("`lay.py write`", reason)

    def test_a_command_not_naming_the_plugin_lets_the_main_conversation_go_on(self):
        # Given: a hook's command giving no name
        # When: the main conversation runs a command
        # Then: nothing is printed, as lane checks subagents alone
        self.assertEqual(self.answered(self.bash("ls", None), ()), {})


class TestEntry(HookTest):
    def test_pretooluse_py_runs_the_hook_on_its_event_with_claude_codes_plugin_folder(self):
        # Given: writer running git commit, and the plugin's folder in CLAUDE_PLUGIN_ROOT
        stdin, out = io.StringIO(json.dumps(self.bash("git commit"))), io.StringIO()
        env = mock.patch.dict(os.environ, {"CLAUDE_PLUGIN_ROOT": self.plugin})
        argv = mock.patch("sys.argv", ["pretooluse.py", "changelog"])
        # When: pretooluse.py runs as Claude Code runs it
        with env, argv, mock.patch("sys.stdin", stdin), mock.patch("sys.stdout", out):
            runpy.run_path(os.path.join(helpers.CODE, "pretooluse.py"), run_name="__main__")
        # Then: it answers as the hook does
        self.assertEqual(helpers.answer(out.getvalue()), denied(RUN_BREAK))


if __name__ == "__main__":
    unittest.main()
