"""The guard on a flow: the orchestrator told its next move as it starts and as each call of a
subagent of the flow comes back, as context Claude Code adds for it; a call other than the move
due, or its end while a move is due, stopped with the flow's sentence and the move; and the answer
of a `from` subagent read from the Agent call that started it, or from the report it handed back."""

from __future__ import annotations

import contextlib
import io
import json
import os
import runpy
import sys
import unittest
from unittest import mock

import helpers
from flowing import FOLLOW, LAID, LEAD_LAID, REVIEWER
from helpers import called
from test_follow_flow import BACK, DONE, WRITER
from test_follow_flow import REVIEWER as REVIEWING
from test_guard import GuardTest

LEAD = "notes:notes-lead"
# What notes-lead and the user are told where a start of the flow came back from the background.
UNREAD = (
    "lane cannot check follow_flow on step 1 of notes-lead: `notes:changelog-writer` came back"
    " from the background, where lane cannot read its answer. Ask the main conversation for the"
    " fix: whoever runs the plugin must set the environment variable"
    " `CLAUDE_CODE_DISABLE_BACKGROUND_TASKS` to `1`, with which Claude Code moves no subagent to"
    " the background, and run it again. Go on with the rest of your work meanwhile."
)
# What notes-lead and the user are told where a start of the flow came back not as Claude Code
# gives it, given the point it is out by.
UNSHAPED = (
    "lane cannot check the lanes of notes-lead: the hook was handed no event as Claude Code hands"
    " it, {point}. Ask the main conversation for the fix: Claude Code must be updated with"
    " `claude update`, and where this goes on, it must be reported at"
    " https://github.com/lovaizu/ccpm/issues. Go on with the rest of your work meanwhile."
)


def context(event: str, said: str) -> dict:
    """The answer adding the text for the agent, as Claude Code reads it at the event."""
    return {"hookSpecificOutput": {"hookEventName": event, "additionalContext": said}}


class FlowGuardTest(GuardTest):
    """The guard in the plugin `notes` with the README's flow laid, notes-lead the orchestrator
    a1 of the session s1, its record holding its prompt alone."""

    def setUp(self) -> None:
        super().setUp()
        self.write(self.agent_file, helpers.LAID)
        self.write(os.path.join(self.plugin, "agents", "notes-lead.md"), LEAD_LAID)
        self.write(os.path.join(self.plugin, "agents", "changelog-reviewer.md"), REVIEWER)
        self.write_json(os.path.join(self.plugin, "hooks", "lanes.json"), LAID)
        self.record([])

    def answered(self, event: dict, entry: str, agent: str = LEAD) -> dict | None:
        """The guard's answer on the event, run as Claude Code runs the entry for the subagent of
        the type, in this process so that the coverage counts it, read as JSON; None where it
        answers nothing."""
        script = os.path.join(helpers.CODE, entry)
        argv = mock.patch.object(sys, "argv", [script, agent])
        stdin = mock.patch.object(sys, "stdin", io.StringIO(json.dumps(event)))
        root = mock.patch.dict(os.environ, {"CLAUDE_PLUGIN_ROOT": self.plugin})
        out = io.StringIO()
        with argv, stdin, root, contextlib.redirect_stdout(out):
            runpy.run_path(script, run_name="__main__")
        return json.loads(out.getvalue()) if out.getvalue() else None

    def start(self, agent: str = LEAD) -> dict | None:
        """The guard's answer as the subagent a1 of the type starts."""
        event = {
            "hook_event_name": "SubagentStart",
            "cwd": self.base,
            "session_id": "s1",
            "agent_id": "a1",
            "agent_type": agent,
        }
        return self.answered(event, "subagentstart.py", agent)

    def back(self, name: str, back: object = None, error: str | None = None) -> dict | None:
        """The guard's answer as notes-lead's Agent call starting the subagent of the name comes
        back, giving back what is given, or failed with the error."""
        given = {"subagent_type": f"notes:{name}", "prompt": "Go."}
        event = {**self.came_back("Agent", given, back, error), "agent_type": LEAD}
        entry = "posttooluse.py" if error is None else "posttoolusefailure.py"
        return self.answered(event, entry)

    def came(self, name: str, answer: str = "", agent: str = "b1") -> dict | None:
        """The guard's answer as notes-lead's Agent call of the subagent of the name comes back
        from the foreground, the subagent of the ID answering the text."""
        content = [{"type": "text", "text": answer}]
        return self.back(name, {"status": "completed", "agentId": agent, "content": content})

    def call(self, tool: str, given: dict) -> dict | None:
        """The guard's answer on notes-lead's call of the tool with the input."""
        return self.answered(self.called(tool, given, LEAD), "pretooluse.py")


class TestToldAtTheStart(FlowGuardTest):
    def test_the_orchestrator_is_told_its_first_move_as_it_starts(self):
        # Given: notes-lead, no call of it kept
        # When: it starts
        # Then: it is told its first move, headed by the plugin
        self.assertEqual(self.start(), context("SubagentStart", f"notes: {WRITER}"))

    def test_an_orchestrator_started_again_is_told_the_move_due(self):
        # Given: notes-lead, its writer's call come back
        self.came("changelog-writer")
        # When: it starts again, resumed
        # Then: it is told the reviewer's start
        self.assertEqual(self.start(), context("SubagentStart", f"notes: {REVIEWING}"))

    def test_a_subagent_that_is_not_the_orchestrator_is_told_nothing(self):
        for what, laid in (
            ("lanes laid", LAID),
            ("no flow laid", {"subagents": LAID["subagents"]}),
            ("hooks/lanes.json out of its form", "{"),
        ):
            with self.subTest(what=what):
                # Given: hooks/lanes.json so
                path = os.path.join(self.plugin, "hooks", "lanes.json")
                self.write(path, laid if isinstance(laid, str) else json.dumps(laid))
                # When: changelog-writer or summarizer, named before notes-lead in order and after
                # it, starts, or notes-lead where no flow is laid
                # Then: nothing is told; the next call is told what is wrong
                self.assertIsNone(self.start(helpers.AGENT))
                self.assertIsNone(self.start("notes:summarizer"))
                if laid is not LAID:
                    self.assertIsNone(self.start())


class TestToldAsACallComesBack(FlowGuardTest):
    def test_each_move_is_told_as_the_call_of_the_one_before_comes_back(self):
        # Given: notes-lead
        # When: its call of the writer comes back, then the reviewer's, answering more, then the
        # writer's and the reviewer's again
        # Then: it is told each next move
        for name, answer, told in (
            ("changelog-writer", "Wrote two.", REVIEWING),
            ("changelog-reviewer", "Entry 2 is wrong.\nmore", BACK),
            ("changelog-writer", "Wrote two.", REVIEWING),
            ("changelog-reviewer", "Both hold.", DONE),
        ):
            with self.subTest(name=name, answer=answer):
                self.assertEqual(self.came(name, answer), context("PostToolUse", f"notes: {told}"))

    def test_the_call_is_kept_with_its_status_and_its_answer(self):
        # Given: notes-lead
        # When: its call of the reviewer comes back answering more
        self.came("changelog-writer")
        self.came("changelog-reviewer", "more")
        # Then: the call is kept with the status and the answer
        kept = called.calls_kept({"session_id": "s1", "agent_id": "a1"})[-1]
        self.assertEqual((kept["status"], kept["answer"]), ("completed", "more"))

    def test_a_report_handed_back_is_the_answer(self):
        # Given: changelog-reviewer, the subagent b7, handing its report back with
        # SubagentHandback, its call kept as it comes back
        handed = self.came_back("SubagentHandback", {"message": "Entry 2.\nmore"}, {"ok": True})
        handed.update(agent_id="b7", agent_type="notes:changelog-reviewer")
        self.assertIsNone(self.answered(handed, "posttooluse.py", "notes:changelog-reviewer"))
        self.came("changelog-writer")
        # When: notes-lead's call of it comes back, a note in place of its report
        # Then: the report it handed back is its answer
        told = self.came("changelog-reviewer", "Handed back.", agent="b7")
        self.assertEqual(told, context("PostToolUse", f"notes: {BACK}"))

    def test_a_failed_start_is_told_the_move_again(self):
        # Given: notes-lead, no call of it kept
        # When: its call of the writer comes back failed
        # Then: it is told to start the writer
        said = context("PostToolUseFailure", f"notes: {WRITER}")
        self.assertEqual(self.back("changelog-writer", error="boom"), said)

    def test_a_start_moved_to_the_background_is_an_error_and_holds_each_later_start(self):
        # Given: notes-lead, no call of it kept
        # When: its call of the writer comes back from the background, Claude Code having moved it
        # there with no answer
        told = self.back("changelog-writer", {"status": "async_launched", "agentId": "b1"})
        # Then: it and the user are told lane cannot check the flow, and who must fix it
        line = f"notes: {UNREAD}"
        self.assertEqual(told, {"systemMessage": line, **context("PostToolUse", line)})
        # And then: each later start of a subagent the flow names is stopped with the same error,
        # as lane cannot tell which move is due; its other calls and its end go on, and it is told
        # nothing as it starts again
        for name in ("changelog-reviewer", "changelog-writer"):
            with self.subTest(name=name):
                given = {"subagent_type": f"notes:{name}", "prompt": "Go."}
                self.assertEqual(
                    self.call("Agent", given), {"systemMessage": line, **helpers.denied(line)}
                )
        self.assertIsNone(self.call("Bash", {"command": "ls"}))
        self.assertIsNone(self.answered(self.stopped("Done.", agent_type=LEAD), "subagentstop.py"))
        self.assertIsNone(self.start())

    def test_a_start_come_back_of_another_status_or_none_is_an_event_lane_cannot_read(self):
        for what, back, point in (
            (
                "another status",
                {"status": "done", "agentId": "b1"},
                (
                    '$.tool_response.status: expected one of "completed", "async_launched",'
                    ' found "done"'
                ),
            ),
            (
                "no status",
                {"agentId": "b1"},
                '$.tool_response: expected the key "status", found an object without it',
            ),
            ("nothing given back", None, "$.tool_response: expected an object, found null"),
        ):
            with self.subTest(what=what):
                # Given: notes-lead, no call of it kept
                self.record([])
                with contextlib.suppress(FileNotFoundError):
                    os.remove(called.place({"session_id": "s1", "agent_id": "a1"}) or "")
                # When: its call of the writer comes back so
                told = self.back("changelog-writer", back)
                # Then: it and the user are told the event is not as Claude Code hands it, and
                # the writer's start is still due
                line = f"notes: {UNSHAPED.format(point=point)}"
                self.assertEqual(told, {"systemMessage": line, **context("PostToolUse", line)})
                said = f"notes: {FOLLOW}\n{WRITER}"
                self.assertEqual(self.call("Bash", {"command": "ls"}), helpers.denied(said))

    def test_another_call_coming_back_is_told_nothing(self):
        for what, tool, given in (
            ("a Bash call", "Bash", {"command": "ls"}),
            ("an Agent call of a subagent no flow names", "Agent", {"subagent_type": "Explore"}),
            ("an Agent call of no subagent", "Agent", {"prompt": "x"}),
            (
                "another tool naming a subagent the flow names",
                "Bash",
                {"subagent_type": "notes:changelog-writer"},
            ),
        ):
            with self.subTest(what=what):
                # Given: notes-lead
                # When: the call comes back
                event = {**self.came_back(tool, given, {"stdout": "x"}), "agent_type": LEAD}
                # Then: nothing is told
                self.assertIsNone(self.answered(event, "posttooluse.py"))

    def test_a_call_of_a_subagent_that_is_not_the_orchestrator_is_told_nothing(self):
        # Given: changelog-writer, with lanes, starting a subagent the flow names
        given = {"subagent_type": "notes:changelog-reviewer"}
        event = self.came_back("Agent", given, {"status": "completed", "agentId": "b1"})
        # When: the call comes back
        # Then: nothing is told
        self.assertIsNone(self.answered(event, "posttooluse.py", helpers.AGENT))


class TestHeld(FlowGuardTest):
    def test_the_move_due_goes_on(self):
        # Given: notes-lead, no call of it kept
        # When: it starts the writer in the foreground
        # Then: the call goes on, nothing said
        given = {"subagent_type": "notes:changelog-writer", "prompt": "Go."}
        self.assertIsNone(self.call("Agent", given))

    def test_a_call_other_than_the_move_due_is_stopped_with_the_sentence_and_the_move(self):
        for what, tool, given in (
            ("another tool", "Bash", {"command": "ls"}),
            ("the reviewer first", "Agent", {"subagent_type": "notes:changelog-reviewer"}),
        ):
            with self.subTest(what=what):
                # Given: notes-lead, no call of it kept
                # When: it makes the call
                # Then: it is stopped, told the sentence and the move due
                said = f"notes: {FOLLOW}\n{WRITER}"
                self.assertEqual(self.call(tool, given), helpers.denied(said))

    def test_ending_while_a_move_is_due_is_kept_going_with_the_sentence_and_the_move(self):
        # Given: notes-lead, its writer's call come back
        self.came("changelog-writer")
        # When: it is about to end
        answer = self.answered(self.stopped("Done.", agent_type=LEAD), "subagentstop.py")
        # Then: it is kept going, told the sentence and the reviewer's start
        self.assertEqual(answer, {"decision": "block", "reason": f"notes: {FOLLOW}\n{REVIEWING}"})

    def test_once_the_flow_is_done_it_ends_free(self):
        # Given: notes-lead, the writer's and the reviewer's calls come back
        self.came("changelog-writer")
        self.came("changelog-reviewer", "Both hold.")
        # When: it is about to end
        # Then: it ends, nothing said
        self.assertIsNone(self.answered(self.stopped("Done.", agent_type=LEAD), "subagentstop.py"))


if __name__ == "__main__":
    unittest.main()
