"""The unit cases of hooks/lane/guard.py: answer, one for each transition of a run that Lane's list
of Claude Code's states brings about, each event given to the guard as Claude Code sends it, from
the skill's call to the end of the routes, the run record kept in the case's temporary folder;
each interface below it, one for each class of the move it takes; and written, one for each event
and class of answer."""

from __future__ import annotations

import copy
import json
import os
from typing import Any

import lane_bench
import lane_entries
import pytest
from guard import (
    Answer,
    answer,
    call_made,
    command_typed,
    fact_added,
    report_made,
    result_reached,
    run_opened,
    skill_called,
    start_made,
    subagent_ended,
    turn_ended,
    written,
)
from lane_events import Event, Events, Subagent, base_directory
from place import Move, SkillCall
from record import Entry, add, runs
from repo_files import write_files
from report import read_report, report
from rules import Step

UNBUILT = pytest.mark.xfail(strict=True, reason="Lane's parts have no bodies yet")

# An adapter of the starts due that gives none, as it waits for the person's answer.
WAITS = 'import json\n\nprint(json.dumps({"starts": []}))\n'
# The rules of `log` giving no order: the main conversation's step `lead` alone, checked for
# .log/up.md.
UP_SAYS = ".log/up.md is missing"
NO_ORDER: Any = {"roles": {"log:up": copy.deepcopy(lane_bench.RULES["roles"]["log:up"])}}
NO_ORDER["roles"]["log:up"]["steps"][0]["rules"].append(
    {"type": "check", "check": f"test -f .log/up.md || {{ echo '{UP_SAYS}'; exit 1; }}"}
)


class Play:
    """The events of one conversation given to the guard in turn, with `log` in its folder."""

    def __init__(self, cwd: str, log: str, capsys: pytest.CaptureFixture[str], session: str):
        transcript = os.path.join(os.path.dirname(cwd), "transcripts", f"{session}.jsonl")
        self.e = Events(cwd, transcript, session)
        self.log = log
        self.capsys = capsys
        self.uses = 0

    def __call__(self, event: Event) -> Answer:
        return answer(event)

    def opened(self, words: str = "1.2.0") -> Answer:
        """The person types /log:up with the words, the skill expands, and the main conversation
        runs `git status`; gives the guard's answer to that call."""
        self(self.e.typed("log:up", words))
        base_directory(self.e.transcript, self.log, "up")
        return self(self.e.bash("git status"))

    def use(self) -> str:
        self.uses += 1
        return f"toolu_{self.uses}"

    def started(self, role: str = "log:writer", agent_id: str = "a1") -> Subagent:
        """The main conversation starts the role, and its Agent call names the subagent."""
        use = self.use()
        self(self.e.start(role, use))
        agent = Subagent(agent_id, role)
        self(self.e.started(agent, use))
        return agent

    def reported(self, agent: Subagent, kind: str, *words: str) -> Answer:
        """The agent runs the reporter of the kind with the words; gives the guard's answer to the
        PostToolUse with the line the reporter printed."""
        command = f"lane-{kind} {' '.join(words)}"
        self(self.e.bash(command, agent))
        report(kind, list(words))
        return self(self.e.bash_ran(command, self.capsys.readouterr().out, agent))

    def kept_steps(self, agent: Subagent, result: str = "written") -> None:
        """The writer keeps each step, as lane_bench.written plays it."""
        cwd = self.e.cwd
        self(self.e.write(os.path.join(cwd, "CHANGELOG.md"), agent))
        self(self.e.read_ran(os.path.join(cwd, "NOTES.md"), 1, 6, 6, agent))
        self.reported(agent, "item", "write", "dated")
        self.reported(agent, "item", "write", "linked")
        self.reported(agent, "step", "write")
        self(self.e.read_ran(os.path.join(cwd, "CHANGELOG.md"), 1, 6, 6, agent))
        self.reported(agent, "result", result)
        self.reported(agent, "step", "report")

    def ended(self, agent: Subagent, use: str = "toolu_1") -> Answer:
        """The agent ends; gives the guard's answer to its task-notification once its end holds,
        else to its SubagentStop."""
        stopped = self(self.e.ended(agent))
        return stopped if stopped.stop else self(self.e.reached(agent, use))

    def to_review(self) -> Subagent:
        """The writer a1 started, kept each step, and ended, so the reviewer is due."""
        self.opened()
        writer = self.started()
        self.kept_steps(writer)
        self.ended(writer)
        return writer


@pytest.fixture
def g(cwd: str, log: str, capsys: pytest.CaptureFixture[str]) -> Play:
    return Play(cwd, log, capsys, "session-1")


# answer, by each transition.


@pytest.mark.supports(
    "test_the_starts_due_come_at_the_main_conversations_next_event_after_the_skills_call"
)
def test_a_skills_call_adds_a_run_with_no_folder_and_answers_nothing(g: Play):
    """Given a conversation with no run
    When the person's /log:up 1.2.0 expands
    Then the guard answers nothing, and the record holds a run of log:up for 1.2.0 with no
    folder"""
    assert answer(g.e.typed("log:up", "1.2.0")) == Answer()
    [run] = runs("session-1")
    assert (run.skill, run.words, run.plugin_root) == ("log:up", "1.2.0", None)


@pytest.mark.supports(
    "test_the_starts_due_come_at_the_main_conversations_next_event_after_the_skills_call"
)
def test_the_next_event_with_the_base_directory_gives_the_folder_and_the_starts_due(g: Play):
    """Given a run of log:up with no folder, and the transcript holding its base directory
    When the main conversation runs `git status`
    Then the guard lets it through with the writer due and its text, and the run has its folder"""
    said = g.opened()
    assert not said.stop
    assert "log:writer" in said.said
    assert runs("session-1")[0].plugin_root == g.log


@pytest.mark.supports(
    "test_the_starts_due_come_at_the_main_conversations_next_event_after_the_skills_call"
)
@pytest.mark.parametrize("agent", [None, Subagent("a9", "general-purpose")])
def test_an_event_before_the_base_directory_or_of_a_subagent_opens_nothing(
    g: Play, agent: Subagent | None
):
    """Given a run of log:up with no folder, the transcript holding no base directory yet
    When the main conversation, or another subagent, runs `git status`
    Then the guard answers nothing, and the run has no folder"""
    g(g.e.typed("log:up", "1.2.0"))
    if agent:
        base_directory(g.e.transcript, g.log, "up")
    assert answer(g.e.bash("git status", agent)) == Answer()
    assert runs("session-1")[0].plugin_root is None


@pytest.mark.supports("test_the_start_due_goes_through_and_leaves_none_due")
def test_the_start_due_goes_through_and_its_tie_leaves_none_due(g: Play):
    """Given the writer due
    When the main conversation starts it, its Agent call names a1, and it ends its turn
    Then the start and the end go through"""
    g.opened()
    assert not answer(g.e.start("log:writer", "toolu_1")).stop
    g(g.e.started(Subagent("a1", "log:writer"), "toolu_1"))
    assert not answer(g.e.stop()).stop


@pytest.mark.supports("test_another_start_of_the_plugins_subagents_is_stopped_with_the_starts_due")
def test_a_start_of_a_role_not_due_is_stopped_with_the_starts_due(g: Play):
    """Given the writer due
    When the main conversation starts the reviewer
    Then the guard stops it, with the writer due and its text"""
    g.opened()
    said = answer(g.e.start("log:reviewer", "toolu_1"))
    assert said.stop
    assert "log:writer" in said.said


@pytest.mark.supports("test_a_write_of_a_file_that_its_step_doesnt_name_is_stopped_with_the_step")
def test_a_tied_subagents_call_is_held_to_its_step(g: Play):
    """Given the writer tied to a1
    When a1 writes notes.txt
    Then the guard stops it with the sentence of the step `write`"""
    g.opened()
    writer = g.started()
    said = answer(g.e.write(os.path.join(g.e.cwd, "notes.txt"), writer))
    assert said.stop
    assert "CHANGELOG.md" in said.said


@pytest.mark.supports("test_an_agent_call_that_fails_after_its_pre_tool_use_leaves_its_start_due")
def test_a_start_whose_call_fails_is_dropped_and_due_again(g: Play):
    """Given the writer's start, untied
    When its Agent call fails, and the main conversation ends its turn
    Then the end is stopped with the writer due"""
    g.opened()
    g(g.e.start("log:writer", "toolu_1"))
    g(g.e.start_failed("log:writer", "toolu_1"))
    said = answer(g.e.stop())
    assert said.stop
    assert "log:writer" in said.said


@pytest.mark.supports("test_a_start_that_another_plugins_hook_denies_is_due_again_at_the_turns_end")
def test_a_start_still_untied_at_the_turns_end_is_dropped_and_due_again(g: Play):
    """Given the writer's start, which no event after its PreToolUse followed
    When the main conversation ends its turn, and then again
    Then each end is stopped with the writer due"""
    g.opened()
    g(g.e.start("log:writer", "toolu_1"))
    assert answer(g.e.stop()).stop
    assert "log:writer" in answer(g.e.stop()).said


@pytest.mark.supports("test_a_result_reaching_the_main_conversation_gives_the_starts_due_after_it")
def test_an_end_that_holds_and_its_notification_give_the_result_and_the_next_starts(g: Play):
    """Given the writer a1 that kept each step
    When it ends, and its task-notification reaches the main conversation
    Then the end goes through, and the notification gives `written` and the reviewer due"""
    g.opened()
    writer = g.started()
    g.kept_steps(writer)
    assert not answer(g.e.ended(writer)).stop
    said = answer(g.e.reached(writer, "toolu_1"))
    assert "written" in said.said
    assert "log:reviewer" in said.said


@pytest.mark.supports("test_a_subagent_stopped_by_task_stop_is_due_again")
def test_a_notification_of_a_subagent_stopped_by_task_stop_gives_its_start_due_again(g: Play):
    """Given the writer tied to a1, running
    When its task-notification says TaskStop stopped it, and the main conversation ends its turn
    Then the guard gives the writer due again with its text, and stops the end"""
    g.opened()
    writer = g.started()
    assert "log:writer" in answer(g.e.killed(writer, "toolu_1")).said
    assert answer(g.e.stop()).stop


@pytest.mark.supports("test_a_resume_that_the_order_makes_due_goes_through_as_its_start")
def test_a_resume_that_a_route_makes_due_is_its_start_tied_by_the_resume(g: Play):
    """Given the writer a1 ended, and the reviewer's `more`, which makes the writer due
    When the main conversation resumes a1 by SendMessage, the call says it resumed a1, and the
    main conversation ends its turn
    Then the resume and the end go through"""
    writer = g.to_review()
    reviewer = g.started("log:reviewer", "a2")
    g.reported(reviewer, "result", "more")
    g.ended(reviewer, "toolu_2")
    assert not answer(g.e.send(writer, "toolu_3")).stop
    g(g.e.resumed(writer, "toolu_3"))
    assert not answer(g.e.stop()).stop


@pytest.mark.supports("test_a_resume_that_the_order_doesnt_make_due_goes_through_as_talk")
def test_a_resume_that_no_route_makes_due_goes_through_and_moves_nothing(g: Play):
    """Given the writer a1 ended, so the reviewer is due
    When the main conversation resumes a1 by SendMessage, and ends its turn
    Then the resume goes through, and the end is stopped with the reviewer due"""
    writer = g.to_review()
    assert not answer(g.e.send(writer, "toolu_2")).stop
    g(g.e.resumed(writer, "toolu_2"))
    said = answer(g.e.stop())
    assert said.stop
    assert "log:reviewer" in said.said


@pytest.mark.supports("test_a_resume_queued_to_a_running_subagent_waits_for_the_end_of_its_pass")
@UNBUILT
def test_a_resume_queued_waits_through_the_turns_end_and_ties_at_the_end_of_the_pass(g: Play):
    """Given the writer a1 running, and a message queued to it by SendMessage
    When the main conversation ends its turn, a1 ends with no result, then keeps each step and
    ends, and then writes notes.txt
    Then the turn's end goes through, the first end is stopped, the second goes through, and the
    write is stopped, as the resume's start is tied to a1"""
    g.opened()
    writer = g.started()
    g(g.e.send(writer, "toolu_2"))
    g(g.e.queued(writer, "toolu_2"))
    assert not answer(g.e.stop()).stop
    assert answer(g.e.ended(writer)).stop
    g.kept_steps(writer)
    assert not answer(g.e.ended(writer)).stop
    assert answer(g.e.write(os.path.join(g.e.cwd, "notes.txt"), writer)).stop


@pytest.mark.supports("test_a_typed_command_that_a_route_goes_after_puts_its_starts_in_place")
def test_a_typed_command_puts_its_starts_in_place_of_those_before(g: Play):
    """Given the reviewer due
    When the person's /log:retry expands, and the main conversation ends its turn
    Then the end is stopped with the writer due, not the reviewer"""
    g.to_review()
    g(g.e.typed("log:retry"))
    said = answer(g.e.stop())
    assert said.stop
    assert "log:writer" in said.said


@pytest.mark.supports("test_a_run_whose_order_says_it_ends_holds_no_move_after")
def test_a_run_whose_routes_start_no_more_holds_no_move_after(g: Play):
    """Given the reviewer's `good`, after which the routes start no more
    When the main conversation writes notes.txt, and ends its turn
    Then the guard answers nothing to either"""
    g.to_review()
    reviewer = g.started("log:reviewer", "a2")
    g.reported(reviewer, "result", "good")
    g.ended(reviewer, "toolu_2")
    assert answer(g.e.write(os.path.join(g.e.cwd, "notes.txt"))) == Answer()
    assert answer(g.e.stop()) == Answer()


@pytest.mark.supports("test_the_plugins_command_typed_again_once_its_run_ended_adds_a_new_run")
def test_the_command_typed_once_its_run_ended_adds_a_new_run(g: Play):
    """Given a run of log:up that ended with the reviewer's `good`
    When the person's /log:up 1.3.0 expands, and the main conversation runs `git status`
    Then the record holds a second run, and the guard gives the writer due for 1.3.0"""
    g.to_review()
    reviewer = g.started("log:reviewer", "a2")
    g.reported(reviewer, "result", "good")
    g.ended(reviewer, "toolu_2")
    assert "log:writer" in g.opened("1.3.0").said
    assert len(runs("session-1")) == 2


@pytest.mark.supports("test_another_skills_command_typed_while_a_subagent_runs_moves_the_run")
def test_another_skills_command_moves_the_run_and_its_subagent_stays_on_its_start(g: Play):
    """Given the writer a1 running in the run of log:up
    When the person's /log:tag expands, the main conversation ends its turn, and a1 writes
    notes.txt
    Then the end is stopped with the tagger due, the write is stopped by a1's step, and the record
    holds the one run"""
    g.opened()
    writer = g.started()
    g(g.e.typed("log:tag"))
    said = answer(g.e.stop())
    assert said.stop
    assert "log:tagger" in said.said
    assert answer(g.e.write(os.path.join(g.e.cwd, "notes.txt"), writer)).stop
    assert len(runs("session-1")) == 1


@pytest.mark.supports("test_after_compact_the_run_goes_on_with_its_starts_due")
def test_the_summarys_end_at_compact_lies_outside_and_the_run_goes_on(g: Play):
    """Given the writer due
    When /compact's summary ends, and the main conversation ends its turn
    Then the guard answers nothing to the summary, and stops the end with the writer due"""
    g.opened()
    assert answer(g.e.summary_ended("a9")) == Answer()
    assert answer(g.e.stop()).stop


@pytest.mark.supports("test_the_command_typed_after_compact_gives_where_the_run_stands")
def test_the_command_typed_while_its_run_stands_gives_where_it_stands(g: Play):
    """Given the reviewer due in the run of log:up for 1.2.0
    When the person's /log:up 1.2.0 expands again
    Then the guard gives the reviewer due at once, and the record holds one run"""
    g.to_review()
    assert "log:reviewer" in answer(g.e.typed("log:up", "1.2.0")).said
    assert len(runs("session-1")) == 1


@pytest.mark.supports("test_a_new_conversation_goes_on_where_the_plugins_own_files_say")
def test_a_new_conversation_takes_its_starts_due_from_the_plugins_order(g: Play):
    """Given `log` deciding its order by ORDER, the conversation's CHANGELOG.md holding the entry
    of 1.2.0, and a conversation with no run
    When the person's /log:up 1.2.0 expands, and the main conversation runs `git status`
    Then the guard gives the reviewer due, as ORDER reads the entry"""
    write_files(g.log, {"lane/adapters/starts_due.py": lane_bench.ORDER})
    write_files(g.e.cwd, {"CHANGELOG.md": lane_bench.ENTRY})
    assert "log:reviewer" in g.opened().said


@pytest.mark.supports("test_a_run_whose_order_gives_no_start_due_waits_and_still_holds_its_moves")
def test_a_turns_end_while_the_order_gives_no_start_due_goes_through_and_the_run_stands(g: Play):
    """Given `log` whose adapter of the starts due gives none, and the person's /log:up 1.2.0
    When the main conversation ends its turn, and then writes notes.txt
    Then the end goes through, the record holds no end of the run, and the write is stopped by the
    step `lead`"""
    write_files(g.log, {"lane/adapters/starts_due.py": WAITS})
    g.opened()
    assert not answer(g.e.stop()).stop
    assert not [e for e in runs("session-1")[0].entries if e["kind"] == "ended"]
    assert answer(g.e.write(os.path.join(g.e.cwd, "notes.txt"))).stop


@pytest.mark.supports("test_a_run_whose_order_says_it_ends_holds_no_move_after")
def test_the_orders_end_of_the_run_is_kept_as_an_ended_entry(g: Play):
    """Given the reviewer due
    When the reviewer gives `good`, after which log's routes say the run ends
    Then the record holds an `ended` entry of the run"""
    g.to_review()
    reviewer = g.started("log:reviewer", "a2")
    g.reported(reviewer, "result", "good")
    g.ended(reviewer, "toolu_2")
    assert runs("session-1")[0].entries[-1]["kind"] == "ended"


@pytest.mark.supports(
    "test_the_turns_end_in_a_run_of_a_plugin_with_no_order_is_held_to_its_skills_check"
)
def test_a_turns_end_in_a_run_with_no_order_is_held_to_its_skills_check(g: Play):
    """Given `log` giving no order, its skill's step `lead` checked for .log/up.md
    When the person types /log:up 1.2.0, and the main conversation ends its turn before
    .log/up.md is there
    Then the guard stops the end with the step `lead` and what its check said, and the run
    stands"""
    write_files(g.log, {"lane/rules.json": json.dumps(NO_ORDER)})
    g.opened()
    said = answer(g.e.stop())
    assert said.stop
    assert "lead" in said.said
    assert UP_SAYS in said.said
    assert not [e for e in runs("session-1")[0].entries if e["kind"] == "ended"]


@pytest.mark.supports(
    "test_a_run_of_a_plugin_with_no_order_ends_at_the_turns_end_that_its_steps_let_through"
)
def test_a_turns_end_that_a_run_with_no_order_lets_through_ends_the_run(g: Play):
    """Given `log` giving no order, and the person's /log:up 1.2.0
    When .log/up.md is there, the main conversation ends its turn, and then writes notes.txt
    Then the end goes through, the record holds an `ended` entry of the run, and the guard answers
    nothing to the write"""
    write_files(g.log, {"lane/rules.json": json.dumps(NO_ORDER)})
    g.opened()
    write_files(g.e.cwd, {".log/up.md": "x\n"})
    assert not answer(g.e.stop()).stop
    assert runs("session-1")[0].entries[-1]["kind"] == "ended"
    assert answer(g.e.write(os.path.join(g.e.cwd, "notes.txt"))) == Answer()


@pytest.mark.supports("test_another_conversation_in_the_repository_is_held_to_no_run_of_the_first")
def test_another_conversations_events_lie_outside_the_first_ones_run(
    cwd: str, log: str, capsys: pytest.CaptureFixture[str], g: Play
):
    """Given the writer due in the conversation session-1
    When the conversation session-2 writes notes.txt and ends its turn
    Then the guard answers nothing to either"""
    g.opened()
    other = Play(cwd, log, capsys, "session-2")
    assert answer(other.e.write(os.path.join(cwd, "notes.txt"))) == Answer()
    assert answer(other.e.stop()) == Answer()


@pytest.mark.supports("test_a_subagents_start_of_a_subagent_is_stopped")
def test_a_subagents_start_is_stopped(g: Play):
    """Given the writer a1 running
    When a1 starts a writer by the Agent tool
    Then the guard stops it"""
    g.opened()
    writer = g.started()
    assert answer(g.e.start("log:writer", "toolu_2", writer)).stop


@pytest.mark.supports("test_a_subagents_message_to_another_subagent_goes_through_as_talk")
def test_a_subagents_message_to_another_subagent_goes_through(g: Play):
    """Given the writer a1 running
    When a1 sends a2 a message by SendMessage
    Then the guard lets it through"""
    g.opened()
    writer = g.started()
    assert not answer(g.e.send(Subagent("a2", "log:writer"), "toolu_2", writer)).stop


@pytest.mark.supports("test_rules_out_of_form_stop_the_call_saying_what_the_author_mends")
def test_rules_out_of_form_stop_the_next_event_saying_what_to_mend(g: Play):
    """Given `log` whose lane/rules.json has no roles
    When the person types /log:up 1.2.0, and the main conversation runs `git status`
    Then the guard stops the call, naming lane/rules.json and the roles"""
    write_files(g.log, {"lane/rules.json": json.dumps({"routes": lane_bench.RULES["routes"]})})
    said = g.opened()
    assert said.stop
    assert "lane/rules.json" in said.said
    assert "roles" in said.said


@pytest.mark.supports("test_work_outside_a_run_of_a_plugin_with_rules_is_left_alone")
def test_a_plugin_with_no_rules_has_each_event_left_alone(g: Play):
    """Given `log` with no lane/rules.json
    When the person types /log:up 1.2.0, the main conversation runs `git status`, and ends its
    turn
    Then the guard answers nothing to each"""
    os.remove(os.path.join(g.log, "lane", "rules.json"))
    assert g.opened() == Answer()
    assert answer(g.e.stop()) == Answer()


# Each interface below answer, by each class of its move.


def move(kind: str, event: Event, agent: Subagent | None = None, step: str | None = None) -> Move:
    """The move of the kind, on the one run of the conversation session-1 as its record stands,
    with the prompt of an Agent call's start."""
    [run] = runs("session-1")
    role = agent.type if agent else run.skill
    steps = lane_bench.RULES["roles"][role].get("steps", [])
    given = event.get("tool_input", {}).get("prompt") if kind == "start" else None
    return Move(kind, event, run, role, agent.id if agent else None, given, steps, step, None)


def last_start() -> Entry:
    """The record's latest `start` entry."""
    return [e for e in runs("session-1")[0].entries if e["kind"] == "start"][-1]


def recorded(log: str, *entries: Entry) -> None:
    """The record of session-1 with a run of log:up for 1.2.0 in log's folder, and the entries."""
    head: list[Entry] = [
        {"kind": "run", "run": "r1", "skill": "log:up", "words": "1.2.0"},
        {"kind": "folder", "run": "r1", "plugin_root": log},
    ]
    add("session-1", [*head, *entries])


WRITER = Subagent("a1", "log:writer")
START: Entry = lane_entries.start("toolu_1", prompt="You are log:writer.")
TIE: Entry = lane_entries.tie("toolu_1", "a1")
GAVE: Entry = lane_entries.result("a1", "written")


@pytest.mark.supports("test_the_turns_end_while_the_commands_start_is_due_is_stopped_with_it")
def test_skill_called_with_no_run_adds_one_with_no_folder(g: Play):
    """Given a conversation with no run
    When log:up is called with 1.2.0
    Then the answer is empty, and the record holds the run with no folder"""
    assert skill_called(SkillCall("session-1", g.e.transcript, "log:up", "1.2.0")) == Answer()
    assert runs("session-1")[0].plugin_root is None


@pytest.mark.supports("test_the_command_typed_after_compact_gives_where_the_run_stands")
def test_command_typed_of_the_skill_that_called_the_run_gives_where_it_stands(g: Play, log: str):
    """Given the writer a1's result `written`, so the reviewer is due
    When the person types /log:up again
    Then the answer gives the reviewer due with its text, and not the writer"""
    gave: Entry = lane_entries.result("a1", "written")
    recorded(log, START, TIE, gave)
    said = command_typed(move("typed", g.e.typed("log:up", "1.2.0")))
    assert "log:reviewer" in said.said


@pytest.mark.supports("test_another_skills_command_typed_while_a_subagent_runs_moves_the_run")
def test_command_typed_of_another_skill_gives_its_routes_starts(g: Play, log: str):
    """Given the writer tied to a1
    When the main conversation calls log:tag by the Skill tool
    Then the answer gives the tagger due with its text, and the record holds the command"""
    recorded(log, START, TIE)
    said = command_typed(move("typed", g.e.skill_post("log:tag", "")))
    assert "log:tagger" in said.said
    last = runs("session-1")[0].entries[-1]
    assert (last["kind"], last.get("command")) == ("typed", "log:tag")


@pytest.mark.supports(
    "test_the_starts_due_come_at_the_main_conversations_next_event_after_the_skills_call"
)
def test_run_opened_reads_the_folder_and_gives_the_starts_due(g: Play, log: str):
    """Given a run with no folder, and the transcript holding its base directory
    When the run opens at the main conversation's Stop
    Then the answer gives the writer due, and the run has its folder"""
    add("session-1", [{"kind": "run", "run": "r1", "skill": "log:up", "words": "1.2.0"}])
    base_directory(g.e.transcript, log, "up")
    said = run_opened(g.e.stop(), runs("session-1")[0])
    assert "log:writer" in said.said
    assert runs("session-1")[0].plugin_root == log


@pytest.mark.supports(
    "test_the_starts_due_come_at_the_main_conversations_next_event_after_the_skills_call"
)
def test_run_opened_before_the_base_directory_gives_nothing(g: Play):
    """Given a run with no folder, and a transcript with no base directory
    When the run opens
    Then the answer is empty, and the run has no folder"""
    add("session-1", [{"kind": "run", "run": "r1", "skill": "log:up", "words": "1.2.0"}])
    os.makedirs(os.path.dirname(g.e.transcript))
    with open(g.e.transcript, "w", encoding="utf-8") as f:
        f.write("{}\n")
    assert run_opened(g.e.stop(), runs("session-1")[0]) == Answer()
    assert runs("session-1")[0].plugin_root is None


@pytest.mark.supports("test_the_start_due_goes_through_and_leaves_none_due")
@pytest.mark.parametrize(
    "role, stop", [("log:writer", False), ("log:reviewer", True), ("general-purpose", False)]
)
def test_start_made_lets_the_start_due_through_and_stops_another(
    g: Play, log: str, role: str, stop: bool
):
    """Given the writer due
    When the main conversation starts the writer, the reviewer, or general-purpose, which isn't
    the plugin's
    Then the writer's and general-purpose's go through, and the reviewer's is stopped with the
    writer due"""
    recorded(log)
    said = start_made(move("start", g.e.start(role, "toolu_1")))
    assert said.stop == stop
    assert ("log:writer" in said.said) == stop


@pytest.mark.supports("test_the_order_tells_the_starts_of_one_role_apart_by_their_prompts")
def test_start_made_keeps_the_start_with_its_prompt(g: Play, log: str):
    """Given the writer due
    When the main conversation starts the writer with a prompt
    Then the record holds the start of the writer with that prompt, untied"""
    recorded(log)
    start_made(move("start", g.e.start("log:writer", "toolu_1", prompt="Write docs/changes/.")))
    kept = last_start()
    assert (kept["role"], kept["prompt"]) == ("log:writer", "Write docs/changes/.")
    assert not [e for e in runs("session-1")[0].entries if e["kind"] == "tie"]


@pytest.mark.supports(
    "test_a_role_with_no_fixed_steps_takes_them_from_the_plugins_adapter_for_each_start"
)
def test_start_made_of_a_role_with_no_steps_keeps_the_steps_its_adapter_gives(g: Play, log: str):
    """Given `log` naming the writer with no steps, with its adapter of the rules, and the writer
    due
    When the main conversation starts the writer to write docs/changes/1.2.0.md
    Then the start goes through, and the record holds it with the step that the adapter gave"""
    write_files(log, {"lane/rules.json": json.dumps(lane_bench.ADAPTED)})
    write_files(log, {"lane/adapters/rules.py": lane_bench.RULES_ADAPTER})
    recorded(log)
    event = g.e.start("log:writer", "toolu_1", prompt="Write docs/changes/1.2.0.md.")
    assert not start_made(move("start", event)).stop
    assert last_start()["steps"] == [
        {"name": "write", "rules": [{"type": "writes", "paths": ["docs/changes/1.2.0.md"]}]}
    ]


@pytest.mark.supports(
    "test_a_start_of_a_role_with_no_steps_and_no_adapter_of_the_rules_is_stopped_saying_so"
)
def test_start_made_of_a_role_with_no_steps_and_no_adapter_is_stopped_naming_it(g: Play, log: str):
    """Given `log` naming the writer with no steps, with no adapter of the rules, and the writer due
    When the main conversation starts the writer
    Then the guard stops it, naming lane/adapters/rules.py and the writer, and keeps no start"""
    write_files(log, {"lane/rules.json": json.dumps(lane_bench.ADAPTED)})
    recorded(log)
    said = start_made(move("start", g.e.start("log:writer", "toolu_1")))
    assert said.stop
    assert "lane/adapters/rules.py" in said.said
    assert "log:writer" in said.said
    assert not [e for e in runs("session-1")[0].entries if e["kind"] == "start"]


@pytest.mark.supports("test_a_resume_that_the_order_makes_due_goes_through_as_its_start")
def test_start_made_of_a_resume_keeps_the_prompt_and_steps_of_the_start_it_resumes(
    g: Play, log: str
):
    """Given `log` naming the writer with no steps and giving no adapter of the rules now, the
    writer a1's start with the steps that the adapter gave, its `written`, and the reviewer's
    `more`, so that the writer is due
    When the main conversation resumes a1 by SendMessage
    Then the resume goes through, and the record holds its start with a1's prompt and steps"""
    write_files(log, {"lane/rules.json": json.dumps(lane_bench.ADAPTED)})
    given: list[Step] = [
        {"name": "write", "rules": [{"type": "writes", "paths": ["CHANGELOG.md"]}]}
    ]
    reviewer: list[Entry] = [
        lane_entries.start("toolu_2", "log:reviewer"),
        lane_entries.tie("toolu_2", "a2"),
        lane_entries.result("a2", "more", "log:reviewer"),
    ]
    recorded(log, {**START, "steps": given}, TIE, GAVE, *reviewer)
    assert not start_made(move("start", g.e.send(WRITER, "toolu_3"))).stop
    kept = last_start()
    assert (kept["tool_use_id"], kept["prompt"], kept["steps"]) == (
        "toolu_3",
        START["prompt"],
        given,
    )


@pytest.mark.supports(
    "test_an_adapter_of_the_starts_due_that_fails_stops_with_the_adapter_and_what_it_said"
)
def test_turn_ended_with_an_adapter_of_the_starts_due_that_fails_stops_with_what_it_said(
    g: Play, log: str
):
    """Given `log` whose adapter of the starts due exits 1 saying it found no version
    When the main conversation ends its turn
    Then the guard stops the end, naming starts_due.py and what it said"""
    write_files(log, {"lane/adapters/starts_due.py": "import sys\n\nsys.exit('no version')\n"})
    recorded(log)
    said = turn_ended(move("turn_end", g.e.stop()))
    assert said.stop
    assert "starts_due.py" in said.said
    assert "no version" in said.said


@pytest.mark.supports("test_the_turns_end_while_the_commands_start_is_due_is_stopped_with_it")
@pytest.mark.parametrize("entries, stop", [((), True), ((START, TIE), False)])
def test_turn_ended_stops_only_while_a_start_is_due(
    g: Play, log: str, entries: tuple[Entry, ...], stop: bool
):
    """Given the writer due, or tied to a1
    When the main conversation ends its turn
    Then the end is stopped with the writer due, or goes through"""
    recorded(log, *entries)
    assert turn_ended(move("turn_end", g.e.stop())).stop == stop


@pytest.mark.supports("test_a_resume_queued_to_a_running_subagent_waits_for_the_end_of_its_pass")
def test_turn_ended_drops_each_start_untied_but_a_resume_queued(g: Play, log: str):
    """Given the writer's start untied, and a resume of a1 queued
    When the main conversation ends its turn
    Then the record drops the untied start and keeps the queued one"""
    resume: Entry = lane_entries.start("toolu_2")
    queued: Entry = {"kind": "queue", "run": "r1", "tool_use_id": "toolu_2", "agent_id": "a1"}
    untied: Entry = lane_entries.start("toolu_3")
    recorded(log, START, TIE, resume, queued, untied)
    turn_ended(move("turn_end", g.e.stop()))
    dropped = [e.get("tool_use_id") for e in runs("session-1")[0].entries if e["kind"] == "drop"]
    assert dropped == ["toolu_3"]


@pytest.mark.supports("test_a_typed_command_that_a_route_goes_after_puts_its_starts_in_place")
def test_command_typed_gives_its_routes_starts(g: Play, log: str):
    """Given the writer tied to a1
    When the person types /log:retry
    Then the answer gives the writer due, and the record holds the command"""
    recorded(log, START, TIE)
    said = command_typed(move("typed", g.e.typed("log:retry")))
    assert "log:writer" in said.said
    assert runs("session-1")[0].entries[-1]["kind"] == "typed"


@pytest.mark.supports("test_a_result_reaching_the_main_conversation_gives_the_starts_due_after_it")
def test_result_reached_gives_the_result_and_its_routes_starts(g: Play, log: str):
    """Given the writer a1's result `written`
    When its end reaches the main conversation
    Then the answer gives `written` and the reviewer due with its text"""
    gave: Entry = lane_entries.result("a1", "written")
    recorded(log, START, TIE, gave)
    said = result_reached(move("result_reached", g.e.reached(WRITER, "toolu_1"), WRITER))
    assert "written" in said.said
    assert "log:reviewer" in said.said


@pytest.mark.supports("test_a_subagent_stopped_by_task_stop_is_due_again")
def test_result_reached_of_a_subagent_stopped_gives_its_start_due_again(g: Play, log: str):
    """Given the writer tied to a1, with no result
    When its notification says TaskStop stopped it
    Then the answer gives the writer due again, and the record holds a1's start stopped"""
    recorded(log, START, TIE)
    said = result_reached(move("result_reached", g.e.killed(WRITER, "toolu_1"), WRITER))
    assert "log:writer" in said.said
    last = runs("session-1")[0].entries[-1]
    assert (last["kind"], last.get("agent_id")) == ("stopped", "a1")


@pytest.mark.supports("test_the_start_due_goes_through_and_leaves_none_due")
@pytest.mark.parametrize(
    "kind",
    [
        "tie",
        "queue",
        "drop",
        "read",
    ],
)
def test_fact_added_adds_its_fact_and_answers_nothing(g: Play, log: str, kind: str):
    """Given the writer's start, untied for a tie, a queue, or a drop, and tied for a read
    When the fact's move comes
    Then the answer is empty, and the record's last entry is of the fact's kind"""
    cwd = g.e.cwd
    events = {
        "tie": (g.e.started(WRITER, "toolu_1"), (START,)),
        "queue": (g.e.queued(WRITER, "toolu_1"), (START,)),
        "drop": (g.e.start_failed("log:writer", "toolu_1"), (START,)),
        "read": (g.e.read_ran(os.path.join(cwd, "NOTES.md"), 1, 6, 6, WRITER), (START, TIE)),
    }
    event, entries = events[kind]
    recorded(log, *entries)
    agent = WRITER if kind == "read" else None
    assert fact_added(move(kind, event, agent, "write" if agent else None)) == Answer()
    assert runs("session-1")[0].entries[-1]["kind"] == kind


@pytest.mark.supports("test_a_write_of_a_file_that_its_step_doesnt_name_is_stopped_with_the_step")
@pytest.mark.parametrize("name, stop", [("notes.txt", True), ("CHANGELOG.md", False)])
def test_call_made_stops_only_a_call_that_breaks_its_step(g: Play, log: str, name: str, stop: bool):
    """Given the writer tied to a1 at its step `write`
    When a1 writes notes.txt, or CHANGELOG.md
    Then the first is stopped with the step's sentence, and the second goes through"""
    recorded(log, START, TIE)
    said = call_made(move("call", g.e.write(os.path.join(g.e.cwd, name), WRITER), WRITER, "write"))
    assert said.stop == stop


def report_move(g: Play, kind: str, *words: str) -> Move:
    """The report move of a1's reporter of the kind, with the report it printed."""
    report(kind, list(words))
    printed = g.capsys.readouterr().out
    [run] = runs("session-1")
    event = g.e.bash_ran(f"lane-{kind}", printed, WRITER)
    steps = lane_bench.RULES["roles"][WRITER.type]["steps"]
    return Move(
        "report", event, run, WRITER.type, WRITER.id, None, steps, "write", read_report(printed)
    )


@pytest.mark.supports("test_a_step_marked_before_its_items_names_each_item_not_done")
def test_report_made_of_a_step_whose_rules_break_gives_the_sentence_and_marks_nothing(
    g: Play, log: str
):
    """Given the writer tied to a1, which read nothing and marked no item
    When it reports the step `write` done
    Then the answer gives the step's sentence, and the record holds no mark"""
    recorded(log, START, TIE)
    said = report_made(report_move(g, "step", "write"))
    assert "NOTES.md" in said.said
    assert not [e for e in runs("session-1")[0].entries if e["kind"] == "mark"]


@pytest.mark.supports("test_a_step_marked_once_each_item_is_done_holds")
@pytest.mark.parametrize("kind, words", [("item", ("write", "dated")), ("result", ("written",))])
def test_report_made_of_an_item_or_a_result_adds_it(
    g: Play, log: str, kind: str, words: tuple[str, ...]
):
    """Given the writer tied to a1
    When it reports the item `dated` of `write`, or the result `written`
    Then the answer is empty, and the record's last entry holds it"""
    recorded(log, START, TIE)
    assert report_made(report_move(g, kind, *words)) == Answer()
    last = runs("session-1")[0].entries[-1]
    assert last["kind"] == ("mark" if kind == "item" else "result")


@pytest.mark.supports("test_an_end_with_no_result_is_stopped_with_the_results_it_may_give")
def test_subagent_ended_with_no_result_is_stopped(g: Play, log: str):
    """Given the writer tied to a1, with no result
    When it ends
    Then the answer stops it, naming `written`"""
    recorded(log, START, TIE)
    said = subagent_ended(move("end", g.e.ended(WRITER), WRITER, "write"))
    assert said.stop
    assert "written" in said.said


@pytest.mark.supports("test_a_resume_queued_to_a_running_subagent_waits_for_the_end_of_its_pass")
def test_subagent_ended_that_holds_ties_the_resume_queued(g: Play, log: str):
    """Given the writer tied to a1, which kept each step and gave `written`, and a resume queued to
    it
    When it ends
    Then the answer is empty, and the record ties the resume's start to a1"""
    marks: list[Entry] = [
        {"kind": "mark", "run": "r1", "agent_id": "a1", "step": "write"},
        {"kind": "mark", "run": "r1", "agent_id": "a1", "step": "report"},
        lane_entries.result("a1", "written"),
    ]
    resume: Entry = lane_entries.start("toolu_2")
    queued: Entry = {"kind": "queue", "run": "r1", "tool_use_id": "toolu_2", "agent_id": "a1"}
    recorded(log, START, TIE, *marks, resume, queued)
    assert subagent_ended(move("end", g.e.ended(WRITER), WRITER, None)) == Answer()
    last = runs("session-1")[0].entries[-1]
    assert (last["kind"], last.get("tool_use_id"), last.get("agent_id")) == ("tie", "toolu_2", "a1")


# written, by each event and class of answer.


def read_json(text: str) -> Any:
    return json.loads(text) if text.strip() else {}


@pytest.mark.supports("test_a_write_of_a_file_that_its_step_doesnt_name_is_stopped_with_the_step")
def test_a_stop_at_pre_tool_use_is_a_deny_with_its_reason(g: Play):
    """Given the guard's stop with the step's sentence
    When it's written for a PreToolUse
    Then Claude Code reads a deny with the sentence as its reason"""
    out = read_json(
        written(g.e.write("/repo/notes.txt", WRITER), Answer(True, "Write CHANGELOG.md."))
    )
    specific = out["hookSpecificOutput"]
    assert (specific["hookEventName"], specific["permissionDecision"]) == ("PreToolUse", "deny")
    assert specific["permissionDecisionReason"] == "Write CHANGELOG.md."


@pytest.mark.supports("test_the_turns_end_while_the_commands_start_is_due_is_stopped_with_it")
@pytest.mark.parametrize("event", ["stop", "subagent_stop", "post_tool_use"])
def test_a_stop_at_another_event_is_a_block_with_its_reason(g: Play, event: str):
    """Given the guard's stop with the starts due
    When it's written for a Stop, a SubagentStop, or a PostToolUse
    Then Claude Code reads a block with them as its reason"""
    given = {
        "stop": g.e.stop(),
        "subagent_stop": g.e.ended(WRITER),
        "post_tool_use": g.e.bash_ran("lane-step write", "", WRITER),
    }[event]
    out = read_json(written(given, Answer(True, "Start log:writer.")))
    assert (out["decision"], out["reason"]) == ("block", "Start log:writer.")


@pytest.mark.supports("test_a_result_reaching_the_main_conversation_gives_the_starts_due_after_it")
def test_what_the_guard_says_without_a_stop_is_additional_context(g: Play):
    """Given the guard's answer that stops nothing and gives the starts due
    When it's written for the UserPromptSubmit of a task-notification
    Then Claude Code reads them as additional context, with no block"""
    out = read_json(written(g.e.reached(WRITER, "toolu_1"), Answer(False, "Start log:reviewer.")))
    assert "decision" not in out
    assert out["hookSpecificOutput"]["additionalContext"] == "Start log:reviewer."


@pytest.mark.supports("test_work_outside_a_run_of_a_plugin_with_rules_is_left_alone")
def test_an_empty_answer_is_written_as_nothing_to_read(g: Play):
    """Given the guard's empty answer
    When it's written for a Stop
    Then Claude Code reads no decision and no context"""
    out = read_json(written(g.e.stop(), Answer()))
    assert "decision" not in out
    assert not out.get("hookSpecificOutput", {}).get("additionalContext")
