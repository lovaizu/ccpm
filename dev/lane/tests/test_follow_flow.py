"""follow_flow, the flow's lane: the move due read from the flow and the orchestrator's calls kept,
each start of a subagent of the flow counted once that subagent has ended, in the foreground or the
background, the answer of a `from` sending the work back; the line telling the move, or to wait for
the subagent running; and a call other than the move, or the end, while a move is due, a drift told
that line, and a start of the flow while a subagent of it runs, a drift told to wait."""

from __future__ import annotations

import unittest

import helpers
from flowing import FLOW
from helpers import NO_PLUGIN, call, follow_flow, moves

# The lines telling each move of the README's flow, as the orchestrator is told them, each move by
# its position in the order.
WRITER = "The next move of the flow is move 1: start `notes:changelog-writer`."
REVIEWER = "The next move of the flow is move 2: start `notes:changelog-reviewer`."
BACK = f"changelog-reviewer answered `more`. {WRITER}"
# The line telling the writer's start at position 3 of an order naming it twice.
WRITER_AGAIN = "The next move of the flow is move 3: start `notes:changelog-writer`."
# The line telling the orchestrator to wait while the writer it started runs in the background.
WAIT = "Wait for `notes:changelog-writer` to end: lane tells the next move once it has."
DONE = "The flow is done: lane tells no more moves."


def started(name: str, answer: str = "", status: str = "completed", **given: object) -> dict:
    """An Agent call of the orchestrator kept as it came back, starting the subagent of the name in
    the plugin `notes`, with the input's other fields given, giving back the status, the ID of the
    subagent it started and the answer."""
    agent = {"subagent_type": f"notes:{name}", "prompt": "Go.", **given}
    back = {"status": status, "agent": "b1", "answer": answer}
    return {"tool": "Agent", "input": agent, "failed": False, **back}


def background(name: str, answer: str | None = None) -> dict:
    """An Agent call of the orchestrator kept as it came back from the background, starting the
    subagent of the name in `notes`, as called.py gives it with what that subagent ended with: the
    answer, or None while it runs."""
    kept = started(name, status="async_launched")
    return {**kept, "ended": answer is not None, "answer": answer or ""}


def run(*kept: dict, flow: dict = FLOW) -> moves.Run:
    """The run of the flow in the plugin `notes`, the orchestrator's calls kept."""
    return moves.Run(flow, "notes", list(kept))


def agent(name: str, **given: object) -> call.Call:
    """The orchestrator's Agent call starting the subagent of the name in `notes`."""
    return helpers.acted("Agent", {"subagent_type": f"notes:{name}", "prompt": "Go.", **given})


class TestDue(unittest.TestCase):
    def test_each_move_of_the_flow_is_told_from_the_calls_kept(self):
        writer, reviewer = started("changelog-writer"), started("changelog-reviewer")
        for what, kept, told in (
            ("no call kept", [], WRITER),
            ("the writer come back", [writer], REVIEWER),
            ("the reviewer come back answering no more", [writer, reviewer], DONE),
            (
                "the reviewer come back answering more",
                [writer, started("changelog-reviewer", "Entry 2 is wrong.\nmore")],
                BACK,
            ),
            (
                "the writer come back again after more",
                [writer, started("changelog-reviewer", "more"), writer],
                REVIEWER,
            ),
        ):
            with self.subTest(what=what):
                # Given: the orchestrator's calls kept so
                # When: the move due is told
                # Then: it is the move the flow and the answers call for
                self.assertEqual(moves.told(run(*kept)), told)

    def test_a_call_that_is_not_the_move_due_changes_nothing(self):
        for what, other in (
            ("the subagent after the one due", started("changelog-reviewer")),
            ("a subagent of another plugin", {**started("x"), "input": {"subagent_type": "a:x"}}),
            ("an Agent call that failed", {**started("changelog-writer"), "failed": True}),
            (
                "an Agent call come back of another status",
                started("changelog-writer", status="done"),
            ),
            (
                "an Agent call come back with no subagent's ID",
                {**started("changelog-writer"), "agent": None},
            ),
            ("another tool", {"tool": "Bash", "input": {"command": "ls"}, "failed": False}),
        ):
            with self.subTest(what=what):
                # Given: the orchestrator's calls kept of such a call alone
                # When: the move due is told
                # Then: it is still the first
                self.assertEqual(moves.told(run(other)), WRITER)

    def test_a_call_that_is_not_the_move_kept_before_it_changes_nothing(self):
        for what, other in (
            ("another tool", {"tool": "Bash", "input": {"command": "ls"}, "failed": False}),
            ("the subagent after the one due", started("changelog-reviewer")),
            ("a start come back of another status", started("changelog-writer", status="done")),
        ):
            with self.subTest(what=what):
                # Given: the call kept, then the writer's
                kept = [other, started("changelog-writer")]
                # When: the move due is told
                # Then: it is the reviewer's start
                self.assertEqual(moves.told(run(*kept)), REVIEWER)

    def test_a_start_of_the_subagent_before_the_one_due_changes_nothing(self):
        # Given: the writer come back, then come back again while the reviewer's start is due
        writer = started("changelog-writer")
        # When: the move due is told
        # Then: it is still the reviewer's start
        self.assertEqual(moves.told(run(writer, writer)), REVIEWER)

    def test_a_back_goes_to_the_position_it_names(self):
        # Given: an order of three, the third sending the work back to the second while it
        # answers more
        flow = {
            **FLOW,
            "order": ["changelog-writer", "changelog-reviewer", "summarizer"],
            "back": [{"from": 3, "to": 2, "while": "more"}],
        }
        kept = [
            started("changelog-writer"),
            started("changelog-reviewer"),
            started("summarizer", "more"),
        ]
        # When: the move due is told
        # Then: it is the reviewer's start again
        said = f"summarizer answered `more`. {REVIEWER}"
        self.assertEqual(moves.told(run(*kept, flow=flow)), said)

    def test_a_start_in_the_background_counts_once_its_subagent_has_ended(self):
        for what, kept, told in (
            ("the writer ended", [background("changelog-writer", "Wrote two.")], REVIEWER),
            (
                "the reviewer ended answering more",
                [background("changelog-writer", ""), background("changelog-reviewer", "more")],
                BACK,
            ),
        ):
            with self.subTest(what=what):
                # Given: the orchestrator's starts come back from the background, each subagent
                # since ended with its answer
                # When: the move due is told
                # Then: it is the move the flow and the answers call for, as in the foreground
                self.assertEqual(moves.told(run(*kept)), told)

    def test_a_start_in_the_background_still_running_leaves_the_orchestrator_waiting(self):
        # Given: the writer's start come back from the background, the writer still running
        kept = background("changelog-writer")
        # When: the move due is read and told
        # Then: no move is due, the writer running, and the orchestrator is told to wait for it
        self.assertEqual(moves.due(run(kept)), moves.Due(None, "", "notes:changelog-writer"))
        self.assertEqual(moves.told(run(kept)), WAIT)

    def test_a_subagent_named_twice_in_the_order_is_told_by_its_position(self):
        # Given: an order of the writer, the reviewer, the writer again and the reviewer again, the
        # second reviewer sending the work back to the third position
        flow = {
            **FLOW,
            "order": [
                "changelog-writer",
                "changelog-reviewer",
                "changelog-writer",
                "changelog-reviewer",
            ],
            "back": [{"from": 4, "to": 3, "while": "more"}],
        }
        writer, reviewer = started("changelog-writer"), started("changelog-reviewer", "more")
        for what, kept, told in (
            (
                "the first reviewer answering more, which sends nothing back",
                [writer, reviewer],
                WRITER_AGAIN,
            ),
            (
                "the second reviewer answering more",
                [writer, reviewer, writer, reviewer],
                f"changelog-reviewer answered `more`. {WRITER_AGAIN}",
            ),
            (
                "the second reviewer done",
                [writer, reviewer, writer, started("changelog-reviewer")],
                DONE,
            ),
        ):
            with self.subTest(what=what):
                # When: the move due is told
                # Then: it is the move of the position reached
                self.assertEqual(moves.told(run(*kept, flow=flow)), told)


class TestReached(unittest.TestCase):
    def test_the_move_due_reached_the_orchestrator_where_told_since_the_last_start(self):
        writer = background("changelog-writer", "Wrote two.")
        for what, kept, said, reached in (
            ("no start yet, told as it started", [], [], True),
            (
                "the last start come back from the foreground",
                [started("changelog-writer")],
                [],
                True,
            ),
            (
                "the last start failed, told as it came back",
                [{**started("changelog-writer"), "failed": True}],
                [],
                True,
            ),
            ("the last start in the background, nothing told since", [writer], [], False),
            ("told the wait alone since", [writer], ["notes: Wait for it."], False),
            ("told the move since", [writer], [f"[x]: notes: Take each move.\n{REVIEWER}"], True),
            (
                "the last start come back of another status",
                [started("changelog-writer", status="done")],
                [],
                False,
            ),
        ):
            with self.subTest(what=what):
                # Given: the orchestrator's calls kept so, and what hooks told it since the last
                # start came back
                # When: whether the move due reached it is read
                # Then: it did where the start's own coming back or a hook since told it
                self.assertEqual(moves.reached(run(*kept), said), reached)

    def test_the_last_start_is_the_last_agent_call_of_the_flow_kept(self):
        # Given: the writer's start, the reviewer's, then a Bash call, a start of another plugin's
        # subagent, and calls of a tool no plugin has, Act, and of Bash, naming the writer
        other = {**started("x"), "input": {"subagent_type": "a:x"}}
        bash = {"tool": "Bash", "input": {"command": "ls"}, "failed": False}
        named = {"subagent_type": "notes:changelog-writer"}
        act = {"tool": "Act", "input": named, "failed": False}
        bash_named = {**bash, "input": named}
        writer = {**started("changelog-writer"), "id": "toolu_w"}
        reviewer = {**started("changelog-reviewer"), "id": "toolu_r"}
        # When: the last start is read
        # Then: it is the reviewer's
        kept = run(writer, reviewer, bash, other, act, bash_named)
        self.assertEqual(moves.last_start(kept), reviewer)
        self.assertIsNone(moves.last_start(run(bash)))


class TestAnswers(unittest.TestCase):
    def test_a_line_of_the_answer_that_is_the_while_answers_it(self):
        for answer in ("more", "Two entries.\nmore", "  **more**  ", "`more`", "_more_\nDone."):
            with self.subTest(answer=answer):
                # Given: an answer holding the while on a line of its own, in marks or not
                # When: it is read
                # Then: it answers the while
                self.assertTrue(moves.answers(answer, "more"))

    def test_the_while_within_a_line_or_in_another_case_does_not_answer_it(self):
        for answer in ("No more entries need the writer.", "More", "mores", "", "more."):
            with self.subTest(answer=answer):
                # Given: an answer holding no line that is the while
                # When: it is read
                # Then: it does not answer it
                self.assertFalse(moves.answers(answer, "more"))


class TestDrift(unittest.TestCase):
    def test_the_move_due_is_no_drift(self):
        for what, kept, made in (
            ("the first move", [], agent("changelog-writer")),
            ("the next move", [started("changelog-writer")], agent("changelog-reviewer")),
            ("in the foreground", [], agent("changelog-writer", run_in_background=False)),
            ("in the background", [], agent("changelog-writer", run_in_background=True)),
        ):
            with self.subTest(what=what):
                # Given: the calls kept so
                # When: the orchestrator makes the call of the move due
                # Then: it is no drift
                self.assertEqual(follow_flow.drifts(made, [], NO_PLUGIN, run(*kept)), "")

    def test_a_call_other_than_the_move_due_drifts_telling_the_move(self):
        for what, made in (
            ("another subagent", agent("changelog-reviewer")),
            ("another tool", helpers.acted("Bash", {"command": "ls"})),
            # A tool named before Agent in order, and one after, naming the subagent due.
            ("a tool before", helpers.acted("Act", {"subagent_type": "notes:changelog-writer"})),
            ("a tool after", helpers.acted("Bash", {"subagent_type": "notes:changelog-writer"})),
            (
                "a subagent of another plugin",
                helpers.acted("Agent", {"subagent_type": "x:changelog-writer"}),
            ),
        ):
            with self.subTest(what=what):
                # Given: no call kept, the writer's start due
                # When: the orchestrator makes the call
                # Then: it drifts, the move due told
                self.assertEqual(follow_flow.drifts(made, [], NO_PLUGIN, run()), WRITER)

    def test_ending_while_a_move_is_due_drifts_telling_the_move(self):
        # Given: the writer come back, the reviewer's start due
        # When: the orchestrator is about to end
        ended = helpers.ended(helpers.HERE, [])
        # Then: it drifts, the move due told
        self.assertEqual(
            follow_flow.drifts(ended, [], NO_PLUGIN, run(started("changelog-writer"))), REVIEWER
        )

    def test_a_start_of_the_move_not_told_since_the_last_start_drifts_telling_the_move(self):
        # Given: the writer started in the background and ended, the reviewer's start due but
        # not told the orchestrator since
        untold = run(background("changelog-writer", "Wrote two."))._replace(told=False)
        # When: the orchestrator starts the reviewer
        # Then: it drifts, the move told
        made = agent("changelog-reviewer")
        self.assertEqual(follow_flow.drifts(made, [], NO_PLUGIN, untold), REVIEWER)

    def test_while_a_subagent_of_the_flow_runs_a_start_of_the_flow_drifts_telling_to_wait(self):
        for what, made, said in (
            ("a start of the next subagent", agent("changelog-reviewer"), WAIT),
            ("a start of the one running", agent("changelog-writer"), WAIT),
            ("another call", helpers.acted("Bash", {"command": "ls"}), ""),
            ("the end", helpers.ended(helpers.HERE, []), ""),
        ):
            with self.subTest(what=what):
                # Given: the writer started in the background, still running
                # When: the orchestrator makes the call, or ends
                # Then: a start of the flow drifts, told to wait; anything else is free
                running = run(background("changelog-writer"))
                self.assertEqual(follow_flow.drifts(made, [], NO_PLUGIN, running), said)

    def test_once_the_flow_is_done_each_call_and_the_end_are_free(self):
        kept = [started("changelog-writer"), started("changelog-reviewer")]
        for what, made in (
            ("a call", helpers.acted("Bash", {"command": "ls"})),
            ("an Agent call", agent("changelog-writer")),
            ("the end", helpers.ended(helpers.HERE, [])),
        ):
            with self.subTest(what=what):
                # Given: the flow done
                # When: the orchestrator makes the call, or ends
                # Then: it is no drift
                self.assertEqual(follow_flow.drifts(made, [], NO_PLUGIN, run(*kept)), "")


if __name__ == "__main__":
    unittest.main()
