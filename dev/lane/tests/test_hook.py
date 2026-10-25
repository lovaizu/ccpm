"""The entry every plugin's hooks run: each check on the event Claude Code hands it, from the folder
the event comes from, answering Claude Code in its JSON output: a drift told the subagent, its
tool's use denied or it kept going; an error told the subagent and the user alike, the subagent
kept going once at its end; an event not as its IN says an error too."""

from __future__ import annotations

import io
import json
import os
import unittest

import helpers
from helpers import hook, testing

# What the entry says, headed by the plugin, where the event is not as its IN says, before the point
# it is out by.
UNREAD = (
    "p: lane cannot check the lanes of a: the hook was handed no event as Claude Code hands it, "
)
FIX = (
    ". Stop here and reply that Claude Code must be updated with `claude update`, and where this"
    " goes on, it must be reported at https://github.com/lovaizu/ccpm/issues."
)


class Says:
    """A check that says what it is given, each a drift, or an error where it begins with `!`,
    recording where it ran."""

    def __init__(self, *said: str) -> None:
        self.said = list(said)
        self.ran_in = None

    def check(self, event: dict) -> list:
        """What the check says, the folder it runs from kept."""
        self.ran_in = os.getcwd()
        return [hook.Said(s.lstrip("!"), s.startswith("!")) for s in self.said]


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

    def stop(self, **fields):
        """A SubagentStop event in Claude Code's shape, with the fields given put in or over."""
        event = {"hook_event_name": "SubagentStop", "cwd": self.base, "agent_type": "p:a"}
        return {**event, "last_assistant_message": "", **fields}

    def handed(self, stream: str, *checks: Says, held: str = "PreToolUse") -> dict | None:
        """What the entry of the hook's event held answers Claude Code, run from `/` on the stream
        with the checks: the JSON object it writes on stdout, None where it writes nothing."""
        out = io.StringIO()
        os.chdir("/")
        hook.run("p", held, checks, io.StringIO(stream), out, "p:a")
        return json.loads(out.getvalue()) if out.getvalue() else None

    def ran(self, *checks: Says) -> dict | None:
        """What the entry answers, run with the checks on an event of Claude Code's."""
        return self.handed(json.dumps(self.event()), *checks)

    def test_checks_saying_something_deny_the_use_with_what_each_says(self):
        # Given: two checks, each saying something
        # When: the entry runs them on a PreToolUse event
        # Then: it denies the use, giving as the reason, which Claude shows the subagent, what both
        # say, one to a line, each headed by the plugin's name, each check run from the folder the
        # event comes from
        first, second = Says("a"), Says("b")
        self.assertEqual(self.ran(first, Says(), second), helpers.denied("p: a\np: b"))
        self.assertEqual((first.ran_in, second.ran_in), (self.base, self.base))

    def test_an_error_is_told_the_subagent_and_the_user(self):
        # Given: a check saying a drift and an error
        # When: the entry runs it on a PreToolUse event
        # Then: it denies the use, telling the subagent both, and tells the user the error
        expected = {**helpers.denied("p: a\np: e"), "systemMessage": "p: e"}
        self.assertEqual(self.ran(Says("a", "!e")), expected)

    def test_checks_saying_nothing_let_the_use_go_on(self):
        # Given: checks that say nothing, or none
        # When: the entry runs them
        # Then: it answers nothing, which lets the use go on
        self.assertIsNone(self.ran(Says(), Says()))
        self.assertIsNone(self.ran())

    def test_a_subagentstop_keeps_the_subagent_going_with_what_is_said(self):
        for event in (self.stop(), self.stop(last_assistant_message=None)):
            with self.subTest(event=event):
                # Given: a SubagentStop event, which names no tool, of a last reply or of none, as
                # after the agent handed its reply back with SubagentHandback
                # When: the entry runs a check saying something on it
                found = self.handed(json.dumps(event), Says("a"), held="SubagentStop")
                # Then: the subagent is kept going with what it says as the reason, which Claude
                # Code gives it as its next instruction
                self.assertEqual(found, {"decision": "block", "reason": "p: a"})

    def test_at_the_end_an_error_keeps_the_subagent_going_once(self):
        for active, expected in (
            (False, {"decision": "block", "reason": "p: e", "systemMessage": "p: e"}),
            (True, {"systemMessage": "p: e"}),
        ):
            with self.subTest(active=active):
                # Given: a SubagentStop event, of a subagent a stop hook kept going before or not
                event = json.dumps(self.stop(stop_hook_active=active))
                # When: the entry runs a check saying an error on it
                found = self.handed(event, Says("!e"), held="SubagentStop")
                # Then: the first time it is kept going with the error, and the user told; once
                # kept going, the user alone is told, and it ends
                self.assertEqual(found, expected)

    def test_an_error_as_a_call_comes_back_is_told_the_user_alone(self):
        # Given: a PostToolUse event, whose call has run
        event = dict(self.event(), hook_event_name="PostToolUse", tool_use_id="t1")
        # When: the entry runs a check saying an error on it
        found = self.handed(json.dumps(event), Says("!e"), held="PostToolUse")
        # Then: the user is told it, as the call cannot be stopped
        self.assertEqual(found, {"systemMessage": "p: e"})

    def test_an_event_not_as_its_in_says_is_an_error_saying_its_point(self):
        event = self.event()
        back = dict(event, hook_event_name="PostToolUse", tool_use_id="t1")
        failed = dict(back, hook_event_name="PostToolUseFailure", error="Exit code 1")
        wrong = {
            "no JSON": ("{", "PreToolUse", "it holds no JSON"),
            "a list": ([event], "PreToolUse", "$: expected an object, found [{"),
            "no hook_event_name": (
                {k: v for k, v in event.items() if k != "hook_event_name"},
                "PreToolUse",
                '$: expected the key "hook_event_name"',
            ),
            "another event's name": (
                dict(event, last_assistant_message=""),
                "SubagentStop",
                '$.hook_event_name: expected "SubagentStop", found "PreToolUse"',
            ),
            "no cwd": (
                {k: v for k, v in event.items() if k != "cwd"},
                "PreToolUse",
                '$: expected the key "cwd"',
            ),
            "a cwd of no folder": (
                dict(event, cwd=os.path.join(self.base, "none")),
                "PreToolUse",
                "$.cwd: expected a folder",
            ),
            "a tool_input that is no object": (
                dict(event, tool_input="git commit"),
                "PreToolUse",
                "$.tool_input: expected an object",
            ),
            "a last reply neither text nor null": (
                self.stop(last_assistant_message=1),
                "SubagentStop",
                "$.last_assistant_message: expected a string or null, found 1",
            ),
            "a PostToolUse of no call ID": (
                {k: v for k, v in back.items() if k != "tool_use_id"},
                "PostToolUse",
                '$: expected the key "tool_use_id"',
            ),
            "a PostToolUseFailure of no error": (
                {k: v for k, v in failed.items() if k != "error"},
                "PostToolUseFailure",
                '$: expected the key "error"',
            ),
        }
        for what, (value, held, point) in wrong.items():
            with self.subTest(what=what):
                # Given: an event not as the IN of the hook's event says
                check = Says("a")
                stream = value if isinstance(value, str) else json.dumps(value)
                # When: the entry is handed it
                found = self.handed(stream, check, held=held)
                # Then: the user is told it is an error, its point and who must fix it, and so is
                # the subagent where the call can be stopped; no check is run
                said = (found or {}).get("systemMessage", "")
                self.assertTrue(said.startswith(UNREAD + point) and said.endswith(FIX), said)
                self.assertIsNone(check.ran_in)
                if held == "PreToolUse":
                    self.assertEqual(found, {**helpers.denied(said), "systemMessage": said})

    def test_checks_do_not_run_on_an_event_of_another_agent(self):
        # Given: a check saying something
        # When: the entry runs it on an event of another agent than the one named
        # Then: it answers nothing, the check not run
        says = Says("a")
        self.assertIsNone(self.handed(json.dumps(self.event(agent_type="p:other")), says))
        self.assertIsNone(says.ran_in)


class TestFailed(unittest.TestCase):
    def test_an_error_no_subagent_can_be_told_from_is_answered_on_the_event(self):
        for held, stream, expected in (
            ("PreToolUse", "{}", {**helpers.denied("e"), "systemMessage": "e"}),
            ("SubagentStop", '{"stop_hook_active": true}', {"systemMessage": "e"}),
            ("SubagentStop", "[]", {"decision": "block", "reason": "e", "systemMessage": "e"}),
            ("SubagentStop", "{", {"decision": "block", "reason": "e", "systemMessage": "e"}),
        ):
            with self.subTest(held=held, stream=stream):
                # Given: an error the hook meets before it can tell a subagent, on an event
                out = io.StringIO()
                # When: it is answered
                hook.failed(held, "e", io.StringIO(stream), out)
                # Then: the call is denied, or the end kept going once, and the user told
                self.assertEqual(json.loads(out.getvalue()), expected)


if __name__ == "__main__":
    unittest.main()
