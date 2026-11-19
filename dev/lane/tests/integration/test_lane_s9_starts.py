"""The integration cases of S9, the starts held to the plugin's order: the run added at the skill's
call, the starts due that the plugin's order gives, each start due let through with its prompt, any
other start and the turn's end while a start is due stopped, a typed command and each result added
and the starts due after them, until the order says the run ends; a run that waits, and a run of a
plugin that gives no order; and each state of Claude Code that bears on them, as
dev/lane/claude-code-states.md lists it. Each runs `log` and Lane through the double of Claude
Code."""

from __future__ import annotations

import os

import pytest
from claude_code import AGENT_DENIED_BY_RULE, AGENT_UNKNOWN_TYPE, FOREGROUND, POSTED_FIRST
from lane_bench import (
    UNBUILT,
    WORDS,
    Bench,
    denier,
    opened,
    prompt,
    reached,
    reviewed,
    started,
    to_review,
    written,
)

# A plugin beside `log` that gives no order: its skill holds the main conversation to one step,
# which writes NOTE.md and passes its check once NOTE.md is there.
NOTE_SAYS = "NOTE.md holds no note"
NOTE_RULES = {
    "roles": {
        "note:up": {
            "steps": [
                {
                    "name": "jot",
                    "rules": [
                        {"type": "writes", "paths": ["NOTE.md"]},
                        {
                            "type": "check",
                            "check": f"test -f NOTE.md || {{ echo '{NOTE_SAYS}'; exit 1; }}",
                        },
                    ],
                }
            ]
        }
    }
}

# An adapter of the starts due that gives no start while it waits for the person's answer, and
# never ends the run.
WAITS = 'import json\n\nprint(json.dumps({"starts": []}))\n'

# An adapter of the starts due that tells the starts of the writer apart by their prompts: the
# writer due until a start of it whose prompt names docs/changes/ is made.
BY_PROMPT = """\
import json, sys

moves = json.load(sys.stdin)["run"]["moves"]
prompts = [m["prompt"] for m in moves if m["kind"] == "start"]
done = any("docs/changes/" in each for each in prompts)
print(json.dumps({"starts": [] if done else [{"role": "log:writer", "count": 1}]}))
"""


@pytest.mark.supports("S9", "Starts due")
@UNBUILT
def test_the_turns_end_while_the_commands_start_is_due_is_stopped_with_it(b: Bench):
    """Given the person typed /log:up 1.2.0
    When the main conversation ends its turn
    Then the end is stopped, with the writer due, as the route after the command makes it"""
    answer = opened(b).stop("Started the run.")
    assert answer.blocked
    assert "log:writer" in answer.said


@pytest.mark.supports("S9")
@UNBUILT
def test_a_skill_called_by_the_skill_tool_adds_the_run(b: Bench):
    """Given a conversation in which no run of `log` stands
    When the main conversation calls log:up by the Skill tool with 1.2.0, and ends its turn
    Then the end is stopped, with the writer due"""
    c = b.converse()
    c.skill("log:up", WORDS)
    answer = c.stop("Called the skill.")
    assert answer.blocked
    assert "log:writer" in answer.said


@pytest.mark.supports("S9")
@UNBUILT
def test_the_start_due_goes_through_and_leaves_none_due(b: Bench):
    """Given the writer due
    When the main conversation starts the writer, and then ends its turn
    Then the start goes through, and the end goes through, as no start is due"""
    c = opened(b)
    answer, agent = c.start("log:writer", prompt("log:writer"), "Write the entry")
    assert agent is not None, answer.said
    assert not c.stop("The writer runs.").blocked


@pytest.mark.supports("S9")
def test_another_start_of_the_plugins_subagents_is_stopped_with_the_starts_due(b: Bench):
    """Given the writer due
    When the main conversation starts the reviewer
    Then the start is stopped, and the main conversation reads the writer due"""
    answer, agent = opened(b).start("log:reviewer", prompt("log:reviewer"), "Review")
    assert agent is None
    assert answer.blocked
    assert "log:writer" in answer.said


@pytest.mark.supports("S9")
def test_a_subagents_start_of_a_subagent_is_stopped(b: Bench):
    """Given the writer running
    When the writer starts a writer by the Agent tool
    Then the start is stopped, as only the main conversation starts the roles"""
    writer = started(opened(b))
    answer, agent = writer.start("log:writer", prompt("log:writer"), "Write the entry")
    assert agent is None
    assert answer.blocked


@pytest.mark.supports("S9", "S7", "Starts due")
@UNBUILT
def test_a_result_reaching_the_main_conversation_gives_the_starts_due_after_it(b: Bench):
    """Given the writer kept each step and reported `written`
    When its end reaches the main conversation
    Then the main conversation reads the result and the reviewer due"""
    writer = started(opened(b))
    written(writer)
    answer = reached(writer)
    assert "written" in answer.said
    assert "log:reviewer" in answer.said


@pytest.mark.supports("S9")
@UNBUILT
def test_a_typed_command_that_a_route_goes_after_puts_its_starts_in_place(b: Bench):
    """Given the writer ended with its result, so the reviewer is due
    When the person types /log:retry, and the main conversation starts the reviewer, and then the
    writer
    Then the reviewer's start is stopped with the writer due, and the writer's goes through"""
    c = to_review(b)
    c.type("/log:retry")
    answer, agent = c.start("log:reviewer", prompt("log:reviewer"), "Review")
    assert agent is None
    assert "log:writer" in answer.said
    assert c.start("log:writer", prompt("log:writer"), "Write again")[1] is not None


@pytest.mark.supports("S9", "Starts due")
@UNBUILT
def test_a_run_whose_order_says_it_ends_holds_no_move_after(b: Bench):
    """Given the reviewer due
    When the reviewer reports `good` and ends, and the main conversation writes a file that no
    step names and ends its turn
    Then the write and the end go through, as the run ended"""
    c = to_review(b)
    reviewed(c, "good")
    assert not c.write(None, b.at("notes.txt"), "x\n").blocked
    assert not c.stop("Done.").blocked


@pytest.mark.supports("S9", "Starts due")
@UNBUILT
def test_a_run_whose_order_gives_no_start_due_waits_and_still_holds_its_moves(b: Bench):
    """Given `log` whose adapter of the starts due gives none, as it waits for the person's answer
    When the person types /log:up 1.2.0, the main conversation ends its turn, and then writes a
    file that its skill's step doesn't name
    Then the end goes through, and the write is stopped with the step `lead`, as the run stands"""
    b.adapter("starts_due.py", WAITS)
    c = opened(b)
    assert not c.stop("Waiting for the person.").blocked
    answer = c.write(None, b.at("notes.txt"), "x\n")
    assert answer.blocked
    assert "lead" in answer.said


@pytest.mark.supports("S9", "Run")
@UNBUILT
def test_the_order_tells_the_starts_of_one_role_apart_by_their_prompts(b: Bench):
    """Given `log` whose adapter of the starts due gives the writer due until a start of it whose
    prompt names docs/changes/ is made
    When the main conversation starts the writer to write CHANGELOG.md and ends its turn, and then
    starts it to write docs/changes/ and ends its turn
    Then the first end is stopped with the writer due, and the second goes through"""
    b.adapter("starts_due.py", BY_PROMPT)
    c = opened(b)
    started(c, given="Write CHANGELOG.md.")
    answer = c.stop("One writer runs.")
    assert answer.blocked
    assert "log:writer" in answer.said
    started(c, given="Write docs/changes/.")
    assert not c.stop("Both writers run.").blocked


@pytest.mark.supports("S9", "S1")
@UNBUILT
def test_a_run_of_a_plugin_with_no_order_holds_the_main_conversation_to_its_skills_steps(
    b: Bench,
):
    """Given `note` beside `log`, which gives steps for its skill and no order
    When the person types /note:up, and the main conversation writes notes.txt, and then NOTE.md
    Then the first write is stopped naming NOTE.md, and the second goes through"""
    c = b.converse(b.other("note", NOTE_RULES))
    c.type("/note:up")
    answer = c.write(None, b.at("notes.txt"), "x\n")
    assert answer.blocked
    assert "NOTE.md" in answer.said
    assert not c.write(None, b.at("NOTE.md"), "x\n").blocked


@pytest.mark.supports("S9", "S8")
@UNBUILT
def test_the_turns_end_in_a_run_of_a_plugin_with_no_order_is_held_to_its_skills_check(b: Bench):
    """Given `note` beside `log`, which gives no order, and the person typed /note:up
    When the main conversation ends its turn before NOTE.md is there
    Then the end is stopped with the step `jot` and what its check said"""
    c = b.converse(b.other("note", NOTE_RULES))
    c.type("/note:up")
    answer = c.stop("Done.")
    assert answer.blocked
    assert "jot" in answer.said
    assert NOTE_SAYS in answer.said


@pytest.mark.supports("S9")
@UNBUILT
def test_a_run_of_a_plugin_with_no_order_ends_at_the_turns_end_that_its_steps_let_through(
    b: Bench,
):
    """Given `note` beside `log`, which gives no order, and the person typed /note:up
    When the main conversation writes NOTE.md, ends its turn, and then writes notes.txt
    Then the end goes through, and so does the write, as the run ended with the turn"""
    c = b.converse(b.other("note", NOTE_RULES))
    c.type("/note:up")
    c.write(None, b.at("NOTE.md"), "x\n")
    assert not c.stop("Noted.").blocked
    assert not c.write(None, b.at("notes.txt"), "x\n").blocked


@pytest.mark.supports("S9")
@pytest.mark.parametrize("record", [AGENT_UNKNOWN_TYPE, AGENT_DENIED_BY_RULE])
@UNBUILT
def test_an_agent_call_that_fails_after_its_pre_tool_use_leaves_its_start_due(
    b: Bench, record: str
):
    """Given the writer due
    When the main conversation starts the writer, and the Agent call fails after its PreToolUse,
    as it names no subagent type that exists or a permission rule denies it
    Then the turn's end is stopped with the writer due again"""
    c = opened(b)
    assert c.start_failing("log:writer", prompt("log:writer"), "Write the entry", record).blocked
    answer = c.stop("The start failed.")
    assert answer.blocked
    assert "log:writer" in answer.said


@pytest.mark.supports("S9")
@UNBUILT
def test_a_start_that_another_plugins_hook_denies_is_due_again_at_the_turns_end(b: Bench):
    """Given another plugin whose hook denies each Agent call, and the writer due
    When the main conversation starts the writer, and ends its turn
    Then the end is stopped with the writer due again"""
    c = b.converse(denier(os.path.join(os.path.dirname(b.log), "deny")))
    c.type(f"/log:up {WORDS}")
    assert c.start("log:writer", prompt("log:writer"), "Write the entry")[1] is None
    answer = c.stop("The start was denied.")
    assert answer.blocked
    assert "log:writer" in answer.said


@pytest.mark.supports("S9")
@UNBUILT
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
    written(first)
    assert not first.end("Done.")[0].blocked
    assert second.end("Done.")[0].blocked


@pytest.mark.supports("S9")
def test_a_start_whose_subagent_start_comes_after_its_post_tool_use_is_held(b: Bench):
    """Given the writer due
    When the main conversation starts it, its SubagentStart coming after the PostToolUse of its
    Agent call, and it writes a file that its step doesn't name
    Then the write is stopped, as the start is tied to the writer at that PostToolUse"""
    c = opened(b)
    writer = c.start("log:writer", prompt("log:writer"), "Write the entry", how=POSTED_FIRST)[1]
    assert writer is not None
    assert writer.write(b.at("notes.txt"), "x\n").blocked


@pytest.mark.supports("S9")
def test_a_start_of_a_subagent_that_isnt_the_plugins_lies_outside_the_run(b: Bench):
    """Given the writer due
    When the main conversation starts general-purpose, and it writes a file that no step names
    Then the start and the write go through, as no rule of `log` names general-purpose"""
    c = opened(b)
    helper = c.start("general-purpose", "Look around.", "Look around")[1]
    assert helper is not None
    assert not helper.write(b.at("notes.txt"), "x\n").blocked


@pytest.mark.supports("S9")
def test_a_subagent_started_in_the_foreground_lies_outside_the_run(b: Bench):
    """Given the writer due
    When the main conversation starts it in the foreground, and it writes a file that its step
    doesn't name
    Then the write goes through, as no start ties the subagent while it works"""
    c = opened(b)
    writer = c.start("log:writer", prompt("log:writer"), "Write the entry", how=FOREGROUND)[1]
    assert writer is not None
    assert not writer.write(b.at("notes.txt"), "x\n").blocked


@pytest.mark.supports("S9")
@UNBUILT
def test_a_resume_that_the_order_makes_due_goes_through_as_its_start(b: Bench):
    """Given the writer ended, and the reviewer's `more`, which makes the writer due
    When the main conversation resumes the writer by SendMessage, and ends its turn
    Then the resume goes through, and the end goes through, as the writer's start is made"""
    c = opened(b)
    writer = started(c)
    written(writer)
    reached(writer)
    reviewed(c, "more")
    assert not c.resume(writer, prompt("log:writer")).blocked
    assert not c.stop("The writer runs again.").blocked


@pytest.mark.supports("S9")
@UNBUILT
def test_a_resume_that_the_order_doesnt_make_due_goes_through_as_talk(b: Bench):
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
    assert "log:reviewer" in answer.said


@pytest.mark.supports("S9")
@UNBUILT
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
@UNBUILT
def test_a_subagent_stopped_by_task_stop_is_due_again(b: Bench):
    """Given the writer running
    When the main conversation stops it by TaskStop, and ends its turn
    Then the main conversation reads the writer due again, and the end is stopped"""
    c = opened(b)
    writer = started(c)
    assert "log:writer" in c.task_stop(writer).said
    assert c.stop("Stopped the writer.").blocked


@pytest.mark.supports("S9")
@UNBUILT
def test_another_skills_command_typed_while_a_subagent_runs_moves_the_run(b: Bench):
    """Given the writer running
    When the person types /log:tag, the main conversation ends its turn, and the writer writes a
    file that its step doesn't name
    Then the end is stopped with the tagger due, as the command moves the run that stands, and the
    write is stopped, as the writer stays on its own start"""
    c = opened(b)
    writer = started(c)
    c.type("/log:tag")
    answer = c.stop("Tagging.")
    assert answer.blocked
    assert "log:tagger" in answer.said
    assert writer.write(b.at("notes.txt"), "x\n").blocked


@pytest.mark.supports("S9", "S1")
@UNBUILT
def test_the_main_conversation_holds_to_the_steps_of_the_latest_commands_skill(b: Bench):
    """Given the person typed /log:up 1.2.0, and then /log:tag
    When the main conversation writes .log/up.md, and then .log/tags.md
    Then the first is stopped naming .log/tags.md, and the second goes through"""
    c = opened(b)
    c.type("/log:tag")
    answer = c.write(None, b.at(".log/up.md"), "x\n")
    assert answer.blocked
    assert ".log/tags.md" in answer.said
    assert not c.write(None, b.at(".log/tags.md"), "x\n").blocked


@pytest.mark.supports("S9")
@UNBUILT
def test_the_plugins_command_typed_again_once_its_run_ended_adds_a_new_run(b: Bench):
    """Given a run that ended with the reviewer's `good`
    When the person types /log:up 1.3.0, and the main conversation ends its turn
    Then the end is stopped with the writer due"""
    c = to_review(b)
    reviewed(c, "good")
    c.type("/log:up 1.3.0")
    answer = c.stop("Started again.")
    assert answer.blocked
    assert "log:writer" in answer.said


@pytest.mark.supports("S9")
@UNBUILT
def test_a_run_goes_on_in_a_worktree_the_conversation_enters(b: Bench):
    """Given the writer due
    When the main conversation enters a worktree, and ends its turn
    Then the end is stopped with the writer due, as the run goes on by its conversation"""
    c = opened(b)
    c.enter_worktree("entry")
    answer = c.stop("In the worktree.")
    assert answer.blocked
    assert "log:writer" in answer.said


@pytest.mark.supports("S9")
@UNBUILT
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
