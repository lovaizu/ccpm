"""The cases of hook.py's contract: Claude Code's hook input read as an event, and the guard's
answer given back in the form the hooks reference documents."""

import json
import os
import subprocess
import sys
from unittest import mock

import helpers
from helpers import exchange, guard, hook, testing

ROOT = "/plugins/changelog"
COMMON = {"session_id": "s1", "cwd": "/work", "transcript_path": "/t.jsonl"}


NOTHING = exchange.Answer()


def answered(given, answer=NOTHING, argv=("hook.py", "changelog"), env=None):
    """What hook.py prints for the input, its exit code, and the arguments that the guard got. A
    stand-in for the guard gives the answer."""
    with mock.patch.object(guard, "answer", return_value=answer) as asked:
        text = given if isinstance(given, str) else json.dumps(given)
        out, code = hook.main(
            list(argv), text, {"CLAUDE_PROJECT_DIR": "/work"} if env is None else env, ROOT
        )
    return out, code, asked.call_args


class TestEvent(testing.FolderTest):
    def test_a_tool_event_of_a_role_reaches_the_guard_with_each_field(self):
        given = {
            **COMMON,
            "hook_event_name": "PostToolUse",
            "agent_id": "a1",
            "agent_type": "changelog:writer",
            "tool_name": "Bash",
            "tool_input": {"command": "ls"},
            "tool_response": {"stdout": "x"},
        }
        _, _, asked = answered(given)
        self.assertEqual(
            asked.args,
            (
                "changelog",
                ROOT,
                "/work",
                exchange.Event(
                    name="PostToolUse",
                    session="s1",
                    cwd="/work",
                    agent_id="a1",
                    agent_type="changelog:writer",
                    tool="Bash",
                    tool_input={"command": "ls"},
                    tool_response={"stdout": "x"},
                ),
            ),
        )

    def test_an_event_of_the_main_conversation_has_no_agent(self):
        given = {**COMMON, "hook_event_name": "UserPromptSubmit", "prompt": "hi"}
        event = answered(given)[2].args[3]
        self.assertEqual((event.agent_type, event.prompt), (None, "hi"))

    def test_the_command_of_an_expansion_is_read(self):
        given = {**COMMON, "hook_event_name": "UserPromptExpansion", "command_name": "c:w"}
        self.assertEqual(answered(given)[2].args[3].command, "c:w")

    def test_whether_a_stop_hook_kept_it_going_is_read(self):
        given = {**COMMON, "hook_event_name": "Stop", "stop_hook_active": True}
        self.assertTrue(answered(given)[2].args[3].stop_active)

    def test_no_project_folder_reaches_the_guard_as_none(self):
        given = {**COMMON, "hook_event_name": "Stop"}
        self.assertIsNone(answered(given, env={})[2].args[2])


class TestAnswer(testing.FolderTest):
    def event(self, name):
        return {**COMMON, "hook_event_name": name, "tool_name": "Bash", "tool_input": {}}

    def test_nothing_to_tell_prints_nothing(self):
        self.assertEqual(answered(self.event("PreToolUse"))[:2], ("", 0))

    def test_a_deny_goes_back_as_the_permission_decision(self):
        out, code, _ = answered(self.event("PreToolUse"), exchange.Answer(deny="why"))
        self.assertEqual(
            (json.loads(out), code),
            (
                {
                    "hookSpecificOutput": {
                        "hookEventName": "PreToolUse",
                        "permissionDecision": "deny",
                        "permissionDecisionReason": "why",
                    }
                },
                0,
            ),
        )

    def test_an_ask_goes_back_as_the_permission_decision(self):
        out, _, _ = answered(self.event("PreToolUse"), exchange.Answer(ask="why"))
        self.assertEqual(json.loads(out)["hookSpecificOutput"]["permissionDecision"], "ask")

    def test_context_goes_back_as_additional_context_of_the_event(self):
        out, _, _ = answered(self.event("PostToolUse"), exchange.Answer(context="next"))
        self.assertEqual(
            json.loads(out),
            {"hookSpecificOutput": {"hookEventName": "PostToolUse", "additionalContext": "next"}},
        )

    def test_a_block_goes_back_as_the_decision_and_its_reason(self):
        out, _, _ = answered(self.event("SubagentStop"), exchange.Answer(block="go on"))
        self.assertEqual(json.loads(out), {"decision": "block", "reason": "go on"})

    def test_what_whoever_runs_the_plugin_hears_goes_back_as_a_system_message(self):
        out, _, _ = answered(self.event("Stop"), exchange.Answer(tell="left"))
        self.assertEqual(json.loads(out), {"systemMessage": "left"})


class TestUnread(testing.FolderTest):
    def test_input_that_is_no_json_blocks_with_why_and_who_fixes_it(self):
        out, code, _ = answered("{")
        self.assertEqual(
            (out, code),
            (
                (
                    "changelog: lane cannot check the lanes of this hook: the hook input is no"
                    " JSON object. Ask the main conversation for the fix: Anthropic must fix"
                    " Claude Code, whose hook input isn't as its documentation gives it. Go on"
                    " with the rest of your work meanwhile."
                ),
                2,
            ),
        )

    def test_input_with_no_event_name_blocks(self):
        out, code, _ = answered({**COMMON})
        self.assertEqual(code, 2)
        self.assertIn("the hook input gives no hook_event_name", out)

    def test_a_tool_event_with_no_tool_name_blocks(self):
        given = {**COMMON, "hook_event_name": "PostToolUse", "tool_input": {}}
        out, _, _ = answered(given)
        self.assertIn("the hook input of PostToolUse gives no tool_name", out)

    def test_a_tool_event_with_no_tool_input_blocks(self):
        given = {**COMMON, "hook_event_name": "PreToolUse", "tool_name": "Bash"}
        out, _, _ = answered(given)
        self.assertIn("the hook input of PreToolUse gives no tool_input", out)

    def test_a_command_naming_no_plugin_blocks_headed_by_lane(self):
        out, code, _ = answered({**COMMON, "hook_event_name": "Stop"}, argv=("hook.py",))
        self.assertEqual(
            (out, code),
            (
                (
                    "lane: lane cannot check the lanes of this hook: the hook's command names no"
                    " plugin. Ask the main conversation for the fix: the maker of the plugin must"
                    " lay its lanes again with Lane's lay.py write. Go on with the rest of your"
                    " work meanwhile."
                ),
                2,
            ),
        )


class TestRun(testing.FolderTest):
    def run_hook(self, text):
        script = os.path.join(helpers.CODE, "hook.py")
        return subprocess.run(
            [sys.executable, "-B", script, "changelog"],
            input=text,
            capture_output=True,
            text=True,
            check=False,
        )

    def test_run_as_a_script_it_prints_the_answer_and_exits_0(self):
        done = self.run_hook(json.dumps({**COMMON, "hook_event_name": "Stop"}))
        self.assertEqual((done.stdout, done.returncode), ("", 0))

    def test_run_as_a_script_on_input_it_cannot_read_it_says_why_on_stderr_and_exits_2(self):
        done = self.run_hook("{")
        self.assertEqual(done.returncode, 2)
        self.assertIn("the hook input is no JSON object", done.stderr)

    def test_the_plugin_folder_is_the_folder_above_hooks(self):
        self.assertEqual(hook.plugin_root(os.path.join(ROOT, "hooks", "lane", "hook.py")), ROOT)
