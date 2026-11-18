"""The unit cases of tree/work.py, which decides the work beyond its schema, of tree/inputs.py,
which decides whether a deliverable's inputs cover the kinds its best practice takes, and of the
work's order in tree/turn.py. The work turns on whether an item names a node, a point of it, and
comes after each input not done, and on a change that renames a node; the inputs turn on whether a
node of the kind or a file outside the tree covers each kind taken, so the cases take each."""

from __future__ import annotations

import copy
from typing import Any

import pytest
from fault import Wrong
from tree import inputs, turn, work
from tree.sign_offs import Kind, SignOff, SignOffs, State

from dev.rn.tests.unit import rn_data as d

AT = "2026-11-18T09:00:00Z"
PLAN_SIGNED = SignOffs((SignOff(Kind.PLAN, "", State.SIGNED_OFF, AT),))


def resting(work_: list[dict[str, Any]]) -> dict[str, Any]:
    """The walkthrough's tree whose second deliverable takes from the first, with the work."""
    data = d.walkthrough_tree()
    data["deliverables"][1]["inputs"] = [*d.CODE_INPUTS, "invoicer"]
    data["work"] = work_
    return data


MAKE_HINTS = {"do": "make", "path": "invoicer"}
MAKE_TYPED = {"do": "make", "path": "invoicer/py.typed"}


@pytest.mark.supports("test_a_change_whose_work_comes_before_an_input_not_done_is_refused")
def test_work_after_each_input_holds() -> None:
    """Given: the second deliverable taking from the first, made after it in the work.
    When: the work is held.
    Then: it holds."""
    work.hold(d.design(resting([MAKE_HINTS, MAKE_TYPED])))


@pytest.mark.supports("test_a_change_whose_work_comes_before_an_input_not_done_is_refused")
@pytest.mark.parametrize("order", [[MAKE_TYPED, MAKE_HINTS], [MAKE_TYPED]])
def test_work_before_an_input_not_done_is_refused(order: list[dict[str, Any]]) -> None:
    """Given: the second deliverable taking from the first, made before it, or with no item that
    makes the first.
    When: the work is held.
    Then: it's refused, naming the item and the input."""
    with pytest.raises(Wrong, match=r"work/0 comes before invoicer, which its inputs name"):
        work.hold(d.design(resting(order)))


@pytest.mark.supports("test_a_change_whose_work_comes_before_an_input_not_done_is_refused")
def test_work_after_an_input_done_holds_with_no_item_of_it() -> None:
    """Given: the second deliverable taking from the first, which is done, and no item makes it.
    When: the work is held.
    Then: it holds."""
    data = resting([MAKE_TYPED])
    data["deliverables"][0] = d.with_status(data, "done")["deliverables"][0]
    work.hold(d.design(data))


@pytest.mark.supports("test_a_change_whose_work_comes_before_an_input_not_done_is_refused")
def test_work_naming_no_node_is_refused() -> None:
    """Given: an item of work naming a path that no deliverable holds.
    When: the work is held.
    Then: it's refused, naming the item and the path."""
    data = d.walkthrough_tree()
    data["work"] = [{"do": "make", "path": "invoicer/gone.py"}]
    with pytest.raises(Wrong, match=r"work/0 names invoicer/gone.py, no deliverable"):
        work.hold(d.design(data))


@pytest.mark.supports("test_a_change_whose_work_comes_before_an_input_not_done_is_refused")
@pytest.mark.parametrize(
    ("condition", "about", "holds"),
    [
        ("N1", "which files the hints cover", True),
        ("N2", "which files the hints cover", False),
        ("N1", "another point", False),
    ],
)
def test_a_point_to_decide_names_a_decision_of_its_condition(
    condition: str, about: str, holds: bool
) -> None:
    """Given: an item of work to decide a point of the first deliverable, by a condition and an
    about that its decision under N1 holds, or by another condition or about.
    When: the work is held.
    Then: it holds for the decision it holds, and is refused otherwise."""
    data = d.walkthrough_tree()
    data["work"] = [{"do": "decide", "path": "invoicer", "condition": condition, "about": about}]
    if holds:
        work.hold(d.design(data))
    else:
        with pytest.raises(Wrong, match=r"work/0 names no point of invoicer"):
            work.hold(d.design(data))


@pytest.mark.supports("test_a_change_whose_work_comes_before_an_input_not_done_is_refused")
def test_a_point_of_a_specific_deliverable_names_one_of_its_decisions() -> None:
    """Given: an item of work to decide a point of a specific deliverable, which holds it.
    When: the work is held.
    Then: it holds."""
    data = d.walkthrough_tree()
    data["deliverables"].append(
        {
            "name": "n",
            "path": "e2e",
            "kind": "specific",
            "inputs": [],
            "status": "open",
            "check": "c",
            "good": False,
            "decisions": [{"about": "runs", "decided": None}],
        }
    )
    data["work"] = [{"do": "decide", "path": "e2e", "about": "runs"}]
    work.hold(d.design(data))


@pytest.mark.supports("test_a_change_whose_work_comes_before_an_input_not_done_is_refused")
def test_a_node_renamed_takes_its_items_of_work_with_it() -> None:
    """Given: a change that renames the second deliverable, leaving the work as it was.
    When: the work follows the change.
    Then: its item names the new path, and the other item stays."""
    before = d.design()
    after = copy.deepcopy(d.walkthrough_tree())
    after["deliverables"][1]["path"] = "invoicer/py.typed.txt"
    moved = work.renamed(before, d.design(after))
    assert d.held(moved)["work"] == [MAKE_HINTS, {"do": "make", "path": "invoicer/py.typed.txt"}]


@pytest.mark.supports("test_a_change_whose_deliverable_leaves_out_an_input_kind_is_refused")
def test_inputs_of_a_file_for_each_kind_taken_hold(tmp_path: Any) -> None:
    """Given: the walkthrough's tree, each deliverable of code resting on a file outside the tree
    for each of the three kinds that the code best practice takes.
    When: the inputs are held.
    Then: they hold."""
    inputs.hold(d.run_of(d.repository(str(tmp_path))), d.RN, d.design())


@pytest.mark.supports("test_a_change_whose_deliverable_leaves_out_an_input_kind_is_refused")
def test_inputs_one_short_of_the_kinds_taken_are_refused(tmp_path: Any) -> None:
    """Given: the first deliverable resting on two files outside the tree, of three kinds taken.
    When: the inputs are held.
    Then: they're refused, naming the deliverable and the kinds left."""
    data = d.walkthrough_tree()
    data["deliverables"][0]["inputs"] = d.CODE_INPUTS[:2]
    with pytest.raises(Wrong, match=r"invoicer names no input of architecture, software-design"):
        inputs.hold(d.run_of(d.repository(str(tmp_path))), d.RN, d.design(data))


@pytest.mark.supports("test_a_change_whose_deliverable_leaves_out_an_input_kind_is_refused")
def test_a_node_of_a_kind_taken_covers_it(tmp_path: Any) -> None:
    """Given: the first deliverable resting on a node of the tree of test design, with no file,
    and on two files outside the tree.
    When: the inputs are held.
    Then: they hold, as the node covers its kind."""
    data = d.walkthrough_tree()
    node = d.open_deliverable(
        "Cases",
        "docs/cases",
        kind="test-design",
        status="done",
        file=False,
    )
    data["deliverables"].append(node)
    data["deliverables"][0]["inputs"] = [*d.CODE_INPUTS[:2], "docs/cases"]
    inputs.hold(d.run_of(d.repository(str(tmp_path))), d.RN, d.design(data))


@pytest.mark.supports("test_a_change_whose_deliverable_leaves_out_an_input_kind_is_refused")
def test_a_path_that_no_file_holds_covers_none(tmp_path: Any) -> None:
    """Given: the first deliverable resting on two files outside the tree and a path where no file
    lies.
    When: the inputs are held.
    Then: they're refused, as the path covers no kind."""
    data = d.walkthrough_tree()
    data["deliverables"][0]["inputs"] = [*d.CODE_INPUTS[:2], "docs/gone.md"]
    with pytest.raises(Wrong, match=r"invoicer names no input"):
        inputs.hold(d.run_of(d.repository(str(tmp_path))), d.RN, d.design(data))


@pytest.mark.supports("test_a_change_whose_deliverable_leaves_out_an_input_kind_is_refused")
def test_a_node_of_a_kind_not_taken_covers_none(tmp_path: Any) -> None:
    """Given: the second deliverable resting on the first, of code, and on two files outside the
    tree.
    When: the inputs are held.
    Then: they're refused, as code is no kind that the code best practice takes."""
    data = d.walkthrough_tree()
    data["deliverables"][1]["inputs"] = [*d.CODE_INPUTS[:2], "invoicer"]
    with pytest.raises(Wrong, match=r"invoicer/py.typed names no input"):
        inputs.hold(d.run_of(d.repository(str(tmp_path))), d.RN, d.design(data))


@pytest.mark.supports("test_a_change_whose_deliverable_leaves_out_an_input_kind_is_refused")
@pytest.mark.parametrize("status", ["done", "specific"])
def test_a_deliverable_done_or_specific_is_not_held_to_inputs(tmp_path: Any, status: str) -> None:
    """Given: the first deliverable done, or specific, resting on nothing.
    When: the inputs are held.
    Then: they hold."""
    data = d.walkthrough_tree()
    if status == "done":
        data["deliverables"][0] = {
            "name": "n",
            "path": "invoicer",
            "kind": "code",
            "status": "done",
        }
    else:
        data["deliverables"][0] = {
            "name": "n",
            "path": "invoicer",
            "kind": "specific",
            "inputs": [],
            "status": "open",
            "check": "c",
            "good": False,
            "decisions": [],
        }
    inputs.hold(d.run_of(d.repository(str(tmp_path))), d.RN, d.design(data))


@pytest.mark.supports("test_the_generator_starts_with_the_first_deliverable_in_the_works_order")
def test_the_turn_follows_the_works_order() -> None:
    """Given: the walkthrough's tree whose work makes the second deliverable first, and the plan
    signed off.
    When: each deliverable whose turn has come is marked, and the deliverables doing are given.
    Then: both come in the work's order."""
    data = d.walkthrough_tree()
    data["work"] = [MAKE_TYPED, MAKE_HINTS]
    tree, marked = turn.mark_doing(d.design(data), PLAN_SIGNED)
    assert marked == ("invoicer/py.typed", "invoicer")
    assert turn.doing(tree) == ("invoicer/py.typed", "invoicer")


@pytest.mark.supports("test_the_generator_starts_with_the_first_deliverable_in_the_works_order")
def test_a_deliverable_that_no_item_makes_gets_no_turn() -> None:
    """Given: the walkthrough's tree whose work makes the first deliverable alone, and the plan
    signed off.
    When: each deliverable whose turn has come is marked.
    Then: only the first is doing."""
    data = d.walkthrough_tree()
    data["work"] = [MAKE_HINTS, {"do": "decide", "path": "invoicer/py.typed", "about": "x"}]
    tree, marked = turn.mark_doing(d.design(data), PLAN_SIGNED)
    assert marked == ("invoicer",) and turn.doing(tree) == ("invoicer",)
