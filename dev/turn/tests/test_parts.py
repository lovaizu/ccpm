"""A run with an item the CCS asks of each part of the work, given lines in every part, and its Good
only then."""

import unittest

from helpers import (
    CALL,
    CHECKLIST,
    CLAIM,
    EACH,
    EACH_CCS,
    EACH_GOOD,
    FOUND,
    FOUND_B1,
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
        self.write_json(CALL["ccs"], EACH_CCS)
        self.write("README.md", SECTIONED)
        self.result = self.started()

    def test_an_item_asked_of_each_part_without_good_is_given_the_generator_as_a_need(self):
        # Given: a first user finding no Good for the item asked of each part, as one part does
        # not give it
        back = dict(NEEDED_B1, item="B-2")
        self.read_as({"items": [FOUND, FOUND_B1, back]})
        # When: the generator runs turn.py to mend it
        # Then: it is given the item with what the receiver would need
        self.assertEqual(self.printed("generator", self.result)["needs"], [back])

    def test_an_item_given_lines_in_every_part_is_good_in_the_result(self):
        # Given: a first user giving an item asked of each part lines in every part
        self.claimed(dict(CLAIM, items=[*CLAIM["items"], EACH_GOOD]))
        self.read_as({"items": [FOUND, FOUND_B1, EACH_GOOD]})
        # When: the run ends
        self.assertEqual(self.turn("reading", self.result)[0], 0)
        self.printed("end", self.result)
        # Then: the result holds the item with its lines
        self.assertEqual(self.read_json(RESULT)["items"], [FOUND, FOUND_B1, EACH_GOOD])

    def test_a_reading_giving_an_each_part_item_without_every_part_is_told_to_fix_it(self):
        # Given: a first user giving an item asked of each part lines in one part alone
        one = dict(EACH_GOOD, lines=EACH_GOOD["lines"][:1])
        self.read_as({"items": [FOUND, FOUND_B1, one]})
        # When: its reading is checked
        # Then: it is told the part holding none of its lines
        out = self.stopped("reading", self.result)
        self.assertIn("README.md:5-7 holds none of its lines", out)


if __name__ == "__main__":
    unittest.main()
