"""The unit cases of sentences.py, how rn splits Markdown words into sentences: a sentence turns
on the marks that end, join, or hold it, so the cases take one for each, and blank words."""

from __future__ import annotations

import pytest
from sentences import sentences


def test_sentences_split_after_a_full_stop_a_question_mark_or_an_exclamation_mark():
    """Given words of three sentences, ending with `.`, `?`, and `!`
    When they're split into sentences
    Then they give the three"""
    assert sentences("It runs. Does it stop? No!") == ["It runs.", "Does it stop?", "No!"]


def test_sentences_split_after_a_quote_that_closes_a_sentence():
    """Given a sentence that ends inside a quote, and a sentence after it
    When they're split into sentences
    Then they give the two"""
    assert sentences('rn says "Done." You merge.') == ['rn says "Done."', "You merge."]


def test_sentences_keep_a_code_span_and_a_link_whole():
    """Given a sentence whose code span and link each hold a full stop before a space
    When it's split into sentences
    Then it gives the one sentence"""
    text = "Run `a. b` as [the guide. Here](a.md) says."
    assert sentences(text) == [text]


@pytest.mark.parametrize(
    "text",
    ["See [the `a. b` page](a.md) here.", "A NUL \x000\x00 stays as written."],
    ids=["a code span in a link", "a NUL around digits"],
)
def test_sentences_give_back_each_character_of_the_text(text: str):
    """Given a sentence with a code span inside a link, or NULs around digits
    When it's split into sentences
    Then it gives the one sentence as written"""
    assert sentences(text) == [text]


def test_sentences_split_at_a_newline():
    """Given words with a newline, which a line that ends with a backslash gives
    When they're split into sentences
    Then the line before the newline is a sentence of its own"""
    assert sentences("One generator over several\nIt costs less.") == [
        "One generator over several",
        "It costs less.",
    ]


def test_sentences_of_blank_words_are_none():
    """Given words that are blank
    When they're split into sentences
    Then they give none"""
    assert sentences(" ") == []
