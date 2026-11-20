"""The property-based test of a run's name, as rn's Test strategy names it: the user types any words
after /rn:up, and the run's worktree, branch, and folder are named by `<yyyymmdd>-<goal>`, as the
architecture's Directory structure says, so a name of another form leaves a run that no pick-up
finds, or a branch git refuses. The model: at most five of the words, each lower case with each
character other than a letter or a digit left out, joined by `-`."""

from __future__ import annotations

import string
from datetime import date

import pytest
from fault import Wrong
from hypothesis import given
from hypothesis import strategies as st
from repository.place import named

pytestmark = pytest.mark.xfail(
    strict=True, reason="repository.place's bodies raise NotImplementedError"
)

MARKS = ",.;:!?'\"()/-_*#&"
# A word as a person types it: letters and digits, with marks around them.
WORD = st.builds(
    lambda before, core, after: before + core + after,
    st.text(MARKS, max_size=2),
    st.text(string.ascii_letters + string.digits, min_size=1, max_size=8),
    st.text(MARKS, max_size=2),
)
DAYS = st.dates(date(2000, 1, 1), date(2099, 12, 31))


def model(words: list[str]) -> str:
    """The goal part of the name, by the contract's words."""
    return "-".join("".join(c for c in w if c.isalnum()).lower() for w in words[:5])


@pytest.mark.supports(
    "test_a_request_makes_the_runs_worktree_and_its_design_tree_with_the_goal_as_put"
)
@given(DAYS, st.lists(WORD, min_size=1, max_size=9), st.sampled_from([" ", "  ", "\t", "\n"]))
def test_a_runs_name_is_the_day_and_at_most_five_of_the_words(
    day: date, words: list[str], gap: str
):
    """Given any day, and any words with a letter or a digit each, as a person types them, joined by
    any space
    When the run's name is made from them
    Then it is `<yyyymmdd>-` and the model's goal: at most five of the words, lower case, with
    each mark left out, joined by `-`
    (Model-based, resting on Directory structure's `rn-<yyyymmdd>-<goal>/`.)"""
    assert named(day, gap.join(words)) == f"{day:%Y%m%d}-{model(words)}"


@pytest.mark.supports(
    "test_a_request_makes_the_runs_worktree_and_its_design_tree_with_the_goal_as_put"
)
@given(DAYS, st.text(MARKS + " \t\n", max_size=12))
def test_words_with_no_letter_or_digit_are_refused(day: date, words: str):
    """Given any day, and any words of marks and spaces alone, or none
    When the run's name is made from them
    Then it's refused as Wrong
    (Invariant, resting on Directory structure's `rn-<yyyymmdd>-<goal>/`.)"""
    with pytest.raises(Wrong):
        named(day, words)
