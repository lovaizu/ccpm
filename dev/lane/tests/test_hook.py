"""The entry every plugin's hooks run: each check on the event Claude Code hands it, from the folder
the event comes from, the use stopped with what the checks say; an event in another shape let
through unchecked, saying so."""

import io
import json
import os
import unittest

from helpers import hook, testing

# What the entry says when it is handed no event as Claude Code hands it.
UNREAD = (
    "p: the hook was handed no event as Claude Code hands it, a JSON object with hook_event_name"
    " and cwd, and for PreToolUse tool_name and tool_input, for SubagentStop"
    " last_assistant_message, for PostToolUse tool_name and tool_input and tool_use_id, for"
    " PostToolUseFailure tool_name and tool_input and tool_use_id and error, so it lets this"
    " through unchecked;"
    " update Claude Code with `claude update`, and where it goes on, report it at"
    " https://github.com/lovaizu/ccpm/issues\n"
)


class Says:
    """A check that says what it is given, recording where it ran."""

    def __init__(self, *said: str) -> None:
        self.said = list(said)
        self.ran_in = None

    def check(self, event: dict) -> list[str]:
        """What the check says, the folder it runs from kept."""
        self.ran_in = os.getcwd()
        return self.said


class TestRun(testing.FolderTest):
    def event(self, **fields):
        """A PreToolUse event in Claude Code's shape, with the fields given put in or over."""
        event = {
            "hook_event_name": "PreToolUse",
            "cwd": self.base,
            "tool_name": "Bash",
            "tool_input": {},
            "agent_type": "p:a",
        }
        return {**event, **fields}

    def handed(self, stream: str, *checks: Says) -> tuple:
        """What the entry gives and writes, run from `/` on the stream with the checks."""
        err = io.StringIO()
        os.chdir("/")
        code = hook.run("p", checks, io.StringIO(stream), err, "p:a")
        return code, err.getvalue()

    def ran(self, *checks: Says) -> tuple:
        """What the entry gives and writes, run with the checks on an event of Claude Code's."""
        return self.handed(json.dumps(self.event()), *checks)

    def ran_on(self, check: Says, **fields: object) -> tuple:
        """What the entry gives and writes, run with the check on an event of the fields."""
        return self.handed(json.dumps(self.event(**fields)), check)

    def test_checks_saying_something_stop_with_what_each_says(self):
        # Given: two checks, each saying something
        # When: the entry runs them on an event
        # Then: it gives 2, on which Claude Code stops the use, with what both say, one to a line,
        # each headed by the plugin's name, each check run from the folder the event comes from
        first, second = Says("a"), Says("b")
        self.assertEqual(self.ran(first, Says(), second), (2, "p: a\np: b\n"))
        self.assertEqual((first.ran_in, second.ran_in), (self.base, self.base))

    def test_checks_saying_nothing_let_the_use_go_on(self):
        # Given: checks that say nothing, or none
        # When: the entry runs them
        # Then: it gives 0 and writes nothing
        self.assertEqual(self.ran(Says(), Says()), (0, ""))
        self.assertEqual(self.ran(), (0, ""))

    def test_an_event_of_another_hook_needs_no_tool(self):
        # Given: a SubagentStop event, which names no tool and holds the subagent's last reply
        event = {
            "hook_event_name": "SubagentStop",
            "cwd": self.base,
            "agent_type": "p:a",
            "last_assistant_message": "",
        }
        # When: the entry runs a check on it
        # Then: the check runs and says what it says
        self.assertEqual(self.handed(json.dumps(event), Says("a")), (2, "p: a\n"))

    def test_a_subagentstop_of_no_last_reply_is_read(self):
        stop = {"hook_event_name": "SubagentStop", "cwd": self.base, "agent_type": "p:a"}
        for event in (stop, dict(stop, last_assistant_message=None)):
            with self.subTest(event=event):
                # Given: a SubagentStop event of no last reply, as after the agent handed its reply
                # back with SubagentHandback
                # When: the entry runs a check on it
                # Then: the check runs and says what it says
                self.assertEqual(self.handed(json.dumps(event), Says("a")), (2, "p: a\n"))

    def test_a_stream_that_is_not_json_goes_on_saying_so(self):
        # Given: a stream that is not JSON
        # When: the entry is handed it
        # Then: it gives 1, on which Claude Code lets the use go on, saying it was handed no event
        # and what to do, and runs no check
        check = Says("a")
        self.assertEqual(self.handed("{", check), (1, UNREAD))
        self.assertIsNone(check.ran_in)

    def test_an_event_not_in_claude_codes_shape_goes_on_unchecked(self):
        event = self.event()
        stop = {"hook_event_name": "SubagentStop", "cwd": self.base, "agent_type": "p:a"}
        back = dict(event, hook_event_name="PostToolUse", tool_use_id="t1")
        failed = dict(back, hook_event_name="PostToolUseFailure", error="Exit code 1")
        wrong = {
            "a list": [event],
            "no hook_event_name": {k: v for k, v in event.items() if k != "hook_event_name"},
            "a hook_event_name that is no text": dict(event, hook_event_name=1),
            "no cwd": {k: v for k, v in event.items() if k != "cwd"},
            "a cwd of no folder": dict(event, cwd=os.path.join(self.base, "none")),
            "a cwd that is no text": dict(event, cwd=1),
            "no tool_name": {k: v for k, v in event.items() if k != "tool_name"},
            "a tool_name that is no text": dict(event, tool_name=None),
            "no tool_input": {k: v for k, v in event.items() if k != "tool_input"},
            "a tool_input that is no object": dict(event, tool_input="git commit"),
            "a SubagentStop whose last reply is neither text nor null": dict(
                stop, last_assistant_message=1
            ),
            "a PostToolUse of no call ID": {k: v for k, v in back.items() if k != "tool_use_id"},
            "a PostToolUse whose call ID is no text": dict(back, tool_use_id=1),
            "a PostToolUseFailure of no error": {k: v for k, v in failed.items() if k != "error"},
        }
        for what, value in wrong.items():
            with self.subTest(what=what):
                # Given: an event in another shape
                check = Says("a")
                # When: the entry is handed it
                # Then: it gives 1, saying it was handed no event, and runs no check
                self.assertEqual(self.handed(json.dumps(value), check), (1, UNREAD))
                self.assertIsNone(check.ran_in)

    def test_checks_do_not_run_on_an_event_of_another_agent(self):
        # Given: a check saying something
        # When: the entry runs it on an event of another agent than the one named
        # Then: it lets the use go on, the check not run and nothing said
        says = Says("a")
        self.assertEqual(self.ran_on(says, agent_type="p:other"), (0, ""))
        self.assertIsNone(says.ran_in)


if __name__ == "__main__":
    unittest.main()
