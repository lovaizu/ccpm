"""The unit cases of steering/record.py, what each change makes of the work's steering: the
orchestrator's first aim, a later one that keeps where each task is on its way and the stage, what
the aim says comes next, each result moving a task on or ending it, and each mark of the stage, with
each refusal."""

from __future__ import annotations

from typing import Any

import pytest
import rn_files
from fault import Wrong
from steering.record import LIMIT, marked, moved, taken_in


def test_a_first_aim_makes_the_steering() -> None:
    """Given the work with no steering, and an aim with its tree, tasks, and decision.
    When the aim is taken in.
    Then the steering holds each, none started, and no stage."""
    assert taken_in(None, rn_files.aim()) == rn_files.steering()


def command(steering: dict[str, Any]) -> dict[str, Any]:
    """The command's task, the first of the steering's."""
    return steering["tasks"][0]


def holding(stage: str | None = None, **fields: Any) -> dict[str, Any]:
    """The walkthrough's steering at the stage given, the command's task with the fields given."""
    held = rn_files.steering(stage=stage)
    command(held).update(fields)
    return held


def told(next_: str) -> dict[str, Any]:
    """An aim that says what the command takes next."""
    held = rn_files.aim()
    command(held)["next"] = next_
    return held


def test_a_later_aim_keeps_where_each_task_is_and_the_stage() -> None:
    """Given a steering in the user's hands whose command is at its evaluator, once judged, in
    content-2, and an aim that puts the guide first, rewords the command's task, and adds one at
    the same path.
    When the aim is taken in.
    Then the first command's task keeps its next role, its judged Rounds, and its entry, with the
    aim's words, the second starts anew, and the stage stays."""
    held = holding("trying", next="evaluator", judged=1, entry="content-2")
    aim = rn_files.aim()
    aim["tasks"].reverse()
    aim["tasks"][1]["task"] = "Print one invoice."
    aim["tasks"].append({"task": "Print a second page.", "path": rn_files.COMMAND, "kind": "code"})
    made = taken_in(held, aim)
    assert made["tasks"][1] == {**command(held), "task": "Print one invoice."}
    assert (made["tasks"][2], made["stage"]) == (aim["tasks"][2], "trying")


def test_an_aim_with_a_new_target_takes_it_to_its_own_hand_over() -> None:
    """Given a steering whose target the user said is enough, and an aim that aims at the rules
    with a solution of their own.
    When the aim is taken in.
    Then the steering holds no stage, as the new target is handed over anew."""
    aim = rn_files.aim(target=False)
    aim["ost"]["opportunities"][1]["solutions"] = [
        {"solution": "The command checks each rule.", "target": True, "assumptions": ["x"]}
    ]
    assert "stage" not in taken_in(rn_files.steering(paths=(), stage="enough"), aim)


@pytest.mark.parametrize(
    ("next_", "fields", "kept"),
    [
        ("generator", {"judged": 1}, {"next": "generator", "judged": 1}),
        ("anew", {"judged": 2}, {"next": "generator"}),
        ("fixer", {"judged": 2}, {"next": "fixer", "judged": 2}),
        ("refactorer", {}, {"next": "refactorer"}),
    ],
    ids=["generator", "anew", "fixer", "refactorer"],
)
def test_what_the_aim_says_comes_next_is_taken_in(
    next_: str, fields: dict[str, Any], kept: dict[str, Any]
) -> None:
    """Given a steering whose command waits on the orchestrator's weighing of content-2.
    When an aim that says what the command takes next is taken in.
    Then the command holds it, with no entry, as its next role starts its own; anew makes it
    again from its first Round."""
    held = holding(next="weigh", entry="content-2", **fields)
    assert command(taken_in(held, told(next_))) == {**rn_files.TASKS[0], **kept}


def test_a_round_past_the_limit_is_refused() -> None:
    """Given a steering whose command has its LIMIT Rounds judged.
    When an aim that has it made again on what was weighed is taken in.
    Then Wrong is raised, saying that the user confirms what's left."""
    held = holding(next="weigh", judged=LIMIT, entry="content-2")
    with pytest.raises(Wrong, match="ask the user"):
        taken_in(held, told("generator"))


def test_a_weighing_that_says_nothing_of_its_task_leaves_it_waiting() -> None:
    """Given a steering whose command waits on the orchestrator's weighing.
    When an aim that says nothing of what the command takes next is taken in.
    Then the command still waits on the weighing, as `steering due` keeps showing it."""
    held = holding(next="weigh", entry="content-1")
    assert command(taken_in(held, rn_files.aim()))["next"] == "weigh"


def results(**by_role: Any) -> dict[str, dict[str, Any]]:
    """The results of the command's entry, by role."""
    return {rn_files.COMMAND: by_role}


MADE = {"result": "made", "files": [rn_files.COMMAND]}
POINT = {"result": "point", "point": "Which printer?"}
GOOD = {"result": "judged", "good": [], "more": []}
MORE = {"result": "judged", "good": [], "more": [{"condition": "N1", "good_when": "x"}]}
FIXED = {"result": "fixed", "files": []}


@pytest.mark.parametrize(
    ("fields", "by_role", "kept"),
    [
        ({}, {"generator": MADE}, {"next": "evaluator"}),
        ({"next": "generator"}, {"generator": POINT}, {"next": "weigh"}),
        (
            {"next": "evaluator"},
            {"generator": MADE, "evaluator": MORE},
            {"next": "weigh", "judged": 1},
        ),
        (
            {"next": "evaluator", "judged": 1},
            {"generator": MADE, "evaluator": GOOD},
            {"next": "refactorer", "judged": 2, "entry": None},
        ),
        ({"next": "fixer"}, {"fixer": FIXED}, {"next": "refactorer", "entry": None}),
        ({"next": "refactorer"}, {"refactorer": POINT}, {"next": "weigh"}),
        ({"next": "evaluator"}, {"generator": MADE}, {}),
    ],
    ids=["made", "point", "more", "good", "fixed", "refactor-point", "no-result"],
)
def test_each_result_moves_its_task_on(
    fields: dict[str, Any], by_role: dict[str, Any], kept: dict[str, Any]
) -> None:
    """Given a steering whose command works in content-1, and the results its entry holds.
    When the steering is moved on by them.
    Then the command takes what follows its next role's result, and stays where that role has
    none yet."""
    held = holding(entry="content-1", **fields)
    want = {**command(held), **kept}
    want = {key: value for key, value in want.items() if value is not None}
    assert command(moved(held, results(**by_role))) == want


@pytest.mark.parametrize(
    ("fields", "by_role"),
    [
        ({"next": "refactorer"}, {"refactorer": MADE}),
        ({"next": "evaluator", "refactor": None}, {"generator": MADE, "evaluator": GOOD}),
        ({"next": "fixer", "refactor": None}, {"fixer": FIXED}),
    ],
    ids=["refactored", "good-with-no-refactoring", "fixed-with-no-refactoring"],
)
def test_a_task_that_ends_goes(fields: dict[str, Any], by_role: dict[str, Any]) -> None:
    """Given a steering whose command works in content-1, refactored, or good or mended with no
    refactoring to take.
    When the steering is moved on.
    Then the command's task goes, and the guide's is left."""
    held = holding(entry="content-1", **fields)
    if fields.get("refactor", "") is None:
        del command(held)["refactor"]
    assert moved(held, results(**by_role))["tasks"] == [rn_files.TASKS[1]]


def test_each_stage_is_marked() -> None:
    """Given a steering with no task left.
    When the work is marked trying, then enough.
    Then the steering is at each stage in turn."""
    trying = marked(rn_files.steering(paths=()), "trying")
    assert (trying["stage"], marked(trying, "enough")["stage"]) == ("trying", "enough")


def test_a_stage_that_is_not_one_is_refused() -> None:
    """Given a steering.
    When the work is marked waiting.
    Then Wrong is raised, naming the stages."""
    with pytest.raises(Wrong, match="trying, enough, inspected"):
        marked(rn_files.steering(), "waiting")
