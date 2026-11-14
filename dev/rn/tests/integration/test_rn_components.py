"""The integration cases of the decisions that a component of rn makes alone and that no story's
case holds: tree.py's form of the design tree and the nodes a change touches; record.py's form of a
record and rn's check of the orchestrator's turn; the adapters' text of a start; and throwaway.py's
home. The test plays the orchestrator and each role."""

from __future__ import annotations

import json
import os

import pytest
from claude_code import Conversation
from rn_example import (
    ANSWERED,
    HINTS,
    TYPED,
    WITH_POINT,
    Repo,
    Run,
    keeper_writes,
    record,
    start,
    started,
    throwaway,
)

pytestmark = pytest.mark.xfail(strict=True, reason="rn's parts are skeletons, their bodies unbuilt")


@pytest.mark.supports("tree.py", "Design tree", "tree-keeper")
def test_write_refuses_a_tree_out_of_the_schemas_form_naming_the_field(
    conv: Conversation, repo: Repo, run: Run
):
    """Given the tree-keeper started
    When it writes a design tree whose goal has no `by`
    Then tree.py exits 1 naming `goal` and `by`, and the run has no design tree"""
    _, keeper = started(conv, repo, run, "tree-keeper")
    wrong = dict(WITH_POINT, goal={"decided": WITH_POINT["goal"]["decided"]})
    refused = keeper_writes(keeper, repo, run, wrong, "The goal.")
    assert refused.exit_code == 1 and "goal" in refused.output and "by" in refused.output
    assert not os.path.exists(os.path.join(run.worktree, run.folder, "design-tree.json"))


@pytest.mark.supports("tree.py", "Design tree", "Deliverable")
def test_write_lists_the_typed_marker_among_the_nodes_a_change_of_the_hints_touches(
    conv: Conversation, repo: Repo, run: Run
):
    """Given the walkthrough's plan written with its point open
    When the tree-keeper writes the user's answer under the hints
    Then tree.py lists the typed marker, which takes from the hints, among the nodes touched"""
    _, keeper = started(conv, repo, run, "tree-keeper")
    keeper_writes(keeper, repo, run, WITH_POINT, "The plan.")
    wrote = keeper_writes(keeper, repo, run, ANSWERED, "The user answered each file.")
    assert TYPED in json.loads(wrote.output)["touched"]


@pytest.mark.supports("record.py", "orchestrator", "guard", "Record")
def test_the_orchestrators_turn_is_held_until_its_record_holds_each_step(
    conv: Conversation, repo: Repo, run: Run
):
    """Given a run begun, whose orchestrator recorded no step
    When the main conversation ends its turn
    Then the guard holds the stop, with what rn's check found missing in the orchestrator's
    record"""
    stopped = conv.stop("The goal, as I'd put it: ...")
    assert stopped.blocked and "orchestrator" in stopped.said


@pytest.mark.supports("record.py", "tree-keeper", "Record")
def test_record_refuses_an_id_that_is_neither_a_step_nor_a_practice(
    conv: Conversation, repo: Repo, run: Run
):
    """Given the tree-keeper started
    When it records `step-one` of tree-keeper
    Then tree.py exits 1 naming the ID and what an ID takes"""
    given, keeper = started(conv, repo, run, "tree-keeper")
    refused = keeper.bash(record(repo, "add", given["record"], "tree-keeper", "step-one", "Read."))
    assert refused.exit_code == 1 and "step-one" in refused.output and "N6.2" in refused.output


@pytest.mark.supports("adapters", "guard", "generator")
def test_the_guard_names_the_generators_start_with_the_text_the_adapter_gives(
    conv: Conversation, repo: Repo, run: Run
):
    """Given the plan signed off with its point answered, and the tree-keeper's end accepted
    When the tree-keeper's end reaches the main conversation
    Then the guard names the start of `rn:generator` with one JSON line of run values naming the
    hints"""
    given, keeper = started(conv, repo, run, "tree-keeper")
    keeper_writes(keeper, repo, run, ANSWERED, "The user answered each file.")
    keeper.bash(record(repo, "add", given["record"], "tree-keeper", "1", "Read."))
    _, reached = keeper.end("Wrote the answer.")
    assert (
        reached and "rn:generator" in reached.said and f'"deliverable": "{HINTS}"' in reached.said
    )


@pytest.mark.supports("adapters", "guard", "evaluator")
def test_a_second_evaluator_of_the_same_group_isnt_due_beside_the_first(
    conv: Conversation, repo: Repo, run: Run
):
    """Given an evaluator of the hints' group C1 running
    When the main conversation starts another evaluator with the same run values
    Then the guard stops the start, as the adapter gives that work to the one running"""
    given, _ = started(conv, repo, run, "evaluator", HINTS, "C1")
    answer, agent = start(conv, "evaluator", given)
    assert agent is None and answer.blocked


@pytest.mark.supports("throwaway.py", "generator")
def test_a_try_runs_with_a_home_of_its_own(conv: Conversation, repo: Repo, run: Run):
    """Given the hints' generator running
    When it tries `echo $HOME` by throwaway.py
    Then the home printed lies in the system's temporary folder of the test, not the user's"""
    _, keeper = started(conv, repo, run, "tree-keeper")
    keeper_writes(keeper, repo, run, ANSWERED, "The user answered each file.")
    _, generator = started(conv, repo, run, "generator", HINTS)
    tried = generator.bash(throwaway(repo, "try", run.folder, HINTS, "1", "echo $HOME"))
    assert tried.output.strip().startswith(os.path.join(repo.temp, "rn", ""))
