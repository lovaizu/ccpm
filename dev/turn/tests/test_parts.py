"""A run with an item asked of each part of the work, given a Good for every part, and its Good only
then."""

import json
import os
import unittest

from helpers import (
    CALL,
    CHECKLIST,
    EACH,
    EACH_GOOD,
    FOUND,
    FOUND_B1,
    GOOD,
    IDS,
    RESULT,
    SECTIONED,
    STOPPED_B1,
    RepoTest,
)


class TestEachPart(RepoTest):
    """An item asked of each part is given a Good for every part, and has its Good only then."""

    def setUp(self):
        super().setUp()
        self.write("checklists/readme.md", CHECKLIST + EACH)
        self.write("README.md", SECTIONED)
        code, out = self.turn("start", json.dumps(CALL))
        self.assertEqual(code, 0, out)
        self.due(self.next())

    def test_an_item_asked_of_each_part_is_sent_back_with_the_parts_without_good(self):
        # Given: a first user giving an item asked of each part no Good where one part does not
        # give it
        # When: the orchestrator goes on
        # Then: the generator is sent the item again, with the part where it stopped
        self.due(self.made(GOOD, dict(GOOD, item="B-1"), EACH_GOOD))
        back = dict(STOPPED_B1, item="B-2", places=["README.md:5-7"])
        move = self.due(self.replied({"items": [FOUND, FOUND_B1, back]}))
        self.assertEqual(move["input"]["to"], IDS["turn:generator"])
        self.assertEqual(json.loads(move["input"]["message"])["sent_back"], [back])

    def test_an_item_given_a_good_for_every_part_is_good_in_the_result(self):
        # Given: a first user giving an item asked of each part a Good for every part
        # When: the run returns
        # Then: the result holds the item with its Good for every part
        claim = (GOOD, dict(GOOD, item="B-1"), EACH_GOOD)
        out = self.first_read(FOUND, FOUND_B1, EACH_GOOD, claim=claim)
        self.assertEqual(self.returned(out), {"returned": RESULT})
        self.assertEqual(self.read_json(RESULT)["items"], [FOUND, FOUND_B1, EACH_GOOD])

    def test_a_reply_giving_an_each_part_item_without_every_part_is_sent_back_to_its_role(self):
        # Given: a generator replying with an item asked of each part given one part alone
        # When: the orchestrator goes on
        # Then: the generator is sent what is wrong, to write its reply again, and the reply file
        # is removed until it does
        one = dict(EACH_GOOD, parts=EACH_GOOD["parts"][:1])
        out = self.made(GOOD, dict(GOOD, item="B-1"), one)
        self.assertEqual(out["move"]["tool"], "SendMessage")
        self.assertEqual(out["move"]["input"]["to"], IDS["turn:generator"])
        self.assertIn("in your form, filled:", out["move"]["input"]["message"])
        self.assertFalse(os.path.exists(self.kept("generator.json")))
        move = self.due(self.made(GOOD, dict(GOOD, item="B-1"), EACH_GOOD))
        self.assertEqual(move["tool"], "Agent")


if __name__ == "__main__":
    unittest.main()
