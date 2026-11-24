"""The unit cases of tree/signoff.py, what waits for the user's sign-off and what a sign-off
changes: `waiting`, for the plan open with each condition good, before a deliverable earlier in the
tree, and with a condition short, for a deliverable whose course is the sign-off with each
condition good or with a finding left past its Rounds, one with each condition good whose course
is another, and for one of several, none, and only those done, and for one whose step the user
checks and one whose step they don't; `checked`, of a deliverable in no step, in a step the user
checks, and in one they don't; and `signed_off`, of the plan, of a deliverable with more paths, of
a node with no file, of one with findings left as its open decisions, each keeping its conditions
and their decisions, with the work that names it and other work, and each refusal."""

from __future__ import annotations

import copy
import json
from typing import Any

import pytest
import rn_files
from fault import Wrong
from rn_files import COMMAND, GOAL, GUIDE
from rounds.course import Next
from tree.signoff import checked, signed_off, waiting

NAME = "20261120-a-command-with-which-the"
PLAN = rn_files.plan_path(NAME)
SIGN_OFF = Next("sign-off", None, False)


def as_read(value: Any) -> Any:
    """The value as its JSON file gives it."""
    return json.loads(json.dumps(value))


def walkthrough(**given: Any) -> dict[str, Any]:
    """The walkthrough's tree, read from its JSON."""
    return as_read(rn_files.walkthrough_tree(NAME, **given))


# waiting


@pytest.mark.supports("test_the_plan_waiting_for_signoff_is_put_up_in_the_runs_pull_request")
def test_the_plan_open_with_each_condition_good_waits_before_a_deliverable_earlier_in_the_tree():
    """Given a tree whose command, first in the tree, is open with each condition good and waits on
    the sign-off, and whose plan, after it, is open with each condition good
    When what waits for the sign-off is found
    Then it is the plan's path"""
    the = walkthrough(plan_done=False, command_good=True)
    the["deliverables"] = [the["deliverables"][1], the["deliverables"][0], the["deliverables"][2]]
    assert waiting(the, {COMMAND: SIGN_OFF, GUIDE: Next("generator", "content", False)}) == PLAN


@pytest.mark.supports("test_the_plan_waiting_for_signoff_is_put_up_in_the_runs_pull_request")
def test_the_plan_open_with_a_condition_short_doesnt_wait():
    """Given a tree whose plan is open with N2 not good, and whose deliverables wait on the
    generator
    When what waits for the sign-off is found
    Then none does"""
    the = walkthrough(plan_done=False)
    the["deliverables"][0]["necessary_conditions"][1]["good"] = False
    nexts = {
        COMMAND: Next("generator", "content", False),
        GUIDE: Next("generator", "content", False),
    }
    assert waiting(the, nexts) is None


@pytest.mark.supports(
    "test_a_finding_the_people_would_never_meet_is_dropped_by_holding_its_condition_good"
)
def test_a_deliverable_with_each_condition_good_waiting_on_the_signoff_waits():
    """Given a tree whose plan is done and whose command is open with each condition good and waits
    on the sign-off
    When what waits for the sign-off is found
    Then it is the command's path"""
    the = walkthrough(command_good=True)
    assert waiting(the, {COMMAND: SIGN_OFF, GUIDE: Next("generator", "content", False)}) == COMMAND


@pytest.mark.supports(
    "test_a_finding_the_people_would_never_meet_is_dropped_by_holding_its_condition_good"
)
def test_of_two_deliverables_waiting_the_first_in_the_trees_order_waits():
    """Given a tree whose command and guide both wait on the sign-off with each condition good, and
    whose work makes the guide first
    When what waits for the sign-off is found
    Then it is the command's path, first in the tree"""
    the = walkthrough(command_good=True, guide_good=True)
    the["work"].reverse()
    assert waiting(the, {GUIDE: SIGN_OFF, COMMAND: SIGN_OFF}) == COMMAND


@pytest.mark.supports(
    "test_a_finding_the_people_would_never_meet_is_dropped_by_holding_its_condition_good"
)
@pytest.mark.parametrize(
    "next_",
    [
        Next("generator", "refactor", False),
        Next("evaluator", "content", False),
        Next("answer", None, False),
        Next("orchestrator", "content", False),
    ],
)
def test_a_deliverable_with_each_condition_good_waiting_on_another_doesnt_wait(next_: Next):
    """Given a tree whose command is open with each condition good, and waits on a refactoring
    generator, the evaluator, the answer, or the orchestrator
    When what waits for the sign-off is found
    Then none does"""
    the = walkthrough(command_good=True)
    assert waiting(the, {COMMAND: next_, GUIDE: Next("generator", "content", False)}) is None


LEFT = rn_files.decision("a comma in a line", None)


def left_past(**given: Any) -> dict[str, Any]:
    """The walkthrough's tree whose command holds N1 not good, N2 and N3 good, and the finding
    left past its Rounds kept as an open decision of N1."""
    return as_read(
        rn_files.walkthrough_tree(
            NAME, command_good=["N2", "N3"], command_decisions={"N1": [LEFT]}, **given
        )
    )


@pytest.mark.supports("test_a_finding_left_past_two_content_rounds_goes_to_the_user_as_a_proposal")
def test_a_deliverable_whose_course_is_the_signoff_with_a_finding_left_waits():
    """Given a tree whose command holds N1 not good with its finding left as an open decision, and
    whose course is the sign-off
    When what waits for the sign-off is found
    Then it is the command's path"""
    nexts = {COMMAND: SIGN_OFF, GUIDE: Next("generator", "content", False)}
    assert waiting(left_past(), nexts) == COMMAND


@pytest.mark.supports("test_a_finding_left_past_two_content_rounds_goes_to_the_user_as_a_proposal")
def test_a_deliverable_with_a_condition_short_whose_course_is_the_orchestrator_doesnt_wait():
    """Given a tree whose command holds N1 not good, its finding not yet kept, and whose course is
    the orchestrator
    When what waits for the sign-off is found
    Then none does"""
    the = walkthrough(command_good=["N2", "N3"])
    nexts = {COMMAND: Next("orchestrator", None, False), GUIDE: Next("generator", "content", False)}
    assert waiting(the, nexts) is None


@pytest.mark.supports("test_a_deliverable_signed_off_is_done_and_the_one_resting_on_it_starts")
def test_a_tree_of_deliverables_each_done_has_none_waiting():
    """Given a tree whose deliverables are each done
    When what waits for the sign-off is found
    Then none does"""
    the = as_read(
        rn_files.tree(
            [
                rn_files.done_node(GOAL, PLAN, "design-tree"),
                rn_files.done_node(rn_files.COMMAND_NAME, COMMAND, "light"),
            ]
        )
    )
    assert waiting(the, {}) is None


# signed_off


@pytest.mark.supports(
    "test_a_signoff_of_the_plan_makes_it_done_and_starts_the_generator_of_each_deliverable_due"
)
def test_the_plan_signed_off_is_done_with_its_conditions():
    """Given a tree whose plan is open with each condition good
    When the user signs the plan off
    Then the plan is done, its name, path, kind, and conditions kept, and the rest of the tree and
    the tree given are as they were"""
    the = walkthrough(plan_done=False)
    before = copy.deepcopy(the)
    got = signed_off(the, PLAN)
    want = copy.deepcopy(before)
    want["deliverables"][0] = rn_files.done_node(GOAL, PLAN, "design-tree")
    assert got == want
    assert the == before


@pytest.mark.supports("test_a_deliverable_signed_off_is_done_and_the_one_resting_on_it_starts")
def test_a_deliverable_signed_off_drops_each_item_of_the_work_that_names_it():
    """Given a tree whose command is open with each condition good and more paths, and whose work
    makes it, decides its N1, and makes the guide
    When the user signs the command off
    Then the command is done keeping its name, path, more paths, kind, and conditions with the
    user's answer, and the work holds only the guide's item"""
    the = walkthrough(command_good=True)
    the["deliverables"][1]["more_paths"] = ["tests/test_main.py"]
    the["work"].insert(1, rn_files.work("decide", COMMAND, "N1", rn_files.TAX_ABOUT))
    got = signed_off(the, COMMAND)
    assert got["deliverables"][1] == {
        "name": rn_files.COMMAND_NAME,
        "path": COMMAND,
        "more_paths": ["tests/test_main.py"],
        "kind": "light",
        "status": "done",
        "necessary_conditions": the["deliverables"][1]["necessary_conditions"],
    }
    assert got["work"] == [rn_files.work("make", GUIDE)]
    assert got["deliverables"][2] == the["deliverables"][2]


@pytest.mark.supports("test_a_deliverable_signed_off_is_done_and_the_one_resting_on_it_starts")
def test_a_node_with_no_file_signed_off_keeps_its_conditions():
    """Given a tree whose node with no file, of the kind light, is open with each condition good and
    a decision of its N1
    When the user signs it off
    Then it is done keeping its name, path, kind, that it has no file, and its conditions with
    their decisions"""
    node = rn_files.decided(
        rn_files.open_node("The invoices' people", "docs/people.md", "light", good=True),
        {"N1": [rn_files.decision("who", "The accounting team.")]},
    )
    node["file"] = False
    the = as_read(rn_files.tree([rn_files.done_node(GOAL, PLAN, "design-tree"), node]))
    got = signed_off(the, "docs/people.md")
    done = rn_files.done_node("The invoices' people", "docs/people.md", "light")
    want = {**done, "file": False, "necessary_conditions": node["necessary_conditions"]}
    assert got["deliverables"][1] == want


@pytest.mark.supports("test_a_deliverable_signed_off_is_done_and_the_one_resting_on_it_starts")
def test_a_deliverable_being_made_signed_off_is_done():
    """Given a tree whose command, status doing, has each condition good
    When the user signs it off
    Then it is done with its conditions"""
    the = walkthrough(command_good=True)
    the["deliverables"][1]["status"] = "doing"
    got = signed_off(the, COMMAND)
    assert got["deliverables"][1] == rn_files.done_node(rn_files.COMMAND_NAME, COMMAND, "light")


@pytest.mark.supports("test_a_deliverable_signed_off_is_done_and_the_one_resting_on_it_starts")
@pytest.mark.parametrize("path", [PLAN, "invoicer/__main__", "docs/guide.txt"])
def test_signed_off_refuses_a_path_of_no_open_deliverable(path: str):
    """Given a tree whose plan is done and whose command and guide are open with each condition
    good
    When the user signs off the done plan, or a path near the command's or the guide's
    Then it refuses with Wrong"""
    the = walkthrough(command_good=True, guide_good=True)
    with pytest.raises(Wrong):
        signed_off(the, path)


@pytest.mark.supports("test_a_finding_left_past_two_content_rounds_goes_to_the_user_as_a_proposal")
def test_a_deliverable_with_a_finding_left_signed_off_keeps_it_among_its_conditions():
    """Given a tree whose command holds N1 not good with its finding left as an open decision
    When the user signs the command off
    Then the command is done keeping N1 not good with the open decision, as the proposal the user
    signed off, and its item of the work gone"""
    got = signed_off(left_past(), COMMAND)
    want = rn_files.done_node(rn_files.COMMAND_NAME, COMMAND, "light", ["N2", "N3"], {"N1": [LEFT]})
    assert got["deliverables"][1] == want
    assert got["work"] == [rn_files.work("make", GUIDE)]


@pytest.mark.supports("test_a_finding_left_past_two_content_rounds_goes_to_the_user_as_a_proposal")
def test_a_node_with_no_file_signed_off_with_a_finding_left_keeps_it_among_its_conditions():
    """Given a tree whose node with no file holds N1 not good with its finding left as an open
    decision
    When the user signs it off
    Then it is done keeping its conditions, N1 not good with the open decision, as the proposal
    the user signed off"""
    node = rn_files.decided(
        rn_files.open_node("The invoices' people", "docs/people.md", "light", good=["N2", "N3"]),
        {"N1": [LEFT]},
    )
    node["file"] = False
    the = as_read(rn_files.tree([rn_files.done_node(GOAL, PLAN, "design-tree"), node]))
    got = signed_off(the, "docs/people.md")
    assert got["deliverables"][1]["status"] == "done"
    assert got["deliverables"][1]["necessary_conditions"] == node["necessary_conditions"]


# The steps that the user checks.

ONE_STEP = (
    "test_a_deliverable_at_a_step_the_user_doesnt_check_is_done_once_put_up_and_the_next_starts"
)


def with_steps(the: dict[str, Any], command: bool, guide: bool) -> dict[str, Any]:
    """The tree with a step of the command and one of the guide, each with the sign-off given."""
    the["steps"] = [
        rn_files.step("what it does", [COMMAND], command),
        rn_files.step("how it's used", [GUIDE], guide),
    ]
    return the


@pytest.mark.supports(
    "test_a_deliverable_at_a_step_the_user_doesnt_check_is_done_once_put_up_and_the_next_starts"
)
def test_a_deliverable_past_its_rounds_at_a_step_the_user_doesnt_check_doesnt_wait():
    """Given a tree whose command waits on the sign-off with each condition good, at a step whose
    sign-off is false
    When what waits for the sign-off is found
    Then none does"""
    the = with_steps(walkthrough(command_good=True), False, True)
    assert waiting(the, {COMMAND: SIGN_OFF, GUIDE: Next("generator", "content", False)}) is None


@pytest.mark.supports(
    "test_a_deliverable_at_a_step_the_user_doesnt_check_is_done_once_put_up_and_the_next_starts"
)
def test_a_deliverable_past_its_rounds_at_a_step_the_user_checks_waits():
    """Given a tree whose command waits on the sign-off with each condition good, at a step whose
    sign-off is true, and the guide's step's false
    When what waits for the sign-off is found
    Then it is the command's path"""
    the = with_steps(walkthrough(command_good=True), True, False)
    assert waiting(the, {COMMAND: SIGN_OFF, GUIDE: Next("generator", "content", False)}) == COMMAND


@pytest.mark.supports(
    "test_a_deliverable_at_a_step_the_user_doesnt_check_is_done_once_put_up_and_the_next_starts"
)
@pytest.mark.parametrize(
    ("steps", "path", "expected"),
    [
        (None, COMMAND, True),
        ((True, False), COMMAND, True),
        ((True, False), GUIDE, False),
        ((True, False), PLAN, True),
    ],
    ids=["no-steps", "checked", "not-checked", "the-plan"],
)
def test_checked_is_false_only_at_a_step_whose_signoff_is_false(
    steps: tuple[bool, bool] | None, path: str, expected: bool
):
    """Given a tree with no steps, or with the command's step checked and the guide's not
    When whether the user checks the command, the guide, or the plan is found
    Then it is false only for the guide at its step not checked, the plan lying in no step"""
    the = walkthrough(plan_done=False)
    if steps is not None:
        the = with_steps(the, *steps)
    assert checked(the, path) is expected
