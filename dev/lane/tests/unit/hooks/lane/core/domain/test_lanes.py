"""The lanes lane lays, by their names, and the sentence of each, made from its wording with what
it takes, which the step says and the guard tells."""

import unittest

from helpers import lanes


class TestLanes(unittest.TestCase):
    def test_the_lanes_laid_are_run_only_and_write_only(self):
        # Given: the lanes this version lays
        # When: they are listed
        # Then: they are run_only and write_only
        self.assertEqual(sorted(lanes.LANES), ["run_only", "write_only"])

    def test_each_lane_has_its_action_and_wording_as_docs_lanes_md_gives_them(self):
        for lane, action, wording in (
            ("run_only", "run", "Run only `<commands>`."),
            ("write_only", "write", "Write only `<output>`."),
        ):
            with self.subTest(lane=lane):
                # Given: the lane's row of docs/lanes.md
                # When: its module is read
                # Then: it has the row's action and wording
                self.assertEqual(
                    (lanes.LANES[lane].ACTION, lanes.LANES[lane].WORDING), (action, wording)
                )


class TestSentence(unittest.TestCase):
    def test_one_thing_taken_is_put_in_its_quotes(self):
        # Given: run_only taking one command
        # When: its sentence is made
        # Then: the command is in quotes in its place
        self.assertEqual(
            lanes.sentence("run_only", ["git log --oneline"]), "Run only `git log --oneline`."
        )

    def test_things_taken_are_listed_with_commas_and_or_before_the_last(self):
        for takes, said in (
            (["a.md", "b.md"], "Write only `a.md` or `b.md`."),
            (["a.md", "b.md", "c/"], "Write only `a.md`, `b.md` or `c/`."),
        ):
            with self.subTest(takes=takes):
                # Given: write_only taking two or three outputs
                # When: its sentence is made
                # Then: each is quoted, listed with commas and or before the last
                self.assertEqual(lanes.sentence("write_only", takes), said)

    def test_a_take_is_put_in_as_it_is_written(self):
        # Given: a command holding a backslash and a comma
        take = r"grep -c '\d,' notes.md"
        # When: run_only's sentence is made
        # Then: the command is put in word for word
        self.assertEqual(lanes.sentence("run_only", [take]), f"Run only `{take}`.")


if __name__ == "__main__":
    unittest.main()
