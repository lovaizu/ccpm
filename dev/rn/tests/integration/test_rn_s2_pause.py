"""The integration cases of S2, a pause and a pick-up: each path through its sequence, the pause
while a generator runs, while an evaluator runs, and while a point waits, and the pick-up from the
runs' commits in a new conversation of each, of a run whose worktree and local branch are gone, and
of none, where the orchestrator asks which run to pick up. Each runs rn and Lane through the double
of Claude Code and the double of gh, with a double of each prompt's work."""

from __future__ import annotations

import os

import pytest
import rn_files
from claude_code import Agent, Conversation
from repo_files import git
from rn_bench import (
    Bench,
    decided_command,
    ended,
    evaluator_started,
    heard,
    held,
    marked,
    pointed,
    ran,
    shared_steps,
    signed_plan,
    started,
    taken,
)
from rn_files import COMMAND, WORDS


def paused(b: Bench, c: Conversation, agents: list[Agent]) -> str:
    """The user types /rn:dn; the orchestrator stops each role given by TaskStop at the step
    `stop`, commits and pushes the run by repository.py pause at the step `pause`, and ends its
    turn; gives the hash that pause printed."""
    c.type("/rn:dn")
    for agent in agents:
        answer = c.task_stop(agent)
        assert not answer.blocked, answer.said
    marked(c, "stop")
    printed = ran(c, b.script("repository", "pause", b.run)).strip()
    marked(c, "pause")
    ended(c, f'Paused "{rn_files.GOAL}".\nIts work so far is pushed.')
    return printed


def picked_up(b: Bench) -> Conversation:
    """A new conversation in which the user typed /rn:up, and the orchestrator found the run by
    repository.py find at the step `find`."""
    c = b.converse()
    c.type("/rn:up")
    assert ran(c, b.script("repository", "find")).split() == [b.run]
    marked(c, "find")
    return c


def mid_command(b: Bench) -> tuple[Conversation, Agent]:
    """A conversation whose command's generator runs, having read its inputs and written the
    command at its step `make`."""
    c, generator = decided_command(b)
    answer = generator.write(os.path.join(b.worktree, COMMAND), "print('invoice')\n")
    assert not answer.blocked, answer.said
    return c, generator


@pytest.mark.supports("S2", "Design tree")
def test_a_pause_stops_the_generator_and_pushes_the_runs_work_so_far(b: Bench):
    """Given a run whose command's generator runs, the command written but not committed
    When the user types /rn:dn, and the orchestrator stops the generator and runs repository.py
    pause
    Then pause prints the head of the remote's branch rn-<name>, which holds the run's design tree,
    the command's Cut, and the command, and the work's branch has nothing left uncommitted"""
    c, generator = mid_command(b)
    printed = paused(b, c, [generator])
    branch = f"rn-{b.name()}"
    assert printed == git(b.origin, "rev-parse", branch).strip()
    files = b.branch_files(branch)
    folder = os.path.relpath(b.folder, b.worktree)
    cut = os.path.relpath(rn_files.round_of(b.folder, COMMAND, "content", 1), b.worktree)
    assert f"{folder}/design-tree.json" in files
    assert f"{cut}/generator-cut.json" in files
    assert COMMAND in files
    assert git(b.worktree, "status", "--porcelain").strip() == ""


@pytest.mark.supports("S2", "Round")
def test_a_pause_stops_the_evaluator_too(b: Bench):
    """Given a run whose command's evaluator runs
    When the user types /rn:dn, and the orchestrator stops the evaluator and pauses the run
    Then the stop goes through, and the remote's branch holds the evaluator's Cut"""
    c, evaluator = evaluator_started(b)
    paused(b, c, [evaluator])
    cut = os.path.relpath(rn_files.round_of(b.folder, COMMAND, "content", 1), b.worktree)
    assert f"{cut}/evaluator-cut.json" in b.branch_files(f"rn-{b.name()}")


@pytest.mark.supports("S2")
def test_a_pause_leaves_the_users_own_worktree_and_branch_as_they_were(b: Bench):
    """Given a run whose command's generator runs, and a file the user is changing on main
    When the user pauses the run
    Then main's head, the user's checked-out branch, and their change are as they were"""
    c, generator = mid_command(b)
    head = git(b.repo, "rev-parse", "main").strip()
    with open(b.at("NOTES.md"), "w", encoding="utf-8") as f:
        f.write("The user's own notes.\n")
    paused(b, c, [generator])
    assert git(b.repo, "rev-parse", "main").strip() == head
    assert git(b.repo, "branch", "--show-current").strip() == "main"
    assert git(b.repo, "status", "--porcelain").strip() == "?? NOTES.md"


@pytest.mark.supports("S2", "Round", "Cut")
def test_a_pick_up_starts_the_stopped_generator_again_in_its_round_with_a_fresh_cut(b: Bench):
    """Given a run paused while its command's generator ran in Round content-1
    When the user types /rn:up in a new conversation, and the orchestrator keeps the shared
    steps and writes the generator's Cut
    Then the Cut lies in Round content-1 again, and the generator starts with it"""
    c, generator = mid_command(b)
    paused(b, c, [generator])
    later = picked_up(b)
    cut_path = shared_steps(
        b, later, ground="Picked up.", moves=[b.script("tree", "cut", b.run, "generator", COMMAND)]
    )[0].strip()
    first = rn_files.round_of(b.folder, COMMAND, "content", 1)
    assert os.path.join(b.repo, cut_path) == os.path.join(first, "generator-cut.json")
    assert started(later, "rn:generator", cut_path) is not None


@pytest.mark.supports("S2", "Round", "Cut")
def test_a_pick_up_starts_the_stopped_evaluator_again_in_its_round(b: Bench):
    """Given a run paused while its command's evaluator ran in Round content-1
    When the user picks it up in a new conversation, and the orchestrator writes the evaluator's
    Cut
    Then the Cut lies in Round content-1, and the evaluator starts with it"""
    c, evaluator = evaluator_started(b)
    paused(b, c, [evaluator])
    later = picked_up(b)
    cut_path = shared_steps(
        b, later, ground="Picked up.", moves=[b.script("tree", "cut", b.run, "evaluator", COMMAND)]
    )[0].strip()
    first = rn_files.round_of(b.folder, COMMAND, "content", 1)
    assert os.path.join(b.repo, cut_path) == os.path.join(first, "evaluator-cut.json")
    assert started(later, "rn:evaluator", cut_path) is not None


@pytest.mark.supports("S2", "Design tree")
def test_a_pick_up_with_a_point_waiting_keeps_it_open_and_starts_no_role(b: Bench):
    """Given a run paused while the generator's point waits on the user, kept as an open
    decision of the command's N1
    When the user picks it up in a new conversation
    Then the design tree still holds the point open, a start of rn:generator is stopped as not
    due, and the turn ends, Lane stopping no move but the start"""
    c, generator = signed_plan(b)
    pointed(b, c, generator, "Should a line's quantity default to 1?")
    point = rn_files.decision("a line's quantity", None)
    taken(b, c, held(b, COMMAND, [], {"N1": [point]}), "The generator's point.")
    ended(
        c,
        "A question that's yours: whether a line's quantity defaults to 1.\n"
        "  I recommend 1, as the team types each line.",
    )
    paused(b, c, [])
    later = picked_up(b)
    shared_steps(b, later, ground="Picked up.")
    assert point in b.tree()["deliverables"][1]["necessary_conditions"][0]["decisions"]
    answer, agent = later.start("rn:generator", "Make the command.", "Run rn:generator")
    assert agent is None
    assert "No start of rn's subagents is due now." in answer.said
    ended(
        later,
        "A question that's yours: whether a line's quantity defaults to 1.\n"
        "  I recommend 1, as the team types each line.",
    )


@pytest.mark.supports("S2", "scripts", "Design tree")
def test_a_pick_up_in_a_repository_whose_worktree_is_gone_makes_it_again(b: Bench):
    """Given a run paused while its command's generator ran, whose worktree and local branch the
    user then removed, so that only origin's branch holds the run
    When the user types /rn:up in a new conversation, the orchestrator runs repository.py find,
    keeps the shared steps, and writes the generator's Cut
    Then find prints the run's folder, its worktree lies there again on rn-<name> at origin's head
    with the design tree that the pause pushed, and the generator starts with a Cut in Round
    content-1"""
    c, generator = mid_command(b)
    paused(b, c, [generator])
    pushed = b.tree()
    git(b.repo, "worktree", "remove", "--force", b.worktree)
    git(b.repo, "branch", "-D", f"rn-{b.name()}")
    later = picked_up(b)
    assert (
        git(b.worktree, "rev-parse", "HEAD").strip()
        == git(b.origin, "rev-parse", f"rn-{b.name()}").strip()
    )
    assert b.tree() == pushed
    cut_path = shared_steps(
        b, later, ground="Picked up.", moves=[b.script("tree", "cut", b.run, "generator", COMMAND)]
    )[0].strip()
    first = rn_files.round_of(b.folder, COMMAND, "content", 1)
    assert os.path.join(b.repo, cut_path) == os.path.join(first, "generator-cut.json")
    assert started(later, "rn:generator", cut_path) is not None


@pytest.mark.supports("S2")
def test_a_pick_up_with_no_run_asks_which_run_to_pick_up(b: Bench):
    """Given invoicer's repository with no run of rn
    When the user types /rn:up, and the orchestrator runs repository.py find, which prints
    nothing, marks `find` done, and asks the user which run to pick up
    Then the turn ends, Lane stopping no move, and the repository has no worktree of rn"""
    c = b.converse()
    typed = c.type("/rn:up")
    assert not typed.blocked, typed.said
    assert ran(c, b.script("repository", "find")) == ""
    marked(c, "find")
    ended(c, "I find no run to pick up here. Which run do you want to pick up?")
    assert not os.path.exists(b.at(".claude/worktrees"))


@pytest.mark.supports("S2", "Design tree")
def test_a_new_request_in_a_paused_runs_words_leaves_the_run_as_it_was(b: Bench):
    """Given a run paused while its command's generator ran
    When the user types /rn:on in a new conversation, then the same words
    Then repository.py new refuses the run's name as taken, the turn ends on blocked, Lane stopping
    no move, and the worktree's design tree is as the pause left it"""
    c, generator = mid_command(b)
    paused(b, c, [generator])
    before = b.tree()
    later = heard(b)
    later.type(WORDS)
    refused = later.bash(b.script("repository", "new", WORDS, rn_files.GOAL, *rn_files.LANGUAGES))
    assert refused.exit_code == 1
    assert b.name() in refused.output
    given = later.bash("lane-result blocked")
    assert not given.blocked, given.said
    ended(later, refused.output)
    assert b.tree() == before
