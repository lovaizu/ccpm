"""The integration cases of S7, the run moved by the result its AI gives: an end with no result, or
one that the role's rule doesn't name, stopped with the results it may give, and each result that a
reporter gives moving the run by its route. Each runs `log` and Lane through the double of Claude
Code."""

from __future__ import annotations

import pytest
from lane_bench import UNREPORTED, Bench, opened, reviewed, started, text, to_review, written

pytestmark = UNREPORTED


@pytest.mark.supports("S7", "rule types")
def test_an_end_with_no_result_is_stopped_with_the_results_it_may_give(b: Bench):
    """Given the reviewer running, with no result reported
    When it ends
    Then the end is stopped with the sentence of its step, naming `good`, `more`, and `split`"""
    reviewer = started(to_review(b), "log:reviewer")
    answer = reviewer.end("Looks good.")[0]
    assert answer.blocked
    for result in ("good", "more", "split"):
        assert result in answer.said


@pytest.mark.supports("S7")
def test_an_end_with_a_result_that_the_rule_doesnt_name_is_stopped(b: Bench):
    """Given the reviewer that reported `fine`
    When it ends
    Then the end is stopped naming the results it may give"""
    reviewer = started(to_review(b), "log:reviewer")
    reviewer.bash("lane-result fine")
    answer = reviewer.end("Fine.")[0]
    assert answer.blocked
    assert "good" in answer.said


@pytest.mark.supports("S7")
def test_a_result_in_the_reply_alone_moves_nothing(b: Bench):
    """Given the writer that kept each step but reported no result
    When it ends replying `written`
    Then the end is stopped with the results it may give"""
    writer = started(opened(b))
    written(writer, result=None)
    answer = writer.end("written")[0]
    assert answer.blocked
    assert "written" in answer.said


@pytest.mark.supports("S7", "Route")
def test_the_reviewers_more_makes_the_writer_due_again(b: Bench):
    """Given the reviewer due
    When it reports `more` and ends
    Then the main conversation reads `more` and the writer due with its text"""
    answer = reviewed(to_review(b), "more")
    assert "more" in answer.said
    assert text("log:writer") in answer.said
