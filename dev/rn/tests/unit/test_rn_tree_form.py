"""The unit cases of tree/form.py, how the design tree is kept as a file: `started`, the tree a run
starts from, for a goal and for none, by a best practice of each order of conditions; `read` and
`write`, of a file in form, out of it, missing, not JSON, and one that can't be written; `at`, of
each kind of node and of each pointer that names none; and `deliverable`, of one path among several,
a near match, and none."""

from __future__ import annotations

import json
import os
from typing import Any

import pytest
import rn_files
from fault import CantRun, Wrong
from rn_files import COMMAND, GOAL, GUIDE
from tree.form import at, deliverable, read, started, write

NAME = "20261120-a-command-with-which-the"
PLAN = rn_files.plan_path(NAME)


def written(folder: str, text: str) -> str:
    """Writes the text as a run's design-tree.json in the folder, and gives its path."""
    path = os.path.join(folder, "design-tree.json")
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)
    return path


def the_tree() -> dict[str, Any]:
    """The walkthrough's design tree, with a decision of the command's N1, read from its JSON."""
    tax = rn_files.decision(rn_files.TAX_ABOUT, rn_files.TAX_ANSWER, "user")
    return json.loads(json.dumps(rn_files.walkthrough_tree(NAME, command_decisions={"N1": [tax]})))


# started


@pytest.mark.supports(
    "test_a_request_makes_the_runs_worktree_and_its_design_tree_with_the_goal_as_put"
)
def test_started_holds_the_goal_by_reasoning_and_the_plan_as_its_one_deliverable():
    """Given the walkthrough's goal, the plan's path, and the design tree best practice
    When the tree a run starts from is made
    Then its goal is the sentence by reasoning, its one deliverable the plan, named by the goal, of
    the kind design-tree, at the plan's path, with no inputs, open, each condition N1 to N6 in order
    not good with no decision, and its work none"""
    got = started(GOAL, PLAN, rn_files.practice("design-tree"))
    assert got == {
        "goal": {"decided": GOAL, "by": "reasoning"},
        "deliverables": [
            {
                "name": GOAL,
                "path": PLAN,
                "kind": "design-tree",
                "inputs": [],
                "status": "open",
                "necessary_conditions": [
                    {"id": each, "good": False, "decisions": []}
                    for each in ["N1", "N2", "N3", "N4", "N5", "N6"]
                ],
            }
        ],
        "work": [],
    }


@pytest.mark.supports(
    "test_a_request_makes_the_runs_worktree_and_its_design_tree_with_the_goal_as_put"
)
def test_started_takes_the_conditions_in_the_best_practices_order_not_by_their_ids():
    """Given a best practice whose conditions stand as N1, N2, N3, N7, N4, N5, N6, test-design's
    When the tree a run starts from is made by it
    Then the plan's conditions stand in that order"""
    got = started(GOAL, PLAN, rn_files.practice("test-design"))
    ids = [each["id"] for each in got["deliverables"][0]["necessary_conditions"]]
    assert ids == ["N1", "N2", "N3", "N7", "N4", "N5", "N6"]


@pytest.mark.supports(
    "test_a_request_makes_the_runs_worktree_and_its_design_tree_with_the_goal_as_put"
)
def test_started_of_a_goal_of_one_character_holds_it():
    """Given a goal of one character
    When the tree a run starts from is made
    Then the goal and the plan's name are that character"""
    got = started("x", PLAN, rn_files.practice("design-tree"))
    assert (got["goal"]["decided"], got["deliverables"][0]["name"]) == ("x", "x")


@pytest.mark.supports(
    "test_a_request_makes_the_runs_worktree_and_its_design_tree_with_the_goal_as_put"
)
def test_started_refuses_an_empty_goal():
    """Given an empty goal
    When the tree a run starts from is made
    Then it refuses with Wrong"""
    with pytest.raises(Wrong):
        started("", PLAN, rn_files.practice("design-tree"))


# read and write


@pytest.mark.supports("test_each_node_a_change_touches_is_read_again_before_the_commit")
def test_read_gives_the_tree_that_the_file_holds(tmp_path: Any):
    """Given a run's design-tree.json holding the walkthrough's tree
    When it's read
    Then it gives that tree"""
    path = written(str(tmp_path), json.dumps(the_tree(), indent=1))
    assert read(path) == the_tree()


@pytest.mark.supports("test_a_tree_change_out_of_form_is_refused_at_its_commit")
def test_read_gives_a_tree_out_of_its_form_as_the_file_holds_it(tmp_path: Any):
    """Given a design-tree.json holding JSON out of the tree's form, with no goal
    When it's read
    Then it gives that JSON, as tree.checks judges the form"""
    path = written(str(tmp_path), '{"deliverables": "none"}')
    assert read(path) == {"deliverables": "none"}


@pytest.mark.supports("test_a_tree_change_out_of_form_is_refused_at_its_commit")
def test_read_refuses_a_file_that_isnt_json_naming_it(tmp_path: Any):
    """Given a design-tree.json whose text isn't JSON
    When it's read
    Then it refuses with Wrong naming the file"""
    path = written(str(tmp_path), '{"goal": ')
    with pytest.raises(Wrong, match="design-tree.json"):
        read(path)


@pytest.mark.supports("test_a_tree_change_out_of_form_is_refused_at_its_commit")
def test_read_refuses_a_missing_file_naming_it(tmp_path: Any):
    """Given no design-tree.json in the folder
    When it's read
    Then it refuses with Wrong naming the file"""
    with pytest.raises(Wrong, match="design-tree.json"):
        read(os.path.join(str(tmp_path), "design-tree.json"))


@pytest.mark.supports("test_each_node_a_change_touches_is_read_again_before_the_commit")
def test_write_keeps_the_tree_indented_by_one_space_in_its_key_order_with_a_newline(
    tmp_path: Any,
):
    """Given the walkthrough's tree, its goal's keys in the order by, decided
    When it's written to a run's design-tree.json, over a file there
    Then the file holds the tree's JSON indented by one space, its keys in the tree's order, and a
    closing newline, and reads back as the tree"""
    the = the_tree()
    the["goal"] = {"by": "user", "decided": GOAL}
    path = written(str(tmp_path), "old\n")
    write(path, the)
    with open(path, encoding="utf-8") as f:
        assert f.read() == json.dumps(the, indent=1) + "\n"
    assert read(path) == the


@pytest.mark.supports("test_each_node_a_change_touches_is_read_again_before_the_commit")
def test_write_refuses_a_file_that_cant_be_written_naming_it(tmp_path: Any):
    """Given a path whose folder is a file
    When a tree is written there
    Then it refuses with CantRun naming the path"""
    blocker = os.path.join(str(tmp_path), "run")
    with open(blocker, "w", encoding="utf-8") as f:
        f.write("a file\n")
    with pytest.raises(CantRun, match="design-tree.json"):
        write(os.path.join(blocker, "design-tree.json"), the_tree())


# at


@pytest.mark.supports("test_each_node_a_change_touches_is_read_again_before_the_commit")
@pytest.mark.parametrize(
    ("pointer", "node"),
    [
        ("/goal", lambda t: t["goal"]),
        ("/deliverables/2", lambda t: t["deliverables"][2]),
        (
            "/deliverables/1/necessary_conditions/0",
            lambda t: t["deliverables"][1]["necessary_conditions"][0],
        ),
        (
            "/deliverables/1/necessary_conditions/0/decisions/0",
            lambda t: t["deliverables"][1]["necessary_conditions"][0]["decisions"][0],
        ),
        ("/deliverables/1/path", lambda t: COMMAND),
        ("/work/1", lambda t: t["work"][1]),
    ],
)
def test_at_gives_the_node_that_the_pointer_names(pointer: str, node: Any):
    """Given the walkthrough's tree, and a pointer to its goal, a deliverable past the first, a
    condition, a decision, a field, or an item of the work
    When the node at the pointer is taken
    Then it gives that node"""
    the = the_tree()
    assert at(the, pointer) == node(the)


@pytest.mark.supports("test_each_node_a_change_touches_is_read_again_before_the_commit")
@pytest.mark.parametrize(
    "pointer",
    [
        "/deliverables/3",
        "/deliverables/-1",
        "/deliverables/x",
        "/deliverable/0",
        "/deliverables/1/necessary_conditions/3",
        "/work/2",
        "deliverables/0",
    ],
)
def test_at_refuses_a_pointer_that_names_no_node_naming_it(pointer: str):
    """Given the walkthrough's tree of 3 deliverables, light's 3 conditions, and 2 items of work
    When the node is taken at an index one past the last, a negative index, a word for an index, a
    key it lacks, or a pointer without its leading /
    Then it refuses with Wrong naming the pointer"""
    with pytest.raises(Wrong, match=pointer):
        at(the_tree(), pointer)


# deliverable


@pytest.mark.supports(
    "test_the_generators_cut_holds_its_deliverables_node_inputs_and_best_practice"
)
def test_deliverable_gives_the_one_of_the_path_among_several_not_the_first():
    """Given the walkthrough's tree, the plan done, the command and the guide open
    When the deliverable of the guide's path is taken
    Then it gives the guide's node"""
    the = the_tree()
    assert deliverable(the, GUIDE) == the["deliverables"][2]


@pytest.mark.supports(
    "test_the_generators_cut_holds_its_deliverables_node_inputs_and_best_practice"
)
def test_deliverable_gives_one_that_is_done():
    """Given the walkthrough's tree, the plan done
    When the deliverable of the plan's path is taken
    Then it gives the plan's line"""
    the = the_tree()
    assert deliverable(the, PLAN) == the["deliverables"][0]


@pytest.mark.supports(
    "test_the_generators_cut_holds_its_deliverables_node_inputs_and_best_practice"
)
@pytest.mark.parametrize("path", ["docs/guide", "docs/guide.md/", "Docs/guide.md", ""])
def test_deliverable_refuses_a_path_that_nearly_matches_naming_each_path(path: str):
    """Given the walkthrough's tree
    When the deliverable of a path short of the guide's, past it, in another case, or empty is
    taken
    Then it refuses with Wrong naming each path the tree holds"""
    with pytest.raises(Wrong) as refused:
        deliverable(the_tree(), path)
    for each in (PLAN, COMMAND, GUIDE):
        assert each in str(refused.value)


@pytest.mark.supports(
    "test_the_generators_cut_holds_its_deliverables_node_inputs_and_best_practice"
)
def test_deliverable_refuses_any_path_of_a_tree_with_no_deliverable():
    """Given a tree with no deliverable
    When the deliverable of the guide's path is taken
    Then it refuses with Wrong"""
    with pytest.raises(Wrong):
        deliverable(rn_files.tree([]), GUIDE)
