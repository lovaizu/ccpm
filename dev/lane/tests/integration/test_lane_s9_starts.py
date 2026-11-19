"""The integration cases of S9, the starts held to the plugin's order: the run added at the skill's
call, the starts due with their text, each start due let through, any other start and the turn's
end while a start is due stopped, a typed command that a route waits for, and each result with the
starts that its route makes due, until the routes start no more; and each state of Claude Code
that bears on them, as dev/lane/claude-code-states.md lists it. Each runs `log` and Lane through
the double of Claude Code."""

from __future__ import annotations

import os

import pytest
from claude_code import AGENT_DENIED_BY_RULE, AGENT_UNKNOWN_TYPE, FOREGROUND, POSTED_FIRST
from lane_bench import (
    UNREPORTED,
    WORDS,
    Bench,
    denier,
    opened,
    reached,
    reviewed,
    started,
    text,
    to_review,
    written,
)

pytestmark = UNREPORTED


@pytest.mark.supports("S9", "Route")
def test_the_turns_end_while_the_commands_start_is_due_is_stopped_with_it(b: Bench):
    """Given the person typed /log:up 1.2.0
    When the main conversation ends its turn
    Then the end is stopped, with the writer due and the text that `log` gives it"""
    answer = opened(b).stop("Started the run.")
    assert answer.blocked
    assert text("log:writer") in answer.said


@pytest.mark.supports("S9")
def test_a_skill_called_by_the_skill_tool_makes_its_routes_start_due(b: Bench):
    """Given a conversation in which no run of `log` stands
    When the main conversation calls log:up by the Skill tool with 1.2.0, and ends its turn
    Then the end is stopped, with the writer due and its text"""
    c = b.converse()
    c.skill("log:up", WORDS)
    answer = c.stop("Called the skill.")
    assert answer.blocked
    assert text("log:writer") in answer.said


@pytest.mark.supports("S9")
def test_a_plugin_without_a_start_adapter_gets_the_role_due_alone(b: Bench):
    """Given `log` with no start adapter, and the person typed /log:up 1.2.0
    When the main conversation ends its turn
    Then the end is stopped with the writer due, and no text of a start"""
    b.adapter("start.py", None)
    answer = opened(b).stop("Started the run.")
    assert answer.blocked
    assert "log:writer" in answer.said
    assert text("log:writer") not in answer.said


@pytest.mark.supports("S9")
def test_the_start_due_goes_through_and_leaves_none_due(b: Bench):
    """Given the writer due
    When the main conversation starts the writer, and then ends its turn
    Then the start goes through, and the end goes through, as no start is due"""
    c = opened(b)
    answer, agent = c.start("log:writer", text("log:writer"), "Write the entry")
    assert agent is not None, answer.said
    assert not c.stop("The writer runs.").blocked


@pytest.mark.supports("S9")
def test_another_start_of_the_plugins_subagents_is_stopped_with_the_starts_due(b: Bench):
    """Given the writer due
    When the main conversation starts the reviewer
    Then the start is stopped, and the main conversation reads the writer due with its text"""
    answer, agent = opened(b).start("log:reviewer", text("log:reviewer"), "Review")
    assert agent is None
    assert answer.blocked
    assert text("log:writer") in answer.said


@pytest.mark.supports("S9")
def test_a_subagents_start_of_a_subagent_is_stopped(b: Bench):
    """Given the writer running
    When the writer starts a writer by the Agent tool
    Then the start is stopped, as only the main conversation starts the roles"""
    writer = started(opened(b))
    answer, agent = writer.start("log:writer", text("log:writer"), "Write the entry")
    assert agent is None
    assert answer.blocked


@pytest.mark.supports("S9", "Route")
def test_a_typed_command_that_a_route_waits_for_puts_its_starts_in_place(b: Bench):
    """Given the writer ended with its result, so the reviewer is due
    When the person types /log:retry, and the main conversation starts the reviewer
    Then the start is stopped with the writer due in place of the reviewer"""
    c = to_review(b)
    c.type("/log:retry")
    answer, agent = c.start("log:reviewer", text("log:reviewer"), "Review")
    assert agent is None
    assert text("log:writer") in answer.said
    assert text("log:reviewer") not in answer.said


@pytest.mark.supports("S9", "S7", "Route")
def test_a_result_reaching_the_main_conversation_gives_the_starts_its_route_makes_due(b: Bench):
    """Given the writer kept each step and reported `written`
    When its end reaches the main conversation
    Then the main conversation reads the result and the reviewer due with its text"""
    writer = started(opened(b))
    written(writer)
    answer = reached(writer)
    assert "written" in answer.said
    assert text("log:reviewer") in answer.said


@pytest.mark.supports("S9", "Route")
def test_a_run_whose_routes_start_no_more_ends_and_holds_no_move_after(b: Bench):
    """Given the reviewer due
    When the reviewer reports `good` and ends, and the main conversation writes a file that no
    step names and ends its turn
    Then the write and the end go through, as the run ended"""
    c = to_review(b)
    reviewed(c, "good")
    assert not c.write(None, b.at("notes.txt"), "x\n").blocked
    assert not c.stop("Done.").blocked


@pytest.mark.supports("S9")
@pytest.mark.parametrize("record", [AGENT_UNKNOWN_TYPE, AGENT_DENIED_BY_RULE])
def test_an_agent_call_that_fails_after_its_pre_tool_use_leaves_its_start_due(
    b: Bench, record: str
):
    """Given the writer due
    When the main conversation starts the writer, and the Agent call fails after its PreToolUse,
    as it names no subagent type that exists or a permission rule denies it
    Then the turn's end is stopped with the writer due again"""
    c = opened(b)
    assert c.start_failing("log:writer", text("log:writer"), "Write the entry", record).blocked
    answer = c.stop("The start failed.")
    assert answer.blocked
    assert text("log:writer") in answer.said


@pytest.mark.supports("S9")
def test_a_start_that_another_plugins_hook_denies_is_due_again_at_the_turns_end(b: Bench):
    """Given another plugin whose hook denies each Agent call, and the writer due
    When the main conversation starts the writer, and ends its turn
    Then the end is stopped with the writer due again"""
    c = b.converse(denier(os.path.join(os.path.dirname(b.log), "deny")))
    c.type(f"/log:up {WORDS}")
    assert c.start("log:writer", text("log:writer"), "Write the entry")[1] is None
    answer = c.stop("The start was denied.")
    assert answer.blocked
    assert text("log:writer") in answer.said


@pytest.mark.supports("S9")
def test_two_starts_of_one_role_are_each_held_to_their_own_start(b: Bench):
    """Given the reviewer's `split`, which makes two writers due
    When the main conversation starts both, one reports `written` and ends, and the other ends with
    no result
    Then the turn's end goes through once both started, the first end goes through, and the second
    is stopped"""
    c = to_review(b)
    reviewed(c, "split")
    first, second = started(c), started(c)
    assert not c.stop("Both writers run.").blocked
    first.bash("lane-result written")
    assert not first.end("Done.")[0].blocked
    assert second.end("Done.")[0].blocked


@pytest.mark.supports("S9")
def test_a_start_whose_subagent_start_comes_after_its_post_tool_use_is_held(b: Bench):
    """Given the writer due
    When the main conversation starts it, its SubagentStart coming after the PostToolUse of its
    Agent call, and it writes a file that its step doesn't name
    Then the write is stopped, as the start is tied to the writer at that PostToolUse"""
    c = opened(b)
    writer = c.start("log:writer", text("log:writer"), "Write the entry", how=POSTED_FIRST)[1]
    assert writer is not None
    assert writer.write(b.at("notes.txt"), "x\n").blocked


@pytest.mark.supports("S9")
def test_a_subagent_started_in_the_foreground_lies_outside_the_run(b: Bench):
    """Given the writer due
    When the main conversation starts it in the foreground, and it writes a file that its step
    doesn't name
    Then the write goes through, as no start ties the subagent while it works"""
    c = opened(b)
    writer = c.start("log:writer", text("log:writer"), "Write the entry", how=FOREGROUND)[1]
    assert writer is not None
    assert not writer.write(b.at("notes.txt"), "x\n").blocked


@pytest.mark.supports("S9")
def test_a_resume_that_a_route_makes_due_goes_through_as_its_start(b: Bench):
    """Given the writer ended, and the reviewer's `more`, which makes the writer due
    When the main conversation resumes the writer by SendMessage, and ends its turn
    Then the resume goes through, and the end goes through, as the writer's start is made"""
    c = opened(b)
    writer = started(c)
    written(writer)
    reached(writer)
    reviewed(c, "more")
    assert not c.resume(writer, text("log:writer")).blocked
    assert not c.stop("The writer runs again.").blocked


@pytest.mark.supports("S9")
def test_a_resume_that_no_route_makes_due_goes_through_as_talk(b: Bench):
    """Given the writer ended, so the reviewer is due
    When the main conversation resumes the writer by SendMessage, and ends its turn
    Then the resume goes through, and the end is stopped with the reviewer still due"""
    c = opened(b)
    writer = started(c)
    written(writer)
    reached(writer)
    assert not c.resume(writer, "Fix the typo.").blocked
    answer = c.stop("Asked for a fix.")
    assert answer.blocked
    assert text("log:reviewer") in answer.said


@pytest.mark.supports("S9")
def test_a_resume_queued_to_a_running_subagent_waits_for_the_end_of_its_pass(b: Bench):
    """Given the writer running, and a message queued to it by SendMessage
    When the writer ends with no result, then keeps each step and ends, and then writes a file that
    its step doesn't name
    Then the first end is stopped, the second goes through, and the write is stopped, as the
    resume's start is tied to the writer once the pass ended"""
    c = opened(b)
    writer = started(c)
    assert not c.resume(writer, "Add the date.").blocked
    assert writer.end("Done.")[0].blocked
    written(writer)
    assert not writer.end("Done.")[0].blocked
    assert writer.write(b.at("notes.txt"), "x\n").blocked


@pytest.mark.supports("S9")
def test_a_subagent_stopped_by_task_stop_is_due_again(b: Bench):
    """Given the writer running
    When the main conversation stops it by TaskStop, and ends its turn
    Then the main conversation reads the writer due again with its text, and the end is stopped"""
    c = opened(b)
    writer = started(c)
    assert text("log:writer") in c.task_stop(writer).said
    assert c.stop("Stopped the writer.").blocked


@pytest.mark.supports("S9")
def test_another_skills_command_typed_while_a_subagent_runs_starts_its_run_beside(b: Bench):
    """Given the writer running
    When the person types /log:tag, the main conversation ends its turn, and the writer writes a
    file that its step doesn't name
    Then the end is stopped with the tagger due, and the write is stopped, as the writer stays on
    its own run"""
    c = opened(b)
    writer = started(c)
    c.type("/log:tag")
    answer = c.stop("Tagging.")
    assert answer.blocked
    assert text("log:tagger") in answer.said
    assert writer.write(b.at("notes.txt"), "x\n").blocked


@pytest.mark.supports("S9")
def test_the_plugins_command_typed_again_once_its_run_ended_adds_a_new_run(b: Bench):
    """Given a run that ended with the reviewer's `good`
    When the person types /log:up 1.3.0, and the main conversation ends its turn
    Then the end is stopped with the writer due for 1.3.0"""
    c = to_review(b)
    reviewed(c, "good")
    c.type("/log:up 1.3.0")
    answer = c.stop("Started again.")
    assert answer.blocked
    assert text("log:writer", "1.3.0") in answer.said


@pytest.mark.supports("S9")
def test_a_run_goes_on_in_a_worktree_the_conversation_enters(b: Bench):
    """Given the writer due
    When the main conversation enters a worktree, and ends its turn
    Then the end is stopped with the writer due, as the run goes on by its conversation"""
    c = opened(b)
    c.enter_worktree("entry")
    answer = c.stop("In the worktree.")
    assert answer.blocked
    assert text("log:writer") in answer.said


@pytest.mark.supports("S9")
def test_a_subagents_message_to_another_subagent_goes_through_as_talk(b: Bench):
    """Given two writers running after the reviewer's `split`
    When the first sends the second a message by SendMessage, and the main conversation ends its
    turn
    Then the message and the end go through"""
    c = to_review(b)
    reviewed(c, "split")
    first, second = started(c), started(c)
    assert not first.send(second, "I take docs/changes/.").blocked
    assert not c.stop("Both writers run.").blocked


@pytest.mark.supports("S9")
def test_another_conversation_in_the_repository_is_held_to_no_run_of_the_first(b: Bench):
    """Given the writer due in one conversation
    When another conversation in the same repository writes a file and ends its turn
    Then the write and the end go through, as no run of its own stands"""
    opened(b)
    other = b.converse()
    assert not other.write(None, b.at("notes.txt"), "x\n").blocked
    assert not other.stop("Done.").blocked
