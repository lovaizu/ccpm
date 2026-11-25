"""The unit cases of tree/signoff.py, what waits for the user's sign-off and what a sign-off
changes: `waiting`, for the plan open with each condition good, before a deliverable earlier in the
tree, for a deliverable whose course is the sign-off, one whose course is another, the first of
several, and one whose step the user doesn't check; `checked`, of a deliverable while the tree
holds no steps, in a step the user doesn't check, and of the plan, in none; and `signed_off`, of
the plan, of a deliverable with more paths, of a node with no file, of one with a finding left as
its open decision, each keeping its conditions and their decisions, and its refusal."""

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


def test_the_plan_open_with_each_condition_good_waits_before_a_deliverable_earlier_in_the_tree():
    """Given a tree whose command, first in the tree, is open with each condition good and waits on
    the sign-off, and whose plan, after it, is open with each condition good
    When what waits for the sign-off is found
    Then it is the plan's path"""
    the = walkthrough(plan_done=False, command_good=True)
    the["deliverables"] = [the["deliverables"][1], the["deliverables"][0], the["deliverables"][2]]
    assert waiting(the, {COMMAND: SIGN_OFF, GUIDE: Next("generator", "content", False)}) == PLAN


def test_a_deliverable_with_each_condition_good_waiting_on_the_signoff_waits():
    """Given a tree whose plan is done and whose command is open with each condition good and waits
    on the sign-off
    When what waits for the sign-off is found
    Then it is the command's path"""
    the = walkthrough(command_good=True)
    assert waiting(the, {COMMAND: SIGN_OFF, GUIDE: Next("generator", "content", False)}) == COMMAND


def test_of_two_deliverables_waiting_the_first_in_the_trees_order_waits():
    """Given a tree whose command and guide both wait on the sign-off with each condition good
    When what waits for the sign-off is found, given the guide's wait first
    Then it is the command's path, first in the tree"""
    the = walkthrough(command_good=True, guide_good=True)
    assert waiting(the, {GUIDE: SIGN_OFF, COMMAND: SIGN_OFF}) == COMMAND


def test_a_deliverable_with_each_condition_good_waiting_on_another_doesnt_wait():
    """Given a tree whose command is open with each condition good, and waits on the evaluator
    When what waits for the sign-off is found
    Then none does"""
    the = walkthrough(command_good=True)
    nexts = {
        COMMAND: Next("evaluator", "content", False),
        GUIDE: Next("generator", "content", False),
    }
    assert waiting(the, nexts) is None


LEFT = rn_files.decision("a comma in a line", None)


def left_past(**given: Any) -> dict[str, Any]:
    """The walkthrough's tree whose command holds N1 not good, N2 and N3 good, and the finding
    left past its Rounds kept as an open decision of N1."""
    return as_read(
        rn_files.walkthrough_tree(
            NAME, command_good=["N2", "N3"], command_decisions={"N1": [LEFT]}, **given
        )
    )


# signed_off


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


def test_a_deliverable_signed_off_is_done_keeping_what_names_it_and_its_conditions():
    """Given a tree whose command is open with each condition good and more paths
    When the user signs the command off
    Then the command is done keeping its name, path, more paths, kind, and conditions with the
    user's answer, and the guide is as it was"""
    the = walkthrough(command_good=True)
    the["deliverables"][1]["more_paths"] = ["tests/test_main.py"]
    got = signed_off(the, COMMAND)
    assert got["deliverables"][1] == {
        "name": rn_files.COMMAND_NAME,
        "path": COMMAND,
        "more_paths": ["tests/test_main.py"],
        "kind": "light",
        "status": "done",
        "necessary_conditions": the["deliverables"][1]["necessary_conditions"],
    }
    assert got["deliverables"][2] == the["deliverables"][2]


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


def test_signed_off_refuses_a_path_of_no_open_deliverable():
    """Given a tree whose plan is done and whose command and guide are open with each condition
    good
    When the user signs off the done plan
    Then it refuses with Wrong"""
    the = walkthrough(command_good=True, guide_good=True)
    with pytest.raises(Wrong):
        signed_off(the, PLAN)


def test_a_deliverable_with_a_finding_left_signed_off_keeps_it_among_its_conditions():
    """Given a tree whose command holds N1 not good with its finding left as an open decision
    When the user signs the command off
    Then the command is done keeping N1 not good with the open decision, as the proposal the user
    signed off"""
    got = signed_off(left_past(), COMMAND)
    want = rn_files.done_node(rn_files.COMMAND_NAME, COMMAND, "light", ["N2", "N3"], {"N1": [LEFT]})
    assert got["deliverables"][1] == want


# The steps that the user checks.


def with_steps(the: dict[str, Any], command: bool, guide: bool) -> dict[str, Any]:
    """The tree with a step of the command and one of the guide, each with the sign-off given."""
    the["steps"] = [
        rn_files.step("what it does", [COMMAND], command),
        rn_files.step("how it's used", [GUIDE], guide),
    ]
    return the


def test_a_deliverable_past_its_rounds_at_a_step_the_user_doesnt_check_doesnt_wait():
    """Given a tree whose command waits on the sign-off with each condition good, at a step whose
    sign-off is false
    When what waits for the sign-off is found
    Then none does"""
    the = with_steps(walkthrough(command_good=True), False, True)
    assert waiting(the, {COMMAND: SIGN_OFF, GUIDE: Next("generator", "content", False)}) is None


@pytest.mark.parametrize(
    ("steps", "path", "expected"),
    [
        (None, COMMAND, True),
        ((True, False), GUIDE, False),
        ((True, False), PLAN, True),
    ],
    ids=["no-steps", "not-checked", "the-plan"],
)
def test_checked_is_false_only_at_a_step_whose_signoff_is_false(
    steps: tuple[bool, bool] | None, path: str, expected: bool
):
    """Given a tree with no steps, or with the command's step checked and the guide's not
    When whether the user checks the command with no steps, the guide, or the plan is found
    Then it is false only for the guide at its step not checked, the plan lying in no step"""
    the = walkthrough(plan_done=False)
    if steps is not None:
        the = with_steps(the, *steps)
    assert checked(the, path) is expected
