"""The integration cases of S4: a pause. Each path of its sequence: the user's /rn:dn, which stops
each generator and evaluator still running and commits and pushes each one's work with the step it
stood at, and the same where git can't push, which commits and says what's missing."""

from __future__ import annotations

import json

import pytest

from dev.rn.tests import rn_walkthrough as w
from dev.rn.tests.rn_walkthrough import Bench

CHANGE = pytest.mark.xfail(strict=True, reason=w.CHANGE_EMPTY)


def stood(walk: w.Walk, record: str) -> list[dict[str, object]]:
    """Each Place that the work's branch holds at its last commit for the start of the record."""
    names = w.git(walk.run["worktree"], "ls-tree", "-r", "--name-only", "HEAD").split()
    rounds = [n for n in names if n.startswith(f"{walk.run['folder']}/rounds/")]
    found = []
    for name in rounds:
        held = json.loads(w.git(walk.run["worktree"], "show", f"HEAD:{name}"))
        if isinstance(held, dict) and held.get("record") == record:
            found.append(held)
    return found


@CHANGE
@pytest.mark.supports("S4", "generator", "Place", "repository", "tree.py")
def test_dn_stops_the_generator_and_pushes_its_work_with_the_step_it_stood_at(b: Bench) -> None:
    """Given: the generator of "Type hints in each file of invoicer" running, which ended its
    step 1.
    When: the user types /rn:dn, the orchestrator stops the generator by TaskStop, runs tree.py
    pause with the generator standing at step 2, and ends its turn with Paused.
    Then: the stop and tree.py pause pass, the remote holds the work's branch at the worktree's
    last commit, which holds the generator's Place at step 2, and the guard lets the turn end."""
    walk, generator, cut = w.generator_in_step_2(b)
    assert not walk.c.type("/rn:dn").blocked
    assert not walk.c.task_stop(generator).blocked
    paused = walk.c.bash(b.fed(b.tree("pause"), {"stood": [{"record": cut["record"], "step": 2}]}))
    assert paused.exit_code == 0, paused.output
    head = w.git(walk.run["worktree"], "rev-parse", "HEAD").strip()
    assert w.git(b.repo, "ls-remote", "origin", walk.branch()).split()[0] == head
    assert [p["step"] for p in stood(walk, cut["record"])] == [2]
    assert not w.orchestrator_ends(b, walk, "dn", w.PAUSED_SHOWN).blocked


@CHANGE
@pytest.mark.supports("S4", "evaluator", "Place")
def test_dn_stops_each_evaluator_still_running_and_keeps_where_each_stood(b: Bench) -> None:
    """Given: the generator of "Type hints in each file of invoicer" ended done, and two of its
    evaluators running, each at step 1.
    When: the user types /rn:dn, the orchestrator stops each by TaskStop, and runs tree.py pause
    with each at step 1.
    Then: each stop and tree.py pause pass, and the work's branch holds each evaluator's Place."""
    walk, _ = w.deliverable_made(b)
    evaluators = []
    for _ in range(2):
        answer, evaluator = w.started(walk.c, "evaluator", walk.said)
        walk.said = answer.posted
        evaluators.append((evaluator, w.cut_of(w.due_text_of(evaluator))["record"]))
    assert not walk.c.type("/rn:dn").blocked
    for evaluator, _ in evaluators:
        assert not walk.c.task_stop(evaluator).blocked
    stand = {"stood": [{"record": record, "step": 1} for _, record in evaluators]}
    assert walk.c.bash(b.fed(b.tree("pause"), stand)).exit_code == 0
    assert all(stood(walk, record) for _, record in evaluators)


@CHANGE
@pytest.mark.supports("S4", "repository", "Point")
def test_dn_where_git_cant_push_commits_and_says_what_is_missing(b: Bench) -> None:
    """Given: the generator of "Type hints in each file of invoicer" running, and the repository's
    remote gone.
    When: the user types /rn:dn, the orchestrator stops the generator, and runs tree.py pause.
    Then: tree.py pause gives 1, saying the work is committed but not pushed and naming the
    remote, and the worktree's last commit holds the generator's Place."""
    walk = w.planned(b)
    generator, cut = w.generator_started(walk)
    w.git(b.repo, "remote", "remove", "origin")
    assert not walk.c.type("/rn:dn").blocked
    assert not walk.c.task_stop(generator).blocked
    paused = walk.c.bash(b.fed(b.tree("pause"), {"stood": [{"record": cut["record"], "step": 1}]}))
    assert paused.exit_code == 1
    assert "committed" in paused.output and "remote" in paused.output
    assert stood(walk, cut["record"])
