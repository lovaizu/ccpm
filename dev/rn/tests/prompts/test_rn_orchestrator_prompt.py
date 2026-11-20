"""The unit cases of the orchestrator's prompt, domain/orchestrator.md, on Opus: for each kind of
request it's for, a run where its description says it acts and one where it says it doesn't, each
run three times, each decided by code from the files the run leaves. Run by the developer on the
model, as rn's Test strategy says; check.sh never runs them."""

from __future__ import annotations

import os
from datetime import date

import opus
import pytest
import rn_files
from rn_files import WORDS
from rn_prompts import RUNS, Room, typed

pytestmark = [opus.NEEDS_LOGIN]


def name() -> str:
    """The name of the walkthrough's run started today."""
    return f"{date.today():%Y%m%d}-{rn_files.NAMED}"


@pytest.mark.supports(
    "test_a_request_makes_the_runs_worktree_and_its_design_tree_with_the_goal_as_put"
)
@pytest.mark.parametrize("run", RUNS)
def test_a_request_in_words_makes_the_run_and_puts_its_goal_to_the_user(room: Room, run: int):
    """Given invoicer's repository with no run of rn
    When the user types /rn:up with the walkthrough's words
    Then the run's design tree holds a goal of one sentence or more by reasoning and the plan as
    its one deliverable, no Round is made, and the reply asks whether the goal is what they're
    after"""
    printed = typed(room, f"/rn:up {WORDS}")
    design_tree = rn_files.read_json(os.path.join(room.folder(name()), "design-tree.json"))
    assert design_tree["goal"]["by"] == "reasoning"
    assert design_tree["goal"]["decided"].strip()
    assert [each["kind"] for each in design_tree["deliverables"]] == ["design-tree"]
    assert not os.path.exists(os.path.join(room.folder(name()), "rounds"))
    assert "Is that what you're after?" in printed


@pytest.mark.supports("test_a_pick_up_with_no_run_says_rn_has_none_to_pick_up")
@pytest.mark.parametrize("run", RUNS)
def test_a_pick_up_with_no_run_makes_none(room: Room, run: int):
    """Given invoicer's repository with no run of rn
    When the user types /rn:up alone
    Then no worktree of rn is made, and the reply picks up nothing"""
    printed = typed(room, "/rn:up")
    assert not os.path.exists(room.at(".claude/worktrees"))
    assert "Picking up" not in printed


@pytest.mark.supports(
    "test_a_point_only_the_user_can_settle_is_kept_open_and_their_answer_written_by_user"
)
@pytest.mark.parametrize("run", RUNS)
def test_a_goal_the_user_confirms_is_written_by_user(room: Room, run: int):
    """Given a conversation in which the user typed /rn:up with the walkthrough's words
    When the user answers yes
    Then the run's design tree holds the goal by user"""
    typed(room, f"/rn:up {WORDS}")
    typed(room, "yes", more=True)
    design_tree = rn_files.read_json(os.path.join(room.folder(name()), "design-tree.json"))
    assert design_tree["goal"]["by"] == "user"


@pytest.mark.supports("test_a_deliverable_whose_point_waits_on_the_user_gets_no_cut")
@pytest.mark.parametrize("run", RUNS)
def test_after_the_goal_the_user_is_asked_at_most_one_point(room: Room, run: int):
    """Given a conversation in which the user typed /rn:up with the walkthrough's words
    When the user answers yes
    Then the reply holds at most one question that's theirs, and the design tree at most one
    decision open"""
    typed(room, f"/rn:up {WORDS}")
    printed = typed(room, "yes", more=True)
    design_tree = rn_files.read_json(os.path.join(room.folder(name()), "design-tree.json"))
    open_ = [
        each
        for node in design_tree["deliverables"]
        for condition in node.get("necessary_conditions", [])
        for each in condition["decisions"]
        if each["decided"] is None
    ]
    assert printed.count("A question that's yours:") <= 1
    assert len(open_) <= 1
