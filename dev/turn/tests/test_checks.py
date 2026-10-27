"""Each role's reply checked by turn.py before the role ends: the generator's claim and the first
user's reading, each against its form, the work's lines and, for an item asked of each part, every
part; what to fix printed and 1 given back, or 0."""

import json
import unittest

from helpers import (
    ALL_GOOD,
    CHECKLIST,
    CHOSEN,
    CLAIM,
    EACH,
    EACH_GOOD,
    FIRST_READ,
    FOUND,
    FOUND_B1,
    MADE,
    MADE_B1,
    NEEDED_B1,
    SECTIONED,
    StartedTest,
)


class TestClaim(StartedTest):
    def test_a_claim_of_every_item_at_its_lines_passes(self):
        # Given: the generator's claim of every item at its lines, on a run with no reading yet
        self.claimed(CLAIM)
        # When: it is checked
        # Then: it passes, naming the reply checked
        self.assertEqual(
            self.printed("claim", self.result), {"filled": self.kept("generator.json")}
        )

    def test_a_claim_not_written_is_told_where_to_write_it(self):
        # Given: no claim written
        # When: it is checked
        # Then: it stops, naming where to write it and its form
        out = self.stopped("claim", self.result)
        self.assertIn(self.kept("generator.json"), out)
        self.assertIn("claim.json", out)

    def test_a_claim_out_of_its_form_is_told_each_thing_to_fix(self):
        # Given: a claim leaving an item out and naming lines the work does not hold
        self.claimed({"items": [dict(MADE, lines=["README.md:9"])], "chosen": []})
        # When: it is checked
        # Then: it stops, saying the claim is not filled, then each thing to fix on a line of its
        # own
        out = self.stopped("claim", self.result).splitlines()
        self.assertIn(self.kept("generator.json"), out[0])
        self.assertIn("README.md:9 is not lines of the work", out[1])
        self.assertIn("B-1 is left out", out[2])

    def test_a_mend_claims_the_items_the_last_reading_left_without_good_alone(self):
        # Given: the first user's last reading leaving B-1 without Good
        self.read_as(FIRST_READ)
        # When: a claim of B-1 alone is checked, and one of every item
        self.claimed({"items": [MADE_B1], "chosen": [CHOSEN]})
        self.assertEqual(self.turn("claim", self.result)[0], 0)
        self.claimed(CLAIM)
        # Then: the first passes, and the second is told F-1 was not sent to be mended
        self.assertIn("F-1 is not an item judged here", self.stopped("claim", self.result))

    def test_after_a_reading_with_every_good_a_claim_gives_every_item(self):
        # Given: the first user's last reading finding every Good
        self.read_as(ALL_GOOD)
        # When: a claim of one item is checked
        self.claimed({"items": [MADE_B1], "chosen": []})
        # Then: it is told the item left out, as no item waits on a mend
        self.assertIn("F-1 is left out", self.stopped("claim", self.result))

    def test_an_item_asked_of_each_part_is_claimed_in_every_part(self):
        # Given: a checklist with an item asked of each part, a work of two parts, and a claim
        # giving it lines in one part alone
        self.write("checklists/readme.md", CHECKLIST + EACH)
        self.write("README.md", SECTIONED)
        one = dict(EACH_GOOD, lines=EACH_GOOD["lines"][:1])
        self.claimed({"items": [MADE, MADE_B1, one], "chosen": []})
        # When: it is checked
        # Then: it is told the part holding none of its lines
        self.assertIn("README.md:5-7 holds none of its lines", self.stopped("claim", self.result))


class TestReading(StartedTest):
    def test_a_reading_of_every_item_passes(self):
        # Given: the first user's reading, one item at its lines and one with a need
        self.read_as(FIRST_READ)
        # When: it is checked
        # Then: it passes, naming the reply checked
        self.assertEqual(
            self.printed("reading", self.result), {"filled": self.kept("first-user.json")}
        )

    def test_a_reading_in_a_json_fence_is_read_as_the_reading(self):
        # Given: a reading written inside a ```json fence, as a model often writes JSON
        self.write(self.kept("first-user.json"), f"```json\n{json.dumps(FIRST_READ)}\n```\n")
        # When: it is checked, and the generator is given what it left without Good
        # Then: it passes, and its need is read from inside the fence
        self.assertEqual(self.turn("reading", self.result)[0], 0)
        self.assertEqual(self.printed("generator", self.result)["needs"], [NEEDED_B1])

    def test_a_reading_not_written_is_told_where_to_write_it(self):
        # Given: no reading written
        # When: it is checked
        # Then: it stops, naming where to write it and its form
        out = self.stopped("reading", self.result)
        self.assertIn(self.kept("first-user.json"), out)
        self.assertIn("reading.json", out)

    def test_a_reading_leaving_an_item_out_is_told_it(self):
        # Given: a reading leaving B-1 out, and one that is no JSON
        for reading in (json.dumps({"items": [FOUND]}), "read"):
            with self.subTest(reading=reading):
                self.write(self.kept("first-user.json"), reading)
                # When: it is checked
                # Then: it stops, saying what to fix
                out = self.stopped("reading", self.result)
                self.assertIn("is not filled", out)

    def test_a_reading_answers_every_item_whatever_the_last_reading_left(self):
        # Given: a reading that left B-1 without Good, then the reading of the mended work giving
        # B-1 alone
        self.read_as(FIRST_READ)
        self.read_as({"items": [FOUND_B1]})
        # When: it is checked
        # Then: it is told F-1 is left out, as every reading answers every item
        self.assertIn("F-1 is left out", self.stopped("reading", self.result))

    def test_a_need_of_blanks_is_told_to_say_it_in_words(self):
        # Given: a reading whose need is blanks alone
        self.read_as({"items": [FOUND, dict(NEEDED_B1, need=" ")]})
        # When: it is checked
        # Then: it is told to say it in words
        self.assertIn('B-1 has an empty "need"', self.stopped("reading", self.result))


if __name__ == "__main__":
    unittest.main()
