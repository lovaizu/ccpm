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

    def test_a_change_to_the_input_restarts_the_count(self):
        # Given: B-1 and B-2 answered, then review.md changed, then B-1 answered again in a file
        # of its own
        self.write("answers.md", "B-1 B-2")
        self.write("x.md", "B-1")
        calls = [
            helpers.kept_call("Write", file_path="answers.md", content="B-1 B-2"),
            helpers.kept_call("Edit", file_path="review.md", old_string="a", new_string="c"),
            helpers.kept_call("Write", file_path="x.md", content="B-1"),
        ]
        found = helpers.did(self.base, self.plugin, calls)
        # When: the subagent gives its result
        # Then: B-2, answered only before the change, is unanswered
        said = every_item.missing({"input": ["review.md"]}, found)
        self.assertEqual(said, "B-2 of `review.md` unanswered")

    def test_another_input_written_answers_nothing(self):
        # Given: other.md, a second input, written with B-1, B-2 and its own C-1 in it
        text = "- C-1: c\nB-1 B-2\n"
        self.write("other.md", text)
        calls = [helpers.kept_call("Write", file_path="other.md", content=text)]
        found = helpers.did(self.base, self.plugin, calls)
        # When: the subagent gives its result
        # Then: no item of either input is answered by the other
        said = every_item.missing({"input": ["review.md", "other.md"]}, found)
        self.assertEqual(said, "B-1, B-2 of `review.md` unanswered; C-1 of `other.md` unanswered")

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
        # And: an input after it is held still
        said = every_item.missing({"input": ["gone.md", "review.md"]}, found)
        self.assertEqual(said, "`gone.md` is no file to read; B-1, B-2 of `review.md` unanswered")


if __name__ == "__main__":
    unittest.main()
