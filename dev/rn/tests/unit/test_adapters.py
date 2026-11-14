"""The unit cases of rn's adapters in hooks/adapters/, through `start_text` and `main` of
start_text.py and `kept` and `main` of kept_results.py, on a run's worktree that each test writes
as tree.py keeps it."""

from __future__ import annotations

import json
import os
from typing import Any

import pytest
from kept_results import kept
from kept_results import main as kept_main
from rn_example import HINTS, TYPED
from rn_parts import ANSWERED, NAME, PLAN_SIGNED, doing, hints, typed, walkthrough
from start_text import StartText, start_text
from start_text import main as text_main
from tree import design, sign_offs
from tree.fault import Wrong
from tree.record import Entry, add, keep_result

pytestmark = pytest.mark.xfail(strict=True, reason="rn's parts are skeletons, their bodies unbuilt")


@pytest.fixture
def worktree(tmp_path: Any) -> str:
    """The run's worktree, at .claude/worktrees/rn-<run>/ of a folder of the test's own, its tree
    holding the hints and the typed marker both doing."""
    root = os.path.join(str(tmp_path), ".claude", "worktrees", f"rn-{NAME}")
    folder = os.path.join(root, ".rn", NAME)
    os.makedirs(folder)
    design.save(folder, walkthrough(doing(hints(ANSWERED)), doing(typed(ANSWERED))))
    sign_offs.save(folder, PLAN_SIGNED)
    return root


def running(role: str, deliverable: str, group: str = "") -> dict[str, Any]:
    """A start that runs, as Lane gives it on stdin."""
    values = {"deliverable": deliverable, **({"group": group} if group else {})}
    return {"role": role, "text": json.dumps(values), "values": values}


@pytest.mark.supports("test_the_guard_names_the_generators_start_with_the_text_the_adapter_gives")
def test_the_generators_text_is_one_json_line_of_its_run_values(worktree: str):
    """Given the hints and the typed marker doing, and nothing running
    When the text of a generator's start is asked for
    Then it's one JSON line of its run values, the same as its values, naming the hints"""
    given = start_text("generator", [], worktree)
    assert json.loads(given.text) == given.values and given.values["deliverable"] == HINTS


@pytest.mark.supports("test_a_second_evaluator_of_the_same_group_isnt_due_beside_the_first")
def test_the_next_generator_works_on_what_no_generator_running_holds(worktree: str):
    """Given a generator of the hints running
    When the text of a generator's start is asked for
    Then its values name the typed marker"""
    assert (
        start_text("generator", [running("generator", HINTS)], worktree).values["deliverable"]
        == TYPED
    )


@pytest.mark.supports("test_a_second_evaluator_of_the_same_group_isnt_due_beside_the_first")
def test_with_each_deliverable_held_no_generators_work_waits(worktree: str):
    """Given a generator of each deliverable running
    When the text of a generator's start is asked for
    Then the text is empty, with no values"""
    held = [running("generator", HINTS), running("generator", TYPED)]
    assert start_text("generator", held, worktree) == StartText("")


@pytest.mark.supports("test_a_second_evaluator_of_the_same_group_isnt_due_beside_the_first")
def test_the_next_evaluator_takes_the_next_group_no_evaluator_running_holds(worktree: str):
    """Given the hints' round 1, and an evaluator of its group C1 running
    When the text of an evaluator's start is asked for
    Then its values name the hints and C2"""
    os.makedirs(os.path.join(worktree, ".rn", NAME, "rounds", "invoicer--", "1"))
    given = start_text("evaluator", [running("evaluator", HINTS, "C1")], worktree)
    assert (given.values["deliverable"], given.values["group"]) == (HINTS, "C2")


@pytest.mark.supports("test_the_tree_keeper_starts_with_its_cut_of_the_run_alone")
def test_the_tree_keepers_text_names_the_runs_design_tree(worktree: str):
    """Given the run
    When the text of the tree-keeper's start is asked for
    Then its values name the run's design-tree.json"""
    assert start_text("tree-keeper", [], worktree).values["tree"] == os.path.join(
        ".rn", NAME, "design-tree.json"
    )


@pytest.mark.parametrize(("role", "where"), [("reviewer", ""), ("generator", "/")])
@pytest.mark.supports("test_the_guard_names_the_generators_start_with_the_text_the_adapter_gives")
def test_start_text_refuses_a_role_not_rns_or_a_folder_of_no_run(
    worktree: str, role: str, where: str
):
    """Given the run
    When the text of a `reviewer`'s start is asked for, or of a generator's from /
    Then it's refused"""
    with pytest.raises(Wrong):
        start_text(role, [], where or worktree)


@pytest.mark.supports("test_the_guard_names_the_generators_start_with_the_text_the_adapter_gives")
def test_main_prints_the_text_and_the_values_as_lanes_form(worktree: str):
    """Given the run
    When start_text.py runs for the generator with `{"running": []}` on stdin
    Then it gives 0 and prints `{"text", "values"}`"""
    code, out, _ = text_main(["generator"], '{"running": []}', worktree)
    assert code == 0 and set(json.loads(out)) == {"text", "values"}


@pytest.mark.parametrize(
    ("argv", "stdin", "expected"), [([], '{"running": []}', 2), (["generator"], "[]", 1)]
)
@pytest.mark.supports("test_the_guard_names_the_generators_start_with_the_text_the_adapter_gives")
def test_main_refuses_arguments_or_stdin_out_of_lanes_form(
    worktree: str, argv: list[str], stdin: str, expected: int
):
    """Given the run
    When start_text.py runs with no role, or with a list on stdin
    Then it gives 2 with the usage, or 1 with why"""
    assert text_main(argv, stdin, worktree)[0] == expected


@pytest.mark.supports("test_the_guard_of_a_new_conversation_picks_the_run_up_from_the_results_kept")
def test_kept_gives_each_result_in_the_order_of_the_starts(worktree: str):
    """Given the tree-keeper's record keeping `done`, and then a generator's keeping `asks`, and a
    second generator's keeping nothing
    When the results kept are asked for
    Then they're the tree-keeper's `done` and then the generator's `asks`"""
    records = os.path.join(worktree, ".rn", NAME, "records")
    add(os.path.join(records, "tree-keeper-1.json"), Entry("tree-keeper", "1", "Read."))
    keep_result(os.path.join(records, "tree-keeper-1.json"), "done")
    add(os.path.join(records, "generator-2.json"), Entry("generator", "1", "Read."))
    keep_result(os.path.join(records, "generator-2.json"), "asks")
    add(os.path.join(records, "generator-3.json"), Entry("generator", "1", "Read."))
    assert kept(worktree) == [("tree-keeper", "done"), ("generator", "asks")]


@pytest.mark.supports("test_the_guard_of_a_new_conversation_picks_the_run_up_from_the_results_kept")
def test_kept_outside_a_runs_worktree_is_none(tmp_path: Any):
    """Given a folder of no run's worktree
    When the results kept are asked for
    Then there are none"""
    assert kept(str(tmp_path)) == []


@pytest.mark.supports("test_the_guard_of_a_new_conversation_picks_the_run_up_from_the_results_kept")
def test_kept_main_prints_the_results_as_lanes_form(worktree: str):
    """Given the run with no result kept
    When kept_results.py runs
    Then it gives 0 and prints `{"results": []}`"""
    assert kept_main([], worktree) == (0, '{"results": []}\n', "")


@pytest.mark.supports("test_the_guard_of_a_new_conversation_picks_the_run_up_from_the_results_kept")
def test_kept_main_given_an_argument_gives_2(worktree: str):
    """Given the run
    When kept_results.py runs with an argument
    Then it gives 2"""
    assert kept_main(["generator"], worktree)[0] == 2
