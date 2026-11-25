"""The unit cases of tree/touched.py, which nodes a change touches: `touched`, from the tree as last
committed and the tree as it stands, of a changed decision with decisions before and after it and
deliverables that name it and that it names, a deliverable added, the goal, a deliverable's path
changed, with inputs that name its old path, its new one, or a path near it, and a pointer of no
node in the tree as it stands; and `changed`, of trees equal, of a value changed, of a decision
answered, and of a node added or taken away.

Each node of the design tree is the goal, a deliverable, a necessary condition, or a decision, by
its JSON Pointer; the nodes up to the goal from a change are those that hold it, and the order from
the goal down is the tree's own, the goal first, then the deliverables."""

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
    command; the spec, with one decision of N1; and notes, resting on a path near the command's."""
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
                ]
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


def test_a_changed_decision_touches_what_holds_it_its_later_decisions_and_each_link():
    """Given the six deliverables' tree
    When the command's N1's second decision changes
    Then it touches, from the goal down, the goal, the command, its N1, its N2's decision, the
    guide and the changelog that rest on it, and the spec it rests on; not its N1's first
    decision or the notes"""
    assert touched_by("/deliverables/1/necessary_conditions/0/decisions/1") == [
        "/goal",
        "/deliverables/1",
        "/deliverables/1/necessary_conditions/0",
        "/deliverables/1/necessary_conditions/1/decisions/0",
        "/deliverables/2",
        "/deliverables/3",
        "/deliverables/4",
    ]


def test_a_deliverable_added_since_the_commit_touches_the_goal_and_the_one_it_names():
    """Given the six deliverables' tree as committed, and the tree as it stands with a seventh, the
    usage, resting on the command
    When touched is asked of the usage
    Then it gives the goal and the command"""
    after = the_tree()
    after["deliverables"].append(rn_files.open_node("The usage", "USAGE.md", "light", [COMMAND]))
    assert touched(the_tree(), after, "/deliverables/6") == ["/goal", "/deliverables/1"]


def test_a_change_of_the_goal_touches_nothing_above_it():
    """Given the six deliverables' tree
    When the goal changes, and when its sentence changes
    Then the goal touches none, and its sentence touches the goal"""
    assert touched_by("/goal", {"decided": "The team prints.", "by": "user"}) == []
    assert touched_by("/goal/decided") == ["/goal"]


def test_touched_refuses_a_pointer_of_no_node():
    """Given the six deliverables' tree, as committed and as it stands
    When a change at a deliverable one past the last is asked
    Then it refuses with Wrong naming the pointer"""
    with pytest.raises(Wrong, match="/deliverables/6"):
        touched(the_tree(), the_tree(), "/deliverables/6")


def test_a_changed_path_touches_one_that_names_the_new_path_and_one_that_names_the_old():
    """Given the six deliverables' tree as committed, and as it stands with the command's path
    invoicer/cli.py, the guide's input renamed to it, the changelog still on the old path, and
    the notes resting on invoicer/cli.pyc
    When the change of the command's path is asked
    Then it touches the guide by the new path and the changelog by the old, and not the notes,
    whose input nearly matches the new path"""
    after = changed_at("/deliverables/1/path", NEW)
    after["deliverables"][2]["inputs"] = [NEW]
    after["deliverables"][5]["inputs"] = ["invoicer/cli.pyc"]
    assert touched(the_tree(), after, "/deliverables/1/path") == [
        "/goal",
        "/deliverables/1",
        "/deliverables/2",
        "/deliverables/3",
        "/deliverables/4",
    ]


# changed


def test_trees_equal_have_no_change():
    """Given the six deliverables' tree, and a copy of it
    When the change between them is found
    Then there is none"""
    assert changed(the_tree(), the_tree()) == []


def test_a_value_changed_is_its_deepest_node():
    """Given the six deliverables' tree, and one whose guide's N1 is good
    When the change between them is found
    Then it is the pointer of that good alone"""
    after = the_tree()
    after["deliverables"][2]["necessary_conditions"][0]["good"] = True
    assert changed(the_tree(), after) == ["/deliverables/2/necessary_conditions/0/good"]


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


def test_a_node_added_or_taken_away_is_the_node_itself():
    """Given the six deliverables' tree, one with a third decision of the command's N1, and one
    without the notes
    When the change from the tree to each is found
    Then it is the decision added, and the notes taken away"""
    added = the_tree()
    added["deliverables"][1]["necessary_conditions"][0]["decisions"].append(D("the font", "Mono."))
    taken = the_tree()
    taken["deliverables"].pop()
    assert changed(the_tree(), added) == ["/deliverables/1/necessary_conditions/0/decisions/2"]
    assert changed(the_tree(), taken) == ["/deliverables/5"]
