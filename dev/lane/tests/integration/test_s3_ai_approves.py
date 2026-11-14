"""The integration cases of S3, an AI approves by its own act: an AI in the main conversation calls
up by the Skill tool, reads the Proposal, mends a step where it falls short, and lays it by its own
run of `lay.py write`, unless a person's run of up waits for their reply, and its plugin's run is
held once the one who gives the conversation its prompts types /reload-plugins. The test plays the
AI and that one."""

from __future__ import annotations

import os

import pytest
from claude_code import Conversation
from lane_example import (
    LAID,
    PROPOSAL,
    WRITER_STEP_2,
    WRITER_STEP_2_WITH_SHOW,
    Repo,
    id_of,
    propose,
    write_command,
)

pytestmark = pytest.mark.xfail(
    strict=True, reason="Lane's parts are skeletons, their bodies unbuilt"
)


@pytest.mark.supports("S3", "Approval", "guard", "Run")
def test_an_ai_that_called_up_by_the_skill_tool_lays_by_its_own_run_of_lay_write(
    up: Conversation, repo: Repo
):
    """Given an AI in the main conversation called `lane:up` by the Skill tool for `changelog`
    When it runs `lay.py print` on the walkthrough's Proposal, and then `lay.py write` on its ID,
    with no person's reply between
    Then the guard lets `lay.py write` through, and lay.py prints what the walkthrough shows,
    ending with the line that asks for /reload-plugins"""
    up.skill("lane:up", "changelog")
    printed = propose(up, repo, PROPOSAL)
    wrote = up.bash(write_command(id_of(printed.output)))
    assert not wrote.blocked
    assert (wrote.exit_code, wrote.output) == (0, LAID)


@pytest.mark.supports("S3", "guard", "Start")
def test_after_an_ai_lays_the_reload_plugins_it_asks_for_has_its_call_of_the_skill_held(
    up: Conversation, repo: Repo
):
    """Given an AI in the main conversation called `lane:up` by the Skill tool, and laid the
    walkthrough's Proposal by its own run of `lay.py write`
    When it ends its turn asking for /reload-plugins, the one who gives the conversation its
    prompts types it, and the AI then calls `changelog:write` by the Skill tool
    Then Lane names writer's start"""
    up.skill("lane:up", "changelog")
    printed = propose(up, repo, PROPOSAL)
    up.bash(write_command(id_of(printed.output)))
    up.stop("Lane laid its checks. Type /reload-plugins, so that they hold.")
    up.type("/reload-plugins")
    up.type("The checks are loaded. Run changelog:write.")
    called = up.skill("changelog:write", "")
    assert "changelog: Start `changelog:writer` with `Carry out your steps`." in called.said


@pytest.mark.supports("S3", "guard", "Run", "Approval")
def test_an_ais_call_of_up_while_a_persons_proposal_awaits_their_reply_keeps_the_persons_run(
    up: Conversation, repo: Repo
):
    """Given the person typed `/lane:up changelog`, and up gave them the walkthrough's Proposal
    When an AI in the main conversation calls `lane:up` by the Skill tool, and runs `lay.py write`
    on that ID
    Then the guard stops `lay.py write`, saying it waits for the person's reply, and nothing is
    laid"""
    up.type("/lane:up changelog")
    printed = propose(up, repo, PROPOSAL)
    up.stop(printed.output)
    up.skill("lane:up", "changelog")
    wrote = up.bash(write_command(id_of(printed.output)))
    assert wrote.blocked and "reply" in wrote.said
    assert not os.path.exists(os.path.join(repo.plugin, "hooks", "lanes.json"))


@pytest.mark.supports("S3", "Step", "Proposal")
def test_an_ai_mends_a_step_that_falls_short_and_lays_the_proposal_made_again(
    up: Conversation, repo: Repo
):
    """Given an AI called `lane:up` by the Skill tool, and `lay.py print` showed the walkthrough's
    Proposal
    When it writes `git show {commit}` into writer's step 2, runs `lay.py print` again, and runs
    `lay.py write` on the new ID
    Then lay.py lays it, and writer's step 2 reads with the AI's words and its sentence"""
    up.skill("lane:up", "changelog")
    propose(up, repo, PROPOSAL)
    writer = os.path.join(repo.plugin, "agents", "writer.md")
    up.edit(writer, WRITER_STEP_2, WRITER_STEP_2_WITH_SHOW)
    again = propose(up, repo, PROPOSAL)
    wrote = up.bash(write_command(id_of(again.output)))
    assert wrote.exit_code == 0
    with open(writer, encoding="utf-8") as f:
        assert WRITER_STEP_2_WITH_SHOW[:-1] in f.read()
