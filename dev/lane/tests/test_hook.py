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
    " last_assistant_message, so it lets this through unchecked;"
    " update Claude Code with `claude update`, and where it goes on, report it at"
    " https://github.com/lovaizu/ccpm/issues\n"
)


class Says:
    """A check that says what it is given, recording where it ran."""

    def __init__(self, *said):
        self.said = list(said)
        self.ran_in = None

    def check(self, event):
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
        }
        return {**event, **fields}

    def handed(self, stream, *checks):
        err = io.StringIO()
        os.chdir("/")
        code = hook.run("p", checks, io.StringIO(stream), err)
        return code, err.getvalue()

    def ran(self, *checks):
        return self.handed(json.dumps(self.event()), *checks)

    def test_checks_saying_something_stop_with_what_each_says(self):
        # Given: two checks, each saying something
        # When: the entry runs them on an event
        # Then: it gives 2, on which Claude Code stops the use, with what both say, one to a line,
        # headed by the plugin's name, each check run from the folder the event comes from
        first, second = Says("a"), Says("b")
        self.assertEqual(self.ran(first, Says(), second), (2, "p: a\nb\n"))
        self.assertEqual((first.ran_in, second.ran_in), (self.base, self.base))

    def test_checks_saying_nothing_let_the_use_go_on(self):
        # Given: checks that say nothing, or none
        # When: the entry runs them
        # Then: it gives 0 and writes nothing
        self.assertEqual(self.ran(Says(), Says()), (0, ""))
        self.assertEqual(self.ran(), (0, ""))

    def test_an_event_of_another_hook_needs_no_tool(self):
        # Given: a SubagentStop event, which names no tool and holds the subagent's last reply
        event = {"hook_event_name": "SubagentStop", "cwd": self.base, "last_assistant_message": ""}
        # When: the entry runs a check on it
        # Then: the check runs and says what it says
        self.assertEqual(self.handed(json.dumps(event), Says("a")), (2, "p: a\n"))

    def test_a_subagentstop_of_no_last_reply_is_read(self):
        stop = {"hook_event_name": "SubagentStop", "cwd": self.base}
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
        stop = {"hook_event_name": "SubagentStop", "cwd": self.base}
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
        }
        for what, value in wrong.items():
            with self.subTest(what=what):
                # Given: an event in another shape
                check = Says("a")
                # When: the entry is handed it
                # Then: it gives 1, saying it was handed no event, and runs no check
                self.assertEqual(self.handed(json.dumps(value), check), (1, UNREAD))
                self.assertIsNone(check.ran_in)


if __name__ == "__main__":
    unittest.main()
