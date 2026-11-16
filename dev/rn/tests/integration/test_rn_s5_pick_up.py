"""The integration cases of S5: picking up. Each path of its sequence: /rn:up alone in a new
conversation in the run's worktree, or at the root with one run left, which picks the run up where
it stopped, each role at the step it stood at; at the root with more than one run left, which asks
the user which; and with no run left, which says so and starts no role."""

from __future__ import annotations

import os

import pytest

from dev.rn.tests import rn_walkthrough as w
from dev.rn.tests.rn_walkthrough import Bench
from dev.tests.claude_code import Conversation

LATER = pytest.mark.xfail(strict=True, reason=w.NOT_YET)


def paused(b: Bench) -> tuple[w.Walk, dict[str, object]]:
    """The walkthrough paused by /rn:dn while its generator stood at step 2 of "Type hints in each
    file of invoicer"; gives the walk and the generator's Cut."""
    walk, generator, cut = w.generator_in_step_2(b)
    assert not walk.c.type("/rn:dn").blocked
    assert not walk.c.task_stop(generator).blocked
    stand = {"stood": [{"record": cut["record"], "step": 2}]}
    assert walk.c.bash(b.fed(b.tree("pause"), stand)).exit_code == 0
    assert not w.orchestrator_ends(b, walk, "dn", w.PAUSED_SHOWN).blocked
    return walk, cut


def new_conversation(b: Bench, folder: str) -> Conversation:
    """A new conversation in the folder, with rn and Lane installed."""
    return Conversation(folder, [b.lane, b.rn], b.env, b.temp)


@LATER
@pytest.mark.supports("S5", "adapters", "record.py", "Record", "Place", "orchestrator")
def test_up_alone_in_the_runs_worktree_picks_up_where_it_stopped(b: Bench) -> None:
    """Given: the walkthrough paused while its generator stood at step 2.
    When: the user types /rn:up alone in a new conversation in the run's worktree, and the
    orchestrator starts the tree-keeper with the text that the guard gives due, which ends done.
    Then: the guard picks the run up from the results kept in its records, giving the tree-keeper's
    start due, and then the generator's, its Cut naming "Type hints in each file of invoicer" at
    step 2."""
    walk, cut = paused(b)
    c = new_conversation(b, walk.run["worktree"])
    typed = c.type("/rn:up")
    assert not typed.blocked
    picked = w.keeper_started(b, c, walk.run, typed.said)
    again = w.cut_of(w.due_text(picked.said, "generator"))
    assert again["deliverable"] == cut["deliverable"]
    assert again["cut"]["step"] == 2


@LATER
@pytest.mark.supports("S5", "adapters", "orchestrator", "user")
def test_up_alone_at_the_root_picks_up_the_one_run_left(b: Bench) -> None:
    """Given: the walkthrough paused, the one run left.
    When: the user types /rn:up alone in a new conversation at the root, the orchestrator runs
    tree.py runs, enters the run's worktree, and ends its turn with Picking up.
    Then: tree.py runs gives the one run with its worktree and the orchestrator's record, the guard
    gives the tree-keeper's start due with its Cut in that run once entered, and lets the turn
    end."""
    walk, _ = paused(b)
    c = new_conversation(b, b.repo)
    assert not c.type("/rn:up").blocked
    [run] = w.printed(c.bash(b.tree("runs")))
    assert run["worktree"] == walk.run["worktree"] and run["record"] == walk.run["record"]
    entered = c.enter_worktree(path=run["worktree"])
    cut = w.cut_of(w.due_text(entered.said, "tree-keeper"))
    assert cut["tree"] == f"{walk.run['folder']}/design-tree.json"
    assert not c.stop(w.PICKED_SHOWN).blocked


@LATER
@pytest.mark.supports("S5", "Point", "user", "adapters")
def test_up_alone_with_two_runs_left_asks_which(b: Bench) -> None:
    """Given: the walkthrough paused, and a second run left beside it.
    When: the user types /rn:up alone in a new conversation at the root, the orchestrator runs
    tree.py runs and asks which, the user names the second, and the orchestrator enters its
    worktree.
    Then: the guard starts a run anew, with the tree-keeper's start due, tree.py runs gives both,
    the guard lets the question end the turn, and once entered gives the tree-keeper's Cut in the
    second run."""
    paused(b)
    other = w.converse(b)
    second = w.printed(other.bash(b.tree("start", "a README for invoicer")))
    c = new_conversation(b, b.repo)
    typed = c.type("/rn:up")
    assert not typed.blocked and "rn:tree-keeper" in typed.said
    assert len(w.printed(c.bash(b.tree("runs")))) == 2
    assert not c.stop("Which run do you want to pick up?").blocked
    assert not c.type(second["folder"]).blocked
    entered = c.enter_worktree(path=second["worktree"])
    cut = w.cut_of(w.due_text(entered.said, "tree-keeper"))
    assert cut["tree"] == os.path.join(second["folder"], "design-tree.json")


@pytest.mark.supports("S5", "orchestrator", "guard")
def test_up_alone_with_no_run_left_says_so_and_starts_no_role(b: Bench) -> None:
    """Given: invoicer with rn installed, and no run of rn.
    When: the user types /rn:up alone, the orchestrator runs tree.py runs, gives the skill's result
    none by Lane's result script, and ends its turn saying no run is left.
    Then: tree.py runs gives none, the result script gives 0, the guard lets the turn end with no
    start due, and holds nothing that the user does next."""
    c = w.converse(b)
    typed = c.type("/rn:up")
    assert not typed.blocked
    assert w.printed(c.bash(b.tree("runs"))) == []
    assert c.bash(b.result("up", "none")).exit_code == 0
    stopped = c.stop(f"{w.NO_RUN_SHOWN}.")
    assert not stopped.blocked and "Start `rn:" not in stopped.said
    assert not c.bash("git status").blocked


@LATER
@pytest.mark.supports("S5", "evaluator", "Place")
def test_each_evaluator_that_stood_in_a_step_starts_again_at_it(b: Bench) -> None:
    """Given: the walkthrough paused by /rn:dn while an evaluator of "Type hints in each file of
    invoicer" stood at step 2.
    When: the user types /rn:up alone in a new conversation in the run's worktree, and the
    orchestrator starts the tree-keeper with the text that the guard gives due, which ends done.
    Then: the guard gives an evaluator's start due again, its Cut naming the same group at step
    2."""
    walk, _ = w.deliverable_made(b)
    _, evaluator = w.started(walk.c, "evaluator", walk.said)
    first = w.cut_of(w.due_text_of(evaluator))
    assert not walk.c.type("/rn:dn").blocked
    assert not walk.c.task_stop(evaluator).blocked
    stand = {"stood": [{"record": first["record"], "step": 2}]}
    assert walk.c.bash(b.fed(b.tree("pause"), stand)).exit_code == 0
    c = new_conversation(b, walk.run["worktree"])
    typed = c.type("/rn:up")
    assert not typed.blocked
    picked = w.keeper_started(b, c, walk.run, typed.said)
    again = w.cut_of(w.due_text(picked.said, "evaluator"))
    assert again["conditions"] == first["conditions"] and again["step"] == 2
