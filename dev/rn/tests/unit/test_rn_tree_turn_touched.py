"""The unit cases of tree/turn.py, which decides each deliverable's turn, and of tree/touched.py,
which decides the nodes a change touches. A turn turns on three conditions, the plan signed off,
an open point under the deliverable, and a deliverable it takes from not yet signed off, so the
cases take each combination that can occur, with a deliverable already doing and one done. The
nodes touched turn on where the node changed lies and what rests on it, so the cases take a node
deep in a deliverable, a deliverable another takes from, no node, and a node changed twice."""

from __future__ import annotations

import pytest
from tree import touched, turn
from tree.sign_offs import Kind, SignOff, SignOffs, State

from dev.rn.tests.unit import rn_data as d

AT = "2026-11-15T09:00:00Z"
PLAN_SIGNED = SignOffs((SignOff(Kind.PLAN, "", State.SIGNED_OFF, AT),))
PLAN_WAITING = SignOffs((SignOff(Kind.PLAN, "", State.WAITING, AT),))
POINT = {"about": "where the marker lies", "decided": None}


@pytest.mark.supports("test_ty_approves_the_plan_and_starts_the_work_resting_on_it")
def test_the_plan_signed_off_with_no_point_open_marks_each_deliverable_doing() -> None:
    """Given: the walkthrough's tree, both deliverables open, no point open, and the plan signed
    off.
    When: each deliverable whose turn has come is marked.
    Then: both are doing, and both paths are given in the order of the work."""
    tree, marked = turn.mark_doing(d.design(), PLAN_SIGNED)
    assert [e["status"] for e in d.held(tree)["deliverables"]] == ["doing", "doing"]
    assert marked == ("invoicer", "invoicer/py.typed")


@pytest.mark.supports("test_work_resting_on_the_plan_waits_until_the_user_signs_it_off")
@pytest.mark.parametrize("signed", [SignOffs(()), PLAN_WAITING])
def test_the_plan_not_signed_off_marks_nothing(signed: SignOffs) -> None:
    """Given: the walkthrough's tree, and the plan not yet put up or waiting for the user.
    When: each deliverable whose turn has come is marked.
    Then: none is, and the tree is as it was."""
    tree, marked = turn.mark_doing(d.design(), signed)
    assert marked == () and tree.data == d.walkthrough_tree()


@pytest.mark.supports("test_a_users_point_written_open_keeps_its_deliverable_waiting")
def test_a_point_open_keeps_its_deliverable_waiting() -> None:
    """Given: the walkthrough's tree with a point open under its second deliverable, and the plan
    signed off.
    When: each deliverable whose turn has come is marked.
    Then: only the first is doing."""
    data = d.walkthrough_tree()
    data["deliverables"][1]["necessary_conditions"][0]["decisions"] = [POINT]
    tree, marked = turn.mark_doing(d.design(data), PLAN_SIGNED)
    assert marked == ("invoicer",)
    assert d.held(tree)["deliverables"][1]["status"] == "open"


@pytest.mark.supports("test_work_resting_on_the_plan_waits_until_the_user_signs_it_off")
@pytest.mark.parametrize("state", [State.WAITING, State.SENT_BACK, None])
def test_a_deliverable_taking_from_one_not_signed_off_waits(state: State | None) -> None:
    """Given: the walkthrough's tree whose second deliverable takes from the first, and the plan
    signed off, with the first deliverable waiting for the user, sent back, or not put up.
    When: each deliverable whose turn has come is marked.
    Then: the second stays open."""
    data = d.walkthrough_tree()
    data["deliverables"][1]["inputs"] = ["invoicer"]
    each = list(PLAN_SIGNED.each)
    if state is not None:
        each.append(SignOff(Kind.DELIVERABLE, "invoicer", state, AT))
    _, marked = turn.mark_doing(d.design(data), SignOffs(tuple(each)))
    assert "invoicer/py.typed" not in marked


@pytest.mark.supports("test_a_deliverable_put_up_and_approved_is_marked_done")
def test_a_deliverable_taking_from_one_signed_off_gets_its_turn() -> None:
    """Given: the walkthrough's tree whose second deliverable takes from the first, the first done,
    and the plan and the first deliverable signed off.
    When: each deliverable whose turn has come is marked.
    Then: the second is doing."""
    data = d.walkthrough_tree()
    data["deliverables"][0] = {
        "name": "Type hints",
        "path": "invoicer",
        "kind": "code",
        "status": "done",
    }
    data["deliverables"][1]["inputs"] = ["invoicer"]
    signed = SignOffs(
        PLAN_SIGNED.each + (SignOff(Kind.DELIVERABLE, "invoicer", State.SIGNED_OFF, AT),)
    )
    _, marked = turn.mark_doing(d.design(data), signed)
    assert marked == ("invoicer/py.typed",)


@pytest.mark.supports("test_a_users_point_answered_marks_its_deliverable_doing")
def test_a_deliverable_already_doing_isnt_given_again() -> None:
    """Given: the walkthrough's tree, its first deliverable doing, and the plan signed off.
    When: each deliverable whose turn has come is marked.
    Then: only the second is given as marked."""
    _, marked = turn.mark_doing(d.design(d.with_status(d.walkthrough_tree(), "doing")), PLAN_SIGNED)
    assert marked == ("invoicer/py.typed",)


@pytest.mark.supports("test_the_generator_starts_with_its_cut_of_the_first_deliverable_doing")
@pytest.mark.parametrize(
    ("statuses", "doing"),
    [
        (("open", "open"), ()),
        (("doing", "open"), ("invoicer",)),
        (("doing", "doing"), ("invoicer", "invoicer/py.typed")),
    ],
)
def test_the_deliverables_doing_are_given_in_the_order_of_the_work(
    statuses: tuple[str, str], doing: tuple[str, ...]
) -> None:
    """Given: the walkthrough's tree with none, one, or both deliverables doing.
    When: the deliverables doing are asked.
    Then: it gives each one's path, in the order of the work."""
    assert turn.doing(d.design(d.with_status(d.walkthrough_tree(), *statuses))) == doing


@pytest.mark.supports("test_a_change_gives_each_node_it_touches_with_the_path_up")
def test_a_decision_changed_touches_the_path_up_to_its_deliverable() -> None:
    """Given: the walkthrough's tree.
    When: the nodes touched by its decision under N1 are asked.
    Then: they hold its necessary condition and its deliverable, each once, in the order of the
    tree."""
    found = touched.touched(d.design(), ["deliverables/0/necessary_conditions/0/decisions/0"])
    assert "deliverables/0/necessary_conditions/0" in found and "deliverables/0" in found
    assert found.index("deliverables/0") < found.index("deliverables/0/necessary_conditions/0")
    assert len(found) == len(set(found))


@pytest.mark.supports("test_a_change_gives_each_node_it_touches_with_the_path_up")
def test_a_deliverable_changed_touches_each_deliverable_that_takes_from_it() -> None:
    """Given: the walkthrough's tree whose second deliverable takes from the first.
    When: the nodes touched by the first deliverable are asked.
    Then: they hold the second deliverable, which rests on it by path."""
    data = d.walkthrough_tree()
    data["deliverables"][1]["inputs"] = ["invoicer"]
    assert "deliverables/1" in touched.touched(d.design(data), ["deliverables/0"])


@pytest.mark.supports("test_a_change_gives_each_node_it_touches_with_the_path_up")
def test_no_node_changed_touches_none() -> None:
    """Given: the walkthrough's tree.
    When: the nodes touched by no change are asked.
    Then: it gives none."""
    assert touched.touched(d.design(), []) == ()


@pytest.mark.supports("test_a_change_gives_each_node_it_touches_with_the_path_up")
def test_two_nodes_of_one_deliverable_touch_its_path_up_once() -> None:
    """Given: the walkthrough's tree.
    When: the nodes touched by two necessary conditions of its first deliverable are asked.
    Then: the deliverable is given once."""
    found = touched.touched(
        d.design(),
        ["deliverables/0/necessary_conditions/0", "deliverables/0/necessary_conditions/1"],
    )
    assert found.count("deliverables/0") == 1
