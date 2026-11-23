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
    assert "What can I help with?" in printed
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
    its one deliverable with one decision open, no Round is made, and the reply asks one question
    with a recommendation"""
    printed = requested(room)
    design_tree = rn_files.read_json(os.path.join(room.folder(name()), "design-tree.json"))
    assert design_tree["goal"]["by"] == "reasoning"
    assert design_tree["goal"]["decided"].strip()
    assert [each["kind"] for each in design_tree["deliverables"]] == ["design-tree"]
    assert not os.path.exists(os.path.join(room.folder(name()), "rounds"))
    assert len(open_decisions(design_tree)) == 1
    assert printed.count("Recommended:") == 1


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
    Then the last reply holds at most one recommendation, and the design tree at most one
    decision open"""
    requested(room)
    for _ in range(2):
        typed(room, "yes", more=True)
    printed = typed(room, "yes", more=True)
    design_tree = rn_files.read_json(os.path.join(room.folder(name()), "design-tree.json"))
    assert printed.count("Recommended:") + printed.count("(I recommend") <= 1
    assert len(open_decisions(design_tree)) <= 1
