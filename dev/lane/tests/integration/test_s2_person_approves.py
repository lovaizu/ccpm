"""The integration cases of S2, a person approves or asks a change: Lane's guard on up holds up's
turn until the person has the Proposal word for word, lets `lay.py write` through only after the
person's reply, and lay.py lays the Proposal whole, or puts every file back where validation fails.
The plugin's run is held once the person types /reload-plugins. The test plays the person and up."""

from __future__ import annotations

import os

import pytest
from claude_code import Conversation
from domain.laid_set import load
from lane_example import (
    LAID,
    PROPOSAL,
    WRITER_STEP_2,
    WRITER_STEP_2_WITH_SHOW,
    Repo,
    id_of,
    print_command,
    proposal_file,
    propose,
    put,
    read,
    write_command,
)

pytestmark = pytest.mark.xfail(
    strict=True, reason="Lane's parts are skeletons, their bodies unbuilt"
)


def shown_to_person(up: Conversation, repo: Repo) -> str:
    """The person typed `/lane:up changelog`, up proposed PROPOSAL, and gave the person what
    `lay.py print` showed; gives that text."""
    up.type("/lane:up changelog")
    printed = propose(up, repo, PROPOSAL)
    up.stop(printed.output)
    return printed.output


@pytest.mark.supports("S2", "user", "Approval", "Laid", "lay.py")
def test_a_persons_yes_lays_the_proposal_and_validation_passes(up: Conversation, repo: Repo):
    """Given up gave the person the walkthrough's Proposal, word for word
    When the person replies `yes` and up runs `lay.py write changelog <ID>`
    Then lay.py prints each `Wrote` line, `claude plugin validate passed`, and the line that asks
    for /reload-plugins, as the walkthrough shows, and the plugin holds hooks/lanes.json and
    hooks/lane/"""
    printed = shown_to_person(up, repo)
    up.type("yes")
    wrote = up.bash(write_command(id_of(printed)))
    assert (wrote.exit_code, wrote.output) == (0, LAID)
    assert os.path.isfile(os.path.join(repo.plugin, "hooks", "lanes.json"))
    assert os.path.isfile(os.path.join(repo.plugin, "hooks", "lane", "hook.py"))


@pytest.mark.supports("S2", "guard", "Proposal")
def test_up_ending_its_turn_without_the_proposal_word_for_word_is_stopped_with_it(
    up: Conversation, repo: Repo
):
    """Given the person typed `/lane:up changelog` and `lay.py print` showed a Proposal
    When up ends its turn with a summary of it in place of what lay.py print showed
    Then the guard stops the end, and gives up what lay.py print showed"""
    up.type("/lane:up changelog")
    printed = propose(up, repo, PROPOSAL)
    stopped = up.stop("Lane proposes five lanes. Reply yes to lay them.")
    assert stopped.blocked and printed.output.strip() in stopped.said


@pytest.mark.supports("S2", "user", "up", "Step")
def test_a_change_the_person_asks_goes_into_the_step_and_up_proposes_again(
    up: Conversation, repo: Repo
):
    """Given up gave the person the walkthrough's Proposal
    When the person asks that writer may also run `git show {commit}`, and up writes that into
    writer's step 2 and runs `lay.py print` again
    Then the new Proposal shows step 2 as the person's words read, with a new ID, and nothing was
    laid"""
    first = shown_to_person(up, repo)
    up.type("Let writer also read each commit with git show.")
    writer = os.path.join(repo.plugin, "agents", "writer.md")
    up.edit(writer, WRITER_STEP_2, WRITER_STEP_2_WITH_SHOW)
    again = propose(up, repo, PROPOSAL)
    assert again.exit_code == 0 and WRITER_STEP_2_WITH_SHOW in again.output
    assert id_of(again.output) not in ("", id_of(first))
    assert not os.path.exists(os.path.join(repo.plugin, "hooks", "lanes.json"))


@pytest.mark.supports("S2", "guard", "Run")
def test_a_reply_that_is_neither_yes_nor_a_change_ends_the_run_of_up(up: Conversation, repo: Repo):
    """Given up gave the person the walkthrough's Proposal
    When the person asks for other work, and the turn ends with no `lay.py write` and no new
    `lay.py print`
    Then the Run of up ends: up's lanes hold no more, so the main conversation's own `lay.py print`
    after it runs, and its turn ends unheld though it gives the person nothing of it"""
    shown_to_person(up, repo)
    up.type("What does tally do?")
    ended = up.stop("tally counts words.")
    path = proposal_file(repo, PROPOSAL, "other.json")
    after = up.bash(print_command(repo, path))
    assert not ended.blocked
    assert after.exit_code == 0 and id_of(after.output)
    assert not up.stop("Done.").blocked


@pytest.mark.supports("S2", "lay.py", "Proposal", "Run")
def test_lay_write_after_the_run_of_up_ended_without_approval_is_refused(
    up: Conversation, repo: Repo
):
    """Given up gave the person the walkthrough's Proposal, and the person asked for other work, so
    that the Run of up ended as the turn ended
    When the main conversation runs `lay.py write` on that Proposal's ID
    Then lay.py exits 1 saying the Run of up that showed it ended without its approval, and
    nothing is laid"""
    printed = shown_to_person(up, repo)
    up.type("What does tally do?")
    up.stop("tally counts words.")
    late = up.bash(write_command(id_of(printed)))
    assert late.exit_code == 1 and "ended" in late.output
    assert not os.path.exists(os.path.join(repo.plugin, "hooks", "lanes.json"))


@pytest.mark.supports("S2", "guard", "Approval", "Laid only on the caller's own act")
def test_lay_write_before_the_persons_reply_is_stopped(broken: bool, up: Conversation, repo: Repo):
    """Given the person typed `/lane:up changelog` and `lay.py print` showed a Proposal
    When up runs `lay.py write` before the person replies
    Then the guard stops it, saying Lane lays only after the person's reply, and nothing is laid"""
    up.type("/lane:up changelog")
    printed = propose(up, repo, PROPOSAL)
    early = up.bash(write_command(id_of(printed.output)))
    assert early.blocked and "reply" in early.said
    assert not os.path.exists(os.path.join(repo.plugin, "hooks", "lanes.json"))


@pytest.mark.supports("S2", "lay.py", "Proposal")
def test_lay_write_of_an_id_that_no_proposal_has_is_refused(up: Conversation, repo: Repo):
    """Given up gave the person the walkthrough's Proposal, and the person replied `yes`
    When up runs `lay.py write changelog 00000000`, an ID that no Proposal has
    Then lay.py exits 1 naming the ID, and nothing is laid"""
    shown_to_person(up, repo)
    up.type("yes")
    refused = up.bash(write_command("00000000"))
    assert refused.exit_code == 1 and "00000000" in refused.output
    assert not os.path.exists(os.path.join(repo.plugin, "hooks", "lanes.json"))


@pytest.mark.supports("S2", "lay.py", "Step", "Proposal")
def test_lay_write_after_the_steps_changed_since_the_proposal_was_shown_is_refused(
    up: Conversation, repo: Repo
):
    """Given up gave the person the walkthrough's Proposal, and the person replied `yes`
    When writer's step 3 changes, and then up runs `lay.py write` on that Proposal's ID
    Then lay.py exits 1 saying the steps changed since it was shown, and nothing is laid"""
    printed = shown_to_person(up, repo)
    up.type("yes")
    writer = os.path.join(repo.plugin, "agents", "writer.md")
    put(repo.plugin, "agents/writer.md", read(writer).replace("new entries", "entries"))
    refused = up.bash(write_command(id_of(printed)))
    assert refused.exit_code == 1 and "changed" in refused.output
    assert not os.path.exists(os.path.join(repo.plugin, "hooks", "lanes.json"))


@pytest.mark.supports("S2", "lay.py", "Laid")
def test_a_failed_validation_puts_back_each_file_that_laying_changed(up: Conversation, repo: Repo):
    """Given `changelog` whose plugin.json `claude plugin validate` refuses, as its version isn't
    text, and up gave the person the walkthrough's Proposal, and the person replied `yes`
    When up runs `lay.py write`
    Then lay.py exits 1 with what the validation said, and no line that asks for /reload-plugins,
    and each file of the plugin is as before"""
    put(repo.plugin, ".claude-plugin/plugin.json", '{"name": "changelog", "version": 1}')
    before = {
        path: read(os.path.join(repo.plugin, path))
        for path in ("skills/write/SKILL.md", "agents/writer.md", "agents/reviewer.md")
    }
    printed = shown_to_person(up, repo)
    up.type("yes")
    refused = up.bash(write_command(id_of(printed)))
    assert refused.exit_code == 1 and "version" in refused.output
    assert "/reload-plugins" not in refused.output
    assert {path: read(os.path.join(repo.plugin, path)) for path in before} == before
    assert not os.path.exists(os.path.join(repo.plugin, "hooks"))


@pytest.mark.supports("S2", "guard", "Start")
def test_after_lane_lays_the_persons_reload_plugins_has_the_plugins_next_run_held(
    up: Conversation, repo: Repo
):
    """Given the person replied `yes` and lay.py laid the walkthrough's Proposal, in the
    conversation that started before it
    When the person types /reload-plugins, and then `/changelog:write`
    Then Lane names writer's start, as the walkthrough shows"""
    printed = shown_to_person(up, repo)
    up.type("yes")
    up.bash(write_command(id_of(printed)))
    up.stop(LAID)
    up.type("/reload-plugins")
    typed = up.type("/changelog:write")
    assert "changelog: Start `changelog:writer` with `Carry out your steps`." in typed.said


@pytest.mark.supports("S2", "guard", "lay.py", "Lane", "Route", "Laid")
def test_the_laid_set_that_lay_py_writes_is_the_one_that_the_guards_code_reads(laid: Repo):
    """Given `changelog` laid with the walkthrough's Proposal by `lay.py write`
    When the guard's code reads the plugin's hooks/lanes.json
    Then it reads each Lane and each Route of the Proposal, and the sentences laid in the Laid"""
    found = load(laid.plugin)
    assert found is not None
    assert len(found.lanes) == len(PROPOSAL["lanes"])
    assert len(found.routes) == len(PROPOSAL["routes"])
    assert found.laid.sentences
