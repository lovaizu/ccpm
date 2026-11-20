"""The unit cases of hooks/lane/place.py: skill_call, one for each event that calls a skill or
doesn't, and for a command of a plugin whose run stands, has ended, or was never added, beside the
runs of another plugin whose name nearly matches; opening, one for each event at which the
transcript holds the skill's base directory or not yet, with runs of which some have a folder;
place, one for each transition of a run's moves that Lane's list of Claude Code's states brings
about, each event placed on its run, its start, its role, and its step, or outside each run, the
latest run not ended picked of several, the latest command whose skill has steps, the latest tie of
a resumed subagent, a resume carrying its start's role, prompt, and steps, a Grep and a Glob, and
the events of another plugin, of an untied subagent, or of no start, which it leaves alone; and
command_of, marked, and latest_start, which place's callers share. Each Then of place gives the
whole move."""

from __future__ import annotations

import dataclasses
import json
import os
from typing import Any

import lane_bench
import lane_entries
import pytest
from lane_events import Event, Events, Subagent
from order import StartsDue, order_run
from place import Move, SkillCall, command_of, latest_start, marked, opening, place, skill_call
from record import Entry, Run
from repo_files import write_files
from report import report
from routes import starts_due
from rules import OutOfForm, Step


def by_routes(run: Run) -> StartsDue:
    """The starts due of the run, as Lane's route adapter gives them from `log`'s routes."""
    return starts_due(lane_bench.RULES.get("routes", []), order_run(run))


WRITER = Subagent("a1", "log:writer")
UP: list[Step] = lane_bench.RULES["roles"]["log:up"]["steps"]
TAG: list[Step] = lane_bench.RULES["roles"]["log:tag"]["steps"]
WRITES: list[Step] = lane_bench.RULES["roles"]["log:writer"]["steps"]


@pytest.fixture
def e(cwd: str) -> Events:
    """The events of a conversation in the folder."""
    return Events(cwd, os.path.join(os.path.dirname(cwd), "transcripts", "session-1.jsonl"))


# The folder of `log` that each run of the case lies in, set by the fixture `folder`.
LOG = {"folder": ""}


@pytest.fixture(autouse=True)
def folder(log: str) -> None:
    LOG["folder"] = log


def run(*entries: Entry, opened: bool = True, rid: str = "r1", skill: str = "log:up") -> Run:
    """A run of the skill for 1.2.0, r1 unless given, with log's folder where it's opened, and the
    entries."""
    head: list[Entry] = [{"kind": "run", "run": rid, "skill": skill, "words": "1.2.0"}]
    root = LOG["folder"] if opened else None
    if root:
        head.append({"kind": "folder", "run": rid, "plugin_root": root})
    return Run(rid, "session-1", skill, "1.2.0", root, [*head, *entries])


PROMPT = "Write the entry."
START: Entry = lane_entries.start("u1", prompt=PROMPT)
TIE: Entry = lane_entries.tie("u1", "a1")
ENDED: Entry = {"kind": "ended", "run": "r1"}


def tied() -> Run:
    """A run of log:up whose writer is tied to a1."""
    return run(START, TIE)


def step_mark(step: str, agent_id: str | None = "a1", item: str | None = None) -> Entry:
    entry: Entry = {"kind": "mark", "run": "r1", "agent_id": agent_id, "step": step}
    if item:
        entry["item"] = item
    return entry


# The writer's `written` and the reviewer's `good`, after which log's routes start no more.
GOOD: tuple[Entry, ...] = (
    START,
    TIE,
    lane_entries.result("a1", "written"),
    lane_entries.start("u2", "log:reviewer"),
    lane_entries.tie("u2", "a2"),
    lane_entries.result("a2", "good", "log:reviewer"),
)
# The writer a1's `written`, and the reviewer's `more`, after which the writer is due again.
MORE: tuple[Entry, ...] = (*GOOD[:5], lane_entries.result("a2", "more", "log:reviewer"))


def main_move(kind: str, event: Event, on: Run, **fields: Any) -> Move:
    """The whole move of the main conversation on the run, of log:up at its step `lead` with no
    prompt or report unless the fields say otherwise."""
    held = Move(kind, event, on, "log:up", None, None, UP, "lead", None)
    return dataclasses.replace(held, **fields)


def writer_move(kind: str, event: Event, on: Run, **fields: Any) -> Move:
    """The whole move of the writer a1 on the run, at its step `write` with no prompt or report
    unless the fields say otherwise."""
    held = Move(kind, event, on, "log:writer", "a1", None, WRITES, "write", None)
    return dataclasses.replace(held, **fields)


def reported(capsys: pytest.CaptureFixture[str], kind: str, words: list[str]) -> str:
    """The line that a reporter of the kind prints for the words."""
    report(kind, words)
    return capsys.readouterr().out


# skill_call


@pytest.mark.supports("test_the_turns_end_while_the_commands_start_is_due_is_stopped_with_it")
def test_a_typed_command_calls_its_skill_with_the_words(e: Events):
    """Given the UserPromptExpansion of /log:up 1.2.0
    When Lane reads which skill it calls
    Then it's log:up, with the words 1.2.0, in the event's conversation"""
    called = skill_call(e.typed("log:up", "1.2.0"), [])
    assert called == SkillCall("session-1", e.transcript, "log:up", "1.2.0")


@pytest.mark.supports("test_a_run_added_by_the_skill_tool_takes_its_arguments_as_the_words")
def test_a_skill_tool_call_that_ran_calls_its_skill_with_its_args(e: Events):
    """Given the PostToolUse of the main conversation's Skill call of log:up with 1.2.0
    When Lane reads which skill it calls
    Then it's log:up, with the words 1.2.0"""
    assert skill_call(e.skill_post("log:up", "1.2.0"), []) == SkillCall(
        "session-1", e.transcript, "log:up", "1.2.0"
    )


@pytest.mark.supports("test_a_run_added_by_the_skill_tool_takes_its_arguments_as_the_words")
def test_a_skill_tool_call_with_no_args_calls_its_skill_with_no_words(e: Events):
    """Given the PostToolUse of the main conversation's Skill call of log:up with no args
    When Lane reads which skill it calls
    Then it's log:up, with no words"""
    given = e.skill_post("log:up", "")
    del given["tool_input"]["args"]
    assert skill_call(given, []) == SkillCall("session-1", e.transcript, "log:up", "")


@pytest.mark.supports("test_a_skill_called_by_the_skill_tool_adds_the_run")
def test_a_skill_tool_call_before_it_runs_calls_no_skill(e: Events):
    """Given the PreToolUse of a Skill call, which a hook may still deny
    When Lane reads which skill it calls
    Then it calls none yet"""
    assert skill_call(e.skill_pre("log:up", "1.2.0"), []) is None


@pytest.mark.supports("test_work_outside_a_run_of_a_plugin_with_rules_is_left_alone")
@pytest.mark.parametrize("by", ["typed", "skill_post"])
def test_a_skill_that_no_plugin_holds_calls_no_skill(e: Events, by: str):
    """Given the person's own skill `hi`, whose name has no plugin's prefix, typed or called by the
    Skill tool
    When Lane reads which skill it calls
    Then it calls none, as Lane checks only a plugin's skill"""
    given = e.typed("hi") if by == "typed" else e.skill_post("hi", "")
    assert skill_call(given, []) is None


@pytest.mark.supports("test_the_turns_end_while_the_commands_start_is_due_is_stopped_with_it")
def test_any_other_event_calls_no_skill(e: Events):
    """Given the main conversation's Stop
    When Lane reads which skill it calls
    Then it calls none"""
    assert skill_call(e.stop(), [run()]) is None


@pytest.mark.supports("test_another_skills_command_typed_while_a_subagent_runs_moves_the_run")
@pytest.mark.parametrize("by", ["typed", "skill_post"])
@pytest.mark.parametrize("opened", [True, False])
def test_a_command_of_the_plugin_whose_run_stands_calls_no_skill(e: Events, by: str, opened: bool):
    """Given a run of log:up, not ended, with log's folder or not yet
    When the UserPromptExpansion of /log:tag, or the PostToolUse of a Skill call of log:tag, comes
    Then it calls no skill, as the command is a move of the run"""
    given = e.typed("log:tag") if by == "typed" else e.skill_post("log:tag", "")
    assert skill_call(given, [run(opened=opened)]) is None


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
    called = skill_call(e.typed("log:up", "1.3.0"), [run(*GOOD, ENDED)])
    assert called == SkillCall("session-1", e.transcript, "log:up", "1.3.0")


@pytest.mark.supports("test_the_plugins_command_typed_again_once_its_run_ended_adds_a_new_run")
def test_a_command_of_the_plugin_with_an_ended_run_and_one_standing_calls_no_skill(e: Events):
    """Given a run r1 of log:up that ended, and a run r2 of log:up after it, not ended
    When the UserPromptExpansion of /log:up 1.3.0 comes
    Then it calls no skill, as r2 stands"""
    runs = [run(*GOOD, ENDED), run(rid="r2")]
    assert skill_call(e.typed("log:up", "1.3.0"), runs) is None


@pytest.mark.supports("test_each_plugins_run_is_held_to_the_rules_in_its_own_folder")
@pytest.mark.parametrize("other", ["memo:up", "logger:up", "lo:up"])
def test_a_command_beside_a_standing_run_of_another_plugin_calls_its_skill(e: Events, other: str):
    """Given a run of another plugin, not ended, among them one whose name begins as log's, or
    one that log's begins with
    When the UserPromptExpansion of /log:up 1.2.0 comes
    Then it calls log:up with 1.2.0"""
    called = skill_call(e.typed("log:up", "1.2.0"), [run(skill=other)])
    assert called == SkillCall("session-1", e.transcript, "log:up", "1.2.0")


# opening


@pytest.mark.supports(
    "test_the_starts_due_come_at_the_main_conversations_next_event_after_the_skills_call"
)
@pytest.mark.parametrize("event", ["bash", "bash_ran", "prompt", "stop"])
def test_the_main_conversations_next_event_opens_a_run_with_no_folder(e: Events, event: str):
    """Given a run of log:up with no folder
    When the main conversation's next event comes: the PreToolUse or PostToolUse of a Bash call,
    the person's prompt, or its Stop
    Then that run opens"""
    given = {
        "bash": e.bash("git status"),
        "bash_ran": e.bash_ran("git status", "clean"),
        "prompt": e.prompt("Go on."),
        "stop": e.stop(),
    }[event]
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


@pytest.mark.supports("test_the_plugins_command_typed_again_once_its_run_ended_adds_a_new_run")
def test_only_the_runs_with_no_folder_open(e: Events):
    """Given a run r1 of log:up with its folder, that ended, and a run r2 after it with no folder
    When the main conversation's Stop comes
    Then r2 alone opens"""
    unopened = run(opened=False, rid="r2")
    assert opening(e.stop(), [run(*GOOD, ENDED), unopened]) == [unopened]


@pytest.mark.supports(
    "test_the_starts_due_come_at_the_main_conversations_next_event_after_the_skills_call"
)
def test_a_subagents_event_opens_no_run(e: Events):
    """Given a run of log:up with no folder
    When a subagent's Bash call comes
    Then no run opens, as the transcript is the main conversation's"""
    assert opening(e.bash("git log", WRITER), [run(opened=False)]) == []


# place: outside each run.


@pytest.mark.supports("test_another_conversation_in_the_repository_is_held_to_no_run_of_the_first")
def test_an_event_of_a_conversation_with_no_run_lies_outside(e: Events):
    """Given a conversation with no run
    When the main conversation writes a file
    Then the event lies outside each run"""
    assert place(e.write("/repo/notes.txt"), [], by_routes) is None


@pytest.mark.supports(
    "test_the_starts_due_come_at_the_main_conversations_next_event_after_the_skills_call"
)
def test_an_event_of_a_run_with_no_folder_yet_lies_outside(e: Events):
    """Given a run of log:up with no folder yet
    When the main conversation writes a file
    Then the event lies outside each run, as Lane can't read its rules yet"""
    assert place(e.write("/repo/notes.txt"), [run(opened=False)], by_routes) is None


@pytest.mark.supports("test_work_outside_a_run_of_a_plugin_with_rules_is_left_alone")
def test_an_event_of_a_run_whose_plugin_gives_no_rules_lies_outside(e: Events, log: str):
    """Given a run of log:up whose plugin has no lane/rules.json
    When the main conversation writes a file
    Then the event lies outside each run"""
    os.remove(os.path.join(log, "lane", "rules.json"))
    assert place(e.write("/repo/notes.txt"), [run()], by_routes) is None


# place: the main conversation.


@pytest.mark.supports("test_the_main_conversations_write_in_a_run_is_held_to_its_skills_step")
def test_the_main_conversations_call_is_a_call_of_the_skills_role(e: Events):
    """Given a run of log:up
    When the main conversation writes a file
    Then the move is a call on that run, of the role log:up and its steps, with no agent, at the
    step `lead`"""
    given, on = e.write("/repo/notes.txt"), run()
    assert place(given, [on], by_routes) == main_move("call", given, on)


@pytest.mark.supports("test_the_plugins_command_typed_again_once_its_run_ended_adds_a_new_run")
@pytest.mark.parametrize("ended", [0, 1])
def test_the_main_conversations_call_lies_on_the_latest_run_not_ended(e: Events, ended: int):
    """Given two runs of log:up, r1 and r2, of which r1 ended, or r2 ended
    When the main conversation writes a file
    Then the move lies on the other"""
    runs = [run(rid="r1"), run(rid="r2")]
    runs[ended].entries.append({"kind": "ended", "run": runs[ended].id})
    given = e.write("/repo/notes.txt")
    assert place(given, runs, by_routes) == main_move("call", given, runs[1 - ended])


@pytest.mark.supports("test_the_main_conversations_write_in_a_run_is_held_to_its_skills_step")
def test_the_main_conversations_call_after_its_step_is_marked_is_at_no_step(e: Events):
    """Given a run of log:up whose main conversation marked `lead`, its one step
    When it writes a file
    Then the move is a call at no step"""
    given, on = e.write("/repo/notes.txt"), run(step_mark("lead", None))
    assert place(given, [on], by_routes) == main_move("call", given, on, step=None)


@pytest.mark.supports("test_the_main_conversation_holds_to_the_steps_of_the_latest_commands_skill")
@pytest.mark.parametrize(
    "commands, role, steps",
    [
        (("log:tag",), "log:tag", TAG),
        (("log:retry",), "log:up", UP),
        (("log:tag", "log:retry"), "log:tag", TAG),
        (("log:retry", "log:tag"), "log:tag", TAG),
        (("log:tag", "log:up"), "log:up", UP),
    ],
)
def test_the_main_conversations_call_after_commands_holds_to_the_latest_skill_with_steps(
    e: Events, commands: tuple[str, ...], role: str, steps: list[Step]
):
    """Given a run of log:up in log's folder, and typed in it /log:tag, whose skill the rules give
    steps of; /log:retry, whose skill they give none of; /log:tag then /log:retry; /log:retry then
    /log:tag; or /log:tag then /log:up
    When the main conversation writes a file
    Then the move is a call of the role log:tag, log:up, log:tag, log:tag, or log:up, held to its
    steps, at the step `lead`"""
    typed: list[Entry] = [{"kind": "typed", "run": "r1", "command": each} for each in commands]
    given, on = e.write("/repo/notes.txt"), run(*typed)
    assert place(given, [on], by_routes) == main_move("call", given, on, role=role, steps=steps)


@pytest.mark.supports("test_the_turns_end_while_the_commands_start_is_due_is_stopped_with_it")
def test_the_main_conversations_stop_is_the_end_of_its_turn(e: Events):
    """Given a run of log:up
    When the main conversation's Stop comes
    Then the move is the end of the turn, at the step `lead`"""
    given, on = e.stop(), run()
    assert place(given, [on], by_routes) == main_move("turn_end", given, on)


@pytest.mark.supports("test_a_typed_command_that_a_route_goes_after_puts_its_starts_in_place")
def test_a_typed_command_that_a_route_waits_for_is_typed(e: Events):
    """Given a run of log:up in log's folder, not ended
    When the UserPromptExpansion of /log:retry comes
    Then the move is a typed command on that run, of the main conversation at the step `lead`"""
    given, on = e.typed("log:retry"), run()
    assert place(given, [on], by_routes) == main_move("typed", given, on)


@pytest.mark.supports("test_another_skills_command_typed_while_a_subagent_runs_moves_the_run")
def test_a_skill_tool_call_of_the_plugins_skill_while_its_run_stands_is_typed(e: Events):
    """Given a run of log:up in log's folder whose writer is tied to a1
    When the PostToolUse of the main conversation's Skill call of log:tag comes
    Then the move is a typed command on that run"""
    given, on = e.skill_post("log:tag", ""), tied()
    assert place(given, [on], by_routes) == main_move("typed", given, on)


@pytest.mark.supports("test_each_plugins_run_is_held_to_the_rules_in_its_own_folder")
@pytest.mark.parametrize("skill", ["memo:tag", "logger:tag"])
def test_a_command_of_a_plugin_with_no_run_lies_outside(e: Events, skill: str):
    """Given a run of log:up, not ended
    When the UserPromptExpansion of a command of another plugin comes, one whose name begins as
    log's among them
    Then it lies outside each run"""
    assert place(e.typed(skill), [run()], by_routes) is None


@pytest.mark.supports("test_rules_out_of_form_stop_the_call_saying_what_the_author_mends")
def test_a_command_of_a_run_whose_rules_are_out_of_form_is_refused(e: Events, log: str):
    """Given a run of log:up whose plugin's lane/rules.json now lacks its roles
    When the UserPromptExpansion of /log:retry comes
    Then Lane refuses with OutOfForm"""
    write_files(log, {"lane/rules.json": "{}"})
    with pytest.raises(OutOfForm):
        place(e.typed("log:retry"), [run()], by_routes)


# place: a start, its tie, and its drop.


@pytest.mark.supports("test_the_order_tells_the_starts_of_one_role_apart_by_their_prompts")
def test_the_main_conversations_agent_call_is_a_start_with_its_prompt(e: Events):
    """Given a run of log:up
    When the main conversation starts the writer by the Agent tool with a prompt
    Then the move is a start of the main conversation, at no step, with that prompt"""
    given, on = e.start("log:writer", "u1", prompt="Write docs/changes/."), run()
    expected = main_move("start", given, on, step=None, prompt="Write docs/changes/.")
    assert place(given, [on], by_routes) == expected


@pytest.mark.supports("test_a_subagents_start_of_a_subagent_is_stopped")
def test_a_subagents_agent_call_is_a_start_by_it(e: Events):
    """Given a run of log:up whose writer is tied to a1
    When a1 starts a writer by the Agent tool
    Then the move is a start by a1, of its role, at no step, with its prompt"""
    given, on = e.start("log:writer", "u2", WRITER), tied()
    expected = writer_move("start", given, on, step=None, prompt="You are log:writer.")
    assert place(given, [on], by_routes) == expected


@pytest.mark.supports("test_the_start_due_goes_through_and_leaves_none_due")
def test_an_agent_call_with_no_prompt_is_a_start_with_none(e: Events):
    """Given a run of log:up
    When the main conversation starts the writer by the Agent tool with no prompt
    Then the move is a start with an empty prompt"""
    given, on = e.start("log:writer", "u1"), run()
    del given["tool_input"]["prompt"]
    assert place(given, [on], by_routes) == main_move("start", given, on, step=None, prompt="")


@pytest.mark.supports("test_the_start_due_goes_through_and_leaves_none_due")
def test_the_post_tool_use_of_a_starts_agent_call_ties_it(e: Events):
    """Given a run of log:up with the writer's start of u1, untied
    When the PostToolUse of u1 names the subagent a1
    Then the move is a tie of a1 to that start, of the writer's role and steps, at no step"""
    given, on = e.started(WRITER, "u1"), run(START)
    assert place(given, [on], by_routes) == writer_move("tie", given, on, step=None)


@pytest.mark.supports("test_a_start_of_a_subagent_that_isnt_the_plugins_lies_outside_the_run")
def test_the_post_tool_use_of_an_agent_call_that_made_no_start_is_no_move(e: Events):
    """Given a run of log:up with the writer's start of u1
    When the PostToolUse of another Agent call, u9, which made no start, names a9
    Then it makes no move"""
    given = e.started(Subagent("a9", "general-purpose"), "u9")
    assert place(given, [run(START)], by_routes) is None


@pytest.mark.supports("test_an_agent_call_that_fails_after_its_pre_tool_use_leaves_its_start_due")
def test_the_failure_of_a_starts_agent_call_drops_it(e: Events):
    """Given a run of log:up with the writer's start of u1, untied
    When the PostToolUseFailure of u1 comes
    Then the move is a drop by the main conversation"""
    given, on = e.start_failed("log:writer", "u1"), run(START)
    assert place(given, [on], by_routes) == main_move("drop", given, on)


@pytest.mark.supports("test_an_agent_call_that_fails_after_its_pre_tool_use_leaves_its_start_due")
def test_the_failure_of_a_call_that_made_no_start_is_no_move(e: Events):
    """Given a run of log:up with the writer's start of u1, untied
    When the PostToolUseFailure of another call, u9, comes
    Then it makes no move"""
    assert place(e.start_failed("log:writer", "u9"), [run(START)], by_routes) is None


# place: a subagent's moves.


@pytest.mark.supports("test_a_write_of_a_file_that_its_step_doesnt_name_is_stopped_with_the_step")
def test_a_tied_subagents_call_is_a_call_of_its_role_at_its_first_step(e: Events):
    """Given the writer tied to a1, no step marked
    When a1 writes a file
    Then the move is a call of the role log:writer, by a1, held to its steps, at the step `write`"""
    given, on = e.write("/repo/notes.txt", WRITER), tied()
    assert place(given, [on], by_routes) == writer_move("call", given, on)


@pytest.mark.supports("test_steps_marked_in_their_order_hold_and_the_end_goes_through")
@pytest.mark.parametrize(
    "marks, step",
    [
        ((step_mark("write"),), "report"),
        ((step_mark("write"), step_mark("report")), None),
        ((step_mark("report"),), "write"),
        ((step_mark("write", None), step_mark("write", "a2")), "write"),
        ((step_mark("write", item="dated"),), "write"),
    ],
)
def test_a_subagents_call_is_at_the_first_step_it_hasnt_marked(
    e: Events, marks: tuple[Entry, ...], step: str | None
):
    """Given the writer tied to a1, which marked `write`; both steps; `report` alone; none, while
    the main conversation and a2 marked `write`; or an item of `write` alone
    When a1 runs a command
    Then the move is at the step `report`, at none, at `write`, at `write`, or at `write`"""
    given, on = e.bash("git log", WRITER), run(START, TIE, *marks)
    assert place(given, [on], by_routes) == writer_move("call", given, on, step=step)


@pytest.mark.supports("test_a_read_of_a_file_under_a_folder_never_to_read_is_stopped_with_the_step")
@pytest.mark.parametrize("tool", ["Grep", "Glob"])
@pytest.mark.parametrize("path", ["secrets", "secrets-old", None])
def test_a_subagents_grep_or_glob_is_a_call_at_its_step(e: Events, tool: str, path: str | None):
    """Given the writer tied to a1, at its step `write`
    When a1 greps or globs in secrets/, in secrets-old/, or with no path, each path relative as
    Claude Code gives it
    Then the move is a call by a1 at the step `write`, for its rules to judge"""
    given = e.search(tool, path, WRITER)
    on = tied()
    assert place(given, [on], by_routes) == writer_move("call", given, on)


@pytest.mark.supports("test_a_read_of_another_file_goes_through")
@pytest.mark.parametrize("tool", ["Grep", "Glob"])
def test_the_post_tool_use_of_a_grep_or_a_glob_is_no_move(e: Events, tool: str):
    """Given the writer tied to a1
    When the PostToolUse of a1's Grep or Glob comes
    Then it makes no move, as only a Read's lines count toward a file read whole"""
    given = e.search_ran(tool, None, ["NOTES.md"], WRITER)
    assert place(given, [tied()], by_routes) is None


@pytest.mark.supports("test_a_read_whole_holds_the_mark")
@pytest.mark.parametrize("name", ["NOTES.md", "CHANGELOG.md"])
def test_the_post_tool_use_of_a_subagents_read_of_a_file_to_read_whole_is_a_read(
    e: Events, name: str
):
    """Given the writer tied to a1, at its step `write`
    When the PostToolUse of a1's Read of NOTES.md, which `write` reads whole, or of CHANGELOG.md,
    which the later step `report` reads whole, comes
    Then the move is a read by a1, at the step `write`"""
    given, on = e.read_ran(os.path.join(e.cwd, name), 1, 6, 6, WRITER), tied()
    assert place(given, [on], by_routes) == writer_move("read", given, on)


@pytest.mark.supports("test_a_read_of_another_file_goes_through")
def test_the_post_tool_use_of_a_read_of_a_file_that_no_step_reads_whole_is_no_move(e: Events):
    """Given the writer tied to a1
    When the PostToolUse of a1's Read of README.md comes
    Then it makes no move"""
    given = e.read_ran(os.path.join(e.cwd, "README.md"), 1, 2, 2, WRITER)
    assert place(given, [tied()], by_routes) is None


@pytest.mark.supports("test_a_read_of_the_main_conversation_counts_for_no_subagent")
def test_the_post_tool_use_of_the_main_conversations_read_is_held_to_its_own_steps(e: Events):
    """Given the writer tied to a1, whose step reads NOTES.md whole, and the main conversation,
    whose steps read no file whole
    When the PostToolUse of the main conversation's Read of NOTES.md comes
    Then it makes no move"""
    given = e.read_ran(os.path.join(e.cwd, "NOTES.md"), 1, 6, 6, WRITER)
    for key in ("agent_id", "agent_type"):
        del given[key]
    assert place(given, [tied()], by_routes) is None


@pytest.mark.supports("test_a_reporters_result_counts_for_the_subagent_that_ran_it")
def test_a_reporters_bash_call_is_a_report_with_what_it_printed(
    e: Events, capsys: pytest.CaptureFixture[str]
):
    """Given the writer tied to a1
    When the PostToolUse of a1's `lane-result written` comes, with the line the reporter printed
    Then the move is a report of the result `written`, by a1, at the step `write`"""
    printed = reported(capsys, "result", ["written"])
    given, on = e.bash_ran("lane-result written", printed, WRITER), tied()
    expected = writer_move("report", given, on, report={"kind": "result", "result": "written"})
    assert place(given, [on], by_routes) == expected


@pytest.mark.supports("test_the_main_conversations_command_in_a_run_is_held_to_its_skills_step")
def test_the_main_conversations_reporter_is_a_report_by_it(
    e: Events, capsys: pytest.CaptureFixture[str]
):
    """Given a run of log:up
    When the PostToolUse of the main conversation's `lane-step lead` comes
    Then the move is a report of the step `lead`, by the main conversation"""
    printed = reported(capsys, "step", ["lead"])
    given, on = e.bash_ran("lane-step lead", printed), run()
    expected = dataclasses.replace(
        main_move("report", given, on), report={"kind": "step", "step": "lead"}
    )
    assert place(given, [on], by_routes) == expected


@pytest.mark.supports("test_a_command_that_its_step_names_goes_through")
def test_the_post_tool_use_of_another_command_is_no_move(e: Events):
    """Given the writer tied to a1
    When the PostToolUse of a1's `git log` comes
    Then it makes no move"""
    assert place(e.bash_ran("git log", "bf742e7 first", WRITER), [tied()], by_routes) is None


@pytest.mark.supports("test_an_end_with_no_result_is_stopped_with_the_results_it_may_give")
def test_a_tied_subagents_stop_is_its_end(e: Events):
    """Given the writer tied to a1
    When a1's SubagentStop comes
    Then the move is the end of a1's start, at the step `write`"""
    given, on = e.ended(WRITER), tied()
    assert place(given, [on], by_routes) == writer_move("end", given, on)


@pytest.mark.supports(
    "test_a_message_queued_to_a_running_subagent_goes_through_and_its_later_pass_is_its_same_start"
)
def test_the_stop_of_a_later_pass_after_a_queued_message_ends_the_same_start(e: Events):
    """Given the writer tied to a1 by u1, which marked `write` before a message queued to it
    started it again
    When a1's SubagentStop of the later pass comes
    Then the move is the end of the start of u1, at the step `report`, its marks as they stand"""
    given, on = e.ended(WRITER), run(START, TIE, step_mark("write"))
    assert place(given, [on], by_routes) == writer_move("end", given, on, step="report")


@pytest.mark.supports("test_after_compact_the_run_goes_on_with_its_starts_due")
def test_the_summarys_end_at_compact_lies_outside(e: Events):
    """Given the writer tied to a1
    When the SubagentStop of /compact's summary comes, with an agent that no start ties
    Then it lies outside each run"""
    assert place(e.summary_ended("a9"), [tied()], by_routes) is None


@pytest.mark.supports("test_a_subagent_started_in_the_foreground_lies_outside_the_run")
@pytest.mark.parametrize("agent", ["a1", "a10"])
def test_a_call_of_a_subagent_that_no_start_ties_lies_outside(e: Events, agent: str):
    """Given the writer's start, untied, and a1 tied to it or not
    When a subagent that no start ties writes a file: a1 while it's untied, or a10, whose ID
    begins as a1's, while a1 is tied
    Then it lies outside each run"""
    on = run(START) if agent == "a1" else tied()
    given = e.write("/repo/notes.txt", Subagent(agent, "log:writer"))
    assert place(given, [on], by_routes) is None


@pytest.mark.supports("test_each_plugins_run_is_held_to_the_rules_in_its_own_folder")
def test_a_subagents_call_is_placed_on_the_run_of_its_start(e: Events):
    """Given a run r1 of log:up whose writer is tied to a1, and a run r2 of memo:up after it
    When a1 writes a file
    Then the move lies on r1"""
    memo = Run("r2", "session-1", "memo:up", "", "/plugins/memo", [])
    given, on = e.write("/repo/notes.txt", WRITER), tied()
    assert place(given, [on, memo], by_routes) == writer_move("call", given, on)


@pytest.mark.supports(
    "test_a_role_with_no_fixed_steps_takes_them_from_the_plugins_adapter_for_each_start"
)
def test_a_call_of_a_start_with_steps_given_is_held_to_them(e: Events, log: str):
    """Given rules that name the writer with no steps, and the writer tied to a1, whose start holds
    the step `draft` that the plugin's adapter of the rules gave
    When a1 writes a file
    Then the move is held to the step `draft`, at that step"""
    write_files(log, {"lane/rules.json": json.dumps(lane_bench.ADAPTED)})
    given_steps: list[Step] = [{"name": "draft", "rules": [{"type": "writes", "paths": ["docs/"]}]}]
    given, on = e.write("/repo/notes.txt", WRITER), run({**START, "steps": given_steps}, TIE)
    expected = Move("call", given, on, "log:writer", "a1", None, given_steps, "draft", None)
    assert place(given, [on], by_routes) == expected


# place: a result reaching the main conversation.


@pytest.mark.supports("test_a_result_reaching_the_main_conversation_gives_the_starts_due_after_it")
@pytest.mark.parametrize("killed", [False, True])
def test_a_task_notification_of_a_tied_subagent_is_its_result_reaching(e: Events, killed: bool):
    """Given the writer tied to a1 by the Agent call u1
    When a1's task-notification reaches the main conversation, of its end or of its stop by
    TaskStop
    Then the move is its result reaching, by a1, of its role, at its step"""
    given = e.killed(WRITER, "u1") if killed else e.reached(WRITER, "u1")
    on = tied()
    assert place(given, [on], by_routes) == writer_move("result_reached", given, on)


@pytest.mark.supports("test_a_result_said_only_in_the_reply_counts_for_nothing")
@pytest.mark.parametrize("agent", ["a9", "a10"])
def test_a_task_notification_of_a_subagent_that_no_start_ties_is_no_move(e: Events, agent: str):
    """Given the writer tied to a1
    When the task-notification of a9, or of a10, whose ID begins as a1's, reaches the main
    conversation
    Then it makes no move"""
    given = e.reached(Subagent(agent, "log:writer"), "u1")
    assert place(given, [tied()], by_routes) is None


@pytest.mark.supports("test_a_result_said_only_in_the_reply_counts_for_nothing")
def test_a_prompt_with_no_task_notification_is_no_move(e: Events):
    """Given the writer tied to a1
    When the person types a prompt that names a1
    Then it makes no move"""
    assert place(e.prompt("Did a1 finish?"), [tied()], by_routes) is None


# place: a SendMessage.


@pytest.mark.supports("test_a_resume_that_the_order_makes_due_goes_through_as_its_start")
def test_a_send_message_to_an_ended_subagent_whose_role_is_due_is_a_start(e: Events):
    """Given the writer a1, whose end came with `written`, and the reviewer's `more`, so that the
    writer is due
    When the main conversation's PreToolUse of SendMessage to a1 comes
    Then the move is a start by the main conversation, at no step, with the role, the prompt, not
    the message, and the steps of a1's start"""
    given, on = e.send(WRITER, "u3"), run(*MORE)
    expected = Move("start", given, on, "log:writer", None, PROMPT, WRITES, None, None)
    assert place(given, [on], by_routes) == expected


@pytest.mark.supports(
    "test_a_role_with_no_fixed_steps_takes_them_from_the_plugins_adapter_for_each_start"
)
def test_a_resume_of_a_start_with_steps_given_carries_those_steps(e: Events, log: str):
    """Given rules that name the writer with no steps, the writer a1, whose start holds the step
    `draft` that the plugin's adapter of the rules gave and whose end came with `written`, and the
    reviewer's `more`, so that the writer is due
    When the main conversation's PreToolUse of SendMessage to a1 comes
    Then the move is a start with the writer's role, a1's prompt, and the step `draft`"""
    write_files(log, {"lane/rules.json": json.dumps(lane_bench.ADAPTED)})
    drafted: list[Step] = [{"name": "draft", "rules": [{"type": "writes", "paths": ["docs/"]}]}]
    given = e.send(WRITER, "u3")
    on = run({**START, "steps": drafted}, *MORE[1:])
    expected = Move("start", given, on, "log:writer", None, PROMPT, drafted, None, None)
    assert place(given, [on], by_routes) == expected


@pytest.mark.supports("test_a_subagent_stopped_by_task_stop_is_due_again")
def test_a_send_message_to_a_subagent_stopped_whose_role_is_due_again_is_a_start(e: Events):
    """Given the writer a1, which TaskStop stopped with no result, so that the writer is due again
    When the main conversation's PreToolUse of SendMessage to a1 comes
    Then the move is a start with the role, the prompt, and the steps of a1's start"""
    stopped: Entry = {"kind": "stopped", "run": "r1", "agent_id": "a1"}
    given, on = e.send(WRITER, "u2"), run(START, TIE, stopped)
    expected = Move("start", given, on, "log:writer", None, PROMPT, WRITES, None, None)
    assert place(given, [on], by_routes) == expected


@pytest.mark.supports("test_a_resume_that_the_order_doesnt_make_due_goes_through_as_talk")
def test_a_send_message_to_an_ended_subagent_whose_role_isnt_due_is_talk(e: Events):
    """Given the writer a1, whose end came with `written`, so that the reviewer is due
    When the main conversation's PreToolUse of SendMessage to a1 comes
    Then it makes no move"""
    on = run(START, TIE, lane_entries.result("a1", "written"))
    assert place(e.send(WRITER, "u2"), [on], by_routes) is None


@pytest.mark.supports(
    "test_a_message_queued_to_a_running_subagent_goes_through_and_its_later_pass_is_its_same_start"
)
def test_a_send_message_to_a_running_subagent_whose_role_is_due_is_talk(e: Events):
    """Given the reviewer's `split`, which makes two writers due, and the writer a3 running as the
    first of them, so that one writer is still due
    When the main conversation's PreToolUse of SendMessage to a3 comes
    Then it makes no move, as Claude Code queues the message to the start that runs"""
    running = (
        *MORE[:5],
        lane_entries.result("a2", "split", "log:reviewer"),
        lane_entries.start("u3"),
        lane_entries.tie("u3", "a3"),
    )
    third = Subagent("a3", "log:writer")
    assert place(e.send(third, "u4"), [run(*running)], by_routes) is None


@pytest.mark.supports("test_a_start_whose_subagent_start_comes_after_its_post_tool_use_is_held")
def test_a_send_message_to_a_resumed_subagent_that_runs_again_is_talk(e: Events):
    """Given the writer a1's `written`, the reviewer's `split`, which makes two writers due, and a1
    resumed by u3 and tied to it again, running, so that one writer is still due
    When the main conversation's PreToolUse of SendMessage to a1 comes
    Then it makes no move, as a1's latest start has no result yet"""
    resumed = (
        *MORE[:5],
        lane_entries.result("a2", "split", "log:reviewer"),
        lane_entries.start("u3", prompt=PROMPT),
        lane_entries.tie("u3", "a1"),
    )
    assert place(e.send(WRITER, "u4"), [run(*resumed)], by_routes) is None


@pytest.mark.supports("test_a_subagents_message_to_another_subagent_goes_through_as_talk")
@pytest.mark.parametrize("by, to", [(Subagent("a2", "log:reviewer"), "a1"), (None, "a9")])
def test_a_send_message_by_a_subagent_or_to_one_with_no_start_is_talk(
    e: Events, by: Subagent | None, to: str
):
    """Given the writer a1, whose end came with `written`, and the reviewer's `more`, so that the
    writer is due
    When the reviewer a2 sends a1 a message, or the main conversation sends a9, which no start
    ties, one
    Then it makes no move"""
    given = e.send(Subagent(to, "log:writer"), "u3", by)
    assert place(given, [run(*MORE)], by_routes) is None


@pytest.mark.supports("test_a_resume_that_the_order_makes_due_goes_through_as_its_start")
def test_a_send_message_that_resumed_its_subagent_ties_it(e: Events):
    """Given the writer tied to a1, and a start by SendMessage u2 to it
    When the PostToolUse of u2 says it resumed a1
    Then the move is a tie of a1, of the writer's role and steps, at no step"""
    resume: Entry = lane_entries.start("u2")
    given, on = e.resumed(WRITER, "u2"), run(START, TIE, resume)
    assert place(given, [on], by_routes) == writer_move("tie", given, on, step=None)


@pytest.mark.supports("test_a_resume_that_the_order_makes_due_goes_through_as_its_start")
def test_a_send_message_that_resumed_its_subagent_ties_it_to_that_subagent(e: Events):
    """Given the writer tied to a1, and a start by SendMessage u2 to it
    When the PostToolUse of u2 says it resumed a1
    Then the move is a tie of a1, on the run, of the call u2, with no prompt or report"""
    resume: Entry = lane_entries.start("u2")
    given, on = e.resumed(WRITER, "u2"), run(START, TIE, resume)
    move = place(given, [on], by_routes)
    assert move is not None
    assert (move.kind, move.event, move.run, move.agent_id, move.prompt, move.report) == (
        "tie",
        given,
        on,
        "a1",
        None,
        None,
    )


@pytest.mark.supports(
    "test_a_message_queued_to_a_running_subagent_goes_through_and_its_later_pass_is_its_same_start"
)
def test_the_post_tool_use_of_a_send_message_queued_to_a_running_subagent_is_no_move(e: Events):
    """Given the writer tied to a1, running, to which the main conversation's SendMessage u2 went
    through as talk
    When the PostToolUse of u2 says the message is queued
    Then it makes no move"""
    assert place(e.queued(WRITER, "u2"), [tied()], by_routes) is None


# command_of, marked, and latest_start


@pytest.mark.supports("test_a_skill_called_by_the_skill_tool_adds_the_run")
@pytest.mark.parametrize(
    "event, skill",
    [
        ("typed", "log:tag"),
        ("skill_post", "log:tag"),
        ("skill_pre", None),
        ("typed_own", None),
        ("stop", None),
    ],
)
def test_a_command_names_its_plugins_skill(e: Events, event: str, skill: str | None):
    """Given the UserPromptExpansion of /log:tag, the PostToolUse or PreToolUse of a Skill call of
    log:tag, the UserPromptExpansion of the person's own /hi, or a Stop
    When Lane reads the skill that the command names
    Then it's log:tag, log:tag, none, none, or none"""
    given = {
        "typed": lambda: e.typed("log:tag"),
        "skill_post": lambda: e.skill_post("log:tag", ""),
        "skill_pre": lambda: e.skill_pre("log:tag", ""),
        "typed_own": lambda: e.typed("hi"),
        "stop": e.stop,
    }[event]()
    assert command_of(given) == skill


@pytest.mark.supports("test_a_read_of_the_main_conversation_counts_for_no_subagent")
def test_the_steps_a_start_marked_are_its_own_marks_of_steps(e: Events):
    """Given a run holding a1's marks of `write` and of the item `dated` of `report`, a2's mark of
    `report`, and the main conversation's mark of `lead`
    When Lane reads the steps that a1, a2, and the main conversation marked
    Then they are `write`, `report`, and `lead`"""
    on = run(
        step_mark("write"),
        step_mark("report", item="dated"),
        step_mark("report", "a2"),
        step_mark("lead", None),
    )
    assert (marked(on, "a1"), marked(on, "a2"), marked(on, None)) == (
        {"write"},
        {"report"},
        {"lead"},
    )


@pytest.mark.supports("test_a_resume_that_the_order_makes_due_goes_through_as_its_start")
def test_the_latest_start_of_a_subagent_is_that_of_its_latest_tie(e: Events):
    """Given the writer a1 started by u1 and resumed by u3, tied to each in turn, and a2 started by
    u2 between them
    When Lane reads the latest start of a1, of a2, and of a9, which no start ties
    Then they are the start of u3, of u2, and none"""
    second: Entry = lane_entries.start("u2", prompt="Write the second.")
    resume: Entry = lane_entries.start("u3", prompt=PROMPT)
    on = run(START, TIE, second, lane_entries.tie("u2", "a2"), resume, lane_entries.tie("u3", "a1"))
    assert (latest_start(on, "a1"), latest_start(on, "a2"), latest_start(on, "a9")) == (
        resume,
        second,
        None,
    )
