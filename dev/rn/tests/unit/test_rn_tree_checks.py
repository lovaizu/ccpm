"""The unit cases of tree/checks.py, the faults that keep a change of the design tree from its
commit: a tree in form, and each fault the contract names, one at a time and two at once: a place
out of the schema, a kind with no best practice, an open deliverable's conditions out of its best
practice's set or order, an input that names neither a deliverable nor a file of the worktree, a
deliverable resting on itself directly or through another, and an item of the work that names no
deliverable, or a decide naming no condition or about of it; with a near match beside each."""

from __future__ import annotations

import copy
import os
from typing import Any

import pytest
import rn_files
from repo_files import write_files
from rn_files import COMMAND, GUIDE
from tree.checks import faults

NAME = "20261120-a-command-with-which-the"
KINDS = ("design-tree", "light", "readme", "code")


def practices() -> dict[str, Any]:
    """The best practice of each kind the cases use, by its name, read from its JSON."""
    return {kind: rn_files.practice(kind) for kind in KINDS}


@pytest.fixture
def worktree(tmp_path: Any) -> str:
    """The run's worktree, holding invoicer's lines."""
    folder = os.path.join(str(tmp_path), "worktree")
    write_files(folder, {"invoicer/lines.py": "LINES = []\n", "docs/old.md": "# Old\n"})
    return folder


def the_tree() -> dict[str, Any]:
    """The walkthrough's tree with the plan done, a settled decision of the command's N1, and the
    work making the command and deciding its N1's tax rate."""
    tax = rn_files.decision(rn_files.TAX_ABOUT, rn_files.TAX_ANSWER, "user")
    the = rn_files.walkthrough_tree(NAME, command_decisions={"N1": [tax]})
    the["work"].append(rn_files.work("decide", COMMAND, "N1", rn_files.TAX_ABOUT))
    return the


def one_fault(found: list[str], pointer: str) -> None:
    """The faults are one line, naming the pointer."""
    assert len(found) == 1, found
    assert pointer in found[0]


@pytest.mark.supports("test_a_tree_change_out_of_form_is_refused_at_its_commit")
def test_a_tree_in_form_has_no_fault(worktree: str):
    """Given the walkthrough's tree, each input a deliverable's path or a file of the worktree
    When its faults are found
    Then there is none"""
    assert faults(the_tree(), practices(), worktree) == []


@pytest.mark.supports("test_a_tree_change_out_of_form_is_refused_at_its_commit")
def test_the_plan_open_with_its_conditions_in_order_has_no_fault(worktree: str):
    """Given the tree a run starts from, the plan open with design-tree's conditions in order
    When its faults are found
    Then there is none"""
    the = rn_files.tree([rn_files.plan(NAME, good=False)], by="reasoning")
    assert faults(the, practices(), worktree) == []


@pytest.mark.supports("test_a_tree_change_out_of_form_is_refused_at_its_commit")
@pytest.mark.parametrize(
    ("change", "pointer"),
    [
        (lambda t: t["work"][0].update(do="build"), "/work/0/do"),
        (lambda t: t["goal"].update(by="nobody"), "/goal/by"),
        (lambda t: t["deliverables"][1].pop("inputs"), "/deliverables/1"),
        (lambda t: t["deliverables"][1].update(status="done"), "/deliverables/1"),
        (
            lambda t: t["deliverables"][1]["necessary_conditions"][0]["decisions"][0].update(
                decided="The rate, as the user decided."
            ),
            "/deliverables/1/necessary_conditions/0/decisions/0",
        ),
        (
            lambda t: t["deliverables"][2]["necessary_conditions"][0].update(good="yes"),
            "/deliverables/2/necessary_conditions/0/good",
        ),
    ],
)
def test_a_place_out_of_the_schema_is_a_fault_naming_its_pointer(
    worktree: str, change: Any, pointer: str
):
    """Given the walkthrough's tree with one place out of design-tree.schema.json: a work item's do
    of neither make nor decide, a goal's by of no one, an open deliverable lacking its inputs or
    done with its conditions kept, a decision whose decided says the user decided it, or a good
    that isn't a boolean
    When its faults are found
    Then they are one line, naming the place's pointer"""
    the = the_tree()
    change(the)
    one_fault(faults(the, practices(), worktree), pointer)


@pytest.mark.supports("test_a_tree_change_out_of_form_is_refused_at_its_commit")
def test_a_kind_with_no_best_practice_is_a_fault(worktree: str):
    """Given the walkthrough's tree whose command's kind is `lights`, near light, which no best
    practice has
    When its faults are found
    Then they are one line, naming /deliverables/1/kind"""
    the = the_tree()
    the["deliverables"][1]["kind"] = "lights"
    one_fault(faults(the, practices(), worktree), "/deliverables/1/kind")


@pytest.mark.supports("test_a_tree_change_out_of_form_is_refused_at_its_commit")
def test_a_done_deliverables_kind_is_held_to_the_best_practices_too(worktree: str):
    """Given the walkthrough's tree whose done plan is of the kind `plan`, which no best practice
    has
    When its faults are found
    Then they are one line, naming /deliverables/0/kind"""
    the = the_tree()
    the["deliverables"][0]["kind"] = "plan"
    one_fault(faults(the, practices(), worktree), "/deliverables/0/kind")


@pytest.mark.supports("test_a_tree_change_out_of_form_is_refused_at_its_commit")
@pytest.mark.parametrize(
    "ids",
    [
        ["N2", "N1", "N3"],
        ["N1", "N2"],
        ["N1", "N2", "N3", "N4"],
        ["N1", "N2", "N4"],
    ],
)
def test_an_open_deliverables_conditions_other_than_its_best_practices_in_order_are_a_fault(
    worktree: str, ids: list[str]
):
    """Given the walkthrough's tree whose command, of the kind light of N1, N2, and N3, holds its
    conditions swapped, one short, one past, or one other
    When its faults are found
    Then they are one line, naming /deliverables/1/necessary_conditions"""
    the = the_tree()
    held = {each["id"]: each for each in the["deliverables"][1]["necessary_conditions"]}
    the["deliverables"][1]["necessary_conditions"] = [
        held.get(each, rn_files.condition(each)) for each in ids
    ]
    one_fault(faults(the, practices(), worktree), "/deliverables/1/necessary_conditions")


@pytest.mark.supports("test_a_tree_change_out_of_form_is_refused_at_its_commit")
def test_a_done_node_with_no_file_keeps_its_conditions_without_a_fault(worktree: str):
    """Given the walkthrough's tree beside a done node with no file of the kind light, holding its
    conditions good
    When its faults are found
    Then there is none"""
    the = the_tree()
    the["deliverables"].append(
        {
            "name": "The invoices' people",
            "path": "docs/people.md",
            "kind": "light",
            "status": "done",
            "file": False,
            "necessary_conditions": [
                rn_files.condition(each, True) for each in rn_files.conditions("light")
            ],
        }
    )
    assert faults(the, practices(), worktree) == []


@pytest.mark.supports("test_a_tree_change_out_of_form_is_refused_at_its_commit")
@pytest.mark.parametrize(
    "named", ["invoicer/nothing.py", "invoicer/lines", "invoicer/lines.py.bak"]
)
def test_an_input_naming_neither_a_deliverable_nor_a_file_of_the_worktree_is_a_fault(
    worktree: str, named: str
):
    """Given the walkthrough's tree whose command names as its input a file the worktree lacks, or
    one short of or past invoicer/lines.py, which it holds
    When its faults are found
    Then they are one line, naming /deliverables/1/inputs/0"""
    the = the_tree()
    the["deliverables"][1]["inputs"] = [named]
    one_fault(faults(the, practices(), worktree), "/deliverables/1/inputs/0")


@pytest.mark.supports("test_a_tree_change_out_of_form_is_refused_at_its_commit")
def test_an_input_is_looked_for_in_the_worktree_not_the_folder_it_runs_in(
    worktree: str, tmp_path: Any, monkeypatch: pytest.MonkeyPatch
):
    """Given the walkthrough's tree whose command names docs/new.md, which the folder the check
    runs in holds and the worktree doesn't
    When its faults are found
    Then they are one line, naming /deliverables/1/inputs/0"""
    write_files(str(tmp_path), {"docs/new.md": "# New\n"})
    monkeypatch.chdir(str(tmp_path))
    the = the_tree()
    the["deliverables"][1]["inputs"] = ["docs/new.md"]
    one_fault(faults(the, practices(), worktree), "/deliverables/1/inputs/0")


@pytest.mark.supports("test_a_tree_change_out_of_form_is_refused_at_its_commit")
def test_inputs_of_none_one_and_several_each_named_hold(worktree: str):
    """Given the walkthrough's tree whose command rests on none, and whose guide rests on the
    command, invoicer's lines, and an old document of the worktree
    When its faults are found
    Then there is none"""
    the = the_tree()
    the["deliverables"][1]["inputs"] = []
    the["deliverables"][2]["inputs"] = [COMMAND, "invoicer/lines.py", "docs/old.md"]
    assert faults(the, practices(), worktree) == []


@pytest.mark.supports("test_a_tree_change_out_of_form_is_refused_at_its_commit")
def test_a_deliverable_resting_on_itself_is_a_fault(worktree: str):
    """Given the walkthrough's tree whose command names its own path in its inputs
    When its faults are found
    Then they are one line, naming /deliverables/1"""
    the = the_tree()
    the["deliverables"][1]["inputs"] = [COMMAND]
    one_fault(faults(the, practices(), worktree), "/deliverables/1")


@pytest.mark.supports("test_a_tree_change_out_of_form_is_refused_at_its_commit")
def test_two_deliverables_resting_on_each_other_are_each_a_fault(worktree: str):
    """Given the walkthrough's tree whose command rests on the guide, which rests on the command
    When its faults are found
    Then they are two lines, one naming /deliverables/1 and one /deliverables/2"""
    the = the_tree()
    the["deliverables"][1]["inputs"] = [GUIDE]
    found = faults(the, practices(), worktree)
    assert len(found) == 2, found
    assert any("/deliverables/1" in each for each in found)
    assert any("/deliverables/2" in each for each in found)


@pytest.mark.supports("test_a_tree_change_out_of_form_is_refused_at_its_commit")
def test_a_deliverable_resting_on_one_twice_rests_on_nothing_of_itself(worktree: str):
    """Given the walkthrough's tree with a changelog resting on both the command and the guide,
    which rests on the command
    When its faults are found
    Then there is none, as no deliverable rests on itself"""
    the = the_tree()
    the["deliverables"].append(
        rn_files.open_node("The changes", "CHANGELOG.md", "light", [COMMAND, GUIDE])
    )
    assert faults(the, practices(), worktree) == []


@pytest.mark.supports("test_a_tree_change_out_of_form_is_refused_at_its_commit")
@pytest.mark.parametrize(
    ("item", "pointer"),
    [
        (rn_files.work("make", "docs/guide"), "/work/2"),
        (rn_files.work("make", "invoicer/lines.py"), "/work/2"),
        (rn_files.work("decide", COMMAND, "N4", rn_files.TAX_ABOUT), "/work/2"),
        (rn_files.work("decide", COMMAND, "N1", "the tax"), "/work/2"),
        (rn_files.work("decide", COMMAND, "N2", rn_files.TAX_ABOUT), "/work/2"),
    ],
)
def test_an_item_of_the_work_naming_no_deliverable_condition_or_about_of_it_is_a_fault(
    worktree: str, item: dict[str, Any], pointer: str
):
    """Given the walkthrough's tree with a third item of the work: a make of a path near the
    guide's, or of a file that's no deliverable, or a decide of the command naming a condition light
    lacks, an about that N1 lacks, or N2, which lacks the tax rate's about that N1 holds
    When its faults are found
    Then they are one line, naming /work/2"""
    the = the_tree()
    the["work"] = the["work"][:2] + [item]
    one_fault(faults(the, practices(), worktree), pointer)


@pytest.mark.supports(
    "test_a_point_the_orchestrator_settles_is_committed_with_its_ground_as_the_message"
)
def test_a_decide_of_an_open_point_of_its_condition_holds(worktree: str):
    """Given the walkthrough's tree whose command's N1 holds the tax rate's point open, and whose
    work decides it
    When its faults are found
    Then there is none"""
    the = the_tree()
    the["deliverables"][1]["necessary_conditions"][0]["decisions"] = [
        rn_files.decision(rn_files.TAX_ABOUT, None)
    ]
    assert faults(the, practices(), worktree) == []


@pytest.mark.supports("test_a_tree_change_out_of_form_is_refused_at_its_commit")
def test_each_fault_of_a_tree_is_given_not_only_the_first(worktree: str):
    """Given the walkthrough's tree whose done plan's kind is `plan`, which no best practice has,
    and whose first item of the work makes a path no deliverable has
    When its faults are found
    Then they are two lines, naming /deliverables/0/kind and /work/0"""
    the = copy.deepcopy(the_tree())
    the["deliverables"][0]["kind"] = "plan"
    the["work"][0]["path"] = "invoicer/cli.py"
    found = faults(the, practices(), worktree)
    assert len(found) == 2, found
    assert any("/deliverables/0/kind" in each for each in found)
    assert any("/work/0" in each for each in found)


# The steps of the way to the goal.

ONE_STEP = (
    "test_a_deliverable_at_a_step_the_user_doesnt_check_is_done_once_put_up_and_the_next_starts"
)


def stepped(*steps: dict[str, Any]) -> dict[str, Any]:
    """The walkthrough's tree with the steps given."""
    the = the_tree()
    the["steps"] = [copy.deepcopy(each) for each in steps]
    return the


@pytest.mark.supports(
    "test_a_deliverable_at_a_step_the_user_doesnt_check_is_done_once_put_up_and_the_next_starts"
)
def test_steps_holding_each_deliverable_but_the_plan_once_have_no_fault(worktree: str):
    """Given the walkthrough's tree whose steps hold the command, then the guide, each once
    When its faults are found
    Then there is none"""
    the = stepped(
        rn_files.step("what it does", [COMMAND], True),
        rn_files.step("how it's used", [GUIDE], False),
    )
    assert faults(the, practices(), worktree) == []


@pytest.mark.supports(
    "test_a_deliverable_at_a_step_the_user_doesnt_check_is_done_once_put_up_and_the_next_starts"
)
def test_a_tree_with_no_steps_has_no_fault_of_them(worktree: str):
    """Given the walkthrough's tree with no steps, as before the plan holds them
    When its faults are found
    Then there is none"""
    assert faults(stepped(), practices(), worktree) == []


@pytest.mark.supports(
    "test_a_deliverable_at_a_step_the_user_doesnt_check_is_done_once_put_up_and_the_next_starts"
)
@pytest.mark.parametrize(
    ("steps", "pointer", "words"),
    [
        (
            [rn_files.step("what it does", [COMMAND, "docs/none.md", GUIDE], True)],
            "/steps/0/deliverables/1",
            "docs/none.md, which no deliverable but the plan has",
        ),
        (
            [rn_files.step("the plan", [rn_files.plan_path(NAME), COMMAND, GUIDE], True)],
            "/steps/0/deliverables/0",
            "which no deliverable but the plan has",
        ),
        (
            [
                rn_files.step("what it does", [COMMAND, GUIDE], True),
                rn_files.step("how it's used", [GUIDE], False),
            ],
            "/steps/1/deliverables/0",
            f"{GUIDE}, which /steps/0 holds already",
        ),
        (
            [rn_files.step("what it does", [COMMAND], True)],
            "/steps",
            f"{GUIDE}, which no step holds",
        ),
    ],
    ids=["no-deliverable", "the-plan", "two-steps", "no-step"],
)
def test_a_fault_of_the_steps_names_its_place(
    worktree: str, steps: list[dict[str, Any]], pointer: str, words: str
):
    """Given the walkthrough's tree whose steps name a path that no deliverable has, the plan, a
    deliverable twice, or leave a deliverable out
    When its faults are found
    Then the one fault names the place and what's wrong there"""
    found = faults(stepped(*steps), practices(), worktree)
    one_fault(found, pointer)
    assert words in found[0]


@pytest.mark.supports(
    "test_a_deliverable_at_a_step_the_user_doesnt_check_is_done_once_put_up_and_the_next_starts"
)
def test_a_step_without_its_signoff_is_out_of_the_schema(worktree: str):
    """Given the walkthrough's tree whose one step lacks `signoff`
    When its faults are found
    Then the one fault names the step"""
    lacking = rn_files.step("what it does", [COMMAND, GUIDE], True)
    del lacking["signoff"]
    one_fault(faults(stepped(lacking), practices(), worktree), "/steps/0")
