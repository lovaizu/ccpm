"""The unit cases of steering/record.py, what each change makes of the work's steering: the
orchestrator's first aim, each new task given the next id, a later aim that keeps where each task
is on its way and the stage, a task the aim leaves out canceled, what the aim says comes next,
each result moving a task on or completing it, and each mark of the stage, with each refusal."""

from __future__ import annotations

from typing import Any

import pytest
import rn_files
from fault import Wrong
from steering.record import LIMIT, marked, moved, taken_in


def test_a_first_aim_makes_the_steering() -> None:
    """Given the work with no steering and no closed task, and an aim with its tree, tasks, and
    decision.
    When the aim is taken in.
    Then the steering holds each, the tasks with ids from 001 in their order, none started, and
    no stage, its version for the command to mark, and no task is canceled."""
    made, canceled = taken_in(None, rn_files.aim(), [])
    assert ({**made, "rn": rn_files.VERSION}, canceled) == (rn_files.steering(), [])


def command(steering: dict[str, Any]) -> dict[str, Any]:
    """The command's task, the first of the steering's."""
    return steering["tasks"][0]


def holding(stage: str | None = None, **fields: Any) -> dict[str, Any]:
    """The walkthrough's steering at the stage given, the command's task with the fields given."""
    held = rn_files.steering(stage=stage)
    command(held).update(fields)
    return held


def told(next_: str) -> dict[str, Any]:
    """An aim that keeps each task by its id and says what the command takes next."""
    held = rn_files.aim(rn_files.tasks())
    command(held)["next"] = next_
    return held


def test_a_new_task_takes_the_id_past_the_steering_and_the_closed_tasks() -> None:
    """Given a steering holding 001 and 002, and a closed task 005.
    When an aim that keeps both and adds a task is taken in.
    Then the new task takes 006, as an id is never given again."""
    aim = rn_files.aim(rn_files.tasks())
    aim["tasks"].append({"task": "Print a second page.", "kind": "code"})
    closed = [{**rn_files.tasks()[0], "id": "005", "closed": "canceled"}]
    made, _ = taken_in(rn_files.steering(), aim, closed)
    assert [each["id"] for each in made["tasks"]] == ["001", "002", "006"]


def test_a_later_aim_keeps_where_each_task_is_and_the_stage() -> None:
    """Given a steering in the user's hands whose command is at its evaluator, once evaluated, in
    02-content, and an aim that puts the guide first and rewords the command's task.
    When the aim is taken in.
    Then the command's task keeps its next role, its evaluated Rounds, and its entry, with the
    aim's words, in the aim's order, and the stage stays."""
    held = holding("trying", next="evaluator", evaluated=1, entry="02-content")
    aim = rn_files.aim(rn_files.tasks())
    aim["tasks"].reverse()
    aim["tasks"][1]["task"] = "Print one invoice."
    made, canceled = taken_in(held, aim, [])
    assert made["tasks"][1] == {**command(held), "task": "Print one invoice."}
    assert (made["tasks"][0]["id"], made["stage"], canceled) == (rn_files.GUIDE_ID, "trying", [])


def test_a_task_the_aim_leaves_out_is_canceled() -> None:
    """Given a steering whose command works in 01-content.
    When an aim that keeps only the guide is taken in.
    Then the steering holds the guide alone, and the command comes back as it was held, canceled."""
    held = holding(entry="01-content")
    made, canceled = taken_in(held, rn_files.aim(rn_files.tasks((rn_files.GUIDE_ID,))), [])
    assert made["tasks"] == rn_files.tasks((rn_files.GUIDE_ID,))
    assert canceled == [{**command(held), "closed": "canceled"}]


def test_an_id_that_names_no_task_left_is_refused() -> None:
    """Given a steering holding 001 and 002.
    When an aim with a task of id 009 is taken in.
    Then Wrong is raised, naming the id."""
    aim = rn_files.aim([{**rn_files.TASKS[0], "id": "009"}])
    with pytest.raises(Wrong, match="no task left has the id 009"):
        taken_in(rn_files.steering(), aim, [])


def test_an_aim_with_a_new_target_takes_it_to_its_own_hand_over() -> None:
    """Given a steering whose target the user said is enough, and an aim that aims at the rules
    with a solution of their own.
    When the aim is taken in.
    Then the steering holds no stage, as the new target is handed over anew."""
    aim = rn_files.aim(target=False)
    aim["ost"]["opportunities"][1]["solutions"] = [
        {"solution": "The command checks each rule.", "target": True, "assumptions": ["x"]}
    ]
    made, _ = taken_in(rn_files.steering(ids=(), stage="enough"), aim, [])
    assert "stage" not in made


@pytest.mark.parametrize(
    ("next_", "fields", "kept"),
    [
        ("generator", {"evaluated": 1}, {"next": "generator", "evaluated": 1}),
        ("fixer", {"evaluated": 2}, {"next": "fixer", "evaluated": 2}),
        ("refactorer", {}, {"next": "refactorer"}),
    ],
    ids=["generator", "fixer", "refactorer"],
)
def test_what_the_aim_says_comes_next_is_taken_in(
    next_: str, fields: dict[str, Any], kept: dict[str, Any]
) -> None:
    """Given a steering whose command waits on the orchestrator's weighing of 02-content.
    When an aim that says what the command takes next is taken in.
    Then the command holds it, with no entry, as its next role starts its own."""
    held = holding(next="weigh", entry="02-content", **fields)
    made, _ = taken_in(held, told(next_), [])
    assert command(made) == {**rn_files.tasks()[0], **kept}


def test_a_round_past_the_limit_is_refused() -> None:
    """Given a steering whose command has its LIMIT Rounds evaluated.
    When an aim that has it made again on what was weighed is taken in.
    Then Wrong is raised, saying that a fixer mends what's left or a new task makes it again."""
    held = holding(next="weigh", evaluated=LIMIT, entry="02-content")
    with pytest.raises(Wrong, match="say fixer to mend what they left, or leave it out"):
        taken_in(held, told("generator"), [])


def test_a_weighing_that_says_nothing_of_its_task_leaves_it_waiting() -> None:
    """Given a steering whose command waits on the orchestrator's weighing.
    When an aim that says nothing of what the command takes next is taken in.
    Then the command still waits on the weighing, as `steering due` keeps showing it."""
    held = holding(next="weigh", entry="01-content")
    made, _ = taken_in(held, rn_files.aim(rn_files.tasks()), [])
    assert command(made)["next"] == "weigh"


def results(**by_role: Any) -> dict[str, dict[str, Any]]:
    """The results of the command's entry, by role."""
    return {rn_files.COMMAND_ID: by_role}


MADE = {"result": "made", "files": [rn_files.COMMAND]}
POINT = {"result": "point", "point": "Which printer?"}
GOOD = {"result": "evaluated", "good": [], "more": []}
MORE = {"result": "evaluated", "good": [], "more": [{"condition": "N1", "good_when": "x"}]}
FIXED = {"result": "made", "files": []}


@pytest.mark.parametrize(
    ("fields", "by_role", "kept"),
    [
        ({}, {"generator": MADE}, {"next": "evaluator"}),
        ({"next": "generator"}, {"generator": POINT}, {"next": "weigh"}),
        (
            {"next": "evaluator"},
            {"generator": MADE, "evaluator": MORE},
            {"next": "weigh", "evaluated": 1},
        ),
        (
            {"next": "evaluator", "evaluated": 1},
            {"generator": MADE, "evaluator": GOOD},
            {"next": "refactorer", "evaluated": 2, "entry": None},
        ),
        ({"next": "fixer"}, {"fixer": FIXED}, {"next": "refactorer", "entry": None}),
        ({"next": "refactorer"}, {"refactorer": POINT}, {"next": "weigh"}),
        ({"next": "fixer"}, {"fixer": POINT}, {"next": "weigh"}),
        ({"next": "evaluator"}, {"generator": MADE}, {}),
    ],
    ids=["made", "point", "more", "good", "fixed", "refactor-point", "fix-point", "no-result"],
)
def test_each_result_moves_its_task_on(
    fields: dict[str, Any], by_role: dict[str, Any], kept: dict[str, Any]
) -> None:
    """Given a steering whose command works in 01-content, and the results its entry holds.
    When the steering is moved on by them.
    Then the command takes what follows its next role's result, and stays where that role has
    none yet, and no task is completed."""
    held = holding(entry="01-content", **fields)
    want = {**command(held), **kept}
    want = {key: value for key, value in want.items() if value is not None}
    made, completed = moved(held, results(**by_role))
    assert (command(made), completed) == (want, [])


@pytest.mark.parametrize(
    ("fields", "by_role"),
    [
        ({"next": "refactorer"}, {"refactorer": MADE}),
        ({"next": "evaluator", "refactor": None}, {"generator": MADE, "evaluator": GOOD}),
        ({"next": "fixer", "refactor": None}, {"fixer": FIXED}),
    ],
    ids=["refactored", "good-with-no-refactoring", "fixed-with-no-refactoring"],
)
def test_a_task_that_ends_is_completed(fields: dict[str, Any], by_role: dict[str, Any]) -> None:
    """Given a steering whose command works in 01-content, refactored, or good or mended with no
    refactoring to take.
    When the steering is moved on.
    Then the command's task goes, the guide's is left, and the command comes back completed."""
    held = holding(entry="01-content", **fields)
    if fields.get("refactor", "") is None:
        del command(held)["refactor"]
    made, completed = moved(held, results(**by_role))
    assert made["tasks"] == rn_files.tasks((rn_files.GUIDE_ID,))
    assert [(each["id"], each["closed"]) for each in completed] == [("001", "completed")]


def test_each_stage_is_marked() -> None:
    """Given a steering with no task left.
    When the work is marked trying, then enough.
    Then the steering is at each stage in turn."""
    trying = marked(rn_files.steering(ids=()), "trying")
    assert (trying["stage"], marked(trying, "enough")["stage"]) == ("trying", "enough")


def test_a_stage_that_is_not_one_is_refused() -> None:
    """Given a steering.
    When the work is marked waiting.
    Then Wrong is raised, naming the stages."""
    with pytest.raises(Wrong, match="trying, enough, inspected"):
        marked(rn_files.steering(), "waiting")
