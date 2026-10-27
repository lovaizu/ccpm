"""The tests of the session's history on its branch as the learnings are looked for in it: each
feedback with its answer, each work made again and each decision an answer replaced, each with its
commit."""

from __future__ import annotations

import unittest
from typing import Any

from helpers import FOLDER, STEERING, RepoTest, plan, steered

REPLACED = f"{FOLDER}/replaced.jsonl"


class HistoryTest(RepoTest):
    """A session kept move by move, its history asked for once the finished work is approved."""

    def setUp(self) -> None:
        super().setUp()
        self.session(steered(part=plan(tasks="")))

    def history(self) -> Any:
        """What rn gives of the session's history."""
        return self.ran("history")

    def kept_as(self, message: str, stage: str = "plan", signoff: str = "none") -> str:
        """The steering kept at the stage and the sign-off waiting, with the message; gives the
        commit."""
        self.write(STEERING, steered(part=plan(tasks=""), stage=stage, signoff=signoff))
        self.commit_with(message)
        return self.head()

    def called(self, number: str, work: str, *decisions: str, message: str = "a call") -> str:
        """The call of the number on the work kept with its decisions and the message; gives the
        commit."""
        self.call(number, work, decisions=decisions)
        self.commit_with(message)
        return self.head()

    def test_a_session_with_nothing_sent_back_made_again_or_replaced_gives_none(self):
        # Given: a session whose plan was proposed and approved, with one call on each work.
        self.called("0001", "plan", "Scope: the cart")
        self.kept_as("Plan sign-off", signoff="plan")
        self.kept_as("The user approved the plan", stage="design")
        self.called("0002", "t1.1", "License: MIT")
        # When: the orchestrator asks for the history.
        # Then: rn gives no feedback, no work made again and no decision replaced.
        self.assertEqual(self.history(), {"feedback": [], "remade": [], "replaced": []})

    def test_each_feedback_is_given_with_the_proposal_that_answered_it(self):
        # Given: the plan proposed, sent back, and proposed again with what changed.
        self.kept_as("Plan sign-off\nAC1: all files", signoff="plan")
        fed = self.kept_as("The user sent the plan back with /rn:gm: too much at once")
        answered = self.kept_as("Plan sign-off\nChanged: AC1: the cart", signoff="plan")
        # When: the orchestrator asks for the history.
        # Then: rn gives the feedback, as the commit that kept it says it, with the proposal that
        # answered it at the same sign-off.
        self.assertEqual(
            self.history()["feedback"],
            [
                {
                    "commit": fed,
                    "signoff": "plan",
                    "message": "The user sent the plan back with /rn:gm: too much at once",
                    "answer": {
                        "commit": answered,
                        "message": "Plan sign-off\nChanged: AC1: the cart",
                    },
                }
            ],
        )

    def test_an_approval_is_no_feedback(self):
        # Given: the plan proposed and approved, the stage moved on.
        self.kept_as("Plan sign-off", signoff="plan")
        self.kept_as("The user approved the plan", stage="design")
        # When: the orchestrator asks for the history.
        # Then: rn gives no feedback.
        self.assertEqual(self.history()["feedback"], [])

    def test_a_feedback_not_yet_answered_has_no_answer(self):
        # Given: the design proposed and sent back, not yet proposed again.
        self.kept_as("Design sign-off", stage="design", signoff="design")
        fed = self.kept_as("The user sent the design back with /rn:gm: no diagram", stage="design")
        # When: the orchestrator asks for the history.
        # Then: rn gives the feedback with no answer.
        self.assertEqual(
            self.history()["feedback"],
            [
                {
                    "commit": fed,
                    "signoff": "design",
                    "message": "The user sent the design back with /rn:gm: no diagram",
                    "answer": None,
                }
            ],
        )

    def test_each_feedback_is_answered_by_the_next_proposal_at_its_own_signoff(self):
        # Given: the plan sent back twice, each proposed again, then approved, and the design
        # proposed and sent back, then proposed again.
        self.kept_as("Plan 1", signoff="plan")
        first = self.kept_as("plan back 1")
        again = self.kept_as("Plan 2", signoff="plan")
        second = self.kept_as("plan back 2")
        last = self.kept_as("Plan 3", signoff="plan")
        self.kept_as("approved", stage="design")
        self.kept_as("Design 1", stage="design", signoff="design")
        third = self.kept_as("design back", stage="design")
        designed = self.kept_as("Design 2", stage="design", signoff="design")
        # When: the orchestrator asks for the history.
        # Then: each feedback is answered by the proposal after it at the same sign-off.
        self.assertEqual(
            [
                (f["commit"], f["signoff"], f["answer"]["commit"])
                for f in self.history()["feedback"]
            ],
            [(first, "plan", again), (second, "plan", last), (third, "design", designed)],
        )

    def test_each_work_made_again_is_given_with_the_call_that_made_it_again(self):
        # Given: a call on the plan, one on t1.1, the plan called again, and t1.1 called again
        # twice.
        self.called("0001", "plan")
        self.called("0002", "t1.1")
        plan_again = self.called("0003", "plan", message="Call 0003 on plan")
        t1_again = self.called("0004", "t1.1", message="Call 0004 on t1.1")
        t1_last = self.called("0005", "t1.1", message="Call 0005 on t1.1")
        # When: the orchestrator asks for the history.
        # Then: rn gives each call after a work's first, in the order made, with the commit that
        # added it and its message.
        self.assertEqual(
            self.history()["remade"],
            [
                {
                    "commit": plan_again,
                    "work": "plan",
                    "call": "0003",
                    "message": "Call 0003 on plan",
                },
                {
                    "commit": t1_again,
                    "work": "t1.1",
                    "call": "0004",
                    "message": "Call 0004 on t1.1",
                },
                {"commit": t1_last, "work": "t1.1", "call": "0005", "message": "Call 0005 on t1.1"},
            ],
        )

    def test_a_call_written_again_is_not_a_work_made_again(self):
        # Given: a call on t1.1 kept, then its CCS written again in a later commit.
        self.called("0001", "t1.1", "License: MIT")
        self.called("0001", "t1.1", "License: MIT", "Form: a page")
        # When: the orchestrator asks for the history.
        # Then: rn gives no work made again.
        self.assertEqual(self.history()["remade"], [])

    def decided(self, title: str, says: str, message: str = "a decision") -> None:
        """A decision of the plan kept by rn.py decide, as a move its step goes on after."""
        self.ran("decide", "plan", f"--title={title}", f"--says={says}", f"--message={message}")

    def stepped(self, message: str) -> str:
        """The step ended by rn.py state, committing every move of it; gives the commit."""
        self.ran("state", f"--message={message}")
        return self.head()

    def test_each_decision_an_answer_replaced_in_its_step_is_given_with_what_it_was(self):
        # Given: a decision of the plan kept, then replaced, then one of another title added, all
        # in one step, which one commit keeps.
        self.decided("License", "MIT")
        self.decided("License", "Apache-2.0", message="License asked again")
        self.decided("Colour", "blue")
        step = self.stepped("The step ends")
        # When: the orchestrator asks for the history.
        # Then: rn gives the decision replaced, what it was and what it is now, with the commit
        # of its step and that commit's message; not the one added.
        self.assertEqual(
            self.history()["replaced"],
            [
                {
                    "commit": step,
                    "work": "plan",
                    "was": "License: MIT",
                    "now": "License: Apache-2.0",
                    "message": self.out("log", "-1", "--format=%B").strip(),
                }
            ],
        )

    def test_a_decision_replaced_in_a_later_step_and_a_new_call_is_given_there(self):
        # Given: a call on the plan with two decisions, closed, a call on t1.1 holding a decision
        # of the same title as the plan's, and in a later step the plan's decision replaced, which
        # a new call carrying the plan's decisions takes.
        self.call("0001", "plan", decisions=("Scope: a cart", "Order: cart first"), result={})
        self.call("0002", "t1.1", decisions=("Scope: the cart page",))
        self.commit_with("two calls")
        self.decided("Scope", "every page", message="Scope asked again")
        step = self.stepped("The step ends")
        # When: the orchestrator asks for the history.
        # Then: rn gives the plan's decision replaced, with the commit of its step, and nothing
        # of t1.1's, which is another work.
        self.assertEqual(
            [(r["commit"], r["work"], r["was"], r["now"]) for r in self.history()["replaced"]],
            [(step, "plan", "Scope: a cart", "Scope: every page")],
        )

    def test_a_decision_kept_again_as_it_was_is_not_replaced(self):
        # Given: a decision of the plan kept, then kept again with the same words, as a fresh
        # conversation taking the step again does.
        self.decided("License", "MIT")
        self.decided("License", "MIT")
        self.stepped("The step ends")
        # When: the orchestrator asks for the history.
        # Then: rn gives no decision replaced.
        self.assertEqual(self.history()["replaced"], [])

    def test_a_line_of_the_replaced_record_that_is_no_json_object_is_none(self):
        # Given: lines of the record of decisions replaced written by hand, one no JSON and one a
        # JSON list, then a decision replaced by rn.
        self.write(REPLACED, "{\n[]\n")
        self.commit_with("by hand")
        self.decided("License", "MIT")
        self.decided("License", "Apache-2.0")
        step = self.stepped("The step ends")
        # When: the orchestrator asks for the history.
        # Then: rn gives the decision rn replaced alone.
        self.assertEqual(
            [(r["commit"], r["was"]) for r in self.history()["replaced"]],
            [(step, "License: MIT")],
        )

    def test_every_decision_replaced_in_the_first_step_is_given(self):
        # Given: two decisions of the plan each kept, then replaced, in the first step that keeps
        # the record of decisions replaced.
        self.decided("License", "MIT")
        self.decided("License", "Apache-2.0")
        self.decided("Colour", "blue")
        self.decided("Colour", "red")
        self.stepped("The step ends")
        # When: the orchestrator asks for the history.
        # Then: rn gives both, in the order they were replaced.
        self.assertEqual(
            [r["now"] for r in self.history()["replaced"]],
            ["License: Apache-2.0", "Colour: red"],
        )

    def test_a_line_after_one_that_is_no_json_in_the_same_commit_is_read(self):
        # Given: one commit holding a line of the record that is no JSON, then a decision replaced
        # written on the line after it.
        self.write(
            REPLACED,
            '{\n{"work": "plan", "was": "License: MIT", "now": "License: Apache-2.0"}\n',
        )
        self.commit_with("by hand")
        commit = self.head()
        # When: the orchestrator asks for the history.
        # Then: rn gives the decision on the line after.
        self.assertEqual(
            [(r["commit"], r["now"]) for r in self.history()["replaced"]],
            [(commit, "License: Apache-2.0")],
        )

    def test_a_decision_replaced_is_kept_in_its_own_letters(self):
        # Given: a decision of the plan kept, then replaced by words in letters beyond ASCII.
        self.decided("License", "MIT")
        self.decided("License", "日本語のライセンス")
        # When: the record of decisions replaced is read as text.
        # Then: it holds the words as written, as the user reads it on the pull request.
        self.assertIn("日本語のライセンス", self.read(REPLACED))

    def test_the_history_without_a_session_stops(self):
        # Given: a branch holding no session.
        self.git("checkout", "-q", "-b", "other", "main")
        # When: the orchestrator asks for the history.
        # Then: rn says there is none.
        self.assertIn("holds no session", self.stopped("history"))


if __name__ == "__main__":
    unittest.main()
