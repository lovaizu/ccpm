"""The run_only type: its sentence, the takes it refuses, and the commands its check lets go."""

from __future__ import annotations

import unittest

import lanetest  # noqa: F401  (puts Lane's code on the path)
from domain import lanes

RUN_ONLY = lanes.TYPES["run_only"]


class Sentence(unittest.TestCase):
    def test_one_command_is_named_in_backticks(self) -> None:
        self.assertEqual(RUN_ONLY.sentence(["git log --oneline"]), "Run only `git log --oneline`.")

    def test_two_commands_are_joined_by_or(self) -> None:
        self.assertEqual(
            RUN_ONLY.sentence(["git log", "git diff"]), "Run only `git log` or `git diff`."
        )


class Refused(unittest.TestCase):
    def test_a_command_is_taken(self) -> None:
        self.assertEqual(RUN_ONLY.refused(["git log --oneline"]), "")

    def test_no_command_is_refused(self) -> None:
        self.assertEqual(RUN_ONLY.refused([]), "run_only takes at least one command")

    def test_a_blank_command_is_refused(self) -> None:
        self.assertEqual(RUN_ONLY.refused(["git log", " "]), "run_only takes no blank command")

    def test_a_command_with_a_backtick_is_refused(self) -> None:
        self.assertEqual(
            RUN_ONLY.refused(["echo `date`"]),
            "run_only takes no command with a backtick, as its sentence names each in backticks",
        )


class Allows(unittest.TestCase):
    def test_the_command_word_for_word_goes_on(self) -> None:
        self.assertTrue(RUN_ONLY.allows("git log --oneline", ["git log --oneline"]))

    def test_blanks_at_the_ends_go_on(self) -> None:
        self.assertTrue(RUN_ONLY.allows("  git log --oneline\n", ["git log --oneline"]))

    def test_another_command_stops(self) -> None:
        self.assertFalse(RUN_ONLY.allows("git commit -m x", ["git log --oneline"]))

    def test_the_command_with_more_after_it_stops(self) -> None:
        self.assertFalse(RUN_ONLY.allows("git log --oneline; git commit", ["git log --oneline"]))

    def test_the_command_in_other_spacing_stops(self) -> None:
        self.assertFalse(RUN_ONLY.allows("git  log --oneline", ["git log --oneline"]))

    def test_any_named_command_goes_on(self) -> None:
        self.assertTrue(RUN_ONLY.allows("git diff", ["git log", "git diff"]))


if __name__ == "__main__":
    unittest.main()
