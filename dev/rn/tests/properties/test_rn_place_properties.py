"""The property-based test of a run's name, as rn's Test strategy names it: the orchestrator gives
a short English slug of the work, from the issue's title or the user's words, and the run's
worktree, branch, and folder are named by `<yyyymmdd>-<slug>`, as the architecture's Directory
structure says, so a name of another form leaves a run that no pick-up finds, or a branch git
refuses. The model: one to five words of lower-case English letters and digits, joined by `-`."""

from __future__ import annotations

import re
import string
from datetime import date

import pytest
from fault import Wrong
from hypothesis import given
from hypothesis import strategies as st
from repository.place import named

# A word of a slug, and a slug of one to five of them, as the orchestrator writes one.
WORD = st.text(string.ascii_lowercase + string.digits, min_size=1, max_size=8)
SLUGS = st.lists(WORD, min_size=1, max_size=5).map("-".join)
# Any text that an AI may give in a slug's place: letters of any case and script, digits, marks,
# and spaces.
TEXT = st.text(string.ascii_letters + string.digits + "-_ .'/経理", max_size=40)
DAYS = st.dates(date(2000, 1, 1), date(2099, 12, 31))


def slug(text: str) -> bool:
    """Whether the text is a slug, by the contract's words."""
    return re.fullmatch(r"[a-z0-9]+(-[a-z0-9]+){0,4}", text) is not None


@pytest.mark.supports(
    "test_a_request_makes_the_runs_worktree_and_its_design_tree_with_the_goal_as_put"
)
@given(DAYS, SLUGS | TEXT)
def test_a_runs_name_is_the_day_and_the_slug_or_refused(day: date, given_slug: str):
    """Given any day, and any slug the orchestrator writes, or any text in its place
    When the run's name is made from it
    Then it is `<yyyymmdd>-` and the slug where the model takes it as a slug, and refused as
    Wrong otherwise
    (Model-based, resting on Directory structure's `rn-<yyyymmdd>-<slug>/`.)"""
    if slug(given_slug):
        assert named(day, given_slug) == f"{day:%Y%m%d}-{given_slug}"
    else:
        with pytest.raises(Wrong):
            named(day, given_slug)
