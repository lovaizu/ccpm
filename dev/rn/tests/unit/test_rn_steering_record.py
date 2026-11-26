"""The unit cases of steering/record.py, what each change makes of a run's steering: the pruner's
first result, a later one that keeps each status the steering holds, one with no steps or issues,
and each mark of a step or a deliverable, with each refusal."""

from __future__ import annotations

from typing import Any

import pytest
import rn_files
from fault import Wrong
from steering.record import deliverable_marked, step_marked, taken_in

STEP = rn_files.WAY


def result(**fields: Any) -> dict[str, Any]:
    """A pruner's result of the walkthrough, with the fields given."""
    return {"message": "the user picked printing", "ost": rn_files.ost(), **fields}


def test_a_first_result_makes_the_steering_with_each_step_open() -> None:
    """Given a run with no steering, and the pruner's result with its tree, issues, and steps.
    When the result is taken in.
    Then the steering holds the tree, the issues, and each step and deliverable open."""
    made = taken_in(None, result(issues={"closes": [38], "refs": []}, steps=[STEP]))
    assert made == rn_files.steering()


def test_a_first_result_with_no_issues_or_steps_holds_none() -> None:
    """Given a run with no steering, and a result with its tree alone, the need not picked.
    When the result is taken in.
    Then the steering holds the tree, no issue, and no step."""
    made = taken_in(None, {"message": "m", "ost": rn_files.ost(target=None)})
    assert made["state"] == {"issues": {"closes": [], "refs": []}, "steps": []}


def test_a_later_result_keeps_each_status_the_steering_holds() -> None:
    """Given a steering whose step is trying with its command done, and a result that names the
    step again with a deliverable added.
    When the result is taken in.
    Then the step stays trying, the command done, and the new deliverable open."""
    held = rn_files.steering([rn_files.step("trying", done=(rn_files.COMMAND,))])
    added = {
        **STEP,
        "deliverables": [*STEP["deliverables"], {"path": "docs/rules.md", "kind": "readme"}],
    }
    made = taken_in(held, result(steps=[added]))
    step = made["state"]["steps"][0]
    assert (step["status"], [each["status"] for each in step["deliverables"]]) == (
        "trying",
        ["done", "open", "open"],
    )


def test_a_later_result_with_no_steps_keeps_those_the_steering_holds() -> None:
    """Given a steering with its step trying, and a result with a new question and no steps.
    When the result is taken in.
    Then the steps and the issues stay, and the tree is the result's."""
    held = rn_files.steering([rn_files.step("trying")])
    made = taken_in(held, result(ost=rn_files.ost(questions=["Which printer?"])))
    assert (made["state"], made["ost"]["questions"]) == (held["state"], ["Which printer?"])


def test_a_step_with_each_deliverable_done_is_marked_trying() -> None:
    """Given a steering whose step has each deliverable done.
    When step 1 is marked trying.
    Then it's trying, and its words are given."""
    held = rn_files.steering([rn_files.step(done=(rn_files.COMMAND, rn_files.GUIDE))])
    marked, words = step_marked(held, 1, "trying")
    assert (marked["state"]["steps"][0]["status"], words) == ("trying", rn_files.SETTLES)


@pytest.mark.parametrize(
    ("number", "status", "says"),
    [
        (2, "done", "no step 2"),
        (0, "done", "no step 0"),
        (1, "waiting", "isn't a step's status"),
        (1, "trying", "docs/guide.md not done"),
    ],
)
def test_a_mark_of_a_step_that_can_not_be_is_refused(number: int, status: str, says: str) -> None:
    """Given a steering of one step whose command alone is done.
    When a step that isn't there, a status that isn't one, or trying is marked.
    Then Wrong is raised, saying why."""
    held = rn_files.steering([rn_files.step(done=(rn_files.COMMAND,))])
    with pytest.raises(Wrong, match=says):
        step_marked(held, number, status)


def test_a_deliverable_is_marked_done() -> None:
    """Given a steering whose step is open.
    When the command is marked done.
    Then it's done, and the step stays open."""
    marked = deliverable_marked(rn_files.steering(), rn_files.COMMAND, "done")
    step = marked["state"]["steps"][0]
    assert (step["deliverables"][0]["status"], step["status"]) == ("done", "open")


def test_a_deliverable_marked_open_opens_its_step_again() -> None:
    """Given a steering whose step is trying with each deliverable done.
    When the command is marked open, as it's made again.
    Then the command and its step are open, and the guide stays done."""
    held = rn_files.steering([rn_files.step("trying", done=(rn_files.COMMAND, rn_files.GUIDE))])
    step = deliverable_marked(held, rn_files.COMMAND, "open")["state"]["steps"][0]
    assert (step["status"], [each["status"] for each in step["deliverables"]]) == (
        "open",
        ["open", "done"],
    )


@pytest.mark.parametrize(
    ("path", "status", "says"),
    [
        ("x.md", "done", "no step names"),
        (rn_files.COMMAND, "trying", "isn't a deliverable's status"),
    ],
)
def test_a_mark_of_a_deliverable_that_can_not_be_is_refused(
    path: str, status: str, says: str
) -> None:
    """Given the walkthrough's steering.
    When a path that no step names, or a status that isn't a deliverable's, is marked.
    Then Wrong is raised, saying why."""
    with pytest.raises(Wrong, match=says):
        deliverable_marked(rn_files.steering(), path, status)
