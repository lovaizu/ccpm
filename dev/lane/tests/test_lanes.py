"""Each lane's wording, held to the README's Lanes, and the sentence made from it with what the lane
takes, the one the step says and the subagent is told."""

import os
import re
import types
import unittest
from unittest import mock

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
            lanes.sentence("in_form", ["out.json", "${CLAUDE_PLUGIN_ROOT}/forms/out.json"]),
            "Write `out.json` in the form of `${CLAUDE_PLUGIN_ROOT}/forms/out.json`.",
        )

    def test_a_lane_holding_more_than_it_shows_shows_the_first_alone(self):
        # Given: wait_for taking the approval and the commands it holds back
        # When: its sentence is made
        # Then: the approval alone stands where the wording shows `<approval>`
        self.assertEqual(
            lanes.sentence("wait_for", ["OK", "lay.py write", "git push"]),
            "Do not go on until `OK`.",
        )

    def test_how_many_things_a_lane_shows(self):
        # Given: wait_for, which shows the approval alone, and hands_off, which shows all
        # When: how many it shows is read
        # Then: it is one for wait_for, all for hands_off
        self.assertEqual((lanes.shown("wait_for"), lanes.shown("hands_off")), (1, None))


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

    def test_a_lane_showing_two_things_takes_one_for_each_the_last_taking_the_rest(self):
        for takes, fits in ((["a"], False), (["a", "b"], True), (["a", "b", "c"], True)):
            with self.subTest(takes=takes):
                # Given: test_after, whose wording shows an output and a test, and names no most
                # When: it is given so many things
                # Then: it takes one for each place or more
                self.assertEqual(lanes.fits("test_after", takes), fits)

    def test_a_lane_holding_more_than_it_shows_takes_one_or_more_after_those(self):
        for takes, fits in ((["OK"], False), (["OK", "a"], True), (["OK", "a", "b"], True)):
            with self.subTest(takes=takes):
                # Given: wait_for, whose sentence shows the approval alone
                # When: it is given so many things
                # Then: it takes the approval and one or more commands its hook holds back
                self.assertEqual(lanes.fits("wait_for", takes), fits)

    def test_a_lane_showing_two_of_one_place_takes_one_or_more_after_them(self):
        # Given: a lane of one place whose sentence shows the first two things it takes
        two = types.SimpleNamespace(WORDING="Put `<a>`.", SHOWN=2)
        for takes, fits in ((["a", "b"], False), (["a", "b", "c"], True)):
            with self.subTest(takes=takes), mock.patch.dict(lanes.LANES, {"two": two}):
                # When: it is given so many things
                # Then: it takes the two it shows and one or more after them
                self.assertEqual(lanes.fits("two", takes), fits)


class TestSlots(unittest.TestCase):
    def test_each_place_takes_one_thing_in_order(self):
        # Given: test_after, whose wording shows two places, taking an output and a test
        # When: its sentence is made
        # Then: the output stands in the first place and the test in the second
        self.assertEqual(
            lanes.sentence("test_after", ["app.py", "make test"]),
            "After changing `app.py`, pass `make test`.",
        )

    def test_the_last_place_takes_the_rest_as_a_list(self):
        # Given: test_after taking an output and three tests
        # When: its sentence is made
        # Then: the tests are listed in the last place, `or` before the last
        self.assertEqual(
            lanes.sentence("test_after", ["app.py", "a", "b", "c"]),
            "After changing `app.py`, pass `a`, `b` or `c`.",
        )

    def test_every_place_but_the_last_takes_one_thing(self):
        # Given: a lane whose wording shows three places, taking four things
        three = types.SimpleNamespace(WORDING="Put `<a>` into `<b>` by `<c>`.")
        with mock.patch.dict(lanes.LANES, {"three": three}):
            # When: its sentence is made
            said = lanes.sentence("three", ["w", "x", "y", "z"])
        # Then: the first two places take one thing each, and the last the rest
        self.assertEqual(said, "Put `w` into `x` by `y` or `z`.")

    def test_a_lane_counts_the_places_its_wording_shows(self):
        # Given: a lane of one place and one of two
        # When: its places are counted
        # Then: each has as many as its wording shows
        self.assertEqual((lanes.slots("hands_off"), lanes.slots("test_after")), (1, 2))


class TestHeldOn(unittest.TestCase):
    def test_a_lane_is_held_on_the_event_its_module_names_or_on_a_tool_call(self):
        # Given: the lanes lane lays
        # When: the event each is held on is read
        # Then: those on how the subagent ends are held on SubagentStop, every other on PreToolUse
        ending = {"test_after", "end_when", "every_item"}
        for name in lanes.LANES:
            with self.subTest(lane=name):
                held = "SubagentStop" if name in ending else "PreToolUse"
                self.assertEqual(lanes.held_on(name), held)


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
