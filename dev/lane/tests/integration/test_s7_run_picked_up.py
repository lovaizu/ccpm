"""The integration cases of S7, a run picked up: after `/compact` the guard finds the conversation's
Run in its run record, and in a new conversation it starts the Run from the Kept results that the
plugin's adapter gives, anew where they hold none or reach the end, and stops the command where
they don't follow the Routes or the adapter fails. The test plays the person, the main
conversation, and each subagent."""

from __future__ import annotations

import os
import stat

import pytest
from claude_code import Conversation
from lane_example import PROPOSAL, Repo, conversation, gives, lay, put, starts

pytestmark = pytest.mark.xfail(
    strict=True, reason="Lane's parts are skeletons, their bodies unbuilt"
)

START_WRITER = "changelog: Start `changelog:writer` with `Carry out your steps`."
START_REVIEWER = "changelog: Start `changelog:reviewer` with `Carry out your steps`."


def kept(repo: Repo, printed: str) -> Conversation:
    """`changelog` laid with an adapter of its records that prints the text given, and a new
    conversation that loads it."""
    path = put(repo.plugin, "hooks/adapters/kept", f"#!/bin/sh\ncat <<'EOF'\n{printed}\nEOF\n")
    os.chmod(path, os.stat(path).st_mode | stat.S_IXUSR)
    lay(repo, {**PROPOSAL, "results_adapter": "kept"})
    return conversation(repo, repo.plugin)


@pytest.mark.supports("S7", "Run", "The run kept in a file")
def test_after_compact_the_run_goes_on_with_the_start_due(
    broken: bool, run: Conversation, laid: Repo
):
    """Given a Run of `changelog` whose writer gave `written`
    When the person types `/compact`, and then `/changelog:write` again
    Then Lane names reviewer's start, the start the Run holds due"""
    run.type("/changelog:write")
    _, writer = starts(run, "writer")
    assert writer
    gives(laid, writer, "written")
    run.compact()
    again = run.type("/changelog:write")
    assert START_REVIEWER in again.said and START_WRITER not in again.said


@pytest.mark.supports("S7", "Kept results", "adapter", "Result")
def test_a_new_conversation_picks_up_from_the_kept_results_that_follow_the_routes(repo: Repo):
    """Given `changelog` laid with an adapter of its records that gives writer `written`
    When the person types `/changelog:write` in a new conversation
    Then Lane says where the run picks up, and names reviewer's start"""
    conv = kept(repo, '{"results": [{"role": "writer", "result": "written"}]}')
    typed = conv.type("/changelog:write")
    assert START_REVIEWER in typed.said and "writer" in typed.said


@pytest.mark.supports("S7", "Kept results", "Run")
def test_kept_results_that_reach_a_route_that_starts_no_more_start_the_run_anew(repo: Repo):
    """Given `changelog` laid with an adapter of its records that gives writer `written` and
    reviewer `good`, a run that ended
    When the person types `/changelog:write` in a new conversation
    Then Lane names writer's start, the first start of a new Run"""
    conv = kept(
        repo,
        '{"results": [{"role": "writer", "result": "written"},'
        ' {"role": "reviewer", "result": "good"}]}',
    )
    assert START_WRITER in conv.type("/changelog:write").said


@pytest.mark.supports("S7", "Kept results", "guard")
def test_kept_results_that_dont_follow_the_routes_stop_the_command_with_who_must_fix_it(
    repo: Repo,
):
    """Given `changelog` laid with an adapter of its records that gives reviewer `good` first,
    which no Route of `first` leads to
    When the person types `/changelog:write` in a new conversation
    Then the guard stops the command, naming reviewer's `good` and who must fix it"""
    conv = kept(repo, '{"results": [{"role": "reviewer", "result": "good"}]}')
    typed = conv.type("/changelog:write")
    assert typed.blocked and "reviewer" in typed.said and "fix" in typed.said


@pytest.mark.supports("S7", "adapter", "guard")
def test_an_adapter_of_the_records_that_fails_stops_the_command_with_why(repo: Repo):
    """Given `changelog` laid with an adapter of its records that prints what isn't JSON
    When the person types `/changelog:write` in a new conversation
    Then the guard stops the command, saying what the adapter printed isn't the form, and who
    must fix it"""
    conv = kept(repo, "no records")
    typed = conv.type("/changelog:write")
    assert typed.blocked and "kept" in typed.said and "fix" in typed.said


@pytest.mark.supports("S7", "Run")
def test_without_an_adapter_of_the_records_a_new_conversation_starts_the_run_over(laid: Repo):
    """Given `changelog` laid with the walkthrough's Proposal, which names no adapter, and a
    conversation whose writer gave `written`
    When the person types `/changelog:write` in a new conversation
    Then Lane names writer's start"""
    first = conversation(laid, laid.plugin)
    first.type("/changelog:write")
    _, writer = starts(first, "writer")
    assert writer
    gives(laid, writer, "written")
    second = conversation(laid, laid.plugin)
    assert START_WRITER in second.type("/changelog:write").said
