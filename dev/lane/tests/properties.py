"""Property-based tests of Lane's code, on many inputs that Hypothesis makes, new on every run, CI
included. A sentence that `lay.py` lays in a step and takes out again leaves the step as the user
wrote it, and an item's ID never counts as answered by a longer ID that holds it."""

from __future__ import annotations

import string
import unittest

from helpers import every_item, sentences, step, testing

hypothesis = testing.hypothesis()
given = hypothesis.given
st = hypothesis.strategies

# The words of a step as the user writes them. They hold no backtick and no line break.
WORDS = st.text(string.ascii_letters + " ,.", min_size=1, max_size=20).map(str.strip).filter(bool)
# A lane's sentence, as lanes/ makes one.
SENTENCES = st.builds(
    lambda w: f"Write only `{w}`.", st.text(string.ascii_lowercase, min_size=1, max_size=8)
)
# An item's ID, such as `B-1` or `KR1.1`.
IDS = st.from_regex(r"[A-Z]{1,2}-?[1-9][0-9]?(\.[1-9])?", fullmatch=True)


class TestSentences(unittest.TestCase):
    @given(
        st.lists(WORDS, min_size=1, max_size=4),
        st.lists(SENTENCES, min_size=1, max_size=3, unique=True),
    )
    def test_sentences_laid_and_taken_out_leave_the_steps_as_they_were(self, steps, said):
        text = "".join(f"{n}. {w}\n" for n, w in enumerate(steps, 1))
        laid = sentences.said(text, step.numbered(text), {1: said}, {})
        self.assertEqual(sentences.said(laid, step.numbered(laid), {}, {1: said}), text)


class TestItems(unittest.TestCase):
    @given(IDS, st.sampled_from(["0", "1", ".2", "-3", "A"]))
    def test_an_id_is_never_answered_by_a_longer_id_that_holds_it(self, item, more):
        longer = item + more if more[0] in "0123456789.-" else more + item
        self.assertFalse(every_item.answered(item, f"See {longer} here."), (item, longer))
