"""The integration cases of Lane's walking skeleton: the thinnest path through S1, S2, S5, and S6,
end to end through the real parts, as the walkthrough runs it. The person types `/lane:up
changelog`, up shows the walkthrough's Proposal, the person replies `yes`, up lays it, and the
person types /reload-plugins and `/changelog:write` in the same conversation. The test plays the
person, up, the main conversation, and each subagent."""

from __future__ import annotations

import os

import pytest
from claude_code import Conversation
from lane_example import PROPOSAL, Repo, gives, id_of, propose, starts, write_command

START_WRITER = "changelog: Start `changelog:writer` with `Carry out your steps`."


def laid_by_person(up: Conversation, repo: Repo) -> None:
    """The person typed `/lane:up changelog`, up showed the walkthrough's Proposal word for word,
    the person replied `yes`, up ran `lay.py write` on its ID, and the person typed
    /reload-plugins, as the walkthrough runs it."""
    up.type("/lane:up changelog")
    printed = propose(up, repo, PROPOSAL)
    assert printed.exit_code == 0, printed.output
    up.stop(printed.output)
    up.type("yes")
    wrote = up.bash(write_command(id_of(printed.output)))
    assert wrote.exit_code == 0, wrote.output
    up.stop(wrote.output)
    up.type("/reload-plugins")


@pytest.mark.supports("S1", "S2", "S6", "user", "up", "lay.py", "guard", "lane types", "Lane")
def test_a_persons_lane_up_lays_a_lane_that_stops_a_subagents_command_outside_its_step(
    up: Conversation, repo: Repo
):
    """Given `changelog` as the walkthrough builds it, laid by the person's `/lane:up changelog`
    and `yes`, and the person's /reload-plugins and `/changelog:write`, and writer started as Lane
    names it
    When writer runs `git -C <repo> log --oneline`, and then `git log --oneline`
    Then the guard stops the first with the sentence of writer's step 2 and the commands writer may
    run, as the walkthrough shows, and lets the second run"""
    laid_by_person(up, repo)
    up.type("/changelog:write")
    _, writer = starts(up, "writer")
    assert writer, "writer started"
    stopped = writer.bash(f"git -C {repo.root} log --oneline")
    ran = writer.bash("git log --oneline")
    result = os.path.join(repo.plugin, "hooks", "lane", "result.py")
    assert stopped.blocked, "the command not word for word is stopped"
    assert stopped.said == (
        "changelog: Run only `git log --oneline`.\nThe commands you may run, each word for word:"
        f" `git log --oneline`, `python3 {result} writer written`."
    )
    assert (ran.blocked, ran.exit_code) == (False, 0), "the command of step 2 runs"


@pytest.mark.supports("S2", "S5", "S6", "guard", "result.py", "Start", "Result", "Route", "Run")
def test_after_a_persons_lane_up_the_run_starts_each_subagent_and_ends_on_the_last_result(
    up: Conversation, repo: Repo
):
    """Given `changelog` laid by the person's `/lane:up changelog` and `yes`, and the person's
    /reload-plugins
    When the person types `/changelog:write`, the main conversation starts each subagent that
    Lane names, writer gives `written`, and reviewer gives `good`, and the main conversation then
    ends its turn
    Then Lane names writer's start, then reviewer's after `written`, and `Start no more
    subagents.` after `good`, as the walkthrough shows, and the turn ends unheld, as the run
    ended"""
    laid_by_person(up, repo)
    typed = up.type("/changelog:write")
    _, writer = starts(up, "writer")
    assert writer, "writer started"
    written = gives(repo, writer, "written")
    _, reviewer = starts(up, "reviewer")
    assert reviewer, "reviewer started"
    good = gives(repo, reviewer, "good")
    ended = up.stop("The entries are written and reviewed.")
    assert typed.said == START_WRITER
    assert written.said == (
        "changelog: writer gave `written`. Start `changelog:reviewer` with `Carry out your steps`."
    )
    assert good.said == "changelog: reviewer gave `good`. Start no more subagents."
    assert not ended.blocked, "the turn ends unheld once the run ended"
