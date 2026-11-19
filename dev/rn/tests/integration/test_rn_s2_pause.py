"""The integration cases of S2, a pause and a pick-up: the orchestrator's stop of each role that
runs, its commit and push of the run's folder, and, in a new conversation, rn's adapter giving Lane
the starts due from the run's folder and rn's script of a start's Cut giving each role stopped a
fresh Cut, joined on the bench of the README's walkthrough through the double of Claude Code, one
case for each path of S2's sequence that rn's parts carry."""

from __future__ import annotations

import os

import pytest
from repo_files import git
from rn_bench import BRANCH, RUN, Bench, judged, made, read_json, typed

# Why a case is xfail while its body isn't written.
NO_STARTS_DUE = "starts_due.main isn't built yet"


def paused(b: Bench, role: str = "generator") -> str:
    """The role's start due started and stopped by /rn:dn's TaskStop, with nothing written beside
    its Cut, the run's folder committed and pushed; gives the Cut's path."""
    c = b.converse()
    cut, agent = b.start(c, role, f"the {role}'s start")
    assert agent is not None
    assert not c.task_stop(agent).blocked
    assert b.commit(c, "Paused").exit_code == 0
    assert c.bash("git push -q").exit_code == 0
    return cut


@pytest.mark.supports("S2")
def test_a_pause_pushes_the_run_with_the_cut_of_the_role_it_stopped(b: Bench):
    """Given the command's generator running
    When the person types /rn:dn, and the orchestrator stops it, commits, and pushes
    Then the remote's work branch holds the run's folder with the generator's Cut and no result"""
    cut = paused(b)
    pushed = git(b.remote, "ls-tree", "-r", "--name-only", BRANCH).split()
    assert cut in pushed
    assert cut.removesuffix(".cut.json") + ".json" not in pushed


@pytest.mark.xfail(strict=True, reason=NO_STARTS_DUE)
@pytest.mark.supports("S2")
def test_a_pause_leaves_lane_no_start_due_so_the_turn_ends(b: Bench):
    """Given the command's generator started after /rn:ty, and then /rn:dn typed, and the
    generator stopped with no result, which Lane leaves out of the run's moves
    When Lane asks rn's adapter of the starts due, as the orchestrator ends its turn
    Then it gives no start, so that the pause holds until /rn:up"""
    paused(b)
    code, printed, said = b.due(moves=[typed("rn:up"), typed("rn:ty"), typed("rn:dn")])
    assert code == 0 and printed in ({"starts": []}, {"ends": True}), said


@pytest.mark.xfail(strict=True, reason=NO_STARTS_DUE)
@pytest.mark.supports("S2")
def test_a_pick_up_in_a_new_conversation_gives_lane_each_role_stopped_again(b: Bench):
    """Given the command made, and its evaluator of C1 paused with no result
    When the person types /rn:up alone in a new conversation, whose run holds no start yet, and
    Lane asks rn's adapter of the starts due
    Then it gives three starts of rn:evaluator, as the Cut that the pause left counts for nothing"""
    made(b)
    paused(b, "evaluator")
    assert b.starts(moves=[typed("rn:up")]) == {"rn:evaluator": 3}


@pytest.mark.supports("S2")
def test_a_generator_stopped_starts_again_with_a_fresh_cut_in_the_next_round(b: Bench):
    """Given the command's generator paused before it wrote its result
    When the orchestrator runs rn's script of the generator's Cut in a new conversation
    Then it gives a fresh Cut of round 2, from the design tree as it stands, and leaves round 1's
    Cut as it was"""
    cut = paused(b)
    again = b.cut("generator")
    assert again == f"{RUN}/rounds/2/generator.cut.json"
    assert read_json(b, again)["deliverable"] == read_json(b, cut)["deliverable"]
    assert os.path.isfile(os.path.join(b.repo, cut))


@pytest.mark.supports("S2")
def test_an_evaluator_stopped_starts_again_with_a_fresh_cut_beside_its_first(b: Bench):
    """Given the command made, and its evaluator of C1 paused before it wrote its result
    When the orchestrator runs rn's script of each evaluator's Cut in a new conversation
    Then it gives C2's and C3's Cuts, then a fresh Cut of C1 in round 1, in a slot of its own"""
    made(b)
    assert paused(b, "evaluator") == f"{RUN}/rounds/1/evaluator-C1.cut.json"
    groups = [(group, cut) for group, cut in judged(b, {})]
    assert groups == [
        ("C2", f"{RUN}/rounds/1/evaluator-C2.cut.json"),
        ("C3", f"{RUN}/rounds/1/evaluator-C3.cut.json"),
        ("C1", f"{RUN}/rounds/1/evaluator-C1.2.cut.json"),
    ]


@pytest.mark.xfail(strict=True, reason=NO_STARTS_DUE)
@pytest.mark.supports("S2")
def test_a_pick_up_from_the_repositorys_root_finds_the_run_in_rns_worktree(b: Bench):
    """Given the run's branch checked out in rn's worktree of the run, and the repository's root
    on main
    When the person types /rn:up alone at the root, and Lane asks rn's adapter of the starts due
    Then it gives the command's generator, from the run's folder in the worktree"""
    git(b.repo, "checkout", "-q", "main")
    git(b.repo, "worktree", "add", "-q", os.path.join(".claude", "worktrees", BRANCH), BRANCH)
    assert not os.path.isdir(b.run)
    assert b.starts(moves=[typed("rn:up")]) == {"rn:generator": 1}


@pytest.mark.xfail(strict=True, reason=NO_STARTS_DUE)
@pytest.mark.supports("S2")
def test_up_with_a_new_request_beside_a_run_paused_starts_no_role(b: Bench):
    """Given a run paused
    When the person types /rn:up with a new request, and Lane asks rn's adapter of the starts due
    Then it gives no start, as the new run's plan waits for its sign-off"""
    paused(b)
    assert b.starts("a dashboard of unpaid invoices", [typed("rn:up")]) == {}


@pytest.mark.xfail(strict=True, reason=NO_STARTS_DUE)
@pytest.mark.supports("S2")
def test_up_alone_with_no_run_starts_no_role(b: Bench):
    """Given the repository with no run's folder
    When the person types /rn:up alone, and Lane asks rn's adapter of the starts due
    Then it gives no start"""
    git(b.repo, "rm", "-r", "-q", RUN)
    assert b.starts(moves=[typed("rn:up")]) == {}
