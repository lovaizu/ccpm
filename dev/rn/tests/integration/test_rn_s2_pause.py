"""The integration cases of S2, a pause and a pick-up: the orchestrator's stop of each role that
runs, its commit and push of the run's folder, and, in a new conversation, rn's adapters giving Lane
the results kept and each role stopped again with its kept Cut, joined on the bench of the README's
walkthrough through the double of Claude Code, one case for each path of S2's sequence that rn's
parts carry."""

from __future__ import annotations

import os

import pytest
from repo_files import git
from rn_bench import RUN, Bench, judged, made


def paused(b: Bench) -> str:
    """The command's generator started and stopped by /rn:dn's TaskStop, with nothing written
    beside its Cut, the run's folder committed and pushed; gives the Cut's path."""
    c = b.converse()
    start = b.started("generator")
    agent = c.start("rn:generator", start["text"], "make the command")[1]
    assert agent is not None
    assert not c.task_stop(agent).blocked
    assert b.commit(c, "Paused while making the command").exit_code == 0
    assert c.bash("git push -q").exit_code == 0
    return start["values"]["cut"]


@pytest.mark.supports("S2")
def test_a_pause_pushes_the_run_with_the_kept_cut_of_the_role_it_stopped(b: Bench):
    """Given the command's generator running
    When the person types /rn:dn, and the orchestrator stops it, commits, and pushes
    Then the remote's work branch holds the run's folder with the generator's Cut and no result"""
    cut = paused(b)
    pushed = git(b.remote, "ls-tree", "-r", "--name-only", "rn/20261119-invoices").split()
    assert cut in pushed
    assert cut.removesuffix(".cut.json") + ".json" not in pushed


@pytest.mark.supports("S2")
def test_a_pick_up_in_a_new_conversation_gets_the_results_kept_in_their_order(b: Bench):
    """Given round 1 of the command made and judged good, and round 2's generator paused
    When the person types /rn:up alone in a new conversation, and Lane asks rn's adapter of the
    results kept
    Then it gives the generator's made, then each evaluator's judged, in the order of the rounds"""
    made(b)
    judged(b, {})
    paused(b)
    code, printed, said = b.adapter("results", [], {"words": ""})
    assert code == 0, said
    assert printed == {
        "results": [
            {"role": "generator", "result": "made"},
            {"role": "evaluator", "result": "judged"},
            {"role": "evaluator", "result": "judged"},
            {"role": "evaluator", "result": "judged"},
        ]
    }


@pytest.mark.supports("S2")
def test_a_role_stopped_starts_again_from_its_kept_cut(b: Bench):
    """Given the command's generator paused before it wrote its result
    When Lane asks rn's adapter for the generator's start in a new conversation
    Then it gives the same Cut as its run value, and no new round"""
    cut = paused(b)
    assert b.started("generator")["values"]["cut"] == cut
    assert not os.path.exists(os.path.join(b.run, "rounds", "2"))


@pytest.mark.supports("S2")
def test_up_with_a_new_request_picks_up_no_run(b: Bench):
    """Given a run paused
    When the person types /rn:up with a new request, and Lane asks rn's adapter of the results kept
    Then it gives no result, as the words ask for a new run"""
    paused(b)
    code, printed, said = b.adapter("results", [], {"words": "a dashboard of unpaid invoices"})
    assert (code, printed) == (0, {"results": []}), said


@pytest.mark.supports("S2")
def test_up_alone_with_no_run_picks_up_none(b: Bench):
    """Given the repository with no run's folder
    When the person types /rn:up alone, and Lane asks rn's adapter of the results kept
    Then it gives no result"""
    git(b.repo, "rm", "-r", "-q", RUN)
    code, printed, said = b.adapter("results", [], {"words": ""})
    assert (code, printed) == (0, {"results": []}), said
