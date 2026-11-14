"""The unit cases of tree/design.py, the form of a run's design tree, through `loads`, `dumps`,
`load`, `save`, `order_faults`, `points`, and `deliverable`."""

from __future__ import annotations

import dataclasses
import json
import os
from typing import Any

import pytest
from fault import Wrong
from rn_example import GOAL, HINTS, POINT, TYPED
from rn_parts import ANSWERED, OPEN_POINT, done, hints, schema_tree, typed, walkthrough
from tree.design import (
    DesignTree,
    Point,
    deliverable,
    dumps,
    load,
    loads,
    order_faults,
    points,
    save,
)

pytestmark = pytest.mark.xfail(strict=True, reason="rn's parts are skeletons, their bodies unbuilt")


@pytest.mark.supports(
    "test_the_goal_and_the_plan_written_commit_the_design_tree_with_the_point_open"
)
def test_loads_reads_the_goal_each_deliverable_and_each_decision():
    """Given the walkthrough's design tree in the schema's form, the typed marker done
    When it's read
    Then it holds the goal by the user, the hints with the answer under N3, and the typed marker
    done with nothing but its name, path, kind, and status"""
    read = loads(json.dumps(schema_tree()), "design-tree.json")
    assert (read.goal, read.by) == (GOAL, "user")
    assert read.deliverables[0].conditions[0].decisions == (ANSWERED,)
    assert read.deliverables[1] == done(typed())


@pytest.mark.supports(
    "test_the_goal_and_the_plan_written_commit_the_design_tree_with_the_point_open"
)
def test_loads_reads_an_open_decision_as_none():
    """Given the walkthrough's tree with the point's `decided` null and no `by`
    When it's read
    Then the decision is open, with `decided` None"""
    given = schema_tree()
    given["deliverables"][0]["necessary_conditions"][0]["decisions"] = [
        {"about": POINT, "decided": None}
    ]
    assert loads(json.dumps(given), "t").deliverables[0].conditions[0].decisions == (OPEN_POINT,)


@pytest.mark.supports(
    "test_the_goal_and_the_plan_written_commit_the_design_tree_with_the_point_open"
)
def test_dumps_gives_what_loads_reads_back_as_it_was():
    """Given the walkthrough's design tree with the point open
    When it's written and read back
    Then it's the same tree"""
    tree = walkthrough(hints(OPEN_POINT), typed())
    assert loads(dumps(tree), "t") == tree


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("goal", {"decided": GOAL}),
        ("goal", {"decided": GOAL, "by": "orchestrator"}),
        ("deliverables", {}),
    ],
)
@pytest.mark.supports("test_write_refuses_a_tree_out_of_the_schemas_form_naming_the_field")
def test_loads_refuses_a_field_out_of_the_schemas_form_naming_it(field: str, value: Any):
    """Given the walkthrough's tree with a goal without `by`, a goal by `orchestrator`, or
    deliverables as an object
    When it's read
    Then it's refused, naming the file and the field"""
    with pytest.raises(Wrong, match=rf"design-tree\.json.*{field}"):
        loads(json.dumps(schema_tree(**{field: value})), "design-tree.json")


@pytest.mark.supports("test_write_refuses_a_tree_out_of_the_schemas_form_naming_the_field")
def test_loads_refuses_text_that_isnt_json():
    """Given `{` as the tree
    When it's read
    Then it's refused, naming the file"""
    with pytest.raises(Wrong, match="design-tree.json"):
        loads("{", "design-tree.json")


@pytest.mark.supports("test_write_refuses_a_tree_out_of_the_schemas_form_naming_the_field")
def test_loads_refuses_a_deliverable_done_with_fields_of_one_open():
    """Given the typed marker done with its inputs still listed
    When it's read
    Then it's refused, naming `inputs`"""
    given = schema_tree()
    given["deliverables"][1]["inputs"] = [HINTS]
    with pytest.raises(Wrong, match="inputs"):
        loads(json.dumps(given), "t")


@pytest.mark.supports(
    "test_the_goal_and_the_plan_written_commit_the_design_tree_with_the_point_open"
)
def test_load_of_a_run_with_no_tree_gives_none(tmp_path: Any):
    """Given a run's folder with no design-tree.json
    When its tree is loaded
    Then there's none"""
    assert load(str(tmp_path)) is None


@pytest.mark.supports(
    "test_the_goal_and_the_plan_written_commit_the_design_tree_with_the_point_open"
)
def test_save_writes_the_tree_that_load_reads(tmp_path: Any):
    """Given the walkthrough's design tree
    When it's saved in a run's folder and loaded
    Then it's the same tree, in the folder's design-tree.json"""
    tree = walkthrough()
    save(str(tmp_path), tree)
    assert load(str(tmp_path)) == tree
    assert os.path.isfile(os.path.join(str(tmp_path), "design-tree.json"))


@pytest.mark.supports(
    "test_write_refuses_a_deliverable_before_one_it_takes_from_and_leaves_the_tree"
)
def test_order_faults_of_the_walkthroughs_plan_are_none():
    """Given the walkthrough's plan, the hints before the typed marker that takes from them
    When its order is checked
    Then it finds no fault"""
    assert order_faults(walkthrough()) == ()


@pytest.mark.supports(
    "test_write_refuses_a_deliverable_before_one_it_takes_from_and_leaves_the_tree"
)
def test_order_faults_name_a_deliverable_before_one_it_takes_from():
    """Given the typed marker before the hints
    When the order is checked
    Then the fault names both paths"""
    (fault,) = order_faults(walkthrough(typed(), hints(ANSWERED)))
    assert TYPED in fault and HINTS in fault


@pytest.mark.supports(
    "test_write_refuses_a_deliverable_before_one_it_takes_from_and_leaves_the_tree"
)
def test_order_faults_name_an_input_that_no_deliverable_and_no_file_holds():
    """Given the typed marker taking from docs/typing.md, which neither the tree nor the worktree
    holds
    When the order is checked
    Then the fault names docs/typing.md"""
    odd = dataclasses.replace(typed(), inputs=("docs/typing.md",))
    assert any("docs/typing.md" in fault for fault in order_faults(walkthrough(hints(), odd)))


@pytest.mark.supports(
    "test_write_refuses_a_deliverable_before_one_it_takes_from_and_leaves_the_tree"
)
def test_order_faults_name_two_deliverables_at_one_path():
    """Given the hints twice
    When the order is checked
    Then the fault names the path"""
    assert any(HINTS in fault for fault in order_faults(walkthrough(hints(), hints())))


@pytest.mark.supports(
    "test_a_users_point_written_open_keeps_the_deliverable_it_lies_under_from_doing"
)
def test_points_gives_each_open_decision_with_where_it_lies():
    """Given the hints with the point open and the typed marker with none
    When the points are asked for
    Then the one point is the hints' under N3"""
    assert points(walkthrough(hints(OPEN_POINT), typed())) == (Point(HINTS, "N3", OPEN_POINT),)


@pytest.mark.supports(
    "test_a_users_point_written_open_keeps_the_deliverable_it_lies_under_from_doing"
)
def test_points_of_a_tree_with_every_decision_settled_are_none():
    """Given the walkthrough's plan with the point answered
    When the points are asked for
    Then there are none"""
    assert points(walkthrough()) == ()


@pytest.mark.supports("test_the_hints_once_due_start_a_generator_with_the_cut_of_its_first_round")
def test_deliverable_finds_the_one_at_the_path_and_none_elsewhere():
    """Given the walkthrough's plan
    When the deliverables at invoicer/ and at README.md are asked for
    Then the first is the hints, and there's none at README.md"""
    tree = walkthrough()
    assert deliverable(tree, HINTS) == tree.deliverables[0]
    assert deliverable(tree, "README.md") is None


@pytest.mark.supports(
    "test_the_goal_and_the_plan_written_commit_the_design_tree_with_the_point_open"
)
def test_a_tree_with_no_deliverable_yet_is_one_the_form_takes():
    """Given the goal alone, with no deliverable yet
    When it's written and read back
    Then it's the same tree"""
    tree = DesignTree(GOAL, "user")
    assert loads(dumps(tree), "t") == tree and tree.deliverables == ()
