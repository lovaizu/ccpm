"""The guard on a flow: the orchestrator's call running lane's flow.py as a command of its own let
through with the run's IDs put before it, one running it together with other commands stopped with
the flow's sentence and how to run it, any lane's stop winning; and each `from` subagent's answer
kept as it ends, by its ID."""

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
from flowing import FLOW, FOLLOW, LAID, LEAD_LAID, REVIEWER
from helpers import called
from test_guard import GuardTest

LEAD = "notes:notes-lead"
REVIEWING = "notes:changelog-reviewer"
# What the orchestrator is told where it runs flow.py together with other commands.
ALONE = f"notes: {FOLLOW}\nRun `flow.py` as a command of its own."


class FlowGuardTest(GuardTest):
    """The guard in the plugin `notes` with the README's flow laid, notes-lead the orchestrator
    a1 of the session s1, its record holding its prompt alone."""

    def setUp(self) -> None:
        super().setUp()
        self.write(self.agent_file, helpers.LAID)
        self.write(os.path.join(self.plugin, "agents", "notes-lead.md"), LEAD_LAID)
        self.write(os.path.join(self.plugin, "agents", "changelog-reviewer.md"), REVIEWER)
        self.write_json(os.path.join(self.plugin, "hooks", "lanes.json"), LAID)
        self.script = os.path.join(self.plugin, "hooks", "lane", "flow.py")
        self.record([])

    def ran(self, command: str, agent: str = LEAD, **given: object) -> dict | None:
        """What the guard answers on a Bash call of the command in the subagent, with the other
        fields of the input given: the answer whole, read as JSON, or None for none."""
        event = self.called("Bash", {"command": command, **given}, agent)
        return self.answered(json.dumps(event), (agent,))

    def answered(self, stream: str, words: tuple, entry: str = "pretooluse.py") -> dict | None:
        """The guard's answer on the stream, run as Claude Code runs the entry, in this process so
        that the coverage counts it, read as JSON; None where it answers nothing."""
        script = os.path.join(helpers.CODE, entry)
        argv = mock.patch.object(sys, "argv", [script, *words])
        stdin = mock.patch.object(sys, "stdin", io.StringIO(stream))
        root = mock.patch.dict(os.environ, {"CLAUDE_PLUGIN_ROOT": self.plugin})
        out = io.StringIO()
        with argv, stdin, root, contextlib.redirect_stdout(out):
            runpy.run_path(script, run_name="__main__")
        return json.loads(out.getvalue()) if out.getvalue() else None


def allowed(given: dict) -> dict:
    """The answer letting a tool call through with the input given in place of the AI's, as
    Claude Code reads it at PreToolUse."""
    output = {"hookEventName": "PreToolUse", "permissionDecision": "allow"}
    return {"hookSpecificOutput": {**output, "updatedInput": given}}


class TestRunAlone(FlowGuardTest):
    def test_flow_py_run_alone_goes_on_with_the_runs_ids_before_it(self):
        for what, command in (
            ("by python3 and its path", f'python3 "{self.script}"'),
            ("by its path", self.script),
            ("by a path from the folder it runs in", "python3 notes/hooks/lane/flow.py"),
        ):
            with self.subTest(what=what):
                # Given: notes-lead, the flow's orchestrator
                # When: it runs lane's flow.py as a command of its own, with a description
                # Then: the call goes on, the command with the session's and its own ID before
                # it, the rest of its input as given
                given = {"command": f"LANE_SESSION=s1 LANE_AGENT=a1 {command}", "description": "d"}
                self.assertEqual(self.ran(command, description="d"), allowed(given))

    def test_the_file_of_its_calls_is_made_as_it_goes_on(self):
        # Given: notes-lead, no call of it kept yet
        # When: it runs flow.py as a command of its own
        self.ran(f'python3 "{self.script}"')
        # Then: the file the guard keeps its calls in is there, empty
        place = called.place({"session_id": "s1", "agent_id": "a1"})
        self.assertEqual(self.read(str(place)), "")

    def test_flow_py_run_with_other_commands_is_stopped_saying_to_run_it_alone(self):
        script = f'python3 "{self.script}"'
        for what, command in (
            ("after a cd", f"cd {self.plugin} && {script}"),
            ("piped", f"{script} | cat"),
            ("its output written", f"{script} > out.txt"),
            ("after an assignment", f"LANE_SESSION=s2 {script}"),
            ("with an argument", f"{script} next"),
            ("after another command", f"ls; {script}"),
        ):
            with self.subTest(what=what):
                # Given: notes-lead, the flow's orchestrator
                # When: it runs lane's flow.py together with other commands or words
                # Then: the call is stopped, and it is told the flow's sentence and to run flow.py
                # alone
                self.assertEqual(self.ran(command), helpers.denied(ALONE))

    def test_another_script_named_flow_py_goes_on_unchanged(self):
        for what, command in (
            ("of another folder", "python3 /p/hooks/lane/flow.py"),
            ("of no path the words settle", 'python3 "$P/hooks/lane/flow.py"'),
            ("no command", ""),
        ):
            with self.subTest(what=what):
                # Given: notes-lead, the flow's orchestrator
                # When: it runs a script named flow.py that is not lane's in the plugin, or none
                # Then: the call goes on, as it is, nothing said
                self.assertIsNone(self.ran(command))

    def test_a_lanes_stop_wins_over_letting_flow_py_through(self):
        # Given: notes-lead holding beside the flow hands_off on step 2, taking flow.py's path
        laid = json.loads(json.dumps(LAID))
        laid["subagents"][0]["steps"].append(
            {"step": 2, "lanes": [{"lane": "hands_off", "takes": ["hooks/lane/flow.py"]}]}
        )
        self.write_json(os.path.join(self.plugin, "hooks", "lanes.json"), laid)
        lead = os.path.join(self.plugin, "agents", "notes-lead.md")
        said = "Do not run `hooks/lane/flow.py`."
        self.write(lead, LEAD_LAID.replace("entries.\n", f"entries. {said}\n"))
        for what, command, told in (
            ("alone", f'python3 "{self.script}"', f"notes: {said}"),
            ("with others", f'ls && python3 "{self.script}"', f"notes: {said}\n{ALONE}"),
        ):
            with self.subTest(what=what):
                # When: it runs flow.py
                # Then: the call is stopped with the lane's sentence, and not let through
                self.assertEqual(self.ran(command), helpers.denied(told))

    def test_flow_py_run_by_another_subagent_goes_on_unchanged(self):
        # Given: changelog-writer and summarizer, subagents with lanes but not the orchestrator,
        # one named before it in order and one after
        summarizer = helpers.LAID.replace("name: changelog-writer", "name: summarizer")
        self.write(os.path.join(self.plugin, "agents", "summarizer.md"), summarizer)
        laid = json.loads(json.dumps(LAID))
        laid["subagents"].append({**laid["subagents"][1], "name": "summarizer"})
        self.write_json(os.path.join(self.plugin, "hooks", "lanes.json"), laid)
        for agent in (helpers.AGENT, "notes:summarizer"):
            with self.subTest(agent=agent):
                # When: it runs flow.py
                # Then: the call goes on as it is, nothing said
                self.assertIsNone(self.ran(f'python3 "{self.script}"', agent))

    def test_an_event_naming_its_subagent_by_no_id_goes_on_unchanged(self):
        # Given: notes-lead's call in an event naming it by no ID as Claude Code gives it
        event = self.called("Bash", {"command": self.script}, LEAD)
        event["agent_id"] = "a 1"
        record = os.path.join(self.base, "session", "subagents", "agent-a 1.jsonl")
        self.write(record, helpers.recorded(self.base, []))
        # When: the guard runs on it
        # Then: the call goes on as it is, nothing said
        self.assertIsNone(self.answered(json.dumps(event), (LEAD,)))

    def test_another_tool_of_the_orchestrator_is_held_to_its_lanes_alone(self):
        # A tool named before Bash in order, and one after.
        for tool in ("Agent", "Read"):
            with self.subTest(tool=tool):
                # Given: notes-lead, the flow's orchestrator, flow.py not yet run
                # When: it calls the tool with an input whose command runs flow.py
                given = {"command": f'python3 "{self.script}"', "file_path": self.script}
                event = self.called(tool, given, LEAD)
                # Then: it goes on as it is, nothing said
                self.assertIsNone(self.answered(json.dumps(event), (LEAD,)))


class TestAnswerKept(FlowGuardTest):
    def ended(self, agent: str, reply: str | None) -> dict | None:
        """What the guard answers as the subagent of the type, the subagent a1, ends with the
        reply, None for none, as Claude Code gives it once the subagent has handed its report
        back."""
        event = {**self.stopped(agent_type=agent), "last_assistant_message": reply}
        return self.answered(json.dumps(event), (agent,), "subagentstop.py")

    def test_a_from_with_no_lanes_has_its_answer_kept_as_it_ends(self):
        # Given: changelog-reviewer, the from of the flow's back, with no lanes
        # When: it ends with its answer
        # Then: it ends, nothing said, and its answer is kept by its ID
        self.assertIsNone(self.ended(REVIEWING, "more"))
        self.assertEqual(called.answer("s1", "a1"), "more")

    def test_a_from_with_lanes_has_its_answer_kept_and_its_lanes_held(self):
        # Given: a flow whose back is from changelog-writer, which lays test_after
        flow = {**FLOW, "order": ["changelog-reviewer", "changelog-writer"]}
        flow["back"] = [{"from": "changelog-writer", "to": "changelog-reviewer", "while": "x"}]
        self.lay((3, "test_after", ["CHANGELOG.md", "python3 check.py"]))
        laid = json.loads(self.read(os.path.join(self.plugin, "hooks", "lanes.json")))
        self.write_json(os.path.join(self.plugin, "hooks", "lanes.json"), {**laid, "flow": flow})
        self.record([helpers.writing("CHANGELOG.md")])
        # When: it ends with its answer, its change not tested
        answer = self.ended(helpers.AGENT, "Wrote it.")
        # Then: its answer is kept, and it is kept going with the lane's sentence
        self.assertEqual(called.answer("s1", "a1"), "Wrote it.")
        self.assertEqual((answer or {}).get("decision"), "block")

    def test_a_subagent_that_is_no_from_keeps_no_answer(self):
        # Given: notes-lead, which is no from
        # When: it ends with nothing due
        self.ended(LEAD, "Done.")
        # Then: no answer is kept
        self.assertIsNone(called.answer("s1", "a1"))

    def test_a_subagent_neither_laid_in_nor_a_from_is_an_error(self):
        # Given: a flow with no back, so changelog-reviewer is neither laid in nor a from
        self.write_json(
            os.path.join(self.plugin, "hooks", "lanes.json"), {**LAID, "flow": {**FLOW, "back": []}}
        )
        # When: it ends
        answer = self.ended(REVIEWING, "more")
        # Then: it is an error saying hooks/lanes.json lays no lanes in it, no answer kept
        self.assertIn(
            "hooks/lanes.json lays no lanes in changelog-reviewer", (answer or {}).get("reason", "")
        )
        self.assertIsNone(called.answer("s1", "a1"))

    def test_a_from_handing_its_report_back_has_the_message_kept(self):
        # Given: changelog-reviewer's call of SubagentHandback coming back
        event = self.came_back("SubagentHandback", {"message": "more"}, {"ok": True})
        event["agent_type"] = REVIEWING
        # When: the entry of a call coming back runs on it, then it ends with no reply
        self.assertIsNone(self.answered(json.dumps(event), (REVIEWING,), "posttooluse.py"))
        self.ended(REVIEWING, None)
        # Then: its answer is the message
        self.assertEqual(called.answer("s1", "a1"), "more")


if __name__ == "__main__":
    unittest.main()
