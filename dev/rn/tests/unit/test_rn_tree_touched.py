"""The unit cases of tree/touched.py, which nodes a change touches: `touched`, from the tree as last
committed and the tree as it stands, of a changed decision with decisions before and after it, the
last decision, a deliverable named by none, a node of another that names it and one it names, the
goal, a deliverable's path changed, with inputs and items of the work that name its old path, its
new one, or a path near either, and a pointer of no node in the tree as it stands, beside a
deliverable whose input nearly matches and items of the work of other paths; and `changed`, of
trees equal, of a value changed, of a node added or taken away, of a decision answered, and of two
changes.

Each node of the design tree is the goal, a deliverable, a necessary condition, a decision, or an
item of the work, by its JSON Pointer; the nodes up to the goal from a change are those that hold
it, and the order from the goal down is the tree's own, the goal first, then the deliverables, then
the work."""

from __future__ import annotations

import json
from typing import Any

import pytest
import rn_files
from fault import Wrong
from rn_files import COMMAND, GOAL, GUIDE
from tree.touched import changed, touched

NAME = "20261120-a-command-with-which-the"
SPEC = "docs/spec.md"
D = rn_files.decision


def the_tree() -> dict[str, Any]:
    """A tree of six deliverables, read from its JSON: the plan, done; the command, resting on the
    spec, with two decisions of N1 and one of N2; the guide and the changelog, each resting on the
    command; the spec, with one decision of N1; and notes, resting on a path near the command's;
    and the work making the command and the guide, deciding the command's N1, and making the
    spec."""
    command = rn_files.decided(
        rn_files.open_node(rn_files.COMMAND_NAME, COMMAND, "light", [SPEC]),
        {
            "N1": [D("the rate", "With each invoice."), D("the file", "CSV.")],
            "N2": [D("the name", "invoicer")],
        },
    )
    spec = rn_files.decided(
        rn_files.open_node("The spec", SPEC, "light"), {"N1": [D("its reader", "The developer.")]}
    )
    return json.loads(
        json.dumps(
            rn_files.tree(
                [
                    rn_files.done_node(GOAL, rn_files.plan_path(NAME), "design-tree"),
                    command,
                    rn_files.open_node(rn_files.GUIDE_NAME, GUIDE, "readme", [COMMAND]),
                    spec,
                    rn_files.open_node("The changes", "CHANGELOG.md", "light", [COMMAND]),
                    rn_files.open_node("Notes", "NOTES.md", "light", ["invoicer/__main__.pyc"]),
                ],
                [
                    rn_files.work("make", COMMAND),
                    rn_files.work("make", GUIDE),
                    rn_files.work("decide", COMMAND, "N1", "the file"),
                    rn_files.work("make", SPEC),
                ],
            )
        )
    )


def changed_at(pointer: str, value: Any) -> dict[str, Any]:
    """The six deliverables' tree with the value at the pointer, as the orchestrator changes it."""
    after = the_tree()
    *path, last = pointer.strip("/").split("/")
    node: Any = after
    for each in path:
        node = node[int(each)] if isinstance(node, list) else node[each]
    if isinstance(node, list):
        node[int(last)] = value
    else:
        node[last] = value
    return after


def touched_by(pointer: str, value: Any = "Changed.") -> list[str]:
    """The nodes that a change of the six deliverables' tree to the value at the pointer touches."""
    return touched(the_tree(), changed_at(pointer, value), pointer)


NEW = "invoicer/cli.py"


# touched


@pytest.mark.supports("test_the_pruner_rewrites_each_node_its_change_touches_before_the_commit")
def test_a_changed_decision_touches_what_holds_it_its_later_decisions_and_each_link():
    """Given the six deliverables' tree
    When the command's N1's second decision changes
    Then it touches, from the goal down, the goal, the command, its N1, its N2's decision, the
    guide and the changelog that rest on it, the spec it rests on, and the work making it and
    deciding its N1; not its N1's first decision, the notes, or the work of the guide or the spec"""
    assert touched_by("/deliverables/1/necessary_conditions/0/decisions/1") == [
        "/goal",
        "/deliverables/1",
        "/deliverables/1/necessary_conditions/0",
        "/deliverables/1/necessary_conditions/1/decisions/0",
        "/deliverables/2",
        "/deliverables/3",
        "/deliverables/4",
        "/work/0",
        "/work/2",
    ]


@pytest.mark.supports("test_the_pruner_rewrites_each_node_its_change_touches_before_the_commit")
def test_the_last_decision_of_a_deliverable_touches_none_of_its_earlier_decisions():
    """Given the six deliverables' tree
    When the command's N2's one decision, its last, changes
    Then it touches the goal, the command, its N2, the guide, the spec, the changelog, and the
    work making it and deciding its N1, and none of its N1's decisions"""
    assert touched_by("/deliverables/1/necessary_conditions/1/decisions/0") == [
        "/goal",
        "/deliverables/1",
        "/deliverables/1/necessary_conditions/1",
        "/deliverables/2",
        "/deliverables/3",
        "/deliverables/4",
        "/work/0",
        "/work/2",
    ]


@pytest.mark.supports("test_the_pruner_rewrites_each_node_its_change_touches_before_the_commit")
def test_a_change_of_a_deliverable_that_one_names_touches_the_one_that_names_it():
    """Given the six deliverables' tree
    When the spec's N1's decision changes
    Then it touches the goal, the command that rests on the spec, the spec, its N1, and the work
    making the spec"""
    assert touched_by("/deliverables/3/necessary_conditions/0/decisions/0") == [
        "/goal",
        "/deliverables/1",
        "/deliverables/3",
        "/deliverables/3/necessary_conditions/0",
        "/work/3",
    ]


@pytest.mark.supports("test_the_pruner_rewrites_each_node_its_change_touches_before_the_commit")
def test_a_change_of_a_deliverable_that_none_names_touches_the_goal_and_itself():
    """Given the six deliverables' tree
    When the done plan's status changes
    Then it touches the goal and the plan alone"""
    assert touched_by("/deliverables/0/status", "doing") == ["/goal", "/deliverables/0"]


@pytest.mark.supports("test_the_pruner_rewrites_each_node_its_change_touches_before_the_commit")
def test_a_change_of_the_goal_touches_nothing_above_it():
    """Given the six deliverables' tree
    When the goal changes, and when its sentence changes
    Then the goal touches none, and its sentence touches the goal"""
    assert touched_by("/goal", {"decided": "The team prints.", "by": "user"}) == []
    assert touched_by("/goal/decided") == ["/goal"]


@pytest.mark.supports("test_the_pruner_rewrites_each_node_its_change_touches_before_the_commit")
def test_a_node_reached_by_two_links_is_touched_once():
    """Given the six deliverables' tree whose spec rests on the command too
    When the command's N2's decision changes
    Then the spec, which the command names and which names it, is touched once"""
    before = the_tree()
    before["deliverables"][3]["inputs"] = [COMMAND]
    after = json.loads(json.dumps(before))
    after["deliverables"][1]["necessary_conditions"][1]["decisions"][0] = D("the name", "inv")
    got = touched(before, after, "/deliverables/1/necessary_conditions/1/decisions/0")
    assert got.count("/deliverables/3") == 1


@pytest.mark.supports("test_the_pruner_rewrites_each_node_its_change_touches_before_the_commit")
@pytest.mark.parametrize(
    "pointer", ["/deliverables/6", "/deliverables/1/necessary_conditions/0/decisions/2", "/work/4"]
)
def test_touched_refuses_a_pointer_of_no_node(pointer: str):
    """Given the six deliverables' tree, as committed and as it stands
    When a change at a deliverable, a decision, or an item one past the last is asked
    Then it refuses with Wrong naming the pointer"""
    with pytest.raises(Wrong, match=pointer):
        touched(the_tree(), the_tree(), pointer)


@pytest.mark.supports("test_the_pruner_rewrites_each_node_its_change_touches_before_the_commit")
def test_a_pointer_of_a_node_taken_away_since_the_commit_is_refused():
    """Given the six deliverables' tree as committed, and as it stands without its notes
    When a change at the notes, /deliverables/5, is asked
    Then it refuses with Wrong naming the pointer, as the pointer names a node of the tree as it
    stands"""
    after = the_tree()
    after["deliverables"].pop()
    with pytest.raises(Wrong, match="/deliverables/5"):
        touched(the_tree(), after, "/deliverables/5")


@pytest.mark.supports("test_the_pruner_rewrites_each_node_its_change_touches_before_the_commit")
def test_a_changed_path_touches_each_deliverable_and_item_that_still_names_the_old_one():
    """Given the six deliverables' tree as committed, and as it stands with the command's path
    invoicer/cli.py, the guide and the changelog still naming invoicer/__main__.py
    When the change of the command's path is asked
    Then it touches the goal, the command, the guide and the changelog by the old path, the spec
    it names, and the work making it and deciding its N1 by the old path; not the notes, whose
    input nearly matches the old path"""
    assert touched_by("/deliverables/1/path", NEW) == [
        "/goal",
        "/deliverables/1",
        "/deliverables/2",
        "/deliverables/3",
        "/deliverables/4",
        "/work/0",
        "/work/2",
    ]


@pytest.mark.supports("test_the_pruner_rewrites_each_node_its_change_touches_before_the_commit")
def test_a_changed_path_touches_one_that_names_the_new_path_and_one_that_names_the_old():
    """Given the six deliverables' tree as committed, and as it stands with the command's path
    invoicer/cli.py, the guide's input and the work's first item renamed to it, the changelog and
    the work's deciding item still on the old path, and the notes resting on invoicer/cli.pyc
    When the change of the command's path is asked
    Then it touches the guide by the new path and the changelog by the old, and both items of the
    work, and not the notes, whose input nearly matches the new path"""
    after = changed_at("/deliverables/1/path", NEW)
    after["deliverables"][2]["inputs"] = [NEW]
    after["deliverables"][5]["inputs"] = ["invoicer/cli.pyc"]
    after["work"][0]["path"] = NEW
    assert touched(the_tree(), after, "/deliverables/1/path") == [
        "/goal",
        "/deliverables/1",
        "/deliverables/2",
        "/deliverables/3",
        "/deliverables/4",
        "/work/0",
        "/work/2",
    ]


@pytest.mark.supports("test_the_pruner_rewrites_each_node_its_change_touches_before_the_commit")
def test_a_changed_path_of_a_deliverable_that_none_names_touches_no_other_deliverable():
    """Given the six deliverables' tree as committed, and as it stands with the notes' path
    NOTES.txt
    When the change of the notes' path is asked
    Then it touches the goal and the notes alone, as no input or item names NOTES.md or
    NOTES.txt"""
    assert touched_by("/deliverables/5/path", "NOTES.txt") == ["/goal", "/deliverables/5"]


# changed


@pytest.mark.supports("test_the_pruner_rewrites_each_node_its_change_touches_before_the_commit")
def test_trees_equal_have_no_change():
    """Given the six deliverables' tree, and a copy of it
    When the change between them is found
    Then there is none"""
    assert changed(the_tree(), the_tree()) == []


@pytest.mark.supports("test_the_pruner_rewrites_each_node_its_change_touches_before_the_commit")
def test_a_value_changed_is_its_deepest_node():
    """Given the six deliverables' tree, and one whose guide's N1 is good
    When the change between them is found
    Then it is the pointer of that good alone"""
    after = the_tree()
    after["deliverables"][2]["necessary_conditions"][0]["good"] = True
    assert changed(the_tree(), after) == ["/deliverables/2/necessary_conditions/0/good"]


@pytest.mark.supports("test_the_pruner_rewrites_each_node_its_change_touches_before_the_commit")
def test_a_decision_answered_changes_its_decided_and_adds_its_by():
    """Given a tree whose command's N1 holds a point open, and one where the user answered it
    When the change between them is found
    Then it is the decision's decided and by, in that order"""
    before = the_tree()
    before["deliverables"][1]["necessary_conditions"][0]["decisions"][0] = D("the rate", None)
    after = the_tree()
    after["deliverables"][1]["necessary_conditions"][0]["decisions"][0] = D(
        "the rate", "Each.", "user"
    )
    assert changed(before, after) == [
        "/deliverables/1/necessary_conditions/0/decisions/0/decided",
        "/deliverables/1/necessary_conditions/0/decisions/0/by",
    ]


@pytest.mark.supports("test_the_pruner_rewrites_each_node_its_change_touches_before_the_commit")
def test_a_node_added_or_taken_away_is_the_node_itself():
    """Given the six deliverables' tree, one with a third decision of the command's N1, and one
    without the work's last item
    When the change from the tree to each is found
    Then it is the decision added, and the item taken away"""
    added = the_tree()
    added["deliverables"][1]["necessary_conditions"][0]["decisions"].append(D("the font", "Mono."))
    taken = the_tree()
    taken["work"].pop()
    assert changed(the_tree(), added) == ["/deliverables/1/necessary_conditions/0/decisions/2"]
    assert changed(the_tree(), taken) == ["/work/3"]


@pytest.mark.supports("test_the_pruner_rewrites_each_node_its_change_touches_before_the_commit")
def test_two_changes_are_given_from_the_goal_down():
    """Given the six deliverables' tree, and one whose work's first item makes the guide and whose
    goal is by reasoning
    When the change between them is found
    Then it is the goal's by, then the work's first item's path"""
    after = the_tree()
    after["work"][0]["path"] = GUIDE
    after["goal"]["by"] = "reasoning"
    assert changed(the_tree(), after) == ["/goal/by", "/work/0/path"]
