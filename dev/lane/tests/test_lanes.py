"""Each lane's wording, held to the README's Lanes, and the sentence made from it with what the lane
takes, the one the step says and the subagent is told."""

import os
import re
import unittest

import helpers
from helpers import lanes

# A row of the README's Lanes: its action, its lane, its sentence and when its hook tells it.
ROW = re.compile(r"^\| (?P<action>[a-z ]+) \| (?P<lane>[a-z_]+) \| (?P<sentence>.+?) \| .+ \|$")


def readme_rows() -> dict:
    """Each lane of the README's Lanes table, by its name: its action and its sentence."""
    with open(os.path.join(helpers.LANE, "README.md"), encoding="utf-8") as f:
        found = [ROW.match(line) for line in f.read().split("## Lanes")[1].splitlines()]
    return {m["lane"]: (m["action"], m["sentence"]) for m in found if m}


class TestWording(unittest.TestCase):
    def test_each_lane_has_the_action_and_wording_of_its_row_in_the_readme(self):
        # Given: the README's Lanes table
        rows = readme_rows()
        for name, lane in lanes.LANES.items():
            with self.subTest(lane=name):
                # When: the lane in lanes/ is read
                # Then: its action and its wording are those of its row
                self.assertEqual((lane.ACTION, lane.WORDING), rows[name])


class TestSentence(unittest.TestCase):
    def test_one_thing_taken_is_put_in_its_quotes(self):
        # Given: hands_off taking one command
        # When: its sentence is made
        # Then: the command stands where the wording shows `<commands>`
        self.assertEqual(lanes.sentence("hands_off", ["git push"]), "Do not run `git push`.")

    def test_two_things_taken_are_joined_by_or(self):
        # Given: hands_off taking two commands
        # When: its sentence is made
        # Then: each is in quotes of its own, joined by `or`, as the README's example reads
        self.assertEqual(lanes.sentence("hands_off", ["git commit", "git push"]), helpers.SENTENCE)

    def test_three_things_taken_are_listed_with_or_before_the_last(self):
        # Given: hands_off taking three commands
        # When: its sentence is made
        # Then: they are listed with commas, `or` before the last
        self.assertEqual(
            lanes.sentence("hands_off", ["a", "b", "c"]), "Do not run `a`, `b` or `c`."
        )

    def test_a_wording_showing_two_things_puts_in_each_taken_in_turn(self):
        # Given: in_form taking an output and its form
        # When: its sentence is made
        # Then: each stands in its own place, in the order taken
        self.assertEqual(
            lanes.sentence("in_form", ["out.json", "forms/out.json"]),
            "Write `out.json` in `forms/out.json`.",
        )


class TestTakes(unittest.TestCase):
    def test_a_lane_showing_one_thing_takes_one_or_more(self):
        for takes, fits in (([], False), (["a"], True), (["a", "b"], True)):
            with self.subTest(takes=takes):
                # Given: hands_off, whose wording shows one thing
                # When: it is given so many things
                # Then: it takes one or more
                self.assertEqual(lanes.fits("hands_off", takes), fits)

    def test_a_lane_showing_two_things_takes_two_alone(self):
        for takes, fits in ((["a"], False), (["a", "b"], True), (["a", "b", "c"], False)):
            with self.subTest(takes=takes):
                # Given: in_form, whose wording shows an output and a form
                # When: it is given so many things
                # Then: it takes two alone, one for each
                self.assertEqual(lanes.fits("in_form", takes), fits)


class TestWords(unittest.TestCase):
    def test_a_lane_is_written_as_its_step_its_name_and_what_it_takes(self):
        # Given: hands_off on step 3 taking two commands
        # When: it is written for the hook's command
        # Then: it reads `<step>:<lane>:<what it takes>`, the things taken joined by commas
        self.assertEqual(
            lanes.word(3, "hands_off", ["git commit", "git push"]),
            "3:hands_off:git commit,git push",
        )


if __name__ == "__main__":
    unittest.main()
