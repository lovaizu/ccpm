"""The integration cases of S5, the steps in their order: a reporter's mark of a step before a step
before it is done stopped with the step due, marks in order let through, an end before each step
is done stopped with the step's sentence, and a result that a step's rules name as ending the start
letting it end at that step. Each runs `log` and Lane through the double of Claude Code."""

from __future__ import annotations

import pytest
from lane_bench import Bench, ending, opened, reached, started, written


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


@pytest.mark.supports("S5", "S7")
def test_a_result_that_ends_the_start_at_its_step_lets_it_end_with_later_steps_undone(b: Bench):
    """Given `log` whose writer's step `write` names `unclear` among the results that end the start,
    and the writer running at that step
    When it reports `unclear` and ends
    Then its end goes through, though `write` and `report` aren't done, and the main conversation
    reads `unclear`"""
    ending(b, 0, "unclear")
    writer = started(opened(b))
    writer.bash("lane-result unclear")
    assert "unclear" in reached(writer).said


@pytest.mark.supports("S5")
def test_a_result_that_ends_the_start_at_a_later_step_leaves_the_steps_before_it_held(b: Bench):
    """Given `log` whose writer's step `report` names `unclear` among the results that end the
    start, and the writer running at its step `write`
    When it reports `unclear` and ends
    Then the end is stopped with the sentence of `write`, as the steps before `report` aren't
    done"""
    ending(b, 1, "unclear")
    writer = started(opened(b))
    writer.bash("lane-result unclear")
    answer = writer.end("Unclear.")[0]
    assert answer.blocked
    assert "write" in answer.said
