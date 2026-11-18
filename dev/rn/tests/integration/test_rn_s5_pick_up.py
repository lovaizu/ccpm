"""The integration cases of S5: picking up. Each path of its sequence: /rn:up alone in a new
conversation in the run's worktree, or at the root with one run left, which picks the run up where
it stopped, each role at the step it stood at, and a generator so started ending once it takes the
steps from there; at the root with more than one run left, which asks the user which; and with no
run left, which says so and starts no role."""

from __future__ import annotations

import json
import os

import pytest

from dev.rn.tests import rn_walkthrough as w
from dev.rn.tests.rn_walkthrough import Bench
from dev.tests.claude_code import Conversation


def paused(b: Bench) -> tuple[w.Walk, dict[str, object]]:
    """The walkthrough paused by /rn:dn while its generator stood at step 2 of the command; gives
    the walk and the generator's Cut."""
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


@pytest.mark.supports("S5", "adapters", "record.py", "Record", "Place", "orchestrator")
def test_up_alone_in_the_runs_worktree_picks_up_where_it_stopped(b: Bench) -> None:
    """Given: the walkthrough paused while its generator stood at step 2.
    When: the user types /rn:up alone in a new conversation in the run's worktree, and the
    orchestrator starts the tree-keeper with the text that the guard gives due, which ends done.
    Then: the guard picks the run up from the results kept in its records, giving the tree-keeper's
    start due, and then the generator's, its Cut naming the command at step 2."""
    walk, cut = paused(b)
    c = new_conversation(b, walk.run["worktree"])
    typed = c.type("/rn:up")
    assert not typed.blocked
    picked = w.keeper_started(b, c, walk.run, typed.said)
    again = w.cut_of(w.due_text(picked.said, "generator"))
    assert again["deliverable"] == cut["deliverable"]
    assert again["cut"]["step"] == 2


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


@pytest.mark.supports("S5", "evaluator", "Place")
def test_each_evaluator_that_stood_in_a_step_starts_again_at_it(b: Bench) -> None:
    """Given: the walkthrough paused by /rn:dn while an evaluator of the command stood at step 2,
    after the generator gave done.
    When: the user types /rn:up alone in a new conversation in the run's worktree.
    Then: the guard gives an evaluator's start due again, with no start of the tree-keeper before
    it, as the generator's done opens none, its Cut naming the same group at step 2."""
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
    again = w.cut_of(w.due_text(typed.said, "evaluator"))
    assert again["conditions"] == first["conditions"] and again["step"] == 2


@pytest.mark.supports("S5", "generator", "record.py", "Record", "Place")
@pytest.mark.xfail(
    strict=True,
    reason="a role started again at the step it stood at records no step 1 in its new record, so"
    " rn's check finds no pass and holds its end for every step, though its part has it go on"
    " from that step",
)
def test_a_generator_started_again_at_its_step_ends_once_it_takes_the_steps_from_it(
    b: Bench,
) -> None:
    """Given: the walkthrough picked up in a new conversation in the run's worktree, with the
    generator's start due at step 2, where it stood.
    When: the generator starts with that text, records step 2, each practice while deciding and
    then while making within its steps 3 and 4, and each step after, commits at the end of each,
    tries the command, writes its Made, and gives done.
    Then: the guard passes its end, as its part has it go on from the step it stood at."""
    walk, _ = paused(b)
    c = new_conversation(b, walk.run["worktree"])
    typed = c.type("/rn:up")
    assert not typed.blocked
    picked = w.keeper_started(b, c, walk.run, typed.said)
    _, generator = w.started(c, "generator", picked.said)
    cut = w.cut_of(w.due_text_of(generator))
    kind, refactor = w.kinds_of(cut)
    steps = [str(n) for n in w.steps_of(b.rn, "domain/generator.md")]
    runs = [("generator", steps[1:3])]
    runs += [(k, w.practices_of(b.rn, k, "decide")) for k in (kind, refactor)]
    runs += [("generator", steps[3:4])]
    runs += [(k, w.practices_of(b.rn, k, "make")) for k in (kind, refactor)]
    runs += [("generator", steps[4:])]
    w.records(b, generator, cut["record"], [(what, named) for what, named in runs if named])
    for number in steps[1:]:
        assert generator.bash(b.tree("commit", cut["record"], number)).exit_code == 0
    made = {
        "decisions": [
            {"path": d["decision"]["path"], "where": cut["deliverable"]}
            for d in cut["cut"]["decisions"]
        ],
        "more": [],
        "settled": [w.LINE_FORM],
    }
    assert not generator.write(os.path.join(c.cwd, cut["made"]), json.dumps(made)).blocked
    ended, _ = w.give(b, generator, "done", "Made.")
    assert not ended.blocked, w.lacks_of(generator, ended, "done", cut)
