"""The unit cases of steering/record.py, what each change makes of the work's steering: the
orchestrator's first aim, a later one that keeps each status the steering holds, one with no steps
or issues, what the aim says comes next, each result moving a deliverable on, each mark of a step,
and the inspection's pass, with each refusal."""

from __future__ import annotations

from typing import Any

import pytest
import rn_files
from fault import Wrong
from steering.record import LIMIT, inspected_marked, moved, step_marked, taken_in

STEP = rn_files.WAY


def result(**fields: Any) -> dict[str, Any]:
    """An aim of the walkthrough, with the fields given."""
    return {"ost": rn_files.ost(), **fields}


def test_a_first_result_makes_the_steering_with_each_step_open() -> None:
    """Given the work with no steering, and an aim with its tree, issues, and steps.
    When the result is taken in.
    Then the steering holds the tree, the issues, and each step and deliverable open."""
    made = taken_in(None, result(issues={"closes": [38], "refs": []}, steps=[STEP]))
    assert made == rn_files.steering()


def test_a_first_result_with_no_issues_or_steps_holds_none() -> None:
    """Given the work with no steering, and a result with its tree alone, the need not picked.
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


def test_a_later_result_keeps_the_final_checks_pass() -> None:
    """Given a steering whose step is done, the inspection passed, and a result with a question
    and its steps again.
    When the result is taken in.
    Then the inspection stays passed."""
    held = rn_files.steering([rn_files.step("done")])
    held["state"]["inspected"] = True
    made = taken_in(held, result(ost=rn_files.ost(questions=["Keep 2?"]), steps=[STEP]))
    assert made["state"]["inspected"] is True


def test_a_result_that_adds_a_step_takes_the_final_check_again() -> None:
    """Given a steering whose step is done and the inspection passed, and a result that keeps the
    step and adds one for a need left.
    When the result is taken in.
    Then the inspection is no longer passed, as the pull request grows."""
    held = rn_files.steering([rn_files.step("done")])
    held["state"]["inspected"] = True
    added = dict(STEP, settles="print a second page")
    made = taken_in(held, result(steps=[STEP, added]))
    assert "checked" not in made["state"]


def test_a_step_with_each_deliverable_done_is_marked_trying() -> None:
    """Given a steering whose step has each deliverable done.
    When step 1 is marked trying.
    Then it's trying."""
    held = rn_files.steering([rn_files.step(done=(rn_files.COMMAND, rn_files.GUIDE))])
    assert step_marked(held, 1, "trying")["state"]["steps"][0]["status"] == "trying"


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


def command(steering: dict[str, Any]) -> dict[str, Any]:
    """The command, the first deliverable of the steering's first step."""
    return steering["state"]["steps"][0]["deliverables"][0]


def holding(step_status: str = "open", **fields: Any) -> dict[str, Any]:
    """The walkthrough's steering, its step at the status given, the guide done, and the command
    with the fields given."""
    held = rn_files.steering([rn_files.step(step_status, done=(rn_files.GUIDE,))])
    command(held).update(fields)
    return held


def told(next_: str, **fields: Any) -> dict[str, Any]:
    """An aim that says what the command takes next."""
    way = {
        **STEP,
        "deliverables": [{**STEP["deliverables"][0], "next": next_}, STEP["deliverables"][1]],
    }
    return result(steps=[way], **fields)


def test_a_later_result_keeps_where_each_deliverable_is_on_its_way() -> None:
    """Given a steering whose command is at its evaluator, once judged, in content-2.
    When a result that says nothing of what it takes next is taken in.
    Then the command keeps its next role, its judged Rounds, and its entry."""
    held = holding(next="evaluator", judged=1, entry="content-2")
    assert command(taken_in(held, result(steps=[STEP]))) == command(held)


@pytest.mark.parametrize(
    ("next_", "fields", "kept"),
    [
        ("generator", {"judged": 1}, {"next": "generator", "judged": 1, "status": "open"}),
        ("anew", {"judged": 2}, {"next": "generator", "status": "open"}),
        ("fixer", {"judged": 2}, {"next": "fixer", "judged": 2, "status": "open"}),
        ("refactorer", {}, {"next": "refactorer", "status": "open"}),
        ("done", {"judged": 1}, {"judged": 1, "status": "done"}),
    ],
    ids=["generator", "anew", "fixer", "refactorer", "done"],
)
def test_what_the_aim_says_comes_next_is_taken_in(
    next_: str, fields: dict[str, Any], kept: dict[str, Any]
) -> None:
    """Given a steering whose command waits on the orchestrator's weighing of content-2.
    When a result that says what the command takes next is taken in.
    Then the command holds it, with no entry, as its next role starts its own; anew makes it
    again from its first Round, and done ends it."""
    held = holding(next="weigh", entry="content-2", **fields)
    assert command(taken_in(held, told(next_))) == {
        "path": rn_files.COMMAND,
        "kind": "code",
        "refactor": "refactor-code",
        **kept,
    }


def test_a_deliverable_to_mend_opens_its_step_again() -> None:
    """Given a steering whose step is trying with each deliverable done.
    When a result that has the command mended is taken in.
    Then the step is open again, as the user tries it once it's mended."""
    held = rn_files.steering([rn_files.step("trying", done=(rn_files.COMMAND, rn_files.GUIDE))])
    assert taken_in(held, told("fixer"))["state"]["steps"][0]["status"] == "open"


def test_a_round_past_the_limit_is_refused() -> None:
    """Given a steering whose command has its LIMIT Rounds judged.
    When a result that has it made again on what was weighed is taken in.
    Then Wrong is raised, saying that the user confirms what's left."""
    held = holding(next="weigh", judged=LIMIT, entry="content-2")
    with pytest.raises(Wrong, match="ask the user"):
        taken_in(held, told("generator"))


def test_a_weighing_that_says_nothing_of_its_deliverable_leaves_it_waiting() -> None:
    """Given a steering whose command waits on the orchestrator's weighing.
    When an aim that says nothing of what the command takes next is taken in.
    Then the command still waits on the weighing, as `steering due` keeps showing it."""
    held = holding(next="weigh", entry="content-1")
    assert command(taken_in(held, result(steps=[STEP])))["next"] == "weigh"


def results(**by_role: Any) -> dict[str, dict[str, Any]]:
    """The results of the command's entry, by role."""
    return {rn_files.COMMAND: by_role}


MADE = {"result": "made", "files": [rn_files.COMMAND]}
POINT = {"result": "point", "point": "Which printer?"}
GOOD = {"result": "judged", "good": [], "more": []}
MORE = {"result": "judged", "good": [], "more": [{"condition": "N1", "good_when": "x"}]}


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
        (
            {"next": "fixer"},
            {"fixer": {"result": "fixed", "files": []}},
            {"next": "refactorer", "entry": None},
        ),
        ({"next": "refactorer"}, {"refactorer": MADE}, {"status": "done", "entry": None}),
        ({"next": "refactorer"}, {"refactorer": POINT}, {"next": "weigh"}),
        ({"next": "evaluator"}, {"generator": MADE}, {}),
    ],
    ids=["made", "point", "more", "good", "fixed", "refactored", "refactor-point", "no-result"],
)
def test_each_result_moves_its_deliverable_on(
    fields: dict[str, Any], by_role: dict[str, Any], kept: dict[str, Any]
) -> None:
    """Given a steering whose command works in content-1, and the results its entry holds.
    When the steering is moved on by them.
    Then the command takes what follows its next role's result, and stays where that role has
    none yet."""
    held = holding(entry="content-1", **fields)
    want = {**command(held), **kept}
    want = {key: value for key, value in want.items() if value is not None}
    if want.get("status") == "done":
        want.pop("next", None)
    assert command(moved(held, results(**by_role))) == want


def test_a_deliverable_with_no_refactoring_ends_once_it_is_good() -> None:
    """Given a steering whose deliverable has no refactoring, its evaluator found each condition
    good.
    When the steering is moved on.
    Then the deliverable is done, as nothing refactors it."""
    held = holding(next="evaluator", entry="content-1")
    del command(held)["refactor"]
    assert command(moved(held, results(generator=MADE, evaluator=GOOD)))["status"] == "done"


def test_a_deliverable_takes_the_refactoring_that_the_aim_gives_it() -> None:
    """Given an aim whose command is of the general kind, to be refactored as code.
    When it's taken in, and its evaluator finds each condition good.
    Then the steering keeps the refactoring, and the command's refactorer is next."""
    way = {
        **STEP,
        "deliverables": [
            {"path": rn_files.COMMAND, "kind": "general", "refactor": "refactor-code"}
        ],
    }
    held = taken_in(None, result(steps=[way]))
    assert command(held)["refactor"] == "refactor-code"
    command(held).update(next="evaluator", entry="content-1")
    assert command(moved(held, results(generator=MADE, evaluator=GOOD)))["next"] == "refactorer"


def test_the_final_check_is_marked_passed_once_each_step_is_done() -> None:
    """Given a steering whose one step is done.
    When the inspection is marked passed.
    Then the steering holds it passed, and the step stays done."""
    marked = inspected_marked(rn_files.steering([rn_files.step("done")]))
    assert (marked["state"]["inspected"], marked["state"]["steps"][0]["status"]) == (True, "done")


def test_the_final_check_is_refused_while_a_step_is_not_done() -> None:
    """Given a steering whose step is trying.
    When the inspection is marked passed.
    Then Wrong is raised, naming the step."""
    with pytest.raises(Wrong, match="step 1 isn't done"):
        inspected_marked(rn_files.steering([rn_files.step("trying")]))
