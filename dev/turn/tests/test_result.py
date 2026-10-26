"""Once every item has its Good, the result is written, the work and each item's Good alone, and the
run returns."""

import os
import unittest
from unittest import mock

from helpers import CHOSEN, FOUND, FOUND_B1, RESULT, ReadTest, flow


class TestResult(ReadTest):
    def test_the_result_holds_the_work_every_good_and_the_choices_alone(self):
        # Given: a generator whose claim names a choice of its own, and a first user finding every
        # item's Good
        # When: the orchestrator goes on
        # Then: the result holds where the work is, each item's Good as the first user gave it and
        # the choice as the generator named it, and nothing else, and the run then returns
        self.assertEqual(
            self.due(self.made(chosen=[CHOSEN]))["input"]["subagent_type"], "turn:first-user"
        )
        with mock.patch.object(flow, "SENDS", 0):
            out = self.replied({"items": [FOUND, FOUND_B1]})
        self.assertEqual(
            self.read_json(RESULT),
            {"work": ["README.md"], "items": [FOUND, FOUND_B1], "chosen": [CHOSEN]},
        )
        self.assertEqual(self.returned(out), {"returned": RESULT})

    def test_once_returned_the_result_alone_stays_of_the_run(self):
        # Given: a run whose every item has its Good
        # When: the run returns
        # Then: the run's folder is removed, and the result stays beside the CCS
        self.returned(self.first_read(FOUND, FOUND_B1))
        self.assertEqual(sorted(os.listdir(".tasks")), ["readme-result.json", "readme.json"])
        self.assertEqual(os.listdir(".turn"), [])

    def test_the_result_is_written_one_key_or_value_to_a_line(self):
        # Given: a run that returns
        # When: its result is written
        # Then: each key and each value of a list stands on a line of its own
        self.returned(self.first_read(FOUND, FOUND_B1))
        with open(RESULT, encoding="utf-8") as f:
            lines = f.read().splitlines()
        self.assertEqual(lines[:4], ["{", ' "work": [', '  "README.md"', " ],"])

    def test_the_result_holds_every_good_in_the_checklists_order(self):
        # Given: a first user giving the Goods out of the checklist's order
        # When: the run returns
        # Then: the result holds them in the checklist's order
        self.due(self.made())
        with mock.patch.object(flow, "SENDS", 0):
            self.returned(self.replied({"items": [FOUND_B1, FOUND]}))
        self.assertEqual(self.read_json(RESULT)["items"], [FOUND, FOUND_B1])


if __name__ == "__main__":
    unittest.main()
