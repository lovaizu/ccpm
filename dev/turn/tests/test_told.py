"""The user is told in the main conversation when a role starts or ends, when a point is asked and
when the result is back, by a line the flow makes from the move, carried in that move."""

import json
import os
import unittest

from helpers import (
    CALL,
    CHECKLIST,
    FIRST_READ,
    FOUND,
    FOUND_B1,
    IDS,
    PASSED,
    RESULT,
    WAITS,
    RepoTest,
    state,
)


def to_main(line):
    """The move sending the line to the main conversation."""
    return {"move": {"tool": "SendMessage", "input": {"to": "main", "message": line}}}


class TestTold(RepoTest):
    def test_a_role_to_start_is_told_first_by_a_move_of_its_own(self):
        # Given: a run started
        self.turn("start", json.dumps(CALL))
        # When: the orchestrator goes on
        out = self.next()
        # Then: the line telling what the generator does as it starts is the message of a move
        # sending it to `main`, as the Agent call starting it returns only at its end
        line = "turn: turn:generator starts: make README.md to give every item its Good, round 1."
        self.assertEqual(out, to_main(line))

    def test_the_role_is_started_once_its_line_is_sent(self):
        # Given: a run whose generator's start was told
        self.turn("start", json.dumps(CALL))
        self.next()
        # When: the orchestrator goes on
        move = self.next()["move"]
        # Then: the generator is started, described by its name
        self.assertEqual(
            (move["tool"], move["input"]["description"]), ("Agent", "turn turn:generator")
        )

    def test_a_role_s_end_is_told_with_the_start_of_the_next(self):
        # Given: a run whose generator was started
        self.started()
        # When: it replies with every item's Good
        out = self.made()
        # Then: one line says what it made and what the first user does as it starts
        line = (
            "turn: turn:generator made README.md. turn:first-user starts: use README.md in the"
            " receiver's place and give each item's Good, round 1."
        )
        self.assertEqual(out, to_main(line))

    def test_a_message_to_a_role_kept_started_is_told_in_the_same_move(self):
        # Given: a run whose first user is reading
        self.started()
        self.due(self.made())
        # When: it finds one item's Good and stops at the other
        out = self.replied({"items": FIRST_READ})
        # Then: the move sending the generator the item back carries the line saying what the
        # first user found and what the generator does as it goes on
        self.assertEqual(
            out["line"],
            "turn: turn:first-user found the Good of 1 of 2 items. turn:generator goes on: make"
            " README.md again for each item the first user found no Good for, round 1.",
        )
        self.assertEqual(out["move"]["input"]["to"], IDS["turn:generator"])

    def test_a_question_is_told_as_it_is_asked_and_the_answer_as_the_role_goes_on(self):
        # Given: a run whose generator was started
        self.started()
        # When: it asks before making anything, and the calling AI answers
        # Then: a line says the generator asks the user one question, with the asking; once
        # answered, a line says so with the message taking the answer to the generator
        out = self.made(WAITS)
        self.assertEqual(
            out, {"line": "turn: turn:generator asks the user 1 question.", "asked": RESULT}
        )
        self.assertEqual(
            self.answered()["line"],
            "turn: The calling AI answered. turn:generator goes on: take in the user's answer,"
            " round 1.",
        )

    def test_the_return_is_told_with_the_result_written_by_then(self):
        # Given: a run whose first user is reading
        self.started()
        # When: it finds every item's Good
        out = self.first_read(FOUND, FOUND_B1)
        # Then: the return comes with a line saying what the first user found and where the result
        # is, the result written by then and the run's state gone
        self.assertEqual(
            out,
            {
                "line": "turn: turn:first-user found the Good of 2 of 2 items. The result is at"
                f" {RESULT}.",
                "returned": RESULT,
            },
        )
        self.assertEqual(self.read_json(RESULT)["items"], [FOUND, FOUND_B1])
        self.assertFalse(os.path.exists(state.state_path(RESULT)))

    def test_a_line_counts_one_item_as_one(self):
        # Given: a checklist of one item
        self.write("checklists/readme.md", CHECKLIST.split("## Benefit")[0])
        # When: the run goes through to its first user's reading
        self.started()
        out = self.first_read(FOUND, claim=(PASSED,))
        # Then: the line counts it as one item
        self.assertIn("found the Good of 1 of 1 item.", out["line"])

    def test_a_start_due_is_told_again_on_a_call_again(self):
        # Given: a run whose generator's start was told
        # When: the same call is made again
        # Then: the start is told again before the generator is started
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
        self.assertIn("読む.md", self.turn("next", RESULT)[1])


if __name__ == "__main__":
    unittest.main()
