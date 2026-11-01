"""flow.py, run by the orchestrator as the guard lets it through with the run's IDs: the next move
of the flow its plugin's hooks/lanes.json lays, printed by the subagent of the flow the orchestrator
started last and the answer of a `from` subagent, as the guard kept them; where it cannot tell the
run, what is wrong on stderr, exiting 1."""

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
from flowing import FLOW, LAID
from helpers import called

# The script as the orchestrator runs it, in the plugin's hooks/lane/.
FLOW_PY = os.path.join("hooks", "lane", "flow.py")
# The run's IDs, as the guard puts them before the command: the session's and the orchestrator's.
IDS = {"LANE_SESSION": "s1", "LANE_AGENT": "a1"}
# What the orchestrator is told to do where flow.py cannot tell the run, by who must fix it: ask
# for the fix and end, as a failed run frees its end.
LAY_AGAIN = (
    "Ask the main conversation for the fix: the maker of notes must lay its lanes again with"
    " `lay.py write`, so they match its steps. End your work with this line.\n"
)
CLAUDE_CODE = (
    "Ask the main conversation for the fix: Claude Code must be updated with `claude update`, and"
    " where this goes on, it must be reported at https://github.com/lovaizu/ccpm/issues. End your"
    " work with this line.\n"
)


def move(name: str) -> str:
    """The line of the move starting the subagent of the name, as follow_next reads it."""
    return json.dumps({"tool": "Agent", "input": {"subagent_type": f"notes:{name}"}}) + "\n"


class FlowTest(helpers.PluginTest):
    """flow.py in the plugin `notes`, its hooks/lane/ a link to lane's code as in a plugin of the
    ccpm marketplace, its hooks/lanes.json the README's flow, the orchestrator a1 of the session
    s1."""

    def setUp(self) -> None:
        super().setUp()
        os.makedirs(os.path.join(self.plugin, "hooks"))
        os.symlink(helpers.CODE, os.path.join(self.plugin, "hooks", "lane"))
        self.laid(LAID)
        self.started_ids = 0

    def laid(self, laid: object) -> None:
        """Writes the plugin's hooks/lanes.json, holding the JSON given."""
        self.write_json(os.path.join(self.plugin, "hooks", "lanes.json"), laid)

    def start(self, name: str, back: object = "", tool: str = "Agent") -> str:
        """Keeps, as the guard keeps it coming back, the orchestrator's call starting the subagent
        of the name, given back an ID of its own, `b<n>`, n counting the starts, or what is given;
        gives that ID."""
        self.started_ids += 1
        agent = f"b{self.started_ids}"
        given = {"subagent_type": name, "description": "d", "prompt": "Do it."}
        back = {"status": "completed", "agentId": agent} if back == "" else back
        event = self.came_back(tool, given, back)
        called.Kept(self.plugin, "notes:notes-lead").check(event)
        return agent

    def failed_start(self, name: str) -> None:
        """Keeps the orchestrator's call starting the subagent, come back failed."""
        given = {"subagent_type": name, "prompt": "Do it."}
        event = self.came_back("Agent", given, error="Agent type not found")
        called.Kept(self.plugin, "notes:notes-lead").check(event)

    def answered(self, agent: str, reply: str) -> None:
        """Keeps the answer of the subagent of the ID, as the guard keeps it as it ends."""
        called.ended({**self.stopped(reply), "agent_id": agent})

    def flow(self, environ: dict | None = None, script: str | None = None) -> tuple:
        """flow.py run by the path in the plugin, or the one given, with the run's IDs or the
        environment given: what it exits with, prints and prints on stderr."""
        out, err = io.StringIO(), io.StringIO()
        path = os.path.join(self.plugin, FLOW_PY) if script is None else script
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = helpers.flow.main(path, IDS if environ is None else environ)
        return code, out.getvalue(), err.getvalue()


class TestMoves(FlowTest):
    def test_with_no_subagent_of_the_flow_started_the_first_is_started(self):
        for what, starts in (
            ("nothing kept", lambda: None),
            ("another call kept", lambda: self.start("notes:other")),
            ("a subagent of another plugin", lambda: self.start("other:changelog-writer")),
            ("a call of another tool", lambda: self.start("notes:changelog-writer", tool="Task")),
            ("a start come back failed", lambda: self.failed_start("notes:changelog-writer")),
        ):
            with self.subTest(what=what):
                # Given: no start of a subagent of the flow kept of the orchestrator, as the guard
                # makes the file of its calls before it runs flow.py
                place = called.place({"session_id": "s1", "agent_id": "a1"})
                self.write(str(place), "")
                starts()
                # When: flow.py is run
                # Then: it prints the line and the move starting the first of the order
                self.assertEqual(
                    self.flow(), (0, "Start `changelog-writer`.\n" + move("changelog-writer"), "")
                )

    def test_the_next_of_the_order_is_started(self):
        # Given: changelog-writer started last
        self.start("notes:changelog-writer")
        # When: flow.py is run
        # Then: it prints the line and the move starting changelog-reviewer
        self.assertEqual(
            self.flow(), (0, "Start `changelog-reviewer`.\n" + move("changelog-reviewer"), "")
        )

    def test_a_from_not_yet_answered_has_no_move(self):
        # Given: changelog-reviewer started last, its answer not kept, as when it runs in the
        # background
        self.start("notes:changelog-writer")
        self.start("notes:changelog-reviewer")
        # When: flow.py is run
        # Then: it prints that the reviewer has not answered yet, and no move
        said = (
            "changelog-reviewer has not answered yet. Run `flow.py` again once its answer has"
            " come.\n"
        )
        self.assertEqual(self.flow(), (0, said, ""))

    def test_a_from_answering_its_while_on_a_line_of_its_own_sends_the_work_back(self):
        for what, answer in (
            ("alone", "more"),
            ("in bold", "**more**"),
            ("in code", "`more`"),
            ("in italics", "_more_"),
            ("between blanks", " \tmore  "),
            ("on a line among others", "Entry 2 misses a fix.\n\nmore\n"),
        ):
            with self.subTest(what=what):
                # Given: changelog-reviewer started last, answering `more` on a line of its own
                self.start("notes:changelog-writer")
                self.answered(self.start("notes:changelog-reviewer"), answer)
                # When: flow.py is run
                # Then: it prints the answer and the move starting changelog-writer again
                said = "changelog-reviewer answered `more`: start `changelog-writer` again.\n"
                self.assertEqual(self.flow(), (0, said + move("changelog-writer"), ""))

    def test_a_from_answering_anything_else_lets_the_flow_go_on(self):
        for what, answer in (
            ("the while in a sentence", "No more entries need the writer."),
            ("the while with a full stop", "more."),
            ("the while in another case", "More"),
            ("a mark inside it", "mo*re"),
            ("nothing", ""),
        ):
            with self.subTest(what=what):
                # Given: changelog-reviewer, the last of the order, started last, answering
                # something other than `more` on a line of its own
                self.start("notes:changelog-writer")
                self.answered(self.start("notes:changelog-reviewer"), answer)
                # When: flow.py is run
                # Then: it prints that the flow is done, and no move
                self.assertEqual(self.flow(), (0, "The flow is done.\n", ""))

    def test_the_answer_of_the_last_start_alone_is_read(self):
        # Given: changelog-reviewer answering `more`, the writer started again, then the reviewer
        # again, not yet answered
        self.start("notes:changelog-writer")
        self.answered(self.start("notes:changelog-reviewer"), "more")
        self.start("notes:changelog-writer")
        self.start("notes:changelog-reviewer")
        # When: flow.py is run
        # Then: the reviewer has not answered yet, its answer before being of another start
        self.assertTrue(self.flow()[1].startswith("changelog-reviewer has not answered yet."))

    def test_a_from_before_the_last_of_the_order_answering_else_starts_the_next(self):
        # Given: a flow of three, the second the from of a back, started last, answering else
        flow = {
            **FLOW,
            "order": ["changelog-writer", "changelog-reviewer", "summarizer"],
        }
        self.laid({**LAID, "flow": flow})
        self.answered(self.start("notes:changelog-reviewer"), "fine")
        # When: flow.py is run
        # Then: it prints the move starting the third
        self.assertEqual(self.flow(), (0, "Start `summarizer`.\n" + move("summarizer"), ""))

    def test_a_subagent_that_is_no_from_before_a_from_named_after_it_starts_the_next(self):
        # Given: a flow of three whose back is from the third, named after the first in order, and
        # the first started last
        flow = {
            **FLOW,
            "order": ["changelog-writer", "changelog-reviewer", "summarizer"],
            "back": [{"from": "summarizer", "to": "changelog-writer", "while": "more"}],
        }
        self.laid({**LAID, "flow": flow})
        self.start("notes:changelog-writer")
        # When: flow.py is run
        # Then: it prints the move starting the second
        self.assertEqual(
            self.flow(), (0, "Start `changelog-reviewer`.\n" + move("changelog-reviewer"), "")
        )

    def test_a_subagent_that_is_no_from_is_followed_by_the_next_whatever_it_answered(self):
        # Given: changelog-writer, the from of no back, started last, its reply kept as `more`
        self.answered(self.start("notes:changelog-writer"), "more")
        # When: flow.py is run
        # Then: it prints the move starting the next
        self.assertTrue(self.flow()[1].startswith("Start `changelog-reviewer`."))

    def test_the_last_of_the_order_with_no_back_ends_the_flow(self):
        # Given: a flow with no back, its last started
        self.laid({**LAID, "flow": {**FLOW, "back": []}})
        self.start("notes:changelog-writer")
        self.start("notes:changelog-reviewer")
        # When: flow.py is run
        # Then: it prints that the flow is done
        self.assertEqual(self.flow(), (0, "The flow is done.\n", ""))

    def test_hooks_lanes_json_is_found_by_the_path_flow_py_is_run_by(self):
        # Given: the plugin's hooks/lane/ a link to lane's code, beside which lane has no flow
        self.start("notes:changelog-writer")
        # When: flow.py is run by its path in the plugin
        # Then: it reads the plugin's flow, not one beside lane's code
        self.assertEqual(
            self.flow()[:2], (0, "Start `changelog-reviewer`.\n" + move("changelog-reviewer"))
        )
        self.assertFalse(os.path.exists(os.path.join(helpers.LANE, "hooks", "lanes.json")))


class TestCannotTell(FlowTest):
    def test_without_the_runs_ids_it_stops(self):
        for what, environ in (
            ("none", {}),
            ("no session", {"LANE_AGENT": "a1"}),
            ("no orchestrator", {"LANE_SESSION": "s1"}),
            ("a session of no ID", {**IDS, "LANE_SESSION": "../s1"}),
            ("an orchestrator of no ID", {**IDS, "LANE_AGENT": "a 1"}),
        ):
            with self.subTest(what=what):
                # Given: flow.py run without the IDs the guard puts before it, or of no ID
                # When: it is run
                # Then: it exits 1, printing on stderr that the guard gave it no run
                said = (
                    "notes: lane cannot check the flow of notes-lead: it was run without the"
                    " session's and the orchestrator's IDs, which the guard puts before flow.py"
                    " run as a command of its own. " + LAY_AGAIN
                )
                self.assertEqual(self.flow(environ), (1, "", said))

    def test_with_no_calls_kept_it_stops(self):
        # Given: no file of the orchestrator's calls kept
        # When: flow.py is run
        # Then: it exits 1, printing on stderr that the calls kept are not found
        said = (
            "notes: lane cannot check the flow of notes-lead: the calls the guard kept of it are"
            " not found. " + CLAUDE_CODE
        )
        self.assertEqual(self.flow(), (1, "", said))

    def test_a_from_started_with_no_id_kept_stops(self):
        # Given: changelog-reviewer started last, its call kept with no ID of the subagent
        self.start("notes:changelog-reviewer", {"status": "completed"})
        # When: flow.py is run
        # Then: it exits 1, printing on stderr that its ID was not kept
        said = (
            "notes: lane cannot check the flow of notes-lead: the start of changelog-reviewer was"
            " kept with no ID of the subagent. " + CLAUDE_CODE
        )
        self.assertEqual(self.flow(), (1, "", said))

    def test_hooks_lanes_json_with_no_flow_or_out_of_its_form_stops(self):
        for what, laid, wrong in (
            ("no flow", {"subagents": []}, "hooks/lanes.json holds no flow"),
            ("no JSON", "{", "hooks/lanes.json holds no JSON"),
            ("not there", None, "hooks/lanes.json is not there"),
            ("a flow out of its form", {"flow": {}, "subagents": []}, "hooks/lanes.json is out of"),
        ):
            with self.subTest(what=what):
                # Given: hooks/lanes.json so
                path = os.path.join(self.plugin, "hooks", "lanes.json")
                if os.path.exists(path):
                    os.remove(path)
                if laid is not None:
                    self.write(path, laid if isinstance(laid, str) else json.dumps(laid))
                # When: flow.py is run
                code, out, err = self.flow()
                # Then: it exits 1, printing on stderr what is wrong, no orchestrator being known
                self.assertEqual((code, out), (1, ""))
                self.assertTrue(
                    err.startswith(f"notes: lane cannot check the flow of this plugin: {wrong}"),
                    err,
                )
                self.assertTrue(err.endswith(LAY_AGAIN), err)

    def test_a_plugin_whose_manifest_names_no_plugin_stops(self):
        for what, manifest in (("none", None), ("no name", "{}"), ("no JSON", "{")):
            with self.subTest(what=what):
                # Given: the plugin's manifest so
                path = os.path.join(self.plugin, ".claude-plugin", "plugin.json")
                if os.path.exists(path):
                    os.remove(path)
                if manifest is not None:
                    self.write(path, manifest)
                # When: flow.py is run
                code, out, err = self.flow()
                # Then: it exits 1, headed by lane, as the plugin is not known
                self.assertEqual((code, out), (1, ""))
                self.assertEqual(
                    err,
                    "lane: lane cannot check the flow of this plugin: its"
                    " .claude-plugin/plugin.json names no plugin. Ask the main conversation for"
                    " the fix: the plugin's maker must fix it. End your work with this line.\n",
                )


class TestMain(FlowTest):
    def test_run_as_the_orchestrator_runs_it_it_prints_the_move(self):
        # Given: flow.py run as a script by its path in the plugin, with the run's IDs, in this
        # process so that the coverage counts it
        place = called.place({"session_id": "s1", "agent_id": "a1"})
        self.write(str(place), "")
        script = os.path.join(self.plugin, FLOW_PY)
        argv = mock.patch.object(sys, "argv", [script])
        environ = mock.patch.dict(os.environ, IDS)
        out = io.StringIO()
        # When: it is run
        with argv, environ, contextlib.redirect_stdout(out), self.assertRaises(SystemExit) as done:
            runpy.run_path(script, run_name="__main__")
        # Then: it exits 0, printing the first move
        expected = "Start `changelog-writer`.\n" + move("changelog-writer")
        self.assertEqual((done.exception.code, out.getvalue()), (0, expected))


if __name__ == "__main__":
    unittest.main()
