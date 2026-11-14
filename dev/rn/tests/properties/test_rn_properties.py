"""The property-based tests of rn's parts whose contracts take a wide input, as rn's Test strategy
names them: tree.py's reading and writing of the design tree, its list of the nodes that a change
touches, its check of a record against a prompt's steps and a best practice's practices, and each
adapter's reading of a Cut or a record into Lane's form. Each finds no
counterexample, by hypothesis, and quality.sh runs them in CI."""

from __future__ import annotations

import json
import os
import tempfile
from typing import Any

import pytest
from fault import Wrong
from hypothesis import given
from hypothesis import strategies as st
from kept_results import kept
from kept_results import main as kept_main
from record.check import record_faults
from record.form import Entry, Record, add, keep_result
from record.steps import Step
from rn_example import HINTS
from rn_parts import ANSWERED, NAME, PLAN_SIGNED, doing, hints, typed, walkthrough
from start_text import start_text
from tree import design, sign_offs
from tree.cut import GENERATOR, TREE_KEEPER, cut, save
from tree.design import (
    BY,
    DOING,
    OPEN,
    Decision,
    Deliverable,
    DesignTree,
    NecessaryCondition,
    dumps,
    loads,
)
from tree.practices import DECIDE, MAKE, BestPractice, Practice
from tree.practices import NecessaryCondition as Condition
from tree.touched import changed, touched

pytestmark = pytest.mark.xfail(strict=True, reason="rn's parts are skeletons, their bodies unbuilt")

WORDS = st.text(st.characters(blacklist_categories=("Cs", "Cc")), min_size=1, max_size=30)
PATHS = st.from_regex(r"[a-z]{1,8}(/[a-z]{1,8}){0,2}(\.[a-z]{1,3})?", fullmatch=True)
DECISIONS = st.builds(Decision, WORDS, st.one_of(st.none(), WORDS), st.sampled_from(BY)).map(
    lambda each: each if each.decided is not None else Decision(each.about, None)
)
CONDITIONS = st.builds(
    NecessaryCondition,
    st.integers(1, 20).map(lambda n: f"N{n}"),
    st.booleans(),
    st.lists(DECISIONS, max_size=3).map(tuple),
)


@st.composite
def trees(draw: Any) -> DesignTree:
    """A design tree of deliverables at paths of their own, each taking from those before it."""
    paths = draw(st.lists(PATHS, min_size=1, max_size=5, unique=True))
    items = []
    for n, path in enumerate(paths):
        before = tuple(draw(st.lists(st.sampled_from(paths[:n]), unique=True))) if n else ()
        conditions = tuple(draw(st.lists(CONDITIONS, max_size=3, unique_by=lambda c: c.id)))
        status = draw(st.sampled_from((OPEN, DOING)))
        items.append(Deliverable(draw(WORDS), path, "code", status, before, (), conditions))
    return DesignTree(draw(WORDS), draw(st.sampled_from(BY)), tuple(items))


@pytest.mark.supports(
    "test_the_goal_and_the_plan_written_commit_the_design_tree_with_the_point_open"
)
@given(trees())
def test_each_tree_written_reads_back_as_it_was(tree: DesignTree):
    """Given any design tree in the parts' form
    When it's written and read back
    Then it's the same tree, with no order fault where each takes only from those before it"""
    assert loads(dumps(tree), "t") == tree
    assert design.order_faults(tree) == ()


@pytest.mark.supports("test_write_refuses_a_tree_out_of_the_schemas_form_naming_the_field")
@given(
    st.recursive(
        st.none() | st.booleans() | st.integers() | WORDS,
        lambda inner: st.lists(inner, max_size=4) | st.dictionaries(WORDS, inner, max_size=4),
        max_leaves=12,
    )
)
def test_any_json_reads_as_a_tree_or_is_refused_naming_the_file(value: Any):
    """Given any JSON value
    When it's read as a design tree
    Then it's a tree, or it's refused naming the file, and nothing else is raised"""
    try:
        loads(json.dumps(value), "design-tree.json")
    except Wrong as refused:
        assert "design-tree.json" in str(refused)


@pytest.mark.supports(
    "test_the_users_answer_written_with_its_ground_marks_the_hints_doing_and_checks_the_path_up"
)
@given(trees(), trees())
def test_the_nodes_changed_and_touched_lie_in_the_trees_and_come_once(
    before: DesignTree, after: DesignTree
):
    """Given any two design trees
    When the nodes changed between them, and those they touch in the second, are asked for
    Then each comes once, and none touched is one changed"""
    moved = changed(before, after)
    reached = touched(after, moved)
    assert len(moved) == len(set(moved)) and len(reached) == len(set(reached))
    assert not set(moved) & set(reached)


@pytest.mark.supports("test_the_guard_holds_a_generators_end_whose_record_lacks_a_step")
@given(st.integers(1, 6), st.data())
def test_a_record_passes_exactly_where_it_holds_each_step_in_order_and_each_practice(
    steps: int, data: Any
):
    """Given steps 1 to n, the second deciding and the last making, a best practice of one
    deciding and one making practice, and any record drawn from those entries
    When the record is checked
    Then it has no fault only where it holds each step and each practice"""
    listed = tuple(
        Step("generator", n, f"Step {n}.", DECIDE if n == 2 else MAKE if n == steps else "")
        for n in range(1, steps + 1)
    )
    practices = (Practice("N1.1", DECIDE, "List."), Practice("N1.2", MAKE, "State."))
    best = BestPractice("code", (Condition("N1", "C1", "One place?", practices),))
    pool = [Entry("generator", str(n), "held") for n in range(1, steps + 1)]
    pool += [Entry("code", "N1.1", "listed"), Entry("code", "N1.2", "stated")]
    entries = tuple(data.draw(st.lists(st.sampled_from(pool), max_size=steps + 3)))
    found = record_faults(Record(entries), listed, (best,))
    ids = [each.id for each in entries]
    whole = [each.id for each in pool]
    assert (found == ()) <= (sorted(set(ids)) == sorted(set(whole)))


@pytest.mark.supports("test_the_guard_names_the_generators_start_with_the_text_the_adapter_gives")
@given(trees())
def test_the_text_of_a_generators_start_is_one_json_line_of_its_values(tree: DesignTree):
    """Given any design tree with the plan signed off, in a run's worktree
    When the text of a generator's start is asked for
    Then it's empty, or one JSON line equal to its values, which name a deliverable doing"""
    with tempfile.TemporaryDirectory() as base:
        worktree = os.path.join(base, ".claude", "worktrees", f"rn-{NAME}")
        folder = os.path.join(worktree, ".rn", NAME)
        os.makedirs(folder)
        design.save(folder, tree)
        sign_offs.save(folder, PLAN_SIGNED)
        text = start_text("generator", [], worktree)
        doing = {each.path for each in tree.deliverables if each.status == DOING}
        assert text.text == "" or (
            json.loads(text.text) == text.values and text.values["deliverable"] in doing
        )


def run_worktree(base: str) -> tuple[str, str]:
    """The walkthrough's run in a worktree under the folder, its hints and typed marker doing and
    its plan signed off; gives the worktree and the run's folder."""
    worktree = os.path.join(base, ".claude", "worktrees", f"rn-{NAME}")
    folder = os.path.join(worktree, ".rn", NAME)
    os.makedirs(folder)
    design.save(folder, walkthrough(doing(hints(ANSWERED)), doing(typed(ANSWERED))))
    sign_offs.save(folder, PLAN_SIGNED)
    return worktree, folder


@pytest.mark.supports("test_the_guard_of_a_new_conversation_picks_the_run_up_from_the_results_kept")
@given(
    st.lists(
        st.tuples(
            st.sampled_from((TREE_KEEPER, GENERATOR)),
            st.sampled_from(("", "done", "asks", "lacks")),
        ),
        max_size=6,
    )
)
def test_the_results_kept_are_each_records_result_in_the_order_of_the_starts(
    starts: list[tuple[str, str]],
):
    """Given any starts of the tree-keeper and of the hints' generator, in the order tree.py's cut
    saved them, each record keeping a result or none
    When the adapter of the results kept runs in the run's worktree
    Then it gives 0 and one JSON line of Lane's form, whose results are each role and result kept,
    in the order of the starts, and none of a record that keeps none"""
    with tempfile.TemporaryDirectory() as base:
        worktree, folder = run_worktree(base)
        for role, result in starts:
            saved = save(cut(folder, role, HINTS if role == GENERATOR else ""))
            add(saved.record, Entry(role, "1", "Read."))
            if result:
                keep_result(saved.record, result)
        expected = [(role, result) for role, result in starts if result]
        code, printed, _ = kept_main([], worktree)
        assert kept(worktree) == expected and code == 0
        assert json.loads(printed) == {
            "results": [{"role": role, "result": result} for role, result in expected]
        }


@pytest.mark.supports("test_the_guard_of_a_new_conversation_picks_the_run_up_from_the_results_kept")
@given(
    st.recursive(
        st.none() | st.booleans() | st.integers() | WORDS,
        lambda inner: st.lists(inner, max_size=4) | st.dictionaries(WORDS, inner, max_size=4),
        max_leaves=12,
    )
)
def test_any_json_in_a_record_reads_as_lanes_form_or_is_refused_naming_the_record(value: Any):
    """Given the tree-keeper's start saved, its record holding any JSON value
    When the adapter of the results kept runs in the run's worktree
    Then it gives 0 with one JSON line of Lane's form, or 1 naming the record, and raises
    nothing"""
    with tempfile.TemporaryDirectory() as base:
        worktree, folder = run_worktree(base)
        record = save(cut(folder, TREE_KEEPER)).record
        with open(record, "w", encoding="utf-8") as file:
            json.dump(value, file)
        code, printed, said = kept_main([], worktree)
        assert (code == 0 and set(json.loads(printed)) == {"results"}) or (
            code == 1 and os.path.basename(record) in said
        )
