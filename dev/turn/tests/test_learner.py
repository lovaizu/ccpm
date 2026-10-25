"""Once every item has its Good, the learner learns from every record of the run, and the result is
written with its lessons."""

import json
import os
import unittest
from unittest import mock

from helpers import (
    CALL,
    CHECKED,
    FOUND,
    FOUND_B1,
    IDS,
    LESSON,
    RESULT,
    ReadTest,
    run,
)


class TestLearner(ReadTest):
    def setUp(self):
        super().setUp()
        for agent, agent_id in IDS.items():
            self.given_record(agent_id, "{}", agent)
        self.given_record("aup", json.dumps(CALL), "turn:up")
        self.learner = self.first_read(FOUND, FOUND_B1)

    def test_the_learner_starts_once_on_every_record_of_the_run_shown_as_text(self):
        # Given: a run whose every item has its Good
        # When: the first user's reading is taken
        # Then: the learner is to be started with the record of every role that replied and the
        # orchestrator's, each shown as text beside the result, and where it replies
        move = self.due(self.learner)
        self.assertEqual(move["input"]["subagent_type"], "turn:learner")
        texts = [self.here(f"{RESULT}.records/{n}.txt") for n in (1, 2, 3)]
        self.assertEqual(
            json.loads(move["input"]["prompt"]),
            {"given": texts, "reply": self.here(RESULT + ".learner.json")},
        )
        self.assertIn("[user] {}", self.read(texts[0]))
        self.assertIn('"result": ".tasks/readme-result.json"', self.read(texts[2]))

    def test_the_lessons_go_into_the_result_with_every_good_and_the_run_returns(self):
        # Given: a learner replying with a general lesson and one of the project's own
        # When: the orchestrator goes on
        # Then: the result holds where the work is, each item's Good as the first user gave it,
        # the lessons, each ground naming its record by its path, and what the learner checked,
        # and the run returns
        own = {
            "lesson": "the checklist names no license item",
            "whose": "own",
            "grounds": [{"record": 2, "quote": "I open it."}, {"record": 3, "quote": "I open it."}],
        }
        self.due(self.learner)
        learnt = self.state()["record_paths"]
        out = self.replied({"lessons": [LESSON, own], "checked": CHECKED})
        named = [
            dict(LESSON, grounds=[dict(LESSON["grounds"][0], record=learnt[0])]),
            dict(own, grounds=[dict(g, record=learnt[n]) for n, g in zip((1, 2), own["grounds"])]),
        ]
        self.assertEqual(
            self.read_json(RESULT),
            {
                "work": ["README.md"],
                "items": [FOUND, FOUND_B1],
                "lessons": named,
                "checked": CHECKED,
            },
        )
        self.assertEqual(self.heard(out), {"returned": RESULT})

    def test_once_returned_what_the_run_kept_beside_the_result_is_removed(self):
        # Given: a run whose learner replied
        # When: the run returns
        # Then: the result and the CCS alone stay beside it
        self.learnt(self.learner)
        self.assertEqual(sorted(os.listdir(".tasks")), ["readme-result.json", "readme.json"])

    def test_the_result_is_written_one_key_or_value_to_a_line(self):
        # Given: a run that returns
        # When: its result is written
        # Then: each key and each value of a list stands on a line of its own
        self.learnt(self.learner)
        with open(RESULT, encoding="utf-8") as f:
            lines = f.read().splitlines()
        self.assertEqual(lines[:4], ["{", ' "work": [', '  "README.md"', " ],"])

    def test_a_lesson_quoting_words_no_record_holds_is_sent_back_to_the_learner(self):
        # Given: a learner whose lesson quotes words its record does not hold
        # When: the orchestrator goes on
        # Then: the learner is sent what is wrong
        self.due(self.learner)
        lesson = dict(LESSON, grounds=[{"record": 1, "quote": "never said"}])
        out = self.replied({"lessons": [lesson], "checked": CHECKED})
        self.assertEqual(out["move"]["input"]["to"], IDS["turn:learner"])
        self.assertIn("is not in record 1 as written", out["move"]["input"]["message"])


class TestLearnerBare(ReadTest):
    """A run with no record kept where Claude Code keeps them, its Goods given as a test sets."""

    def test_a_record_not_kept_is_left_out(self):
        # Given: a run whose records are not where Claude Code keeps them
        # When: the learner is started
        # Then: it is given none
        self.due(self.first_read(FOUND, FOUND_B1))
        self.assertEqual(self.prompt()["given"], [])

    def test_the_result_holds_every_good_in_the_checklists_order(self):
        # Given: a first user giving the Goods out of the checklist's order
        # When: the run returns
        # Then: the result holds them in the checklist's order
        self.due(self.made())
        with mock.patch.object(run, "SENDS", 0):
            self.learnt(self.replied({"items": [FOUND_B1, FOUND]}))
        self.assertEqual(self.read_json(RESULT)["items"], [FOUND, FOUND_B1])


if __name__ == "__main__":
    unittest.main()
