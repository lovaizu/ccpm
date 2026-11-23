"""The unit cases of runner/command.py, what `queue.py run` takes and the exit code it ends with:
`main`, of the stacker's handoff on its standard input, of arguments, of input not in the
handoff's form and of none, and of a queue that another runner holds, each with a stand-in for
`runner.schedule.carry`."""

from __future__ import annotations

from typing import Any

import pytest
from record.lock import Held
from runner import handoff, schedule
from runner.command import main
from runner.handoff import Carried, Handoff
from stacker.queue_file import Task

pytestmark = pytest.mark.xfail(strict=True, reason="overnight's parts are not built yet")

GIVEN = Handoff(
    "/home/dev/overnight/tonight.json",
    "23:00",
    (Carried(Task("review", "/home/dev/overnight/review.md", "/home/dev/work/shop", False), "s"),),
)


def carried_by(monkeypatch: Any, refusal: Exception | None = None) -> list[Handoff]:
    """Puts a stand-in for `runner.schedule.carry` that raises the refusal, where one is given, and
    gives each handoff it was asked to carry."""
    asked: list[Handoff] = []

    def stand_in(given: Handoff) -> None:
        asked.append(given)
        if refusal is not None:
            raise refusal

    monkeypatch.setattr(schedule, "carry", stand_in)
    return asked


@pytest.mark.supports(
    "test_the_walkthroughs_queue_is_stacked_and_each_task_finishes_past_the_limit"
)
def test_the_stackers_handoff_is_carried_and_gives_0(monkeypatch: Any):
    """Given the stacker's handoff of a queue on the standard input, and no arguments
    When `queue.py run` runs
    Then it carries that queue, and gives 0"""
    asked = carried_by(monkeypatch)

    code, _, _ = main([], handoff.encode(GIVEN))

    assert (code, asked) == (0, [GIVEN])


@pytest.mark.supports(
    "test_the_walkthroughs_queue_is_stacked_and_each_task_finishes_past_the_limit"
)
def test_arguments_give_the_usage_carrying_nothing(monkeypatch: Any):
    """Given the stacker's handoff, and the argument `tonight.json`
    When `queue.py run` runs
    Then it gives 2 with the usage, and carries nothing"""
    asked = carried_by(monkeypatch)

    code, out, err = main(["tonight.json"], handoff.encode(GIVEN))

    assert (code, "usage" in (out + err).lower(), asked) == (2, True, [])


@pytest.mark.supports(
    "test_the_walkthroughs_queue_is_stacked_and_each_task_finishes_past_the_limit"
)
@pytest.mark.parametrize("stdin", ["", '{"queue": 1}'], ids=["none", "another form"])
def test_input_not_of_the_handoffs_form_gives_1_with_whats_wrong(monkeypatch: Any, stdin: str):
    """Given no standard input, or JSON of another form
    When `queue.py run` runs
    Then it gives 1 with what's wrong, and carries nothing"""
    asked = carried_by(monkeypatch)

    code, out, err = main([], stdin)

    assert (code, bool(out + err), asked) == (1, True, [])


@pytest.mark.supports("test_a_runner_started_on_a_queue_that_another_runner_carries_runs_no_task")
def test_a_queue_another_runner_holds_gives_1_with_whats_wrong(monkeypatch: Any):
    """Given the stacker's handoff of a queue whose lock another runner holds
    When `queue.py run` runs
    Then it gives 1 with what's wrong"""
    carried_by(monkeypatch, Held("/home/dev/overnight/tonight/runner.lock"))

    code, out, err = main([], handoff.encode(GIVEN))

    assert (code, bool(out + err)) == (1, True)
