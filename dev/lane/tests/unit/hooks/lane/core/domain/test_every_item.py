"""every_item: a result is given only once each item of an input the lane names, read at the items
port, has its ID standing as a word of its own in a file the subagent wrote in this run, the input
left out."""

from __future__ import annotations

import unittest

import helpers
from helpers import every_item

REVIEW = "- B-1: a\n- **B-2**: b\n"


class TestMissing(helpers.PluginTest):
    def setUp(self) -> None:
        super().setUp()
        self.write("review.md", REVIEW)

    def missing(self, written: dict, run: list | None = None, items=None) -> str:
        """What every_item taking review.md finds missing, the files of `written` written by the
        subagent with their texts, its calls of this run those given or all."""
        calls = []
        for path, text in written.items():
            self.write(path, text)
            calls.append(helpers.kept_call("Write", file_path=path, content=text))
        found = helpers.did(self.base, self.plugin, calls, run, items)
        return every_item.missing({"input": ["review.md"]}, found)

    def test_every_item_answered_in_a_file_written_is_nothing_missing(self):
        # Given: each ID in a file the subagent wrote
        # When: it gives its result
        # Then: nothing is missing
        self.assertEqual(self.missing({"answers.md": "B-1 fixed. B-2 kept."}), "")

    def test_an_item_unanswered_is_named(self):
        for written in (
            {"answers.md": "B-1 fixed."},
            {"answers.md": "B-1 fixed. B-21 and B-2.1 and AB-2."},
            {"review.md": REVIEW + "B-2 done\n", "answers.md": "B-1"},
        ):
            with self.subTest(written=written):
                # Given: B-2 nowhere, only in IDs it begins, or only in the input rewritten
                # When: the subagent gives its result
                # Then: B-2 is named as unanswered
                self.assertEqual(self.missing(written), "B-2 of `review.md` unanswered")

    def test_a_file_written_in_an_earlier_run_answers_nothing(self):
        # Given: the answers written in an earlier run alone
        # When: the subagent gives its result
        # Then: both are unanswered
        self.assertEqual(
            self.missing({"answers.md": "B-1 B-2"}, run=[]), "B-1, B-2 of `review.md` unanswered"
        )

    def test_the_items_are_read_as_given_and_an_input_not_there_is_named(self):
        # Given: items read by an adapter, giving R1 alone
        # When: the subagent gives its result with R1 answered
        # Then: nothing is missing
        self.assertEqual(self.missing({"a.md": "R1"}, items=lambda path, text: ["R1"]), "")
        # And: an input not there is named so
        found = helpers.did(self.base, self.plugin)
        said = every_item.missing({"input": ["gone.md"]}, found)
        self.assertEqual(said, "`gone.md` is no file to read")


if __name__ == "__main__":
    unittest.main()
