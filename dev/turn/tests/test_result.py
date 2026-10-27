"""The result written once the first user has ended: the work, each item at the lines of its Good
and each item left with what the receiver would need, from the first user's last reading, and each
choice from the generator's last claim; the run's folder then removed."""

import json
import os
import unittest

from helpers import (
    ALL_GOOD,
    CALL,
    CCS,
    CHOSEN,
    CLAIM,
    FIRST_READ,
    FOUND,
    FOUND_B1,
    NEEDED_B1,
    NEEDED_F1,
    RESULT,
    StartedTest,
)


class TestResult(StartedTest):
    def ended(self, claim=CLAIM, reading=ALL_GOOD):
        """The run ended with the claim and the reading in its folder; what end printed."""
        self.claimed(claim)
        self.read_as(reading)
        return self.printed("end", self.result)

    def test_every_good_found_writes_the_work_the_goods_and_the_choices(self):
        # Given: a first user that found every item's Good, and a claim naming a choice
        # When: the run ends
        # Then: the result holds where the work is, each item at its lines, nothing left, and the
        # choice; end prints the result as the call names it
        self.assertEqual(self.ended(), {"returned": RESULT})
        self.assertEqual(
            self.read_json(RESULT),
            {"work": ["README.md"], "items": [FOUND, FOUND_B1], "left": [], "chosen": [CHOSEN]},
        )

    def test_an_item_left_without_good_comes_back_with_what_the_receiver_would_need(self):
        # Given: a last reading finding no Good for B-1, and for both items
        for reading, items, left in (
            (FIRST_READ, [FOUND], [NEEDED_B1]),
            ({"items": [NEEDED_F1, NEEDED_B1]}, [], [NEEDED_F1, NEEDED_B1]),
        ):
            with self.subTest(left=left):
                self.result = self.started()
                # When: the run ends
                self.ended(reading=reading)
                # Then: each item without Good is left with its need, and each other at its lines
                found = self.read_json(RESULT)
                self.assertEqual((found["items"], found["left"]), (items, left))

    def test_lines_given_by_whole_paths_are_named_as_the_ccs_names_the_work(self):
        # Given: a work of three files, its first named between the other two, and a last reading
        # giving one Good at lines of each later file by its whole path, as the first user is
        # given the work
        work = ["README.md", "A.md", "Z.md"]
        ccs = dict(
            CCS, focal_entities=[*({"deliverable": w} for w in work), CCS["focal_entities"][1]]
        )
        self.write_json(CALL["ccs"], ccs)
        for path in work[1:]:
            self.write(path, "one line\n")
        found = [
            dict(FOUND, lines=[f"{os.path.abspath('A.md')}:1"]),
            dict(FOUND_B1, lines=[f"{os.path.abspath('Z.md')}:1-1"]),
        ]
        # When: the run ends
        self.ended(reading={"items": found})
        # Then: the result names each range's file as the CCS names it, the range as it was given
        self.assertEqual(
            [i["lines"] for i in self.read_json(RESULT)["items"]], [["A.md:1"], ["Z.md:1-1"]]
        )

    def test_the_work_is_named_in_the_result_as_a_path_of_its_own(self):
        # Given: a CCS naming the work as `./README.md`
        ccs = dict(CCS, focal_entities=[{"deliverable": "./README.md"}, CCS["focal_entities"][1]])
        self.write_json(CALL["ccs"], ccs)
        # When: the run ends
        self.ended()
        # Then: the result names the work as the path it is, `README.md`
        self.assertEqual(self.read_json(RESULT)["work"], ["README.md"])

    def test_the_result_holds_the_items_in_the_checklists_order_as_the_ccs_names_them(self):
        # Given: a reading giving the items out of the checklist's order, each checklist named by
        # its whole path, as the first user is given it
        whole = self.here("checklists/readme.md")
        reading = {"items": [dict(NEEDED_B1, checklist=whole), dict(FOUND, checklist=whole)]}
        # When: the run ends
        self.ended(reading=reading)
        # Then: the result holds them in the checklist's order, the checklist as the CCS names it
        found = self.read_json(RESULT)
        self.assertEqual((found["items"], found["left"]), ([FOUND], [NEEDED_B1]))

    def test_once_returned_the_result_alone_stays_of_the_run(self):
        # Given: a run with its claim and its reading
        # When: it ends
        self.ended()
        # Then: the run's folder is removed, and the result stays beside the CCS
        self.assertEqual(sorted(os.listdir(".tasks")), ["readme-result.json", "readme.json"])
        self.assertEqual(os.listdir(".turn"), [])

    def test_the_result_is_written_one_key_or_value_to_a_line(self):
        # Given: a run that ends
        # When: its result is written
        self.ended()
        # Then: each key and each value of a list stands on a line of its own
        lines = self.read(RESULT).splitlines()
        self.assertEqual(lines[:4], ["{", ' "work": [', '  "README.md"', " ],"])

    def test_the_result_keeps_letters_beyond_ascii_as_they_are(self):
        # Given: a claim whose choice is said in Japanese
        # When: the run ends
        self.ended(claim=dict(CLAIM, chosen=[{"chosen": "例", "why": "決まり"}]))
        # Then: the result holds the words as written
        self.assertIn("決まり", self.read(RESULT))

    def test_a_reading_missing_or_out_of_its_form_writes_no_result(self):
        # Given: no reading, or one leaving an item out
        for reading in (None, {"items": [FOUND]}):
            with self.subTest(reading=reading):
                self.claimed(CLAIM)
                if reading is not None:
                    self.read_as(reading)
                # When: the run is to end
                out = self.stopped("end", self.result)
                # Then: it stops, naming the reading and saying to call turn again, and writes no
                # result, the run's folder kept
                self.assertIn(self.kept("first-user.json"), out)
                self.assertIn("call turn again with the same call", out)
                self.assertFalse(os.path.exists(RESULT))
                self.assertTrue(os.path.exists(self.kept("call.json")))

    def test_a_claim_missing_or_its_choices_out_of_form_writes_no_result(self):
        # Given: a reading finding every Good, and no claim, a claim that is no JSON, or one whose
        # choice lacks its why
        for claim in (None, "made", json.dumps(dict(CLAIM, chosen=[{"chosen": "x"}]))):
            with self.subTest(claim=claim):
                if claim is None:
                    if os.path.exists(self.kept("generator.json")):
                        os.remove(self.kept("generator.json"))
                else:
                    self.write(self.kept("generator.json"), claim)
                self.read_as(ALL_GOOD)
                # When: the run is to end
                out = self.stopped("end", self.result)
                # Then: it stops, naming the claim and saying to call turn again, and writes no
                # result
                self.assertIn(self.kept("generator.json"), out)
                self.assertIn("call turn again with the same call", out)
                self.assertFalse(os.path.exists(RESULT))

    def test_a_claim_of_a_mend_gives_its_choices_to_the_result(self):
        # Given: the generator's last claim of a mend, of B-1 alone, naming a choice, and the
        # reading of the mended work finding every Good
        # When: the run ends
        self.ended(claim={"items": [FOUND_B1], "chosen": [CHOSEN]})
        # Then: the result holds the choice, as the claim is read for its choices alone
        self.assertEqual(self.read_json(RESULT)["chosen"], [CHOSEN])


if __name__ == "__main__":
    unittest.main()
