"""A role's Step list: read from the numbered list under its file's `## Steps`, and a sentence laid
at the end of one of its steps."""

from __future__ import annotations

import unittest

import lanetest  # noqa: F401  (puts Lane's code on the path)
from domain import steps

FILE = """---
name: writer
---

Intro.

## Steps

1. Read `CHANGELOG.md`.
2. Read the commits
   with `git log --oneline`.
3. Write the entries.

## Notes

- 9. Not a step.
"""


class Read(unittest.TestCase):
    def test_each_numbered_item_under_steps_is_a_step(self) -> None:
        self.assertEqual(
            steps.read(FILE),
            {
                1: "Read `CHANGELOG.md`.",
                2: "Read the commits with `git log --oneline`.",
                3: "Write the entries.",
            },
        )

    def test_a_step_may_run_on_over_several_lines(self) -> None:
        text = "Intro.\n## Steps\n1. One\n   two\n   three\n2. Four\n"
        self.assertEqual(steps.read(text), {1: "One two three", 2: "Four"})

    def test_a_blank_line_under_the_heading_leaves_each_step_whole(self) -> None:
        self.assertEqual(steps.read("## Steps\n\n1. One\n   two\n"), {1: "One two"})

    def test_a_line_indented_by_one_blank_goes_on_its_step(self) -> None:
        self.assertEqual(steps.read("## Steps\n1. One\n two\n"), {1: "One two"})

    def test_an_indented_line_before_the_first_step_is_no_step(self) -> None:
        self.assertEqual(steps.read("## Steps\n   note\n1. One\n"), {1: "One"})

    def test_an_indented_line_after_a_paragraph_is_no_step(self) -> None:
        text = "## Steps\n1. One\nA paragraph.\n   indented\n2. Two\n"
        self.assertEqual(steps.read(text), {1: "One", 2: "Two"})

    def test_a_numbered_list_under_a_later_heading_is_no_step(self) -> None:
        self.assertEqual(steps.read("## Steps\n1. One\n## Notes\n2. Two\n"), {1: "One"})

    def test_a_file_with_no_steps_heading_is_refused(self) -> None:
        with self.assertRaisesRegex(steps.StepsError, "no `## Steps` heading"):
            steps.read("---\nname: writer\n---\n\n1. A step.\n")

    def test_a_steps_heading_with_no_numbered_item_is_refused(self) -> None:
        with self.assertRaisesRegex(steps.StepsError, "no numbered step under `## Steps`"):
            steps.read("## Steps\n\nNothing here.\n")


class Laid(unittest.TestCase):
    def test_the_sentence_ends_the_step(self) -> None:
        laid = steps.laid(FILE, 1, "Run only `x`.", [])
        self.assertIn("1. Read `CHANGELOG.md`. Run only `x`.\n2. Read the commits\n", laid)

    def test_the_sentence_ends_the_last_line_of_a_step_of_two_lines(self) -> None:
        laid = steps.laid(FILE, 2, "Run only `git log --oneline`.", [])
        self.assertIn("   with `git log --oneline`. Run only `git log --oneline`.\n3.", laid)

    def test_every_other_line_stays(self) -> None:
        laid = steps.laid(FILE, 3, "Run only `x`.", [])
        self.assertEqual(laid.replace(" Run only `x`.", ""), FILE)

    def test_a_sentence_laid_already_is_not_laid_twice(self) -> None:
        once = steps.laid(FILE, 1, "Run only `x`.", [])
        self.assertEqual(steps.laid(once, 1, "Run only `x`.", ["Run only `x`."]), once)

    def test_a_sentence_laid_before_goes(self) -> None:
        once = steps.laid(FILE, 1, "Run only `x`.", [])
        again = steps.laid(once, 1, "Run only `y`.", ["Run only `x`."])
        self.assertIn("1. Read `CHANGELOG.md`. Run only `y`.\n", again)

    def test_a_step_the_list_lacks_is_refused(self) -> None:
        with self.assertRaisesRegex(steps.StepsError, "no step 7"):
            steps.laid(FILE, 7, "Run only `x`.", [])


if __name__ == "__main__":
    unittest.main()
