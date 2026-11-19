"""The unit cases of hooks/lane/place.py: skill_call, one for each event that calls a skill or
doesn't, and for a command of a plugin whose run stands, has ended, or was never added; opening, one
for each
event at which the transcript holds the skill's base directory or not yet; and place, one for each
transition of a run's moves that Lane's list of Claude Code's states brings about, each event placed
on its run, its start, its role, and its step, or outside each run."""

from __future__ import annotations

import json
import os
from typing import Any

import lane_bench
import lane_entries
import pytest
from lane_events import Events, Subagent
from order import StartsDue, order_run
from place import SkillCall, opening, place, skill_call
from record import Entry, Run
from repo_files import write_files
from report import report
from routes import starts_due
from rules import OutOfForm, Step

UNBUILT = pytest.mark.xfail(strict=True, reason="Lane's parts have no bodies yet")


def by_routes(run: Run) -> StartsDue:
    """The starts due of the run, as Lane's route adapter gives them from `log`'s routes."""
    return starts_due(lane_bench.RULES.get("routes", []), order_run(run))


WRITER = Subagent("a1", "log:writer")


@pytest.fixture
def e(cwd: str) -> Events:
    """The events of a conversation in the folder."""
    return Events(cwd, os.path.join(os.path.dirname(cwd), "transcripts", "session-1.jsonl"))


# The folder of `log` that each run of the case lies in, set by the fixture `folder`.
LOG = {"folder": ""}


@pytest.fixture(autouse=True)
def folder(log: str) -> None:
    LOG["folder"] = log


def run(*entries: Entry, opened: bool = True) -> Run:
    """A run r1 of log:up for 1.2.0, with log's folder where it's opened, and the entries."""
    head: list[Entry] = [{"kind": "run", "run": "r1", "skill": "log:up", "words": "1.2.0"}]
    root = LOG["folder"] if opened else None
    if root:
        head.append({"kind": "folder", "run": "r1", "plugin_root": root})
    return Run("r1", "session-1", "log:up", "1.2.0", root, [*head, *entries])


PROMPT = "Write the entry."
START: Entry = lane_entries.start("u1", prompt=PROMPT)
TIE: Entry = lane_entries.tie("u1", "a1")


def tied() -> Run:
    """A run of log:up whose writer is tied to a1."""
    return run(START, TIE)


# The writer's `written` and the reviewer's `good`, after which log's routes start no more.
GOOD: tuple[Entry, ...] = (
    START,
    TIE,
    lane_entries.result("a1", "written"),
    lane_entries.start("u2", "log:reviewer"),
    lane_entries.tie("u2", "a2"),
    lane_entries.result("a2", "good", "log:reviewer"),
)


def kind(move: Any) -> str | None:
    return move.kind if move else None


def reported(capsys: pytest.CaptureFixture[str], kind: str, words: list[str]) -> str:
    """The line that a reporter of the kind prints for the words."""
    report(kind, words)
    return capsys.readouterr().out


@pytest.mark.supports("test_the_turns_end_while_the_commands_start_is_due_is_stopped_with_it")
def test_a_typed_command_calls_its_skill_with_the_words(e: Events):
    """Given the UserPromptExpansion of /log:up 1.2.0
    When Lane reads which skill it calls
    Then it's log:up, with the words 1.2.0, in the event's conversation"""
    called = skill_call(e.typed("log:up", "1.2.0"), [])
    assert called == SkillCall("session-1", e.transcript, "log:up", "1.2.0")


@pytest.mark.supports("test_a_skill_called_by_the_skill_tool_adds_the_run")
def test_a_skill_tool_call_that_ran_calls_its_skill_with_its_args(e: Events):
    """Given the PostToolUse of the main conversation's Skill call of log:up with 1.2.0
    When Lane reads which skill it calls
    Then it's log:up, with the words 1.2.0"""
    assert skill_call(e.skill_post("log:up", "1.2.0"), []) == SkillCall(
        "session-1", e.transcript, "log:up", "1.2.0"
    )


@pytest.mark.supports("test_a_skill_called_by_the_skill_tool_adds_the_run")
def test_a_skill_tool_call_before_it_runs_calls_no_skill(e: Events):
    """Given the PreToolUse of a Skill call, which a hook may still deny
    When Lane reads which skill it calls
    Then it calls none yet"""
    assert skill_call(e.skill_pre("log:up", "1.2.0"), []) is None


@pytest.mark.supports("test_work_outside_a_run_of_a_plugin_with_rules_is_left_alone")
def test_a_skill_that_no_plugin_holds_calls_no_skill(e: Events):
    """Given the UserPromptExpansion of the person's own skill /hi, whose name has no plugin's
    prefix
    When Lane reads which skill it calls
    Then it calls none, as Lane checks only a plugin's skill"""
    assert skill_call(e.typed("hi"), []) is None


@pytest.mark.supports("test_the_turns_end_while_the_commands_start_is_due_is_stopped_with_it")
def test_any_other_event_calls_no_skill(e: Events):
    """Given the main conversation's Stop
    When Lane reads which skill it calls
    Then it calls none"""
    assert skill_call(e.stop(), [run()]) is None


@pytest.mark.supports("test_another_skills_command_typed_while_a_subagent_runs_moves_the_run")
@pytest.mark.parametrize("by", ["typed", "skill_post"])
def test_a_command_of_the_plugin_whose_run_stands_calls_no_skill(e: Events, by: str):
    """Given a run of log:up in log's folder, not ended
    When the UserPromptExpansion of /log:tag, or the PostToolUse of a Skill call of log:tag, comes
    Then it calls no skill, as the command is a move of the run"""
    given = e.typed("log:tag") if by == "typed" else e.skill_post("log:tag", "")
    assert skill_call(given, [run()]) is None


@pytest.mark.supports("test_a_typed_command_that_a_route_goes_after_puts_its_starts_in_place")
def test_a_command_that_a_route_of_the_standing_run_goes_after_calls_no_skill(e: Events):
    """Given a run of log:up in log's folder, not ended, whose rules route after /log:retry
    When the UserPromptExpansion of /log:retry comes
    Then it calls no skill, as the command is a move of the run"""
    assert skill_call(e.typed("log:retry"), [run()]) is None


@pytest.mark.supports("test_the_plugins_command_typed_again_once_its_run_ended_adds_a_new_run")
def test_a_command_of_the_plugin_whose_run_ended_calls_its_skill(e: Events):
    """Given a run of log:up in log's folder that ended with the reviewer's `good`, its record
    holding its `ended` entry
    When the UserPromptExpansion of /log:up 1.3.0 comes
    Then it calls log:up with 1.3.0"""
    ended: Entry = {"kind": "ended", "run": "r1"}
    called = skill_call(e.typed("log:up", "1.3.0"), [run(*GOOD, ended)])
    assert called == SkillCall("session-1", e.transcript, "log:up", "1.3.0")


@pytest.mark.supports(
    "test_the_starts_due_come_at_the_main_conversations_next_event_after_the_skills_call"
)
@pytest.mark.parametrize("event", ["bash", "stop"])
def test_the_main_conversations_next_event_opens_a_run_with_no_folder(e: Events, event: str):
    """Given a run of log:up with no folder
    When the main conversation's next event, a Bash call or its Stop, comes
    Then that run opens"""
    given = e.bash("git status") if event == "bash" else e.stop()
    unopened = run(opened=False)
    assert opening(given, [unopened]) == [unopened]


@pytest.mark.supports(
    "test_the_starts_due_come_at_the_main_conversations_next_event_after_the_skills_call"
)
@pytest.mark.parametrize("event", ["typed", "skill_pre", "skill_post"])
def test_the_skills_own_call_opens_no_run(e: Events, event: str):
    """Given a run of log:up with no folder
    When the UserPromptExpansion of its command, or the PreToolUse or PostToolUse of its Skill
    call, comes, before the transcript holds the base directory
    Then no run opens"""
    given = {
        "typed": e.typed("log:up", "1.2.0"),
        "skill_pre": e.skill_pre("log:up", "1.2.0"),
        "skill_post": e.skill_post("log:up", "1.2.0"),
    }[event]
    assert opening(given, [run(opened=False)]) == []


@pytest.mark.supports(
    "test_the_starts_due_come_at_the_main_conversations_next_event_after_the_skills_call"
)
def test_a_run_with_its_folder_opens_no_more(e: Events):
    """Given a run of log:up with its folder
    When the main conversation's Stop comes
    Then no run opens"""
    assert opening(e.stop(), [run()]) == []


@pytest.mark.supports(
    "test_the_starts_due_come_at_the_main_conversations_next_event_after_the_skills_call"
)
def test_a_subagents_event_opens_no_run(e: Events):
    """Given a run of log:up with no folder
    When a subagent's Bash call comes
    Then no run opens, as the transcript is the main conversation's"""
    assert opening(e.bash("git log", WRITER), [run(opened=False)]) == []


@pytest.mark.supports("test_another_conversation_in_the_repository_is_held_to_no_run_of_the_first")
def test_an_event_of_a_conversation_with_no_run_lies_outside(e: Events):
    """Given a conversation with no run
    When the main conversation writes a file
    Then the event lies outside each run"""
    assert place(e.write("/repo/notes.txt"), [], by_routes) is None


@pytest.mark.supports("test_the_main_conversations_write_in_a_run_is_held_to_its_skills_step")
def test_the_main_conversations_call_is_a_call_of_the_skills_role(e: Events):
    """Given a run of log:up
    When the main conversation writes a file
    Then the move is a call on that run, of the role log:up, with no agent, at the step `lead`"""
    move = place(e.write("/repo/notes.txt"), [run()], by_routes)
    assert move is not None
    assert (move.kind, move.run.id, move.role, move.agent_id, move.step) == (
        "call",
        "r1",
        "log:up",
        None,
        "lead",
    )


@pytest.mark.supports("test_the_start_due_goes_through_and_leaves_none_due")
@pytest.mark.parametrize("by", [None, WRITER])
def test_an_agent_call_is_a_start(e: Events, by: Subagent | None):
    """Given a run of log:up whose writer is tied to a1
    When the main conversation, or the writer, starts a writer by the Agent tool
    Then the move is a start, with the agent that made it"""
    move = place(e.start("log:writer", "u2", by), [tied()], by_routes)
    assert move is not None
    assert (move.kind, move.agent_id) == ("start", by.id if by else None)


@pytest.mark.supports("test_the_start_due_goes_through_and_leaves_none_due")
def test_the_post_tool_use_of_a_starts_agent_call_ties_it(e: Events):
    """Given a run of log:up with the writer's start of u1, untied
    When the PostToolUse of u1 names the subagent a1
    Then the move is a tie of that start"""
    assert kind(place(e.started(WRITER, "u1"), [run(START)], by_routes)) == "tie"


@pytest.mark.supports("test_an_agent_call_that_fails_after_its_pre_tool_use_leaves_its_start_due")
@UNBUILT
def test_the_failure_of_a_starts_agent_call_drops_it(e: Events):
    """Given a run of log:up with the writer's start of u1, untied
    When the PostToolUseFailure of u1 comes
    Then the move is a drop"""
    assert kind(place(e.start_failed("log:writer", "u1"), [run(START)], by_routes)) == "drop"


@pytest.mark.supports("test_a_write_of_a_file_that_its_step_doesnt_name_is_stopped_with_the_step")
def test_a_tied_subagents_call_is_a_call_of_its_role_at_its_first_step(e: Events):
    """Given the writer tied to a1, no step marked
    When a1 writes a file
    Then the move is a call of the role log:writer, by a1, at the step `write`"""
    move = place(e.write("/repo/notes.txt", WRITER), [tied()], by_routes)
    assert move is not None
    assert (move.kind, move.role, move.agent_id, move.step) == ("call", "log:writer", "a1", "write")


@pytest.mark.supports("test_steps_marked_in_their_order_hold_and_the_end_goes_through")
def test_a_subagents_call_after_a_step_marked_is_at_the_next_step(e: Events):
    """Given the writer tied to a1, its step `write` marked done
    When a1 runs a command
    Then the move is at the step `report`"""
    marked: Entry = {"kind": "mark", "run": "r1", "agent_id": "a1", "step": "write"}
    move = place(e.bash("git log", WRITER), [run(START, TIE, marked)], by_routes)
    assert move is not None
    assert move.step == "report"


@pytest.mark.supports("test_a_read_whole_holds_the_mark")
def test_the_post_tool_use_of_a_subagents_read_is_a_read(e: Events):
    """Given the writer tied to a1
    When the PostToolUse of a1's Read of NOTES.md comes
    Then the move is a read"""
    notes = os.path.join(e.cwd, "NOTES.md")
    assert kind(place(e.read_ran(notes, 1, 6, 6, WRITER), [tied()], by_routes)) == "read"


@pytest.mark.supports("test_a_reporters_result_counts_for_the_subagent_that_ran_it")
@UNBUILT
def test_a_reporters_bash_call_is_a_report_with_what_it_printed(
    e: Events, capsys: pytest.CaptureFixture[str]
):
    """Given the writer tied to a1
    When the PostToolUse of a1's `lane-result written` comes, with the line the reporter printed
    Then the move is a report of the result `written`, by a1"""
    printed = reported(capsys, "result", ["written"])
    move = place(e.bash_ran("lane-result written", printed, WRITER), [tied()], by_routes)
    assert move is not None
    assert (move.kind, move.agent_id, move.report) == (
        "report",
        "a1",
        {"kind": "result", "result": "written"},
    )


@pytest.mark.supports("test_a_command_that_its_step_names_goes_through")
@UNBUILT
def test_the_post_tool_use_of_another_command_is_no_move(e: Events):
    """Given the writer tied to a1
    When the PostToolUse of a1's `git log` comes
    Then it makes no move"""
    assert place(e.bash_ran("git log", "bf742e7 first", WRITER), [tied()], by_routes) is None


@pytest.mark.supports("test_an_end_with_no_result_is_stopped_with_the_results_it_may_give")
@UNBUILT
def test_a_tied_subagents_stop_is_its_end(e: Events):
    """Given the writer tied to a1
    When a1's SubagentStop comes
    Then the move is the end of a1's start"""
    move = place(e.ended(WRITER), [tied()], by_routes)
    assert move is not None
    assert (move.kind, move.agent_id, move.role) == ("end", "a1", "log:writer")


@pytest.mark.supports("test_the_turns_end_while_the_commands_start_is_due_is_stopped_with_it")
@UNBUILT
def test_the_main_conversations_stop_is_the_end_of_its_turn(e: Events):
    """Given a run of log:up
    When the main conversation's Stop comes
    Then the move is the end of the turn"""
    assert kind(place(e.stop(), [run()], by_routes)) == "turn_end"


@pytest.mark.supports("test_a_typed_command_that_a_route_goes_after_puts_its_starts_in_place")
@UNBUILT
def test_a_typed_command_that_a_route_waits_for_is_typed(e: Events):
    """Given a run of log:up in log's folder, not ended
    When the UserPromptExpansion of /log:retry comes
    Then the move is a typed command on that run"""
    move = place(e.typed("log:retry"), [run()], by_routes)
    assert (kind(move), move.run.id if move else None) == ("typed", "r1")


@pytest.mark.supports("test_another_skills_command_typed_while_a_subagent_runs_moves_the_run")
@UNBUILT
def test_a_skill_tool_call_of_the_plugins_skill_while_its_run_stands_is_typed(e: Events):
    """Given a run of log:up in log's folder whose writer is tied to a1
    When the PostToolUse of the main conversation's Skill call of log:tag comes
    Then the move is a typed command on that run"""
    move = place(e.skill_post("log:tag", ""), [run(START, TIE)], by_routes)
    assert (kind(move), move.run.id if move else None) == ("typed", "r1")


@pytest.mark.supports("test_the_main_conversation_holds_to_the_steps_of_the_latest_commands_skill")
@pytest.mark.parametrize("command, role", [("log:tag", "log:tag"), ("log:retry", "log:up")])
def test_the_main_conversations_call_after_a_command_holds_to_its_skills_steps_if_any(
    e: Events, command: str, role: str
):
    """Given a run of log:up in log's folder, and the command /log:tag, whose skill the rules give
    steps of, or /log:retry, whose skill they give none of, typed in it
    When the main conversation writes a file
    Then the move is a call of the role log:tag, or still log:up, at the step `lead`"""
    typed: Entry = {"kind": "typed", "run": "r1", "command": command}
    move = place(e.write("/repo/notes.txt"), [run(typed)], by_routes)
    assert move is not None
    assert (move.kind, move.role, move.step) == ("call", role, "lead")


@pytest.mark.supports("test_a_result_reaching_the_main_conversation_gives_the_starts_due_after_it")
@pytest.mark.parametrize("killed", [False, True])
@UNBUILT
def test_a_task_notification_of_a_tied_subagent_is_its_result_reaching(e: Events, killed: bool):
    """Given the writer tied to a1 by the Agent call u1
    When a1's task-notification reaches the main conversation, of its end or of its stop by
    TaskStop
    Then the move is its result reaching, by a1"""
    given = e.killed(WRITER, "u1") if killed else e.reached(WRITER, "u1")
    move = place(given, [tied()], by_routes)
    assert (kind(move), move.agent_id if move else None) == ("result_reached", "a1")


@pytest.mark.supports("test_a_resume_that_the_order_makes_due_goes_through_as_its_start")
@UNBUILT
def test_a_send_message_from_the_main_conversation_is_a_start(e: Events):
    """Given the writer tied to a1, whose end came
    When the main conversation's PreToolUse of SendMessage to a1 comes
    Then the move is a start"""
    assert kind(place(e.send(WRITER, "u2"), [tied()], by_routes)) == "start"


@pytest.mark.supports("test_a_resume_that_the_order_makes_due_goes_through_as_its_start")
@UNBUILT
def test_a_send_message_that_resumed_its_subagent_ties_it(e: Events):
    """Given the writer tied to a1, and a start by SendMessage u2 to it
    When the PostToolUse of u2 says it resumed a1
    Then the move is a tie"""
    resume: Entry = lane_entries.start("u2")
    assert kind(place(e.resumed(WRITER, "u2"), [run(START, TIE, resume)], by_routes)) == "tie"


@pytest.mark.supports("test_a_resume_queued_to_a_running_subagent_waits_for_the_end_of_its_pass")
@UNBUILT
def test_a_send_message_queued_to_a_running_subagent_is_a_queue(e: Events):
    """Given the writer tied to a1, running, and a start by SendMessage u2 to it
    When the PostToolUse of u2 says the message is queued
    Then the move is a queue"""
    resume: Entry = lane_entries.start("u2")
    assert kind(place(e.queued(WRITER, "u2"), [run(START, TIE, resume)], by_routes)) == "queue"


@pytest.mark.supports("test_a_resume_queued_to_a_running_subagent_waits_for_the_end_of_its_pass")
@UNBUILT
def test_the_stop_of_a_subagent_with_a_resume_queued_ends_the_pass_that_ran(e: Events):
    """Given the writer tied to a1 by u1, and a resume u2 queued to it
    When a1's SubagentStop comes
    Then the move is the end of the start that a1 ran, with u2 still untied"""
    resume: Entry = lane_entries.start("u2")
    queued: Entry = {"kind": "queue", "run": "r1", "tool_use_id": "u2", "agent_id": "a1"}
    move = place(e.ended(WRITER), [run(START, TIE, resume, queued)], by_routes)
    assert (kind(move), move.agent_id if move else None) == ("end", "a1")


@pytest.mark.supports("test_after_compact_the_run_goes_on_with_its_starts_due")
def test_the_summarys_end_at_compact_lies_outside(e: Events):
    """Given the writer tied to a1
    When the SubagentStop of /compact's summary comes, with an agent that no start ties
    Then it lies outside each run"""
    assert place(e.summary_ended("a9"), [tied()], by_routes) is None


@pytest.mark.supports("test_a_subagent_started_in_the_foreground_lies_outside_the_run")
def test_a_call_of_a_subagent_that_no_start_ties_lies_outside(e: Events):
    """Given the writer's start, untied
    When a subagent a1 writes a file
    Then it lies outside each run"""
    assert place(e.write("/repo/notes.txt", WRITER), [run(START)], by_routes) is None


@pytest.mark.supports("test_each_plugins_run_is_held_to_the_rules_in_its_own_folder")
def test_a_subagents_call_is_placed_on_the_run_of_its_start(e: Events):
    """Given a run r1 of log:up whose writer is tied to a1, and a run r2 of memo:up after it
    When a1 writes a file
    Then the move lies on r1"""
    memo = Run("r2", "session-1", "memo:up", "", "/plugins/memo", [])
    move = place(e.write("/repo/notes.txt", WRITER), [tied(), memo], by_routes)
    assert move is not None
    assert move.run.id == "r1"


@pytest.mark.supports("test_the_order_tells_the_starts_of_one_role_apart_by_their_prompts")
def test_an_agent_calls_start_carries_its_prompt(e: Events):
    """Given a run of log:up
    When the main conversation starts the writer by the Agent tool with a prompt
    Then the start move carries that prompt"""
    move = place(e.start("log:writer", "u1", prompt="Write docs/changes/."), [run()], by_routes)
    assert (kind(move), move.prompt if move else None) == ("start", "Write docs/changes/.")


@pytest.mark.supports("test_a_resume_that_the_order_makes_due_goes_through_as_its_start")
@UNBUILT
def test_a_resumes_start_carries_the_prompt_of_the_start_it_resumes(e: Events):
    """Given the writer tied to a1, started with its prompt
    When the main conversation's PreToolUse of SendMessage to a1 comes
    Then the start move carries the prompt of a1's start, not the message"""
    move = place(e.send(WRITER, "u2"), [tied()], by_routes)
    assert (kind(move), move.prompt if move else None) == ("start", PROMPT)


@pytest.mark.supports(
    "test_a_role_with_no_fixed_steps_takes_them_from_the_plugins_adapter_for_each_start"
)
def test_a_call_of_a_start_with_steps_given_is_held_to_them(e: Events, log: str):
    """Given rules that name the writer with no steps, and the writer tied to a1, whose start holds
    the step `draft` that the plugin's adapter of the rules gave
    When a1 writes a file
    Then the move is held to the step `draft`, at that step"""
    write_files(log, {"lane/rules.json": json.dumps(lane_bench.ADAPTED)})
    given: list[Step] = [{"name": "draft", "rules": [{"type": "writes", "paths": ["docs/"]}]}]
    move = place(
        e.write("/repo/notes.txt", WRITER), [run({**START, "steps": given}, TIE)], by_routes
    )
    assert move is not None
    assert (move.steps, move.step) == (given, "draft")


@pytest.mark.supports("test_rules_out_of_form_stop_the_call_saying_what_the_author_mends")
def test_a_command_of_a_run_whose_rules_are_out_of_form_is_refused(e: Events, log: str):
    """Given a run of log:up whose plugin's lane/rules.json now lacks its roles
    When the UserPromptExpansion of /log:retry comes
    Then Lane refuses with OutOfForm"""
    write_files(log, {"lane/rules.json": "{}"})
    with pytest.raises(OutOfForm):
        place(e.typed("log:retry"), [run()], by_routes)
