"""The integration cases of the decisions that one component alone makes, where no story's case
shows them: tree.py keeping the design tree's form and one run of each name, record.py keeping a
record's form, and throwaway.py running only in a run's worktree, each as a role meets it through
the double."""

from __future__ import annotations

import pytest

from dev.rn.tests import rn_walkthrough as w
from dev.rn.tests.rn_walkthrough import Bench

LATER = pytest.mark.xfail(strict=True, reason=w.NOT_YET)


@LATER
@pytest.mark.supports("tree.py", "Design tree", "tree-keeper")
def test_tree_py_refuses_a_change_that_leaves_the_design_trees_form(b: Bench) -> None:
    """Given: the walkthrough's goal and plan written.
    When: the tree-keeper writes a status that the design tree's form has no place for, and a node
    by a path that names none.
    Then: tree.py write gives 1 for each, naming the path, and the design tree is as it was."""
    walk = w.opened(b)
    before = w.tree_in(walk)
    record = w.cut_of(w.due_text_of(walk.keeper))["record"]
    for path, node in (("deliverables/0/status", "finished"), ("deliverables/7/name", "x")):
        change = {"nodes": {path: node}, "more": []}
        assert not walk.c.resume(walk.keeper, w.resume_text("Write it.", None, change)).blocked
        refused = walk.keeper.bash(b.fed(b.tree("write", record, "Write it."), change))
        assert refused.exit_code == 1 and path in refused.output
    assert w.tree_in(walk) == before


@pytest.mark.supports("tree.py", "orchestrator")
def test_tree_py_refuses_a_run_whose_name_a_run_left_holds(b: Bench) -> None:
    """Given: the walkthrough's run started today.
    When: the orchestrator runs tree.py start with the same words again.
    Then: tree.py start gives 1, naming the run left, and makes no second worktree."""
    c, _ = w.asked(b)
    run, _ = w.run_made(b, c)
    again = c.bash(b.tree("start", w.GOAL_NAME))
    assert again.exit_code == 1 and run["folder"].split("/")[-1] in again.output
    assert len(w.printed(c.bash(b.tree("runs")))) == 1


@LATER
@pytest.mark.supports("record.py", "Record", "generator")
def test_record_py_refuses_an_entry_out_of_its_form(b: Bench) -> None:
    """Given: the generator of "Type hints in each file of invoicer" running.
    When: it records a step 0, a practice named X1, and a step with nothing it left.
    Then: record.py add gives 1 for each, saying what's wrong, and the record holds none of them."""
    walk = w.planned(b)
    generator, cut = w.generator_started(walk)
    for of, number, gave in (("generator", "0", "x"), ("code", "X1", "x"), ("generator", "1", "")):
        ran = generator.bash(b.record("add", cut["record"], of, number, gave))
        assert ran.exit_code == 1 and ran.output
    held = w.files_holding(walk.folder("records"), '"X1"')
    assert held == []


@pytest.mark.supports("throwaway.py", "generator")
def test_throwaway_py_refuses_a_folder_in_no_runs_worktree(b: Bench) -> None:
    """Given: invoicer with rn installed, and no run of rn.
    When: a command is tried by throwaway.py at the root.
    Then: throwaway.py gives 1, saying the folder lies in no run's worktree with no traceback, and
    runs nothing."""
    c = w.converse(b)
    tried = c.bash(b.throwaway(w.HINTS_PATH, "touch tried.txt"))
    assert tried.exit_code == 1 and "worktree" in tried.output
    assert "Traceback" not in tried.output
    assert w.git(b.repo, "status", "--porcelain") == ""
