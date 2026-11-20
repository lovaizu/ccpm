"""The property-based tests of the design tree, as rn's Test strategy names them: each invariant
that the architecture states of the Design tree, which the orchestrator writes as an AI would, with
any words and any of the forms its schema allows, and on which every review and pick-up rests.

- Each design tree edit is checked before its commit (Data model, P1.1): a change that leaves the
  schema always gives a fault at or above its place, and a tree in form none, else the work rests
  on a tree out of form and the run stops.
- The run's state lives in files (P6.1): a tree written and read back is the tree, key order
  included, else a pick-up goes on from another state than the one paused.
- A change is read again by each node it touches (Sequences, S1, P1.1): the changed nodes are
  none between equal trees, and exactly the node changed, either way round, else a node the change
  touches goes unread or the orchestrator reads what didn't change.
- A change of a deliverable's path touches each node that names its old path or its new one (S1,
  P1.1), else a deliverable resting on it goes on naming a path that's gone.
- A sign-off makes its deliverable done (P1.3): the deliverable keeps its one line, its work
  leaves, and nothing else changes, its conditions good or, past its Rounds, short with the
  proposals the user signed; and what waits for the sign-off is the plan once each of its
  conditions is good, else the first deliverable whose Rounds are over, else the user signs off
  what isn't the next."""

from __future__ import annotations

import copy
import json
import os
import re
import tempfile
from typing import Any

import pytest
import rn_files
from hypothesis import assume, given
from hypothesis import strategies as st
from rounds.course import Next
from tree import checks, form, signoff, touched

pytestmark = pytest.mark.xfail(
    strict=True, reason="the design tree's bodies raise NotImplementedError"
)

NAME = "20261120-invoices"
KINDS = ("light", "readme", "code")
PATHS = ("invoicer/__main__.py", "docs/guide.md", "CHANGELOG.md", "tests/", "invoicer/cli.py")
# What the schema refuses in a decision's `decided`: a ground or a date.
REFUSED = re.compile(r"\bas the user (decided|asked|said)\b|\b20[0-9]{2}-[0-9]{2}-[0-9]{2}\b")
# Words as an AI or a person writes them: any letters, marks, quotes, and newlines.
TEXT = st.text(st.characters(blacklist_categories=("Cs",)), min_size=1, max_size=30).filter(
    lambda s: not REFUSED.search(s)
)
BY = st.sampled_from(["user", "maker", "reasoning", "research"])


@st.composite
def decisions(draw: Any) -> list[dict[str, Any]]:
    """None, one, or several decisions, each settled or open."""
    found = []
    for _ in range(draw(st.integers(0, 2))):
        about = draw(TEXT)
        if draw(st.booleans()):
            found.append({"about": about, "decided": None})
        else:
            found.append({"about": about, "decided": draw(TEXT), "by": draw(BY)})
    return found


@st.composite
def deliverable(draw: Any, path: str, before: list[str]) -> dict[str, Any]:
    """A deliverable at the path, open, being made, or done, resting on some of the paths before
    it, so that none rests on itself."""
    kind = draw(st.sampled_from(KINDS))
    name = draw(TEXT)
    if draw(st.integers(0, 3)) == 0:
        return rn_files.done_node(name, path, kind)
    node = rn_files.open_node(
        name, path, kind, draw(st.lists(st.sampled_from(before), unique=True)) if before else []
    )
    node["status"] = draw(st.sampled_from(["open", "doing"]))
    if path.endswith("/"):
        node["more_paths"] = ["tests/conftest.py"]
    for each in node["necessary_conditions"]:
        each["good"] = draw(st.booleans())
        each["decisions"] = draw(decisions())
    return node


@st.composite
def trees(draw: Any) -> dict[str, Any]:
    """A design tree in its schema and its checks: the goal by anyone, the plan done or open, then
    one to four deliverables, and work that makes some of them and decides some of their points."""
    head = rn_files.plan(NAME, good=draw(st.booleans()))
    if draw(st.booleans()):
        head = rn_files.done_node(rn_files.GOAL, rn_files.plan_path(NAME), "design-tree")
    paths = draw(st.lists(st.sampled_from(PATHS), min_size=1, max_size=4, unique=True))
    nodes = [draw(deliverable(path, paths[:n])) for n, path in enumerate(paths)]
    order = []
    for node in nodes:
        if node["status"] == "done":
            continue
        if draw(st.booleans()):
            order.append(rn_files.work("make", node["path"]))
        for each in node["necessary_conditions"]:
            for d in each["decisions"]:
                if draw(st.integers(0, 3)) == 0:
                    order.append(rn_files.work("decide", node["path"], each["id"], d["about"]))
    return rn_files.tree([head, *nodes], order, goal=draw(TEXT), by=draw(BY))


def leaves(value: Any, pointer: str = "") -> list[tuple[str, Any]]:
    """Each leaf of the JSON value, a string, a boolean, a number, or null, by its JSON Pointer."""
    if isinstance(value, dict):
        return [leaf for key, each in value.items() for leaf in leaves(each, f"{pointer}/{key}")]
    if isinstance(value, list):
        return [leaf for n, each in enumerate(value) for leaf in leaves(each, f"{pointer}/{n}")]
    return [(pointer, value)]


def put(tree: dict[str, Any], pointer: str, value: Any) -> dict[str, Any]:
    """A copy of the tree with the value at the pointer."""
    changed = copy.deepcopy(tree)
    *path, last = pointer.split("/")[1:]
    held: Any = changed
    for key in path:
        held = held[int(key)] if isinstance(held, list) else held[key]
    held[int(last) if isinstance(held, list) else last] = value
    return changed


def other(value: Any) -> Any:
    """A value of a leaf other than the one given."""
    if isinstance(value, bool):
        return not value
    if isinstance(value, str):
        return value + "x"
    if value is None:
        return "decided"
    return value + 1


@st.composite
def breaks(draw: Any) -> tuple[dict[str, Any], dict[str, Any], str]:
    """A tree in form, a copy of it that leaves the schema in one place, and that place's pointer:
    a key it needs left out, a value of another type, a key it doesn't take, or a word it doesn't
    name."""
    tree = draw(trees())
    n = draw(st.integers(0, len(tree["deliverables"]) - 1))
    node = tree["deliverables"][n]
    choices = [
        (f"/deliverables/{n}/name", None),
        (f"/deliverables/{n}/kind", 7),
        ("/goal/by", "an AI"),
        ("/goal/note", "as I'd put it"),
    ]
    if node.get("necessary_conditions"):
        choices.append((f"/deliverables/{n}/necessary_conditions/0/good", "yes"))
    if tree["work"]:
        choices.append(("/work/0/do", "build"))
    pointer, value = draw(st.sampled_from(choices))
    if value is None:
        broken = copy.deepcopy(tree)
        del broken["deliverables"][n]["name"]
    else:
        broken = put(tree, pointer, value)
    return tree, broken, pointer


PRACTICES = {kind: rn_files.practice(kind) for kind in (*KINDS, "design-tree")}


@pytest.mark.supports("test_a_tree_change_out_of_form_is_refused_at_its_commit")
@given(breaks())
def test_a_change_out_of_the_schema_always_gives_a_fault_at_or_above_its_place(
    case: tuple[dict[str, Any], dict[str, Any], str],
):
    """Given any design tree in form, and any copy of it that leaves the schema in one place
    When the checks find its faults, of each
    Then the tree in form has none, and the copy has one whose pointer is the place or above it
    (Metamorphic, resting on Data model's strategy of each design tree edit checked before its
    commit, P1.1.)"""
    tree, broken, pointer = case
    with tempfile.TemporaryDirectory() as worktree:
        assert checks.faults(tree, PRACTICES, worktree) == []
        found = checks.faults(broken, PRACTICES, worktree)
    assert found
    assert any(pointer.startswith(fault.split(":", 1)[0]) for fault in found)


@pytest.mark.supports(
    "test_a_point_the_orchestrator_settles_is_committed_with_its_ground_as_the_message"
)
@given(trees())
def test_a_tree_written_and_read_back_is_the_tree(tree: dict[str, Any]):
    """Given any design tree, its words in any characters
    When it is written to a run's design-tree.json and read back
    Then the tree read is the tree written, its keys in the same order, and the file closes with a
    newline
    (Inductive, resting on P6.1, the run's state living in files.)"""
    with tempfile.TemporaryDirectory() as folder:
        path = os.path.join(folder, "design-tree.json")
        form.write(path, tree)
        back = form.read(path)
        with open(path, encoding="utf-8") as f:
            text = f.read()
    assert json.dumps(back) == json.dumps(tree)
    assert text.endswith("\n")


@pytest.mark.supports("test_each_node_a_change_touches_is_read_again_before_the_commit")
@given(trees(), st.data())
def test_the_nodes_changed_are_none_between_equal_trees_and_the_one_changed_either_way(
    tree: dict[str, Any], data: Any
):
    """Given any design tree, and a copy of it with any one leaf given another value
    When the changed nodes are found between the tree and itself, and between it and the copy each
    way round
    Then none between equal trees, and the leaf's pointer alone each way round
    (Metamorphic, resting on S1's arrow that lists each node the change touches, P1.1.)"""
    pointer, value = data.draw(st.sampled_from(leaves(tree)))
    changed = put(tree, pointer, other(value))
    assert touched.changed(tree, copy.deepcopy(tree)) == []
    assert touched.changed(tree, changed) == [pointer]
    assert touched.changed(changed, tree) == [pointer]


@pytest.mark.supports("test_each_node_a_change_touches_is_read_again_before_the_commit")
@given(trees(), TEXT)
def test_a_decision_added_is_the_one_node_changed(tree: dict[str, Any], about: str):
    """Given any design tree with an open deliverable, and a copy with a decision added to its
    first condition
    When the changed nodes are found between them
    Then they are the added decision's pointer alone
    (Metamorphic, resting on S1's arrow that lists each node the change touches, P1.1.)"""
    opened = [n for n, each in enumerate(tree["deliverables"]) if "inputs" in each]
    assume(opened)
    n = opened[0]
    conditions = tree["deliverables"][n]["necessary_conditions"]
    changed = copy.deepcopy(tree)
    changed["deliverables"][n]["necessary_conditions"][0]["decisions"].append(
        {"about": about, "decided": None}
    )
    added = f"/deliverables/{n}/necessary_conditions/0/decisions/{len(conditions[0]['decisions'])}"
    assert touched.changed(tree, changed) == [added]


@pytest.mark.supports("test_each_node_a_change_touches_is_read_again_before_the_commit")
@given(trees(), st.data())
def test_a_path_changed_touches_each_node_that_names_its_old_path_or_its_new(
    tree: dict[str, Any], data: Any
):
    """Given any design tree as last committed, and the tree as it stands with one deliverable's
    path changed, the inputs and the work left naming its old path
    When the nodes that the change touches are found
    Then they hold each other deliverable whose inputs name the old path or the new one, and each
    item of the work that names either, and never the changed node
    (Postcondition, resting on S1's arrow that lists each node the change touches, P1.1.)"""
    n = data.draw(st.integers(0, len(tree["deliverables"]) - 1))
    old = tree["deliverables"][n]["path"]
    new = "invoicer/printed.py"
    assume(all(each["path"] != new for each in tree["deliverables"]))
    after = put(tree, f"/deliverables/{n}/path", new)
    found = touched.touched(tree, after, f"/deliverables/{n}/path")
    for m, each in enumerate(after["deliverables"]):
        if m != n and {old, new} & set(each.get("inputs", [])):
            assert f"/deliverables/{m}" in found
    for m, each in enumerate(after["work"]):
        if each["path"] in (old, new):
            assert f"/work/{m}" in found
    assert f"/deliverables/{n}/path" not in found


@st.composite
def signed(draw: Any) -> tuple[dict[str, Any], int]:
    """A design tree and the place of an open deliverable in it, its conditions good or not, as a
    deliverable past its Rounds waits for its sign-off with a condition short, of a file or, once
    in a while, with no file."""
    tree = draw(trees())
    opened = [n for n, each in enumerate(tree["deliverables"]) if "inputs" in each]
    assume(opened)
    n = draw(st.sampled_from(opened))
    if draw(st.integers(0, 3)) == 0:
        tree["deliverables"][n]["file"] = False
        tree["deliverables"][n].pop("more_paths", None)
    return tree, n


@pytest.mark.supports("test_a_signoff_of_the_plan_makes_its_deliverables_generator_due")
@given(signed())
def test_a_signoff_makes_the_deliverable_done_in_its_one_line_and_changes_nothing_else(
    case: tuple[dict[str, Any], int],
):
    """Given any design tree with an open deliverable, each of its conditions good or not
    When the user signs it off
    Then the deliverable is done in its one line, with its necessary conditions where it has no
    file, each item of the work that names it is gone, and the goal, each other deliverable, and
    each other item are as they were, in their order
    (Postcondition, resting on P1.3, P3.3, and Data model's strategy of each sign-off as its
    deliverable done.)"""
    tree, n = case
    node = tree["deliverables"][n]
    after = signoff.signed_off(copy.deepcopy(tree), node["path"])
    line = {key: node[key] for key in ("name", "path", "more_paths", "kind") if key in node}
    line["status"] = "done"
    if node.get("file") is False:
        line.update(file=False, necessary_conditions=node["necessary_conditions"])
    assert after["deliverables"][n] == line
    assert after["goal"] == tree["goal"]
    assert [d for m, d in enumerate(after["deliverables"]) if m != n] == [
        d for m, d in enumerate(tree["deliverables"]) if m != n
    ]
    assert after["work"] == [each for each in tree["work"] if each["path"] != node["path"]]


WAITS = st.sampled_from(["generator", "evaluator", "answer", "orchestrator", "sign-off"])


@pytest.mark.supports("test_the_plan_waiting_for_signoff_is_put_up_in_the_runs_pull_request")
@given(trees(), st.data())
def test_what_waits_for_signoff_is_the_plan_good_else_the_first_whose_rounds_are_over(
    tree: dict[str, Any], data: Any
):
    """Given any design tree, and for each open deliverable but the plan any of what Rounds wait
    on
    When the deliverable that waits for the user's sign-off is found
    Then it's the plan where it's open with each condition good, else the first open deliverable
    in the tree's order that waits on the sign-off, else none
    (Model-based, resting on P1.3 and Data model's strategy of the plan kept as the design tree's
    own deliverable.)"""
    nexts = {
        each["path"]: Next(data.draw(WAITS), None, False)
        for each in tree["deliverables"]
        if "inputs" in each and each["kind"] != "design-tree"
    }
    head = tree["deliverables"][0]
    if "inputs" in head and all(c["good"] for c in head["necessary_conditions"]):
        model: str | None = head["path"]
    else:
        model = next((path for path, each in nexts.items() if each.waits_on == "sign-off"), None)
    assert signoff.waiting(tree, nexts) == model
