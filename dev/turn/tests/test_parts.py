"""A run with an item asked of each part of the work, given lines in every part, and its Good only
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
    IDS,
    NEEDED_B1,
    RESULT,
    SECTIONED,
    RepoTest,
)


class TestEachPart(RepoTest):
    """An item asked of each part is given lines in every part, and has its Good only then."""

    def setUp(self):
        super().setUp()
        self.write("checklists/readme.md", CHECKLIST + EACH)
        self.write("README.md", SECTIONED)
        code, out = self.turn("start", json.dumps(CALL))
        self.assertEqual(code, 0, out)
        self.due(self.next())

    def test_an_item_asked_of_each_part_without_good_is_sent_with_what_the_receiver_would_need(
        self,
    ):
        # Given: a generator claiming every item at the lines of every part, and a first user
        # finding no Good for the item asked of each part, as one part does not give it
        # When: the orchestrator goes on
        # Then: the generator is sent the item again, with what the receiver would need
        self.due(self.made())
        back = dict(NEEDED_B1, item="B-2")
        move = self.due(self.replied({"items": [FOUND, FOUND_B1, back]}))
        self.assertEqual(move["input"]["to"], IDS["turn:generator"])
        self.assertEqual(json.loads(move["input"]["message"])["needs"], [back])

    def test_an_item_given_lines_in_every_part_is_good_in_the_result(self):
        # Given: a first user giving an item asked of each part lines in every part
        # When: the run returns
        # Then: the result holds the item with its lines
        out = self.first_read(FOUND, FOUND_B1, EACH_GOOD)
        self.assertEqual(self.returned(out), {"returned": RESULT})
        self.assertEqual(self.read_json(RESULT)["items"], [FOUND, FOUND_B1, EACH_GOOD])

    def test_a_reply_giving_an_each_part_item_without_every_part_is_sent_back_to_its_role(self):
        # Given: a first user replying with an item asked of each part given lines in one part
        # alone
        # When: the orchestrator goes on
        # Then: the first user is sent what is wrong, to write its reply again, and the reply file
        # is removed until it does; once filled, the run returns
        self.due(self.made())
        one = dict(EACH_GOOD, lines=EACH_GOOD["lines"][:1])
        out = self.replied({"items": [FOUND, FOUND_B1, one]})
        self.assertEqual(out["move"]["tool"], "SendMessage")
        self.assertEqual(out["move"]["input"]["to"], IDS["turn:first-user"])
        self.assertIn("in your form, filled:", out["move"]["input"]["message"])
        self.assertFalse(os.path.exists(self.kept("first-user.json")))
        out = self.replied({"items": [FOUND, FOUND_B1, EACH_GOOD]})
        self.assertEqual(self.returned(out), {"returned": RESULT})


if __name__ == "__main__":
    unittest.main()
