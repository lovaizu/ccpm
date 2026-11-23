"""The unit cases of the orchestrator's prompt, domain/orchestrator.md, on Opus: for each kind of
request it's for, a run where its description says it acts and one where it says it doesn't, each
run three times, each decided by code from the files and the records the run leaves. Run by the
developer on the model, as rn's Test strategy says; check.sh never runs them."""

from __future__ import annotations

import os
from datetime import date

import opus
import pytest
import rn_files
from repo_files import git, write_files
from rn_files import COMMAND, WORDS
from rn_prompts import (
    RUNS,
    Room,
    commands_of,
    first_turn_commands,
    first_turn_said,
    run_of,
    typed,
)

pytestmark = [opus.NEEDS_LOGIN]

# A deliverable that rests on none, beside the command, for a case of two deliverables.
CHANGELOG = "CHANGELOG.md"
# The command as a Round made it, which prints the invoice of a file of lines.
COMMAND_TEXT = (
    "import argparse\n"
    "from decimal import Decimal\n"
    "from pathlib import Path\n\n"
    "from invoicer import parse_lines, render\n\n"
    "parser = argparse.ArgumentParser(prog='invoicer')\n"
    "parser.add_argument('lines')\n"
    "parser.add_argument('--rate', type=Decimal, required=True)\n"
    "given = parser.parse_args()\n"
    "print(render(parse_lines(Path(given.lines).read_text()), given.rate))\n"
)


def name() -> str:
    """The name of the walkthrough's run started today."""
    return f"{date.today():%Y%m%d}-{rn_files.NAMED}"


def requested(room: Room) -> str:
    """What Claude Code printed once the user typed /rn:on, then the walkthrough's words in the
    same conversation."""
    typed(room, "/rn:on")
    return typed(room, WORDS, more=True)


def questions(printed: str) -> list:
    """Each line of what Claude Code printed that asks, as the README's walkthrough closes each
    question on its one line that asks."""
    return [each for each in printed.splitlines() if each.rstrip().endswith(("?", "？"))]


def open_decisions(design_tree: dict) -> list:
    """Each decision of the design tree still open."""
    return [
        each
        for node in design_tree["deliverables"]
        for condition in node.get("necessary_conditions", [])
        for each in condition["decisions"]
        if each["decided"] is None
    ]


@pytest.mark.supports("test_rn_on_asks_what_to_make_letting_its_commands_through")
@pytest.mark.parametrize("run", RUNS)
def test_rn_on_asks_what_it_can_help_with_and_makes_nothing(room: Room, run: int):
    """Given invoicer's repository with no run of rn
    When the user types /rn:on alone
    Then the reply asks what rn can help with, no worktree of rn is made, the repository's files
    are as they were, and no command of rn's scripts ran"""
    printed = typed(room, "/rn:on")
    assert "help" in printed.lower() and questions(printed)
    assert not os.path.exists(room.at(".claude/worktrees"))
    assert git(room.repo, "status", "--porcelain") == ""
    assert not [each for each in commands_of(room) if "/scripts/" in each]


@pytest.mark.supports(
    "test_a_request_makes_the_runs_worktree_and_its_design_tree_with_the_goal_as_put"
)
@pytest.mark.parametrize("run", RUNS)
def test_the_words_after_rn_on_make_the_run_and_ask_whom_its_goal_is_for(room: Room, run: int):
    """Given a conversation in which the user typed /rn:on
    When the user types the walkthrough's words
    Then the run's design tree holds a goal of one sentence or more by reasoning and the plan as
    its one deliverable with one decision open, no Round is made, and the reply asks one question,
    rn's own proposal of whom the goal is for to confirm, with nothing recommended"""
    printed = requested(room)
    design_tree = rn_files.read_json(os.path.join(room.folder(name()), "design-tree.json"))
    assert design_tree["goal"]["by"] == "reasoning"
    assert design_tree["goal"]["decided"].strip()
    assert [each["kind"] for each in design_tree["deliverables"]] == ["design-tree"]
    assert not os.path.exists(os.path.join(room.folder(name()), "rounds"))
    assert len(open_decisions(design_tree)) == 1
    assert len(questions(printed)) == 1
    assert "recommend" not in printed.lower()


@pytest.mark.supports("test_a_pick_up_with_no_run_asks_which_run_to_pick_up")
@pytest.mark.parametrize("run", RUNS)
def test_a_pick_up_with_no_run_asks_which_run(room: Room, run: int):
    """Given invoicer's repository with no run of rn
    When the user types /rn:up alone
    Then no worktree of rn is made, and the reply picks up nothing and asks which run to pick up"""
    printed = typed(room, "/rn:up")
    assert not os.path.exists(room.at(".claude/worktrees"))
    assert "Picking up" not in printed
    assert "Which run do you want to pick up?" in printed


@pytest.mark.supports("test_a_pick_up_with_a_point_waiting_keeps_it_open_and_starts_no_role")
@pytest.mark.parametrize("run", RUNS)
def test_a_pick_up_with_a_point_waiting_picks_up_the_run_and_puts_the_point(room: Room, run: int):
    """Given a run in its worktree, its plan done and the command open, whose decision about the
    tax rate waits on the user
    When the user types /rn:up in a new conversation
    Then the reply picks up the run and puts the tax rate's point, the decision stays open, and no
    Round is made"""
    tax = rn_files.decision(rn_files.TAX_ABOUT, None)
    node = rn_files.decided(
        rn_files.open_node(rn_files.COMMAND_NAME, COMMAND, "light", ["invoicer/lines.py"]),
        {"N1": [tax]},
    )
    folder = run_of(room, name(), node)
    printed = typed(room, "/rn:up")
    design_tree = rn_files.read_json(os.path.join(folder, "design-tree.json"))
    assert "Picking up" in printed
    assert "tax" in printed.lower()
    assert [each["about"] for each in open_decisions(design_tree)] == [rn_files.TAX_ABOUT]
    assert not os.path.exists(os.path.join(folder, "rounds"))


@pytest.mark.supports("test_a_blocker_only_the_user_can_mend_stops_only_its_deliverable")
@pytest.mark.parametrize("run", RUNS)
def test_a_put_up_refused_for_gh_leaves_the_changelog_going_on(room: Room, run: int):
    """Given a run in its worktree, its plan done, the command made and open with each condition
    good, waiting for sign-off, and a changelog resting on none, open with nothing made, and gh
    with no login
    When the user types /rn:up in a new conversation
    Then in that turn, the put-up of the command is refused, the changelog's generator gets its
    Cut, the turn doesn't give blocked, and its messages tell the user of gh's login"""
    command = rn_files.open_node(
        rn_files.COMMAND_NAME, COMMAND, "light", ["invoicer/lines.py"], good=True
    )
    check = rn_files.decision(
        "The check", "A developer opens CHANGELOG.md and reads the entry for the command."
    )
    changelog = rn_files.decided(
        rn_files.open_node("A changelog of the command", CHANGELOG, "light"), {"N1": [check]}
    )
    folder = run_of(room, name(), command)
    design_tree = rn_files.read_json(os.path.join(folder, "design-tree.json"))
    design_tree["deliverables"].append(changelog)
    design_tree["work"] = [rn_files.work("make", COMMAND), rn_files.work("make", CHANGELOG)]
    rn_files.write_json(os.path.join(folder, "design-tree.json"), design_tree)
    write_files(room.worktree(name()), {COMMAND: COMMAND_TEXT})
    git(room.worktree(name()), "add", "-A")
    git(room.worktree(name()), "commit", "-q", "-m", "The command, and the changelog.")
    typed(room, "/rn:up")
    ran = first_turn_commands(room)
    cut = os.path.join(rn_files.round_of(folder, CHANGELOG, "content", 1), "generator-cut.json")
    assert any("repository.py put-up" in each for each in ran)
    assert os.path.exists(cut)
    assert not any("lane-result blocked" in each for each in ran)
    told = first_turn_said(room)
    assert "gh" in told and "login" in told


@pytest.mark.supports(
    "test_a_point_only_the_user_can_settle_is_kept_open_and_their_answer_written_by_user"
)
@pytest.mark.parametrize("run", RUNS)
def test_a_goal_the_user_confirms_is_written_by_user(room: Room, run: int):
    """Given a conversation in which the user typed /rn:on, then the walkthrough's words
    When the user answers yes to whom it's for, to the goal, and to their summary
    Then the run's design tree holds the goal by user"""
    requested(room)
    for _ in range(3):
        typed(room, "yes", more=True)
    design_tree = rn_files.read_json(os.path.join(room.folder(name()), "design-tree.json"))
    assert design_tree["goal"]["by"] == "user"


@pytest.mark.supports("test_a_deliverable_whose_point_waits_on_the_user_gets_no_cut")
@pytest.mark.parametrize("run", RUNS)
def test_after_the_goal_the_user_is_asked_at_most_one_point(room: Room, run: int):
    """Given a conversation in which the user typed /rn:on, then the walkthrough's words
    When the user answers yes to whom it's for, to the goal, and to their summary
    Then the last reply asks at most one question, and the design tree holds at most one decision
    open"""
    requested(room)
    for _ in range(2):
        typed(room, "yes", more=True)
    printed = typed(room, "yes", more=True)
    design_tree = rn_files.read_json(os.path.join(room.folder(name()), "design-tree.json"))
    assert len(questions(printed)) <= 1
    assert len(open_decisions(design_tree)) <= 1


def tax_waiting(room: Room) -> str:
    """Makes a run in its worktree, its plan done and the command open, whose decision about the
    tax rate waits on the user; gives its folder."""
    tax = rn_files.decision(rn_files.TAX_ABOUT, None)
    node = rn_files.decided(
        rn_files.open_node(rn_files.COMMAND_NAME, COMMAND, "light", ["invoicer/lines.py"]),
        {"N1": [tax]},
    )
    return run_of(room, name(), node)


@pytest.mark.supports(
    "test_a_pause_in_the_users_words_pushes_the_work_and_lets_the_conversation_go"
)
@pytest.mark.parametrize("run", RUNS)
def test_a_pause_in_the_users_words_pauses_the_run_and_ends_it(room: Room, run: int):
    """Given a run picked up by /rn:up, whose decision about the tax rate waits on the user
    When the user asks in their own words to stop for today
    Then in that turn, repository.py pause ran, then lane-result paused, cancel didn't run, and
    origin holds the run's branch"""
    tax_waiting(room)
    typed(room, "/rn:up")
    typed(room, "Let's stop here for today. I'll come back to it tomorrow.", more=True)
    ran = commands_of(room)
    paused = [i for i, each in enumerate(ran) if "repository.py pause" in each]
    reported = [i for i, each in enumerate(ran) if "lane-result paused" in each]
    assert paused and reported and paused[-1] < reported[-1]
    assert not any("repository.py cancel" in each for each in ran)
    assert git(room.repo, "ls-remote", "--heads", "origin", f"rn-{name()}").strip()


@pytest.mark.supports(
    "test_a_cancel_in_the_users_words_asks_once_then_removes_the_worktree_and_its_branch"
)
@pytest.mark.parametrize("run", RUNS)
def test_a_cancel_in_the_users_words_asks_once_then_removes_the_run(room: Room, run: int):
    """Given a run picked up by /rn:up, whose decision about the tax rate waits on the user
    When the user asks in their own words to drop the run, then answers yes to the question
    Then the first reply asks, with the worktree still there and no cancel run; after yes,
    repository.py cancel ran, then lane-result cancelled, and the worktree and the local branch
    rn-<name> are gone"""
    tax_waiting(room)
    typed(room, "/rn:up")
    asked = typed(room, "Cancel this run. We don't need the command after all.", more=True)
    assert "?" in asked
    assert os.path.isdir(room.worktree(name()))
    assert not any("repository.py cancel" in each for each in commands_of(room))
    typed(room, "yes", more=True)
    ran = commands_of(room)
    cancelled = [i for i, each in enumerate(ran) if "repository.py cancel" in each]
    reported = [i for i, each in enumerate(ran) if "lane-result cancelled" in each]
    assert cancelled and reported and cancelled[-1] < reported[-1]
    assert not os.path.exists(room.worktree(name()))
    assert git(room.repo, "branch", "--list", f"rn-{name()}").strip() == ""


@pytest.mark.supports("test_a_cancel_declined_leaves_the_run_going_on")
@pytest.mark.parametrize("run", RUNS)
def test_an_answer_that_says_stop_is_taken_as_the_answer(room: Room, run: int):
    """Given a run picked up by /rn:up, whose decision about the tax rate waits on the user
    When the user answers the point in words that hold "stop"
    Then neither pause nor cancel ran, no result paused or cancelled was given, the worktree
    stays, and the tax rate's decision is no longer open"""
    folder = tax_waiting(room)
    typed(room, "/rn:up")
    typed(room, "Stop asking for the rate each time; it's 10%, set once.", more=True)
    ran = commands_of(room)
    assert not any(
        word in each
        for each in ran
        for word in ("repository.py pause", "repository.py cancel", "paused", "cancelled")
    )
    assert os.path.isdir(room.worktree(name()))
    design_tree = rn_files.read_json(os.path.join(folder, "design-tree.json"))
    assert not open_decisions(design_tree)
