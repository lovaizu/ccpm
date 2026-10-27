"""A run stopped anywhere goes on from its last move when the same call is made again."""

import json
import os
import unittest
from unittest import mock

from helpers import (
    CALL,
    CLAIM,
    FIRST_READ,
    FOUND,
    RESULT,
    STOPPED_B1,
    WAITS,
    RepoTest,
    flow,
    state,
)


class TestResumed(RepoTest):
    def test_a_call_again_on_a_run_kept_goes_on_from_its_move(self):
        # Given: a run whose first user is due
        self.started()
        self.due(self.replied(CLAIM))
        # When: the same call is made again
        code, out = self.turn("start", json.dumps(CALL))
        # Then: it gives the result, and goes on from that move, told again
        self.assertEqual((code, json.loads(out)["result"]), (0, self.here(RESULT)))
        self.assertEqual(self.due(self.next())["input"]["subagent_type"], "turn:first-user")

    def test_a_call_again_on_a_ccs_laid_out_anew_begins_the_run_again(self):
        # Given: a run whose first user is due, and a CCS that now names another file of the work
        self.started()
        self.due(self.replied(CLAIM))
        self.laid_out_anew()
        # When: the same call is made again
        code, out = self.turn("start", json.dumps(CALL))
        self.assertEqual(code, 0, out)
        # Then: the generator is due again on the CCS as it is now, in the first round
        move = self.due(self.next())
        self.assertEqual(move["input"]["subagent_type"], "turn:generator")
        self.assertEqual(self.state()["work"], ["README.md", "LICENSE"])
        self.assertEqual(self.state()["round"], 1)

    def test_a_kept_role_sent_a_message_is_started_anew_with_what_was_sent_to_it_since(self):
        # Given: a run whose generator, kept started, was sent an item back
        self.started()
        self.due(self.replied(CLAIM))
        sent = self.due(self.replied({"items": FIRST_READ}))
        # When: the same call is made again
        self.turn("start", json.dumps(CALL))
        # Then: the generator is started anew with what it was given first and the message sent
        # since, and no role is kept started any more
        self.assertNotIn("started", self.state())
        move = self.due(self.next())
        self.assertEqual(move["tool"], "Agent")
        prompt = json.loads(move["input"]["prompt"])
        self.assertEqual(prompt["since"], [json.loads(sent["input"]["message"])])
        self.assertEqual(prompt["sent_back"], [])

    def test_a_kept_role_due_a_message_not_sent_yet_is_started_anew_with_it(self):
        # Given: a run whose generator, kept started, is due an item back not sent yet
        self.started()
        self.due(self.replied(CLAIM))
        self.replied({"items": FIRST_READ})
        # When: the same call is made again
        self.turn("start", json.dumps(CALL))
        # Then: the generator is started anew with the message due among those since
        prompt = json.loads(self.due(self.next())["input"]["prompt"])
        sent_back = {"sent_back": [STOPPED_B1], "reply": self.kept("generator.json")}
        self.assertEqual(prompt["since"], [sent_back])

    def test_a_run_waiting_on_an_answer_asks_again_on_a_call_again(self):
        # Given: a run whose generator asked before making anything, the question sent
        # When: the same call is made again, and the answer is handed on
        # Then: the question is told and asked again; the generator, its conversation gone, is
        # started anew with the answer in what it is given
        self.started()
        self.made(WAITS)
        self.turn("start", json.dumps(CALL))
        out = self.next()
        self.assertEqual(
            out, {"line": "turn: turn:generator asks the user 1 question.", "asked": RESULT}
        )
        self.assertEqual(len(json.loads(self.turn("questions", RESULT)[1])["questions"]), 1)
        move = self.due(self.answered())
        self.assertEqual(move["tool"], "Agent")
        prompt = json.loads(move["input"]["prompt"])
        self.assertEqual((prompt["sent_back"], len(prompt["answers"])), ([], 1))

    def test_a_run_stopped_after_the_first_user_s_reading_goes_on_from_the_next_round(self):
        # Given: a run whose first user's reading ended, the second round's generator due
        # When: the same call is made again
        # Then: the generator is told again and started anew with the items without Good
        self.started()
        self.first_read(FOUND)
        self.turn("start", json.dumps(CALL))
        move = self.due(self.next())
        self.assertEqual(move["tool"], "Agent")
        self.assertEqual(json.loads(move["input"]["prompt"])["sent_back"], self.reading(FOUND)[1:])

    def test_a_run_stopped_once_its_result_is_written_returns_on_a_call_again(self):
        # Given: a run whose every item has its Good, the result written, stopped before its folder
        # was removed
        self.started()
        self.due(self.made())
        with (
            mock.patch.object(flow.shutil, "rmtree", side_effect=KeyboardInterrupt),
            self.assertRaises(KeyboardInterrupt),
        ):
            self.replied({"items": [FOUND, dict(FOUND, item="B-1")]})
        # When: the same call is made again
        self.turn("start", json.dumps(CALL))
        # Then: the run returns, told again
        self.assertEqual(self.returned(self.next()), {"returned": RESULT})
        self.assertFalse(os.path.exists(state.state_path(RESULT)))

    def test_a_call_again_with_another_call_on_the_same_result_stops(self):
        # Given: a run kept for a result
        # When: another call names the same result
        # Then: it stops, saying a run of another call is kept there
        self.started()
        other = dict(CALL, kind=dict(CALL["kind"], has="decisions"))
        code, out = self.turn("start", json.dumps(other))
        self.assertEqual(code, 1)
        self.assertIn("a run of another call is kept at", out)

    def test_a_call_again_on_a_ccs_gone_wrong_stops(self):
        # Given: a run kept, whose CCS was taken away
        # When: the same call is made again
        # Then: it stops, as turn cannot take it
        self.started()
        os.remove(CALL["ccs"])
        code, out = self.turn("start", json.dumps(CALL))
        self.assertEqual(code, 1)
        self.assertIn("is not there", out)


if __name__ == "__main__":
    unittest.main()
