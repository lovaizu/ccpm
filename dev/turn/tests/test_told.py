"""Each move is told to the main conversation first, by a line the flow makes from the move."""

import json
import os
import unittest

from helpers import (
    CALL,
    CAN,
    CHECKLIST,
    CLAIM,
    FOUND,
    QUESTION,
    RESULT,
    WAITS,
    RepoTest,
    state,
)


class TestTold(RepoTest):
    def test_a_role_s_move_is_told_first_by_a_line_the_flow_makes(self):
        # Given: a run started
        self.turn("start", json.dumps(CALL))
        # When: the orchestrator's check finds what gives every item its Good
        out = self.next({"items": CAN, "questions": []})
        # Then: the line telling the calling AI what was done and what comes next, how far and
        # how, is the message of the move sending it to `main`
        line = (
            "turn: turn:up found in the CCS what gives the Good of 2 items. Next, turn:generator"
            " will make the work to give every item its Good, and run what it gives as the"
            " receiver would, of README.md, for 2 items, round 1."
        )
        self.assertEqual(
            out,
            {
                "line": line,
                "move": {"tool": "SendMessage", "input": {"to": "main", "message": line}},
            },
        )

    def test_the_role_is_started_once_its_line_is_sent(self):
        # Given: a run whose generator's line was told
        self.turn("start", json.dumps(CALL))
        self.next({"items": CAN, "questions": []})
        # When: the orchestrator goes on
        move = self.next()["move"]
        # Then: the generator is started, described by its name
        self.assertEqual(
            (move["tool"], move["input"]["description"]), ("Agent", "turn turn:generator")
        )

    def test_a_role_s_reply_is_told_in_the_line_after_it(self):
        # Given: a run whose generator was started
        self.started()
        # When: it replies with every item's Good
        out = self.replied(CLAIM)
        # Then: the line after says what it made
        self.assertTrue(
            str(out["line"]).startswith("turn: turn:generator made README.md. Next,"), out
        )

    def test_the_orchestrators_check_is_told_before_it_is_shown(self):
        # Given: a run started
        self.turn("start", json.dumps(CALL))
        # When: the orchestrator goes on with nothing, and once more
        out = self.next()
        # Then: a line telling the check is sent to `main`, and then the check is shown
        line = (
            "turn: Next, turn:up will check that the CCS gives every item its Good, of README.md,"
            " for 2 items, round 1."
        )
        self.assertEqual(
            out,
            {
                "line": line,
                "move": {"tool": "SendMessage", "input": {"to": "main", "message": line}},
            },
        )
        self.assertEqual(self.next()["check"][0]["item"], "F-1")

    def test_a_question_is_told_before_it_is_asked_and_the_answer_before_the_check(self):
        # Given: a run started and told its check
        # When: the check finds an item waiting on the user's answer, and the run goes on, and
        # on once answered
        # Then: a line says what the check found and that the question is asked, before the run
        # asks; once answered, a line says so before the check is shown again
        self.turn("start", json.dumps(CALL))
        self.next()
        out = self.next({"items": [CAN[0], WAITS], "questions": [QUESTION]})
        self.assertEqual(
            out["line"],
            "turn: turn:up found 1 of 2 items waiting on the user's answer. Next, turn:up will ask"
            " what only the user can decide, of README.md, for 2 items, round 1.",
        )
        self.assertEqual(self.next(), {"asked": RESULT})
        out = self.answered()
        self.assertTrue(
            str(out["line"]).startswith("turn: The calling AI answered. Next, turn:up will check"),
            out,
        )
        self.assertEqual(self.next()["check"][1]["item"], "B-1")

    def test_the_return_is_told_with_the_result_written_by_then(self):
        # Given: every item's Good found
        # When: the orchestrator goes on
        # Then: the line telling the return comes with the result written by then, and the run's
        # state is gone once it returns
        self.started()
        self.first_read(FOUND, dict(FOUND, item="B-1"))
        self.assertEqual(self.read_json(RESULT)["items"], [FOUND, dict(FOUND, item="B-1")])
        self.assertEqual(self.next(), {"returned": RESULT})
        self.assertFalse(os.path.exists(state.state_path(RESULT)))

    def test_a_line_counts_one_item_as_one(self):
        # Given: a checklist of one item
        self.write("checklists/readme.md", CHECKLIST.split("## Benefit")[0])
        # When: the run is started, and the check told
        self.turn("start", json.dumps(CALL))
        # Then: the line counts it as one item
        self.assertTrue(str(self.next()["line"]).endswith("of README.md, for 1 item, round 1."))

    def test_a_judgment_due_is_told_again_on_a_call_again(self):
        # Given: a run whose check was told
        # When: the same call is made again
        # Then: the check is told again before it is shown
        self.turn("start", json.dumps(CALL))
        self.next()
        self.turn("start", json.dumps(CALL))
        self.assertEqual(self.next()["move"]["input"]["to"], "main")

    def test_a_move_is_printed_with_letters_beyond_ascii_as_they_are(self):
        # Given: a work named in letters beyond ASCII
        # When: its move is printed
        # Then: the letters stand as they are
        ccs = self.read_json(CALL["ccs"])
        ccs["focal_entities"][0] = {"deliverable": "読む.md"}
        self.write_json(CALL["ccs"], ccs)
        self.write("読む.md", "# x\n")
        self.turn("start", json.dumps(CALL))
        self.turn("next", RESULT, stdin=json.dumps({"items": CAN, "questions": []}))
        self.assertIn("読む.md", self.turn("next", RESULT)[1])


if __name__ == "__main__":
    unittest.main()
