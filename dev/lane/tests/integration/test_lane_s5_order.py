"""The integration cases of S5, the steps in their order: a reporter's mark of a step before a step
before it is done stopped with the step due, marks in order let through, and an end before each step
is done stopped with the step's sentence. Each runs `log` and Lane through the double of Claude
Code."""

from __future__ import annotations

import pytest
from lane_bench import UNREPORTED, Bench, opened, reached, started, written

pytestmark = UNREPORTED


@pytest.mark.supports("S5", "rule types")
def test_a_step_marked_before_the_step_before_it_is_stopped_with_the_step_due(b: Bench):
    """Given the writer running, its step `write` not done
    When it reports the step `report` done
    Then it reads the sentence of `report` naming `write` as the step due"""
    said = started(opened(b)).bash("lane-step report").said
    assert "report" in said
    assert "write" in said


@pytest.mark.supports("S5")
def test_steps_marked_in_their_order_hold_and_the_end_goes_through(b: Bench):
    """Given the writer running
    When it keeps each step in its order and ends
    Then its end reaches the main conversation"""
    writer = started(opened(b))
    written(writer)
    assert reached(writer) is not None


@pytest.mark.supports("S5")
def test_an_end_before_each_step_is_done_is_stopped_with_the_step_left(b: Bench):
    """Given the writer that kept its step `write` and reported `written`, its step `report` not
    done
    When it ends
    Then the end is stopped with the sentence of `report`"""
    writer = started(opened(b))
    written(writer, report=False)
    answer = writer.end("Done.")[0]
    assert answer.blocked
    assert "report" in answer.said
