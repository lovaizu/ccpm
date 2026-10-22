"""every_item: as the subagent is about to end, an item of the input whose key stands in neither its
last reply nor a file it wrote in this run is a drift; an item is a top-level Markdown list item
keyed by the ID it begins with, and one that begins with none is not counted."""

import os
import unittest

import helpers
from helpers import call, every_item, testing, writing

TAKES = ["review.md"]
# A review of two findings, each keyed by its ID, with a nested item and prose beside them.
REVIEW = """# Review

Findings, B-1 first.

- B-1: the step names no output.
  - B-9: a note under B-1, not an item of its own.
- **B-2** the hook runs twice.
"""


class EveryItemTest(testing.FolderTest):
    def setUp(self) -> None:
        super().setUp()
        self.write(os.path.join(self.base, "review.md"), REVIEW)

    def drifts(self, reply, *calls, takes=TAKES):
        """Whether the subagent drifts, about to end with the reply, having made the calls in the
        test's folder."""
        made = helpers.made(self.base, list(calls))
        return every_item.drifts(call.End(made, reply, False), takes)


class TestReply(EveryItemTest):
    def test_a_reply_naming_every_key_is_no_drift(self):
        # Given: the review of B-1 and B-2
        # When: the subagent ends with a reply answering each by its key
        # Then: it is no drift, the nested B-9 not being an item
        self.assertFalse(self.drifts("B-1: fixed. B-2: fixed."))

    def test_a_reply_leaving_a_key_out_drifts(self):
        # Given: the review of B-1 and B-2
        # When: the subagent ends with a reply answering B-1 alone
        # Then: it is a drift
        self.assertTrue(self.drifts("B-1: fixed."))

    def test_a_key_within_another_word_does_not_answer_it(self):
        for reply in ("B-12 and B-2", "B-1.2 and B-2", "AB-1 and B-2", "B-1a and B-2"):
            with self.subTest(reply=reply):
                # Given: the review of B-1 and B-2
                # When: the subagent's reply holds B-1 only within another word
                # Then: it is a drift
                self.assertTrue(self.drifts(reply))

    def test_a_key_set_off_by_marks_answers_it(self):
        # Given: the review of B-1 and B-2
        # When: the reply sets each key off in bold, code or a bracket, or ends a sentence with it
        # Then: it is no drift
        self.assertFalse(self.drifts("**B-1** done; see (`B-2`)."))


class TestWritten(EveryItemTest):
    def test_a_key_in_a_file_written_in_this_run_answers_it(self):
        # Given: an answer file written in this run holding B-2
        self.write(os.path.join(self.base, "answers.md"), "- B-2: fixed\n")
        # When: the subagent ends with a reply answering B-1
        # Then: it is no drift
        self.assertFalse(self.drifts("B-1 fixed", writing("answers.md")))

    def test_a_file_not_written_in_this_run_answers_nothing(self):
        for calls in ([], [writing("answers.md", helpers.Failed("stopped"))]):
            with self.subTest(calls=calls):
                # Given: an answer file holding B-2, there from before or its write failed
                self.write(os.path.join(self.base, "answers.md"), "- B-2: fixed\n")
                # When: the subagent ends with a reply answering B-1
                # Then: it is a drift
                self.assertTrue(self.drifts("B-1 fixed", *calls))

    def test_the_input_written_answers_nothing(self):
        # Given: the input itself rewritten in this run, holding every key still
        # When: the subagent ends with a reply answering B-1
        # Then: it is a drift, as the input holds its keys whether answered or not
        self.assertTrue(self.drifts("B-1 fixed", writing("review.md")))

    def test_a_written_file_not_there_answers_nothing(self):
        # Given: an answer file written in this run and then gone
        # When: the subagent ends with a reply answering B-1
        # Then: it is a drift
        self.assertTrue(self.drifts("B-1 fixed", writing("answers.md")))


class TestItems(EveryItemTest):
    def test_the_items_a_check_can_tell_are_keyed_by_their_ids(self):
        # Given: an input of top-level items in each marker, each ID set off as the AI writes it,
        # and lines that are no keyed item
        text = """1. R33 (lane's as_printed) holds.
2) KR1.1: defects.
* `T18` brought forward.
+ [G-1] the builder.
- B2B sales, no ID followed by a mark.
- Flow: no number.
 - X-1 not at the line's start.
Prose naming Y-1.
- z-1 in small letters.
-Q-1 with no blank after the marker.
"""
        self.write(os.path.join(self.base, "review.md"), text)
        # When: the subagent ends with a reply naming the four IDs
        # Then: it is no drift, the other lines being no items to answer
        self.assertFalse(self.drifts("R33 KR1.1 T18 G-1"))
        # And: leaving any of the four out is a drift
        for left in ("R33", "KR1.1", "T18", "G-1"):
            with self.subTest(left=left):
                reply = " ".join(k for k in ("R33", "KR1.1", "T18", "G-1") if k != left)
                self.assertTrue(self.drifts(reply))

    def test_an_input_of_no_keyed_items_or_none_tells_nothing(self):
        for takes in (["plain.md"], ["missing.md"], ["$IN"]):
            with self.subTest(takes=takes):
                # Given: an input whose items begin with no ID, one not there, or one named by no
                # settled path
                self.write(os.path.join(self.base, "plain.md"), "- fix the step\n- fix the hook\n")
                # When: the subagent ends with any reply
                # Then: it is no drift, as no item can be told answered
                self.assertFalse(self.drifts("", takes=takes))

    def test_every_input_taken_has_its_items_answered(self):
        # Given: two inputs, the second of one item C-1
        self.write(os.path.join(self.base, "more.md"), "- C-1: one more\n")
        # When: the subagent ends answering the first's items alone
        # Then: it is a drift
        self.assertTrue(self.drifts("B-1 B-2", takes=["review.md", "more.md"]))


if __name__ == "__main__":
    unittest.main()
