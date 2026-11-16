"""The unit cases of tree/design.py, which decides the design tree's form on disk: reading it, a
change applied to its nodes by their paths, the paths that differ, and writing it. The cases take a
tree in its form and each way out of it, a file missing, a change that sets, adds, and removes a
node, one whose path names none, one that leaves the form, and trees that differ by nothing, one
node, a node added, and a node removed."""

from __future__ import annotations

import os
from typing import Any

import pytest
from fault import CantRun, Wrong
from tree import design
from tree.design import Change

from dev.rn.tests.unit import rn_data as d

DECISION = "deliverables/0/necessary_conditions/0/decisions/0"


@pytest.mark.supports("test_the_goal_and_the_plan_reach_the_design_tree_through_the_tree_keeper")
def test_a_tree_in_its_form_is_read_as_written(tmp_path: Any) -> None:
    """Given: a run whose design-tree.json holds the walkthrough's tree.
    When: the tree is read.
    Then: it gives the tree as written."""
    run = d.run_of(d.repository(str(tmp_path)))
    d.tree_written(run)
    assert design.read(run).data == d.walkthrough_tree()


@pytest.mark.supports("test_tree_py_refuses_a_change_that_leaves_the_design_trees_form")
@pytest.mark.parametrize(
    ("place", "data"),
    [
        ("goal", {"deliverables": []}),
        (
            "deliverables/0/status",
            {**d.walkthrough_tree(), "deliverables": [{"status": "finished"}]},
        ),
        ("unknown", {**d.walkthrough_tree(), "unknown": 1}),
    ],
)
def test_a_tree_out_of_its_form_is_refused_naming_the_place(
    tmp_path: Any, place: str, data: dict[str, Any]
) -> None:
    """Given: a run whose design-tree.json lacks the goal, holds a deliverable out of its form, or
    holds a field the form has no place for.
    When: the tree is read.
    Then: it's refused, naming the place out of form."""
    run = d.run_of(d.repository(str(tmp_path)))
    d.write_json(os.path.join(run.folder, "design-tree.json"), data)
    with pytest.raises(Wrong, match=place.split("/")[0]):
        design.read(run)


@pytest.mark.supports("test_the_goal_and_the_plan_reach_the_design_tree_through_the_tree_keeper")
def test_a_tree_missing_cant_be_read(tmp_path: Any) -> None:
    """Given: a run whose folder holds no design-tree.json.
    When: the tree is read.
    Then: it couldn't run."""
    with pytest.raises(CantRun):
        design.read(d.run_of(d.repository(str(tmp_path))))


@pytest.mark.supports("test_a_users_point_answered_marks_its_deliverable_doing")
def test_a_change_sets_a_node_by_its_path(tmp_path: Any) -> None:
    """Given: the walkthrough's tree.
    When: a change sets the decision at its path to one by reasoning.
    Then: the tree changed holds it there, and the tree given is as it was."""
    tree = d.design()
    decided = {"about": "which files the hints cover", "decided": "each file", "by": "reasoning"}
    after = design.apply(tree, Change({DECISION: decided}))
    assert d.held(after)["deliverables"][0]["necessary_conditions"][0]["decisions"] == [decided]
    assert tree.data == d.walkthrough_tree()


@pytest.mark.supports("test_a_change_to_a_best_practice_the_user_takes_is_added_as_a_deliverable")
def test_a_change_adds_a_node_at_the_end_of_a_list(tmp_path: Any) -> None:
    """Given: the walkthrough's tree of two deliverables.
    When: a change sets deliverables/2, one past the last.
    Then: the tree changed holds three deliverables, the new one last."""
    added = d.open_deliverable(
        "A maker of a typed library ships its marker", ".rn/best-practices/code"
    )
    after = design.apply(d.design(), Change({"deliverables/2": added}))
    assert d.held(after)["deliverables"][-1] == added and len(d.held(after)["deliverables"]) == 3


@pytest.mark.supports("test_a_change_sent_back_to_the_tree_keeper_is_written_again")
def test_a_change_removes_a_node_given_none(tmp_path: Any) -> None:
    """Given: the walkthrough's tree, with one decision under N1 of its first deliverable.
    When: a change gives that decision none.
    Then: the tree changed holds no decision there."""
    after = design.apply(d.design(), Change({DECISION: None}))
    assert d.held(after)["deliverables"][0]["necessary_conditions"][0]["decisions"] == []


@pytest.mark.supports("test_tree_py_refuses_a_change_that_leaves_the_design_trees_form")
@pytest.mark.parametrize(
    "path", ["deliverables/7/name", "deliverables/0/nothing/0", "deliverables/0/nothing", "goals"]
)
def test_a_change_whose_path_names_no_node_is_refused(path: str) -> None:
    """Given: the walkthrough's tree.
    When: a change sets a node by a path past the end of a list, through a field that isn't there,
    or at the top beside the goal.
    Then: it's refused, naming the path."""
    with pytest.raises(Wrong, match=path):
        design.apply(d.design(), Change({path: "x"}))


@pytest.mark.supports("test_tree_py_refuses_a_change_that_leaves_the_design_trees_form")
def test_a_change_that_leaves_the_form_is_refused(tmp_path: Any) -> None:
    """Given: the walkthrough's tree.
    When: a change sets a deliverable's status to one the form doesn't name.
    Then: it's refused, naming the place."""
    with pytest.raises(Wrong, match="deliverables/0/status"):
        design.apply(d.design(), Change({"deliverables/0/status": "finished"}))


@pytest.mark.supports("test_a_change_gives_each_node_it_touches_with_the_path_up")
def test_trees_alike_differ_by_nothing() -> None:
    """Given: two trees alike.
    When: what changed between them is asked.
    Then: it gives no path."""
    assert design.changed(d.design(), d.design()) == ()


@pytest.mark.supports("test_a_change_gives_each_node_it_touches_with_the_path_up")
def test_trees_that_differ_by_one_decision_give_its_path() -> None:
    """Given: the walkthrough's tree, and the same with the decision under N1 changed.
    When: what changed is asked.
    Then: it gives the decision's path alone."""
    after = d.walkthrough_tree()
    after["deliverables"][0]["necessary_conditions"][0]["decisions"][0]["decided"] = "some files"
    assert design.changed(d.design(), d.design(after)) == (DECISION,)


@pytest.mark.supports("test_the_goal_and_the_plan_reach_the_design_tree_through_the_tree_keeper")
def test_trees_that_differ_by_nodes_added_and_removed_give_each_in_the_trees_order() -> None:
    """Given: the walkthrough's tree, and the same with its goal changed and its second deliverable
    removed.
    When: what changed is asked.
    Then: it gives the goal's path and then the deliverable's, in the order of the tree."""
    after = d.walkthrough_tree()
    after["goal"]["by"] = "reasoning"
    del after["deliverables"][1]
    assert design.changed(d.design(), d.design(after)) == ("goal", "deliverables/1")


@pytest.mark.supports("test_the_goal_and_the_plan_reach_the_design_tree_through_the_tree_keeper")
def test_a_tree_written_is_read_back_alike(tmp_path: Any) -> None:
    """Given: a run, and the walkthrough's tree.
    When: the tree is written, and read again.
    Then: writing gives the path of design-tree.json from the worktree, and reading gives the tree
    alike."""
    run = d.run_of(d.repository(str(tmp_path)))
    path = design.write(run, d.design())
    assert path == os.path.relpath(os.path.join(run.folder, "design-tree.json"), run.worktree)
    assert design.read(run).data == d.walkthrough_tree()
