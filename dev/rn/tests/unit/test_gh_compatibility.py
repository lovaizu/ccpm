"""The unit cases of the compatibility test of gh, gh/compatibility.py, as rn's architecture says
under Test strategy: each case compares a line of a record of a run of gh in gh/recorded/ with what
a new gh gave, as its Given says."""

from __future__ import annotations

import copy
import json
from typing import Any

import pytest
from compatibility import Ran, differences, runs
from gh_double import AUTH, PR_VIEW, line

pytestmark = pytest.mark.xfail(strict=True, reason="the comparison is a skeleton, its body unbuilt")

NO_LOGIN = "gh auth status finds no login"
COMMENTS = "gh pr view gives the pull request with its comments"


def as_given(each: dict[str, Any]) -> Ran:
    """What the line shows gh giving."""
    return Ran(each["exit"], each["stdout"], each["stderr"])


@pytest.mark.supports("test_the_double_of_gh_agrees_with_each_recorded_run_of_gh")
def test_runs_take_each_line_of_each_record_of_a_run_and_none_of_the_manual():
    """Given gh/recorded/ with the records of gh 2.102.1 and gh-manual.jsonl
    When the compatibility test lists the lines it runs again
    Then it lists each line of the two records of runs, and none of the manual"""
    found = runs()
    assert {name for name, _ in found} == {AUTH, PR_VIEW}
    assert (PR_VIEW, line(PR_VIEW, COMMENTS)) in found


@pytest.mark.supports("test_the_double_of_gh_agrees_with_each_recorded_run_of_gh")
def test_what_gh_gave_as_the_line_shows_differs_in_nothing():
    """Given the line of gh pr view that gives the pull request with its comments
    When gh gives what the line shows
    Then no difference comes"""
    each = line(PR_VIEW, COMMENTS)
    assert differences(each, as_given(each)) == []


@pytest.mark.supports("test_the_double_of_gh_agrees_with_each_recorded_run_of_gh")
def test_values_that_change_on_each_run_differ_in_nothing():
    """Given the line of gh pr view with its comments, and what gh gave with another URL, comment
    ID, and author
    When the two are compared
    Then no difference comes, as only the fields and their types must agree"""
    each = line(PR_VIEW, COMMENTS)
    shown = json.loads(each["stdout"])
    shown["url"] = "https://github.com/someone/else/pull/7"
    shown["comments"][0].update(id="IC_other", author={"login": "someone"})
    assert differences(each, Ran(0, json.dumps(shown), "")) == []


@pytest.mark.supports("test_the_double_of_gh_agrees_with_each_recorded_run_of_gh")
def test_a_field_that_gh_no_longer_gives_is_a_difference_naming_the_event_and_the_field():
    """Given the line of gh pr view with its comments, and what gh gave without `isDraft`
    When the two are compared
    Then one difference names the line's event and `isDraft`"""
    each = line(PR_VIEW, COMMENTS)
    shown = json.loads(each["stdout"])
    del shown["isDraft"]
    (found,) = differences(each, Ran(0, json.dumps(shown), ""))
    assert COMMENTS in found and "isDraft" in found


@pytest.mark.supports("test_the_double_of_gh_agrees_with_each_recorded_run_of_gh")
def test_another_exit_code_is_a_difference_naming_the_event():
    """Given the line of gh auth status that finds no login, which exits 1
    When gh exits 4 with the same words
    Then one difference names the line's event and both exit codes"""
    each = line(AUTH, NO_LOGIN)
    (found,) = differences(each, Ran(4, each["stdout"], each["stderr"]))
    assert NO_LOGIN in found and "1" in found and "4" in found


@pytest.mark.supports("test_the_double_of_gh_agrees_with_each_recorded_run_of_gh")
def test_other_words_on_stderr_are_a_difference_naming_the_event():
    """Given the line of gh auth status that finds no login
    When gh says on stderr that no account is logged in, in other words
    Then one difference names the line's event"""
    each = copy.deepcopy(line(AUTH, NO_LOGIN))
    (found,) = differences(each, Ran(1, "", "No account is logged in. Run gh auth login.\n"))
    assert NO_LOGIN in found
