"""The integration cases of S4, proposed again after the steps or Lane change: up reads each Step
without the sentences that the Laid names, lay.py keeps a laid sentence the user changed as their
own words, and laying again replaces Lane's part laid before and keeps the user's own hook
entries."""

from __future__ import annotations

import json
import os

import pytest
from claude_code import Conversation
from lane_example import (
    LANE,
    LAY,
    PROPOSAL,
    PROPOSAL_AGAIN,
    REVIEWER_STEP_1_MENDED,
    WRITER_STEP_2_MENDED,
    Repo,
    conversation,
    id_of,
    lay,
    propose,
    put,
    read,
    write_command,
)

pytestmark = pytest.mark.xfail(
    strict=True, reason="Lane's parts are skeletons, their bodies unbuilt"
)

STEP_2_SENTENCE = "Run only `git log --oneline`."
STEP_2_LAID = (
    "2. Read the commits since then with `git log --oneline`. Run only `git log --oneline`."
)


def mend_steps(repo: Repo) -> None:
    """The user mends writer's step 2 and reviewer's step 1 as the walkthrough does, where writer's
    step 2 holds the sentence that Lane laid."""
    writer = os.path.join(repo.plugin, "agents", "writer.md")
    put(repo.plugin, "agents/writer.md", read(writer).replace(STEP_2_LAID, WRITER_STEP_2_MENDED))
    reviewer = os.path.join(repo.plugin, "agents", "reviewer.md")
    old = "1. Read the new entries in `CHANGELOG.md` against the commits they name."
    put(repo.plugin, "agents/reviewer.md", read(reviewer).replace(old, REVIEWER_STEP_1_MENDED))


@pytest.mark.supports("S4", "lay.py", "Laid", "Step")
def test_up_again_after_the_steps_changed_shows_the_lanes_of_the_steps_as_they_now_read(
    laid: Repo,
):
    """Given `changelog` laid with the walkthrough's Proposal, and the user mended writer's step 2
    and reviewer's step 1 as the walkthrough does
    When the person types `/lane:up changelog` and up proposes the walkthrough's second Proposal
    Then lay.py print shows the lanes that the walkthrough shows for it, and reviewer's step 1 as
    it'll read with `Run only `git log --oneline` or `git show {commit}`.`"""
    mend_steps(laid)
    up = conversation(laid, LANE, laid.plugin)
    up.type("/lane:up changelog")
    printed = propose(up, laid, PROPOSAL_AGAIN)
    assert printed.exit_code == 0
    assert (
        "  step 1  run: Run only `git log --oneline` or `git show {commit}`.  type run_only"
        in printed.output
    )
    assert REVIEWER_STEP_1_MENDED + " Run only `git log --oneline` or `git show {commit}`." in (
        printed.output
    )


@pytest.mark.supports("S4", "lay.py", "Laid", "Step")
def test_a_laid_sentence_that_the_user_changed_is_kept_as_their_words_with_a_note(laid: Repo):
    """Given `changelog` laid with the walkthrough's Proposal, and the user changed the sentence
    that Lane laid on writer's step 2 to `Run only git log, never commit.`
    When up proposes the walkthrough's Proposal again
    Then lay.py print shows step 2 with the user's sentence kept, and a note beside it that Lane
    keeps it as the user's own words"""
    writer = os.path.join(laid.plugin, "agents", "writer.md")
    changed = STEP_2_LAID.replace(STEP_2_SENTENCE, "Run only git log, never commit.")
    put(laid.plugin, "agents/writer.md", read(writer).replace(STEP_2_LAID, changed))
    up = conversation(laid, LANE, laid.plugin)
    up.type("/lane:up changelog")
    printed = propose(up, laid, PROPOSAL)
    assert printed.exit_code == 0
    assert "Run only git log, never commit." in printed.output
    noted = [each for each in printed.output.splitlines() if "own words" in each]
    assert noted and "step 2" in noted[0]


@pytest.mark.supports("S4", "lay.py", "Laid", "Lane's part replaced whole")
def test_laying_again_replaces_lanes_part_laid_before_and_keeps_the_users_hook_entries(
    broken: bool, repo: Repo
):
    """Given `changelog` laid with the walkthrough's Proposal, and a hook entry of the user's own
    added to hooks/hooks.json
    When the user mends the steps, and Lane lays the walkthrough's second Proposal
    Then writer's step 2 holds the new sentence and not the old one, hooks/hooks.json holds the
    user's entry once and Lane's entries once each, and lanes.json holds the second Proposal's
    Lanes alone"""
    lay(repo, PROPOSAL)
    hooks_path = os.path.join(repo.plugin, "hooks", "hooks.json")
    hooks = json.loads(read(hooks_path))
    own = {"type": "command", "command": "python3", "args": ["${CLAUDE_PLUGIN_ROOT}/hooks/own.py"]}
    hooks["hooks"].setdefault("SessionStart", []).append({"hooks": [own]})
    put(repo.plugin, "hooks/hooks.json", json.dumps(hooks))
    mend_steps(repo)
    lay(repo, PROPOSAL_AGAIN)
    writer = read(os.path.join(repo.plugin, "agents", "writer.md"))
    assert STEP_2_SENTENCE + "\n" not in writer
    assert "Run only `git log --oneline` or `git show {commit}`." in writer
    after = json.loads(read(hooks_path))["hooks"]
    assert after["SessionStart"].count({"hooks": [own]}) == 1
    assert all(len(groups) == 1 for event, groups in after.items() if event != "SessionStart")
    lanes = json.loads(read(os.path.join(repo.plugin, "hooks", "lanes.json")))
    assert len(lanes["lanes"]) == len(PROPOSAL_AGAIN["lanes"])


@pytest.mark.supports("S4", "lay.py", "Laid")
def test_up_after_an_update_of_lane_lays_the_newest_code_of_lane(laid: Repo):
    """Given `changelog` laid by an earlier Lane, whose copy in hooks/lane/ differs from Lane's
    code now
    When the caller lays the walkthrough's Proposal again
    Then hooks/lane/ holds Lane's code now, and no module that Lane has no more"""
    old = os.path.join(laid.plugin, "hooks", "lane", "result.py")
    put(laid.plugin, "hooks/lane/result.py", "# an earlier Lane's result.py\n")
    put(laid.plugin, "hooks/lane/stale.py", "# a module that Lane now has no more\n")
    up: Conversation = conversation(laid, LANE, laid.plugin)
    up.skill("lane:up", "changelog")
    printed = propose(up, laid, PROPOSAL)
    up.bash(write_command(id_of(printed.output)))
    assert read(old) == read(os.path.join(LANE, "hooks", "lane", "result.py"))
    assert not os.path.exists(os.path.join(laid.plugin, "hooks", "lane", "stale.py"))


@pytest.mark.supports("S4", "up", "lay.py", "Laid", "Step")
def test_lay_steps_gives_each_step_without_the_sentences_that_lane_laid(laid: Repo):
    """Given `changelog` laid with the walkthrough's Proposal, so that writer's step 2 holds the
    sentence `Run only `git log --oneline`.` that Lane laid
    When the person types `/lane:up changelog`, and up runs `lay.py steps changelog`
    Then writer's step 2 reads as the user wrote it, without Lane's sentence"""
    up = conversation(laid, LANE, laid.plugin)
    up.type("/lane:up changelog")
    printed = up.bash(f"python3 {LAY} steps changelog")
    assert printed.exit_code == 0
    assert "2. Read the commits since then with `git log --oneline`." in printed.output
    assert STEP_2_LAID not in printed.output
