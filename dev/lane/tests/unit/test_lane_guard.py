"""The unit cases of hooks/lane/guard.py: answer, one for each transition of a run that Lane's list
of Claude Code's states brings about, each event given to the guard as Claude Code sends it, from
the skill's call to the end of the routes, the run record kept in the case's temporary folder, with
the answers of an opening and a move joined; each interface below it, one for each class of the move
it takes, a role due once and twice at once among them, a start of another plugin's subagent whose
name nearly matches, and each class of the order's answer; and written, one for each event and
class of answer. Each Then gives the whole answer, as Lane's rules-and-adapters.md words it, and
each entry that the record gains."""

from __future__ import annotations

import copy
import dataclasses
import json
import os
from typing import Any

import lane_bench
import lane_entries
import pytest
from adapters import AdapterFailed
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
from lane_sentences import check_fails, no_result, reads_whole_of, writes_only
from place import Move, SkillCall
from record import Entry, Run, add, runs
from repo_files import write_files
from report import read_report, report
from rules import Step

# An adapter of the starts due that gives none, as it waits for the person's answer.
WAITS = 'import json\n\nprint(json.dumps({"starts": []}))\n'
# The rules of `log` giving no order: the main conversation's step `lead` alone, checked for
# .log/up.md.
UP_SAYS = ".log/up.md is missing"
NO_ORDER: Any = {"roles": {"log:up": copy.deepcopy(lane_bench.RULES["roles"]["log:up"])}}
NO_ORDER["roles"]["log:up"]["steps"][0]["rules"].append(
    {"type": "check", "check": f"test -f .log/up.md || {{ echo '{UP_SAYS}'; exit 1; }}"}
)
# What the main conversation reads of the starts due.
WRITER_DUE = "Due: log:writer."
REVIEWER_DUE = "Due: log:reviewer."
# The step's sentence of a write of notes.txt, by the main conversation at `lead`, and by the writer
# at `write`.
LEAD_WRITES = writes_only("lead", [".log/up.md"], "notes.txt", "log:up")
WRITER_WRITES = writes_only("write", ["CHANGELOG.md", "docs/changes/"], "notes.txt")


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

    def reviewed(self, result: str) -> Subagent:
        """The writer a1 and then the reviewer a2 kept their steps and ended, the reviewer with the
        result; gives the writer."""
        writer = self.to_review()
        reviewer = self.started("log:reviewer", "a2")
        self.reported(reviewer, "result", result)
        self.ended(reviewer, "toolu_2")
        return writer


@pytest.fixture
def g(cwd: str, log: str, capsys: pytest.CaptureFixture[str]) -> Play:
    return Play(cwd, log, capsys, "session-1")


def entries() -> list[Entry]:
    """The entries of the one run of the conversation session-1."""
    [run] = runs("session-1")
    return run.entries


def of_kind(kind: str) -> list[Entry]:
    """The entries of the kind of the one run of session-1."""
    return [each for each in entries() if each["kind"] == kind]


RUN: Entry = {"kind": "run", "run": "r1", "skill": "log:up", "words": "1.2.0"}


# answer, by each transition.


@pytest.mark.supports(
    "test_the_starts_due_come_at_the_main_conversations_next_event_after_the_skills_call"
)
def test_a_skills_call_adds_a_run_with_no_folder_and_answers_nothing(g: Play):
    """Given a conversation with no run
    When the person's /log:up 1.2.0 expands
    Then the guard answers nothing, and the record holds a run r1 of log:up for 1.2.0 with no
    folder"""
    assert answer(g.e.typed("log:up", "1.2.0")) == Answer()
    assert runs("session-1") == [Run("r1", "session-1", "log:up", "1.2.0", None, [RUN])]


@pytest.mark.supports(
    "test_the_starts_due_come_at_the_main_conversations_next_event_after_the_skills_call"
)
def test_the_next_event_with_the_base_directory_gives_the_folder_and_the_starts_due(g: Play):
    """Given a run of log:up with no folder, and the transcript holding its base directory
    When the main conversation runs `git status`
    Then the guard lets it through with the writer due, and the record gains the run's folder
    alone"""
    assert g.opened() == Answer(False, WRITER_DUE)
    assert entries() == [RUN, {"kind": "folder", "run": "r1", "plugin_root": g.log}]


@pytest.mark.supports(
    "test_the_starts_due_come_at_the_main_conversations_next_event_after_the_skills_call"
)
def test_the_next_event_that_breaks_its_step_gives_the_starts_due_and_the_steps_sentence(g: Play):
    """Given a run of log:up with no folder, and the transcript holding its base directory
    When the main conversation writes notes.txt, which its step `lead` doesn't name
    Then the guard stops the write, giving the writer due and then the sentence of `lead`"""
    g(g.e.typed("log:up", "1.2.0"))
    base_directory(g.e.transcript, g.log, "up")
    said = answer(g.e.write(os.path.join(g.e.cwd, "notes.txt")))
    assert said == Answer(True, f"{WRITER_DUE}\n{LEAD_WRITES}")


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
    assert entries() == [RUN]


@pytest.mark.supports("test_the_start_due_goes_through_and_leaves_none_due")
def test_the_start_due_goes_through_and_its_tie_leaves_none_due(g: Play):
    """Given the writer due
    When the main conversation starts it, its Agent call names a1, and it ends its turn
    Then the guard answers nothing to each, and the record gains the start and its tie"""
    g.opened()
    assert answer(g.e.start("log:writer", "toolu_1")) == Answer()
    assert answer(g.e.started(Subagent("a1", "log:writer"), "toolu_1")) == Answer()
    assert answer(g.e.stop()) == Answer()
    assert entries()[2:] == [
        lane_entries.start("toolu_1"),
        {"kind": "tie", "run": "r1", "agent_id": "a1", "tool_use_id": "toolu_1"},
    ]


@pytest.mark.supports("test_another_start_of_the_plugins_subagents_is_stopped_with_the_starts_due")
def test_a_start_of_a_role_not_due_is_stopped_with_the_starts_due(g: Play):
    """Given the writer due
    When the main conversation starts the reviewer
    Then the guard stops it, with the writer due, and the record gains no start"""
    g.opened()
    assert answer(g.e.start("log:reviewer", "toolu_1")) == Answer(True, WRITER_DUE)
    assert not of_kind("start")


@pytest.mark.supports("test_a_write_of_a_file_that_its_step_doesnt_name_is_stopped_with_the_step")
def test_a_tied_subagents_call_is_held_to_its_step(g: Play):
    """Given the writer tied to a1
    When a1 writes notes.txt
    Then the guard stops it with the sentence of the step `write`"""
    g.opened()
    writer = g.started()
    said = answer(g.e.write(os.path.join(g.e.cwd, "notes.txt"), writer))
    assert said == Answer(True, WRITER_WRITES)


@pytest.mark.supports("test_an_agent_call_that_fails_after_its_pre_tool_use_leaves_its_start_due")
def test_a_start_whose_call_fails_is_dropped_and_due_again(g: Play):
    """Given the writer's start, untied
    When its Agent call fails, and the main conversation ends its turn
    Then the guard answers nothing to the failure, the record drops the start, and the end is
    stopped with the writer due"""
    g.opened()
    g(g.e.start("log:writer", "toolu_1"))
    assert answer(g.e.start_failed("log:writer", "toolu_1")) == Answer()
    assert of_kind("drop") == [
        {"kind": "drop", "run": "r1", "agent_id": None, "tool_use_id": "toolu_1"}
    ]
    assert answer(g.e.stop()) == Answer(True, WRITER_DUE)


@pytest.mark.supports("test_a_start_that_another_plugins_hook_denies_is_due_again_at_the_turns_end")
def test_a_start_still_untied_at_the_turns_end_is_dropped_and_due_again(g: Play):
    """Given the writer's start, which no event after its PreToolUse followed
    When the main conversation ends its turn, and then again
    Then each end is stopped with the writer due, and the record drops the start once"""
    g.opened()
    g(g.e.start("log:writer", "toolu_1"))
    assert answer(g.e.stop()) == Answer(True, WRITER_DUE)
    assert answer(g.e.stop()) == Answer(True, WRITER_DUE)
    assert of_kind("drop") == [{"kind": "drop", "run": "r1", "tool_use_id": "toolu_1"}]


@pytest.mark.supports("test_a_result_reaching_the_main_conversation_gives_the_starts_due_after_it")
def test_an_end_that_holds_and_its_notification_give_the_result_and_the_next_starts(g: Play):
    """Given the writer a1 that kept each step
    When it ends, and its task-notification reaches the main conversation
    Then the end goes through, and the notification gives `written` and the reviewer due"""
    g.opened()
    writer = g.started()
    g.kept_steps(writer)
    assert answer(g.e.ended(writer)) == Answer()
    said = answer(g.e.reached(writer, "toolu_1"))
    assert said == Answer(False, f"log:writer gave written. {REVIEWER_DUE}")


@pytest.mark.supports("test_a_subagent_stopped_by_task_stop_is_due_again")
def test_a_notification_of_a_subagent_stopped_by_task_stop_gives_its_start_due_again(g: Play):
    """Given the writer tied to a1, running
    When its task-notification says TaskStop stopped it, and the main conversation ends its turn
    Then the guard says the writer stopped with no result and gives it due again, and stops the
    end with the writer due"""
    g.opened()
    writer = g.started()
    said = answer(g.e.killed(writer, "toolu_1"))
    assert said == Answer(False, f"log:writer stopped with no result. {WRITER_DUE}")
    assert answer(g.e.stop()) == Answer(True, WRITER_DUE)


@pytest.mark.supports("test_a_resume_that_the_order_makes_due_goes_through_as_its_start")
def test_a_resume_that_a_route_makes_due_is_its_start_tied_by_the_resume(g: Play):
    """Given the writer a1 ended, and the reviewer's `more`, which makes the writer due
    When the main conversation resumes a1 by SendMessage, the call says it resumed a1, and the
    main conversation ends its turn
    Then the guard answers nothing to each, and the record gains the resume's start and its tie"""
    writer = g.reviewed("more")
    assert answer(g.e.send(writer, "toolu_3")) == Answer()
    assert answer(g.e.resumed(writer, "toolu_3")) == Answer()
    assert answer(g.e.stop()) == Answer()
    assert entries()[-2:] == [
        lane_entries.start("toolu_3"),
        {"kind": "tie", "run": "r1", "agent_id": "a1", "tool_use_id": "toolu_3"},
    ]


@pytest.mark.supports("test_a_resume_that_the_order_doesnt_make_due_goes_through_as_talk")
def test_a_resume_that_no_route_makes_due_goes_through_and_moves_nothing(g: Play):
    """Given the writer a1 ended, so the reviewer is due
    When the main conversation resumes a1 by SendMessage, and ends its turn
    Then the resume goes through and the record gains nothing, and the end is stopped with the
    reviewer due"""
    writer = g.to_review()
    before = entries()
    assert answer(g.e.send(writer, "toolu_2")) == Answer()
    assert answer(g.e.resumed(writer, "toolu_2")) == Answer()
    assert entries() == before
    assert answer(g.e.stop()) == Answer(True, REVIEWER_DUE)


@pytest.mark.supports(
    "test_a_message_queued_to_a_running_subagent_goes_through_and_its_later_pass_is_its_same_start"
)
def test_a_message_queued_to_a_running_subagent_is_talk_and_its_later_pass_is_its_start(g: Play):
    """Given the writer a1 running
    When the main conversation sends it a message, which Claude Code queues, and ends its turn,
    a1 ends with no result, and then keeps each step and ends
    Then the message and the turn's end go through, the first end is stopped with the result rule
    of `report`, the second goes through, and the record holds the one start of a1"""
    g.opened()
    writer = g.started()
    assert answer(g.e.send(writer, "toolu_2")) == Answer()
    assert answer(g.e.queued(writer, "toolu_2")) == Answer()
    assert answer(g.e.stop()) == Answer()
    assert answer(g.e.ended(writer)) == Answer(True, no_result("report", ["written"]))
    g.kept_steps(writer)
    assert answer(g.e.ended(writer)) == Answer()
    assert of_kind("start") == [lane_entries.start("toolu_1")]


@pytest.mark.supports("test_a_typed_command_that_a_route_goes_after_puts_its_starts_in_place")
def test_a_typed_command_puts_its_starts_in_place_of_those_before(g: Play):
    """Given the reviewer due
    When the person's /log:retry expands, and the main conversation ends its turn
    Then the guard gives the writer due at the command, and stops the end with the writer due, not
    the reviewer"""
    g.to_review()
    assert answer(g.e.typed("log:retry")) == Answer(False, WRITER_DUE)
    assert answer(g.e.stop()) == Answer(True, WRITER_DUE)


@pytest.mark.supports("test_a_run_whose_order_says_it_ends_holds_no_move_after")
def test_a_run_whose_routes_start_no_more_holds_no_move_after(g: Play):
    """Given the reviewer's `good`, after which the routes start no more
    When the main conversation writes notes.txt, and ends its turn
    Then the guard answers nothing to either, and the record gains nothing"""
    g.reviewed("good")
    before = entries()
    assert answer(g.e.write(os.path.join(g.e.cwd, "notes.txt"))) == Answer()
    assert answer(g.e.stop()) == Answer()
    assert entries() == before


@pytest.mark.supports("test_the_plugins_command_typed_again_once_its_run_ended_adds_a_new_run")
def test_the_command_typed_once_its_run_ended_adds_a_new_run(g: Play):
    """Given a run of log:up that ended with the reviewer's `good`
    When the person's /log:up 1.3.0 expands, and the main conversation runs `git status`
    Then the record holds a second run r2 for 1.3.0 with its folder, and the guard gives the writer
    due"""
    g.reviewed("good")
    assert g.opened("1.3.0") == Answer(False, WRITER_DUE)
    second = runs("session-1")[1]
    assert second.entries == [
        {"kind": "run", "run": "r2", "skill": "log:up", "words": "1.3.0"},
        {"kind": "folder", "run": "r2", "plugin_root": g.log},
    ]


@pytest.mark.supports("test_another_skills_command_typed_while_a_subagent_runs_moves_the_run")
def test_another_skills_command_moves_the_run_and_its_subagent_stays_on_its_start(g: Play):
    """Given the writer a1 running in the run of log:up
    When the person's /log:tag expands, the main conversation ends its turn, and a1 writes
    notes.txt
    Then the guard gives the tagger due at the command, the end is stopped with the tagger due, the
    write is stopped by a1's step, and the record holds the one run"""
    g.opened()
    writer = g.started()
    assert answer(g.e.typed("log:tag")) == Answer(False, "Due: log:tagger.")
    assert answer(g.e.stop()) == Answer(True, "Due: log:tagger.")
    assert answer(g.e.write(os.path.join(g.e.cwd, "notes.txt"), writer)) == Answer(
        True, WRITER_WRITES
    )
    assert len(runs("session-1")) == 1


@pytest.mark.supports("test_after_compact_the_run_goes_on_with_its_starts_due")
def test_the_summarys_end_at_compact_lies_outside_and_the_run_goes_on(g: Play):
    """Given the writer due
    When /compact's summary ends, and the main conversation ends its turn
    Then the guard answers nothing to the summary, and stops the end with the writer due"""
    g.opened()
    assert answer(g.e.summary_ended("a9")) == Answer()
    assert answer(g.e.stop()) == Answer(True, WRITER_DUE)


@pytest.mark.supports("test_the_command_typed_after_compact_gives_where_the_run_stands")
def test_the_command_typed_while_its_run_stands_gives_where_it_stands(g: Play):
    """Given the reviewer due in the run of log:up for 1.2.0
    When the person's /log:up 1.2.0 expands again
    Then the guard gives the reviewer due at once, and the record holds one run"""
    g.to_review()
    assert answer(g.e.typed("log:up", "1.2.0")) == Answer(False, REVIEWER_DUE)
    assert len(runs("session-1")) == 1


@pytest.mark.supports("test_a_new_conversation_goes_on_where_the_plugins_own_files_say")
def test_a_new_conversation_takes_its_starts_due_from_the_plugins_order(g: Play):
    """Given `log` deciding its order by ORDER, the conversation's CHANGELOG.md holding the entry
    of 1.2.0, and a conversation with no run
    When the person's /log:up 1.2.0 expands, and the main conversation runs `git status`
    Then the guard gives the reviewer due, as ORDER reads the entry"""
    write_files(g.log, {"lane/adapters/starts_due.py": lane_bench.ORDER})
    write_files(g.e.cwd, {"CHANGELOG.md": lane_bench.ENTRY})
    assert g.opened() == Answer(False, REVIEWER_DUE)


@pytest.mark.supports("test_a_run_whose_order_gives_no_start_due_waits_and_still_holds_its_moves")
def test_a_turns_end_while_the_order_gives_no_start_due_goes_through_and_the_run_stands(g: Play):
    """Given `log` whose adapter of the starts due gives none, and the person's /log:up 1.2.0
    When the main conversation ends its turn, and then writes notes.txt
    Then the end goes through, the record holds no end of the run, and the write is stopped by the
    step `lead`"""
    write_files(g.log, {"lane/adapters/starts_due.py": WAITS})
    assert g.opened() == Answer()
    assert answer(g.e.stop()) == Answer()
    assert not of_kind("ended")
    assert answer(g.e.write(os.path.join(g.e.cwd, "notes.txt"))) == Answer(True, LEAD_WRITES)


@pytest.mark.supports("test_a_run_whose_order_says_it_ends_holds_no_move_after")
def test_the_orders_end_of_the_run_is_kept_as_an_ended_entry(g: Play):
    """Given the reviewer due
    When the reviewer gives `good`, after which log's routes say the run ends, and its end reaches
    the main conversation
    Then the guard says the reviewer gave `good` with no start due, and the record's last entry is
    the run's `ended`"""
    g.to_review()
    reviewer = g.started("log:reviewer", "a2")
    g.reported(reviewer, "result", "good")
    assert answer(g.e.ended(reviewer)) == Answer()
    assert answer(g.e.reached(reviewer, "toolu_2")) == Answer(False, "log:reviewer gave good.")
    assert entries()[-1] == {"kind": "ended", "run": "r1"}


@pytest.mark.supports(
    "test_the_turns_end_in_a_run_of_a_plugin_with_no_order_is_held_to_its_skills_check"
)
def test_a_turns_end_in_a_run_with_no_order_is_held_to_its_skills_check(g: Play):
    """Given `log` giving no order, its skill's step `lead` checked for .log/up.md
    When the person types /log:up 1.2.0, and the main conversation ends its turn before
    .log/up.md is there
    Then the guard stops the end with the check's sentence of `lead`, and the run stands"""
    write_files(g.log, {"lane/rules.json": json.dumps(NO_ORDER)})
    assert g.opened() == Answer()
    assert answer(g.e.stop()) == Answer(True, check_fails("lead", UP_SAYS, "log:up"))
    assert not of_kind("ended")


@pytest.mark.supports(
    "test_a_run_of_a_plugin_with_no_order_ends_at_the_turns_end_that_its_steps_let_through"
)
def test_a_turns_end_that_a_run_with_no_order_lets_through_ends_the_run(g: Play):
    """Given `log` giving no order, and the person's /log:up 1.2.0
    When .log/up.md is there, the main conversation ends its turn, and then writes notes.txt
    Then the end goes through, the record's last entry is the run's `ended`, and the guard answers
    nothing to the write"""
    write_files(g.log, {"lane/rules.json": json.dumps(NO_ORDER)})
    g.opened()
    write_files(g.e.cwd, {".log/up.md": "x\n"})
    assert answer(g.e.stop()) == Answer()
    assert entries()[-1] == {"kind": "ended", "run": "r1"}
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
    """Given the writer a1 running, so that no start is due
    When a1 starts a writer by the Agent tool
    Then the guard stops it, with no start due to give, and the record gains no start"""
    g.opened()
    writer = g.started()
    assert answer(g.e.start("log:writer", "toolu_2", writer)) == Answer(True, "")
    assert len(of_kind("start")) == 1


@pytest.mark.supports("test_a_subagents_message_to_another_subagent_goes_through_as_talk")
def test_a_subagents_message_to_another_subagent_goes_through(g: Play):
    """Given the writer a1 running
    When a1 sends a2 a message by SendMessage
    Then the guard answers nothing"""
    g.opened()
    writer = g.started()
    assert answer(g.e.send(Subagent("a2", "log:writer"), "toolu_2", writer)) == Answer()


# What the plugin's author mends a rule file out of Lane's form to.
MEND = "The plugin's author mends it to the form of Lane's hooks/lane/rules.schema.json."


@pytest.mark.supports("test_rules_out_of_form_stop_the_call_saying_what_the_author_mends")
def test_rules_out_of_form_stop_the_next_event_saying_what_to_mend(g: Play):
    """Given `log` whose lane/rules.json has no roles
    When the person types /log:up 1.2.0, and the main conversation runs `git status`
    Then the guard stops the call, naming the file and the roles, and who mends it to which form"""
    write_files(g.log, {"lane/rules.json": json.dumps({"routes": lane_bench.RULES["routes"]})})
    said = g.opened()
    assert said.stop
    assert said.said.startswith(f"Lane: {os.path.join(g.log, 'lane', 'rules.json')}, at ")
    assert "roles" in said.said
    assert said.said.endswith(MEND)


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


def recorded(log: str, *more: Entry) -> None:
    """The record of session-1 with a run of log:up for 1.2.0 in log's folder, and the entries."""
    add("session-1", [RUN, {"kind": "folder", "run": "r1", "plugin_root": log}, *more])


def gained(log: str) -> list[Entry]:
    """The entries that the record of session-1 gained after the run, its folder, and the entries
    that `recorded` gave it, which `before` counts."""
    return entries()[BEFORE["count"] :]


BEFORE = {"count": 0}


def recorded_now(log: str, *more: Entry) -> None:
    """`recorded`, noting how many entries the record holds."""
    recorded(log, *more)
    BEFORE["count"] = len(entries())


WRITER = Subagent("a1", "log:writer")
START: Entry = lane_entries.start("toolu_1", prompt="You are log:writer.")
TIE: Entry = lane_entries.tie("toolu_1", "a1")
GAVE: Entry = lane_entries.result("a1", "written")
# The writer a1's `written`, and the reviewer a2's `split`, after which two writers are due.
SPLIT: tuple[Entry, ...] = (
    START,
    TIE,
    GAVE,
    lane_entries.start("toolu_2", "log:reviewer"),
    lane_entries.tie("toolu_2", "a2"),
    lane_entries.result("a2", "split", "log:reviewer"),
)


@pytest.mark.supports("test_the_turns_end_while_the_commands_start_is_due_is_stopped_with_it")
def test_skill_called_with_no_run_adds_one_with_no_folder(g: Play):
    """Given a conversation with no run
    When log:up is called with 1.2.0
    Then the answer is empty, and the record holds the run r1 with no folder"""
    assert skill_called(SkillCall("session-1", g.e.transcript, "log:up", "1.2.0")) == Answer()
    assert runs("session-1") == [Run("r1", "session-1", "log:up", "1.2.0", None, [RUN])]


@pytest.mark.supports("test_the_plugins_command_typed_again_once_its_run_ended_adds_a_new_run")
def test_skill_called_after_a_run_adds_the_next(g: Play, log: str):
    """Given a run r1 of log:up that ended
    When log:up is called with 1.3.0
    Then the answer is empty, and the record gains a run r2 of log:up for 1.3.0"""
    recorded_now(log, {"kind": "ended", "run": "r1"})
    assert skill_called(SkillCall("session-1", g.e.transcript, "log:up", "1.3.0")) == Answer()
    assert runs("session-1")[1] == Run(
        "r2",
        "session-1",
        "log:up",
        "1.3.0",
        None,
        [{"kind": "run", "run": "r2", "skill": "log:up", "words": "1.3.0"}],
    )


@pytest.mark.supports(
    "test_the_starts_due_come_at_the_main_conversations_next_event_after_the_skills_call"
)
def test_run_opened_reads_the_folder_and_gives_the_starts_due(g: Play, log: str):
    """Given a run with no folder, and the transcript holding its base directory
    When the run opens at the main conversation's Stop
    Then the answer gives the writer due, and the record gains the run's folder"""
    add("session-1", [RUN])
    base_directory(g.e.transcript, log, "up")
    assert run_opened(g.e.stop(), runs("session-1")[0]) == Answer(False, WRITER_DUE)
    assert entries() == [RUN, {"kind": "folder", "run": "r1", "plugin_root": log}]


@pytest.mark.supports("test_the_starts_due_are_those_that_the_plugins_order_gives")
def test_run_opened_gives_each_role_due_and_how_many_at_once(g: Play, log: str):
    """Given a run with no folder, the transcript holding its base directory, and `log`'s adapter of
    the starts due, which gives the writer twice and the reviewer once
    When the run opens
    Then the answer gives the writer due twice at once and the reviewer, in that order"""
    starts = [{"role": "log:writer", "count": 2}, {"role": "log:reviewer", "count": 1}]
    code = f"import json\n\nprint(json.dumps({{'starts': {starts!r}}}))\n"
    write_files(log, {"lane/adapters/starts_due.py": code})
    add("session-1", [RUN])
    base_directory(g.e.transcript, log, "up")
    said = run_opened(g.e.stop(), runs("session-1")[0])
    assert said == Answer(False, "Due: log:writer 2 times at once, log:reviewer.")


@pytest.mark.supports(
    "test_the_starts_due_come_at_the_main_conversations_next_event_after_the_skills_call"
)
@pytest.mark.parametrize("transcript", [False, True])
def test_run_opened_before_the_base_directory_gives_nothing(g: Play, transcript: bool):
    """Given a run with no folder, and no transcript yet, or one with no base directory
    When the run opens
    Then the answer is empty, and the run has no folder"""
    add("session-1", [RUN])
    if transcript:
        write_files(os.path.dirname(g.e.transcript), {os.path.basename(g.e.transcript): "{}\n"})
    assert run_opened(g.e.stop(), runs("session-1")[0]) == Answer()
    assert entries() == [RUN]


@pytest.mark.supports("test_work_outside_a_run_of_a_plugin_with_rules_is_left_alone")
def test_run_opened_of_a_plugin_with_no_rules_keeps_its_folder_and_gives_nothing(g: Play, log: str):
    """Given a run with no folder, the transcript holding its base directory, and `log` with no
    lane/rules.json
    When the run opens
    Then the answer is empty, and the record gains the run's folder"""
    os.remove(os.path.join(log, "lane", "rules.json"))
    add("session-1", [RUN])
    base_directory(g.e.transcript, log, "up")
    assert run_opened(g.e.stop(), runs("session-1")[0]) == Answer()
    assert entries() == [RUN, {"kind": "folder", "run": "r1", "plugin_root": log}]


@pytest.mark.supports("test_the_start_due_goes_through_and_leaves_none_due")
def test_start_made_of_the_role_due_goes_through_and_keeps_the_start(g: Play, log: str):
    """Given the writer due
    When the main conversation starts the writer with a prompt
    Then the answer is empty, and the record gains the start of the writer with that prompt,
    untied"""
    recorded_now(log)
    said = start_made(move("start", g.e.start("log:writer", "toolu_1", prompt="Write it.")))
    assert said == Answer()
    assert gained(log) == [lane_entries.start("toolu_1", prompt="Write it.")]


@pytest.mark.supports("test_another_start_of_the_plugins_subagents_is_stopped_with_the_starts_due")
def test_start_made_of_a_role_not_due_is_stopped_with_the_starts_due(g: Play, log: str):
    """Given the writer due
    When the main conversation starts the reviewer
    Then the answer stops it with the writer due, and the record gains nothing"""
    recorded_now(log)
    assert start_made(move("start", g.e.start("log:reviewer", "toolu_1"))) == Answer(
        True, WRITER_DUE
    )
    assert gained(log) == []


@pytest.mark.supports("test_a_start_of_a_subagent_that_isnt_the_plugins_lies_outside_the_run")
@pytest.mark.parametrize("role", ["general-purpose", "logger:writer", "lo:writer"])
def test_start_made_of_another_plugins_subagent_goes_through_and_keeps_nothing(
    g: Play, log: str, role: str
):
    """Given the writer due
    When the main conversation starts general-purpose, or a subagent of another plugin whose name
    begins as log's, or one that log's begins with
    Then the answer is empty, and the record gains nothing"""
    recorded_now(log)
    assert start_made(move("start", g.e.start(role, "toolu_1"))) == Answer()
    assert gained(log) == []


@pytest.mark.supports("test_a_subagents_start_of_a_subagent_is_stopped")
@pytest.mark.parametrize("role", ["log:writer", "general-purpose"])
def test_start_made_by_a_subagent_is_stopped(g: Play, log: str, role: str):
    """Given the writer due, and a writer a1 tied to an earlier start
    When a1 starts a writer, or general-purpose
    Then the answer stops it with the writer due, and the record gains nothing"""
    recorded_now(log, START, TIE, {"kind": "stopped", "run": "r1", "agent_id": "a1"})
    said = start_made(move("start", g.e.start(role, "toolu_2", WRITER), WRITER))
    assert said == Answer(True, WRITER_DUE)
    assert gained(log) == []


@pytest.mark.supports("test_a_role_named_twice_in_a_route_is_due_twice_at_once")
def test_start_made_of_a_role_due_twice_lets_two_starts_through_and_stops_a_third(
    g: Play, log: str
):
    """Given the reviewer's `split`, which makes the writer due twice at once
    When the main conversation starts the writer three times
    Then the first two go through and the record gains their starts, and the third is stopped
    with no start due to give"""
    recorded_now(log, *SPLIT)
    said = [
        start_made(move("start", g.e.start("log:writer", use, prompt="Write it.")))
        for use in ("toolu_3", "toolu_4", "toolu_5")
    ]
    assert said == [Answer(), Answer(), Answer(True, "")]
    assert gained(log) == [
        lane_entries.start("toolu_3", prompt="Write it."),
        lane_entries.start("toolu_4", prompt="Write it."),
    ]


@pytest.mark.supports(
    "test_a_role_with_no_fixed_steps_takes_them_from_the_plugins_adapter_for_each_start"
)
def test_start_made_of_a_role_with_no_steps_keeps_the_steps_its_adapter_gives(g: Play, log: str):
    """Given `log` naming the writer with no steps, with its adapter of the rules, and the writer
    due
    When the main conversation starts the writer to write docs/changes/1.2.0.md
    Then the start goes through, and the record gains it with the step that the adapter gave"""
    write_files(log, {"lane/rules.json": json.dumps(lane_bench.ADAPTED)})
    write_files(log, {"lane/adapters/rules.py": lane_bench.RULES_ADAPTER})
    recorded_now(log)
    prompt = "Write docs/changes/1.2.0.md."
    assert start_made(move("start", g.e.start("log:writer", "toolu_1", prompt=prompt))) == Answer()
    steps: list[Step] = [
        {"name": "write", "rules": [{"type": "writes", "paths": ["docs/changes/1.2.0.md"]}]}
    ]
    assert gained(log) == [{**lane_entries.start("toolu_1", prompt=prompt), "steps": steps}]


@pytest.mark.supports(
    "test_a_start_of_a_role_with_no_steps_and_no_adapter_of_the_rules_is_stopped_saying_so"
)
def test_start_made_of_a_role_with_no_steps_and_no_adapter_is_stopped_naming_it(g: Play, log: str):
    """Given `log` naming the writer with no steps, with no adapter of the rules, and the writer due
    When the main conversation starts the writer
    Then the guard stops it, naming lane/adapters/rules.py, the writer, and `log`'s folder, and
    the record gains nothing"""
    write_files(log, {"lane/rules.json": json.dumps(lane_bench.ADAPTED)})
    recorded_now(log)
    said = start_made(move("start", g.e.start("log:writer", "toolu_1")))
    assert said.stop
    for named in ("lane/adapters/rules.py", "log:writer", log):
        assert named in said.said
    assert gained(log) == []


@pytest.mark.supports(
    "test_an_adapter_of_the_rules_that_fails_or_gives_out_of_its_form_stops_the_start"
)
def test_start_made_with_an_adapter_of_the_rules_that_fails_is_stopped_with_what_it_said(
    g: Play, log: str
):
    """Given `log` naming the writer with no steps, whose adapter of the rules exits 1 saying it
    found no prompt, and the writer due
    When the main conversation starts the writer
    Then the guard stops it, naming the adapter's path and what it said, and the record gains
    nothing"""
    write_files(log, {"lane/rules.json": json.dumps(lane_bench.ADAPTED)})
    write_files(log, {"lane/adapters/rules.py": "import sys\n\nsys.exit('no prompt')\n"})
    recorded_now(log)
    said = start_made(move("start", g.e.start("log:writer", "toolu_1")))
    assert said.stop
    assert os.path.join(log, "lane", "adapters", "rules.py") in said.said
    assert "no prompt" in said.said
    assert gained(log) == []


@pytest.mark.supports("test_a_resume_that_the_order_makes_due_goes_through_as_its_start")
@pytest.mark.parametrize("adapted", [False, True])
def test_start_made_of_a_resume_keeps_the_prompt_and_steps_of_the_start_it_resumes(
    g: Play, log: str, adapted: bool
):
    """Given the writer a1's start, its `written`, and the reviewer's `more`, so that the writer is
    due; and `log` naming the writer with its steps, or with none and giving no adapter of the
    rules now, a1's start holding the steps that the adapter gave
    When the main conversation resumes a1 by SendMessage
    Then the resume goes through, and the record gains its start with a1's prompt and, where a1's
    start holds steps, those steps"""
    given: list[Step] = [
        {"name": "write", "rules": [{"type": "writes", "paths": ["CHANGELOG.md"]}]}
    ]
    first: Entry = {**START, "steps": given} if adapted else START
    if adapted:
        write_files(log, {"lane/rules.json": json.dumps(lane_bench.ADAPTED)})
    reviewer: list[Entry] = [
        lane_entries.start("toolu_2", "log:reviewer"),
        lane_entries.tie("toolu_2", "a2"),
        lane_entries.result("a2", "more", "log:reviewer"),
    ]
    recorded_now(log, first, TIE, GAVE, *reviewer)
    assert start_made(resume(g, first)) == Answer()
    assert gained(log) == [{**first, "tool_use_id": "toolu_3"}]


def resume(
    g: Play, resumed: Entry, prompt: str | None = None, steps: list[Step] | None = None
) -> Move:
    """The start move of the main conversation's SendMessage toolu_3 to a1, as place gives it: with
    the role, the prompt, and the steps of the start it resumes, or the prompt and steps given."""
    held = steps or resumed.get("steps") or lane_bench.RULES["roles"]["log:writer"]["steps"]
    [run] = runs("session-1")
    event = g.e.send(WRITER, "toolu_3")
    return Move(
        "start", event, run, "log:writer", None, prompt or resumed["prompt"], held, None, None
    )


@pytest.mark.supports("test_a_resume_that_the_order_makes_due_goes_through_as_its_start")
@pytest.mark.xfail(
    strict=True,
    reason="start_made takes a resume's role, prompt, and steps from its move, as place gives them,"
    " and doesn't find the start it resumes again",
)
def test_start_made_of_a_resume_keeps_the_prompt_and_steps_that_its_move_carries(g: Play, log: str):
    """Given `log` naming the writer with no steps, the writer a1's start, its `written`, and the
    reviewer's `more`, so that the writer is due
    When the main conversation resumes a1, its move carrying the prompt `Write it again.` and the
    step `redo`
    Then the resume goes through, and the record gains its start with that prompt and step"""
    write_files(log, {"lane/rules.json": json.dumps(lane_bench.ADAPTED)})
    first: Entry = {**START, "steps": [{"name": "write", "rules": []}]}
    redo: list[Step] = [{"name": "redo", "rules": []}]
    reviewer: list[Entry] = [
        lane_entries.start("toolu_2", "log:reviewer"),
        lane_entries.tie("toolu_2", "a2"),
        lane_entries.result("a2", "more", "log:reviewer"),
    ]
    recorded_now(log, first, TIE, GAVE, *reviewer)
    assert start_made(resume(g, first, "Write it again.", redo)) == Answer()
    assert gained(log) == [
        {**first, "tool_use_id": "toolu_3", "prompt": "Write it again.", "steps": redo}
    ]


@pytest.mark.supports(
    "test_an_adapter_of_the_starts_due_that_fails_stops_with_the_adapter_and_what_it_said"
)
@pytest.mark.parametrize("kind", ["turn_end", "start"])
def test_a_move_with_an_adapter_of_the_starts_due_that_fails_stops_with_what_it_said(
    g: Play, log: str, kind: str
):
    """Given `log` whose adapter of the starts due exits 1 saying it found no version, and the
    writer tied to a1 with its `written`
    When the main conversation ends its turn, or starts the writer
    Then the guard stops the move, naming the adapter's path and what it said"""
    write_files(log, {"lane/adapters/starts_due.py": "import sys\n\nsys.exit('no version')\n"})
    recorded(log, START, TIE, GAVE)
    if kind == "turn_end":
        said = turn_ended(move("turn_end", g.e.stop()))
    else:
        said = start_made(move("start", g.e.start("log:writer", "toolu_2")))
    assert said.stop
    assert os.path.join(log, "lane", "adapters", "starts_due.py") in said.said
    assert "no version" in said.said


@pytest.mark.supports(
    "test_an_adapter_of_the_starts_due_that_fails_stops_with_the_adapter_and_what_it_said"
)
@pytest.mark.parametrize("kind", ["typed", "result_reached"])
def test_a_command_or_a_result_with_an_adapter_of_the_starts_due_that_fails_is_refused(
    g: Play, log: str, kind: str
):
    """Given `log` whose adapter of the starts due exits 1 saying it found no version, and the
    writer tied to a1 with its `written`
    When the person types /log:retry, or a1's end reaches the main conversation
    Then the interface refuses with AdapterFailed naming the adapter's path and what it said, and
    answer stops the event with it"""
    write_files(log, {"lane/adapters/starts_due.py": "import sys\n\nsys.exit('no version')\n"})
    recorded(log, START, TIE, GAVE)
    event = g.e.typed("log:retry") if kind == "typed" else g.e.reached(WRITER, "toolu_1")
    with pytest.raises(AdapterFailed) as raised:
        if kind == "typed":
            command_typed(move("typed", event))
        else:
            result_reached(move("result_reached", event, WRITER))
    said = answer(event)
    assert said == Answer(True, str(raised.value))
    assert os.path.join(log, "lane", "adapters", "starts_due.py") in said.said
    assert "no version" in said.said


@pytest.mark.supports("test_the_turns_end_while_the_commands_start_is_due_is_stopped_with_it")
@pytest.mark.parametrize("more, said", [((), Answer(True, WRITER_DUE)), ((START, TIE), Answer())])
def test_turn_ended_stops_only_while_a_start_is_due(
    g: Play, log: str, more: tuple[Entry, ...], said: Answer
):
    """Given the writer due, or tied to a1
    When the main conversation ends its turn
    Then the end is stopped with the writer due, or goes through, and the record gains nothing"""
    recorded_now(log, *more)
    assert turn_ended(move("turn_end", g.e.stop())) == said
    assert gained(log) == []


@pytest.mark.supports("test_a_start_that_another_plugins_hook_denies_is_due_again_at_the_turns_end")
def test_turn_ended_drops_each_start_still_untied(g: Play, log: str):
    """Given the writer's start tied to a1, and two other starts untied
    When the main conversation ends its turn
    Then the record gains the drop of each untied start, in their order, alone"""
    recorded_now(log, START, TIE, lane_entries.start("toolu_3"), lane_entries.start("toolu_4"))
    turn_ended(move("turn_end", g.e.stop()))
    assert gained(log) == [
        {"kind": "drop", "run": "r1", "tool_use_id": "toolu_3"},
        {"kind": "drop", "run": "r1", "tool_use_id": "toolu_4"},
    ]


@pytest.mark.supports(
    "test_the_turns_end_in_a_run_of_a_plugin_with_no_order_is_held_to_its_skills_check"
)
def test_turn_ended_that_breaks_its_step_is_stopped_and_drops_its_untied_starts(g: Play, log: str):
    """Given `log` giving no order, its step `lead` checked for .log/up.md, which isn't there, and
    an untied start
    When the main conversation ends its turn
    Then the end is stopped with the check's sentence of `lead`, and the record gains the start's
    drop and no end of the run"""
    write_files(log, {"lane/rules.json": json.dumps(NO_ORDER)})
    recorded_now(log, START)
    ended = dataclasses.replace(
        move("turn_end", g.e.stop(), step="lead"), steps=NO_ORDER["roles"]["log:up"]["steps"]
    )
    assert turn_ended(ended) == Answer(True, check_fails("lead", UP_SAYS, "log:up"))
    assert gained(log) == [{"kind": "drop", "run": "r1", "tool_use_id": "toolu_1"}]


@pytest.mark.supports(
    "test_a_run_of_a_plugin_with_no_order_ends_at_the_turns_end_that_its_steps_let_through"
)
def test_turn_ended_that_its_steps_let_through_ends_a_run_with_no_order(g: Play, log: str):
    """Given `log` giving no order, its step `lead` checked for .log/up.md, which is there
    When the main conversation ends its turn
    Then the end goes through, and the record gains the run's `ended`"""
    write_files(log, {"lane/rules.json": json.dumps(NO_ORDER)})
    write_files(g.e.cwd, {".log/up.md": "x\n"})
    recorded_now(log)
    ended = dataclasses.replace(
        move("turn_end", g.e.stop(), step="lead"), steps=NO_ORDER["roles"]["log:up"]["steps"]
    )
    assert turn_ended(ended) == Answer()
    assert gained(log) == [{"kind": "ended", "run": "r1"}]


@pytest.mark.supports("test_a_typed_command_that_a_route_goes_after_puts_its_starts_in_place")
def test_command_typed_gives_its_routes_starts(g: Play, log: str):
    """Given the writer tied to a1
    When the person types /log:retry
    Then the answer gives the writer due, and the record gains the command"""
    recorded_now(log, START, TIE)
    assert command_typed(move("typed", g.e.typed("log:retry"))) == Answer(False, WRITER_DUE)
    assert gained(log) == [{"kind": "typed", "run": "r1", "command": "log:retry"}]


@pytest.mark.supports("test_the_command_typed_after_compact_gives_where_the_run_stands")
def test_command_typed_of_the_skill_that_called_the_run_gives_where_it_stands(g: Play, log: str):
    """Given the writer a1's result `written`, so the reviewer is due
    When the person types /log:up again
    Then the answer gives the reviewer due, and not the writer, and the record gains the command"""
    recorded_now(log, START, TIE, GAVE)
    assert command_typed(move("typed", g.e.typed("log:up", "1.2.0"))) == Answer(False, REVIEWER_DUE)
    assert gained(log) == [{"kind": "typed", "run": "r1", "command": "log:up"}]


@pytest.mark.supports("test_another_skills_command_typed_while_a_subagent_runs_moves_the_run")
def test_command_typed_of_another_skill_gives_its_routes_starts(g: Play, log: str):
    """Given the writer tied to a1
    When the main conversation calls log:tag by the Skill tool
    Then the answer gives the tagger due, and the record gains the command"""
    recorded_now(log, START, TIE)
    said = command_typed(move("typed", g.e.skill_post("log:tag", "")))
    assert said == Answer(False, "Due: log:tagger.")
    assert gained(log) == [{"kind": "typed", "run": "r1", "command": "log:tag"}]


@pytest.mark.supports("test_a_result_that_no_route_goes_after_ends_the_run_once_no_start_runs")
def test_command_typed_that_no_route_goes_after_ends_the_run(g: Play, log: str):
    """Given `log` whose routes go after no /log:retry, and the writer a1's `written` and the
    reviewer's `good`, so that no start runs
    When the person types /log:retry
    Then the answer gives nothing, and the record gains the command and the run's `ended`"""
    rules = copy.deepcopy(lane_bench.RULES)
    rules["routes"] = [
        each for each in rules["routes"] if each["after"] != {"command": "log:retry"}
    ]
    write_files(log, {"lane/rules.json": json.dumps(rules)})
    recorded_now(log, START, TIE, GAVE)
    assert command_typed(move("typed", g.e.typed("log:retry"))) == Answer()
    assert gained(log) == [
        {"kind": "typed", "run": "r1", "command": "log:retry"},
        {"kind": "ended", "run": "r1"},
    ]


@pytest.mark.supports("test_a_result_reaching_the_main_conversation_gives_the_starts_due_after_it")
@pytest.mark.parametrize(
    "results, said",
    [
        (("written",), f"log:writer gave written. {REVIEWER_DUE}"),
        (("unclear", "written"), f"log:writer gave written. {REVIEWER_DUE}"),
    ],
)
def test_result_reached_gives_the_latest_result_and_its_routes_starts(
    g: Play, log: str, results: tuple[str, ...], said: str
):
    """Given the writer a1's result `written`, or `unclear` and then `written`
    When its end reaches the main conversation
    Then the answer gives `written` and the reviewer due, and the record gains nothing"""
    recorded_now(log, START, TIE, *[lane_entries.result("a1", each) for each in results])
    given = move("result_reached", g.e.reached(WRITER, "toolu_1"), WRITER)
    assert result_reached(given) == Answer(False, said)
    assert gained(log) == []


@pytest.mark.supports("test_a_role_named_twice_in_a_route_is_due_twice_at_once")
def test_result_reached_gives_a_role_due_twice_at_once(g: Play, log: str):
    """Given the reviewer a2's `split`, which makes the writer due twice at once
    When its end reaches the main conversation
    Then the answer gives `split` and the writer due twice at once"""
    recorded(log, *SPLIT)
    given = move(
        "result_reached",
        g.e.reached(Subagent("a2", "log:reviewer"), "toolu_2"),
        Subagent("a2", "log:reviewer"),
    )
    said = result_reached(given)
    assert said == Answer(False, "log:reviewer gave split. Due: log:writer 2 times at once.")


@pytest.mark.supports("test_a_result_said_only_in_the_reply_counts_for_nothing")
def test_result_reached_of_a_subagent_with_no_result_gives_the_starts_due_alone(g: Play, log: str):
    """Given the writer tied to a1, which gave no result, and `log` whose routes start the writer
    after /log:retry, typed since
    When a1's end reaches the main conversation, its reply saying `written`
    Then the answer gives the writer due alone, and no result"""
    recorded(log, START, TIE, {"kind": "typed", "run": "r1", "command": "log:retry"})
    given = move("result_reached", g.e.reached(WRITER, "toolu_1", "written"), WRITER)
    assert result_reached(given) == Answer(False, WRITER_DUE)


@pytest.mark.supports("test_a_run_whose_order_says_it_ends_holds_no_move_after")
def test_result_reached_after_which_the_run_ends_gives_the_result_and_ends_it(g: Play, log: str):
    """Given the writer a1's `written` and the reviewer a2's `good`
    When a2's end reaches the main conversation
    Then the answer gives `good` alone, and the record gains the run's `ended`"""
    reviewer = Subagent("a2", "log:reviewer")
    recorded_now(log, *SPLIT[:5], lane_entries.result("a2", "good", "log:reviewer"))
    said = result_reached(move("result_reached", g.e.reached(reviewer, "toolu_2"), reviewer))
    assert said == Answer(False, "log:reviewer gave good.")
    assert gained(log) == [{"kind": "ended", "run": "r1"}]


@pytest.mark.supports("test_a_subagent_stopped_by_task_stop_is_due_again")
def test_result_reached_of_a_subagent_stopped_gives_its_start_due_again(g: Play, log: str):
    """Given the writer tied to a1, with no result
    When its notification says TaskStop stopped it
    Then the answer says it stopped with no result and gives the writer due again, and the record
    gains a1's start stopped"""
    recorded_now(log, START, TIE)
    said = result_reached(move("result_reached", g.e.killed(WRITER, "toolu_1"), WRITER))
    assert said == Answer(False, f"log:writer stopped with no result. {WRITER_DUE}")
    assert gained(log) == [{"kind": "stopped", "run": "r1", "agent_id": "a1"}]


@pytest.mark.supports("test_the_start_due_goes_through_and_leaves_none_due")
@pytest.mark.parametrize("kind", ["tie", "drop", "read"])
def test_fact_added_adds_its_fact_and_answers_nothing(g: Play, log: str, kind: str):
    """Given the writer's start, untied for a tie or a drop, and tied for a read
    When the fact's move comes: a1's tie, the drop of the start's call, or a1's read of the lines 1
    to 5 of the 6 of NOTES.md
    Then the answer is empty, and the record gains the fact alone"""
    cwd = g.e.cwd
    events = {
        "tie": (g.e.started(WRITER, "toolu_1"), (START,), WRITER, None),
        "drop": (g.e.start_failed("log:writer", "toolu_1"), (START,), None, None),
        "read": (
            g.e.read_ran(os.path.join(cwd, "NOTES.md"), 1, 5, 6, WRITER),
            (START, TIE),
            WRITER,
            "write",
        ),
    }
    facts: dict[str, Entry] = {
        "tie": {"agent_id": "a1", "tool_use_id": "toolu_1"},
        "drop": {"agent_id": None, "tool_use_id": "toolu_1"},
        "read": {"agent_id": "a1", "path": "NOTES.md", "first_line": 1, "last_line": 5},
    }
    event, more, agent, step = events[kind]
    recorded_now(log, *more)
    assert fact_added(move(kind, event, agent, step)) == Answer()
    assert gained(log) == [{"kind": kind, "run": "r1", **facts[kind]}]


@pytest.mark.supports("test_a_step_marked_done_after_a_read_in_part_names_the_lines_not_read")
@pytest.mark.parametrize("first, count, last", [(1, 1, 1), (3, 4, 6)])
def test_fact_added_keeps_a_reads_first_and_last_line(
    g: Play, log: str, first: int, count: int, last: int
):
    """Given the writer tied to a1
    When a1 reads one line of NOTES.md from its line 1, or 4 lines from its line 3
    Then the record gains the read of the lines 1 to 1, or 3 to 6"""
    recorded_now(log, START, TIE)
    given = g.e.read_ran(os.path.join(g.e.cwd, "NOTES.md"), first, count, 6, WRITER)
    fact_added(move("read", given, WRITER, "write"))
    assert gained(log) == [
        {
            "kind": "read",
            "run": "r1",
            "agent_id": "a1",
            "path": "NOTES.md",
            "first_line": first,
            "last_line": last,
        }
    ]


@pytest.mark.supports("test_a_write_of_a_file_that_its_step_doesnt_name_is_stopped_with_the_step")
@pytest.mark.parametrize(
    "name, said", [("notes.txt", Answer(True, WRITER_WRITES)), ("CHANGELOG.md", Answer())]
)
def test_call_made_stops_only_a_call_that_breaks_its_step(
    g: Play, log: str, name: str, said: Answer
):
    """Given the writer tied to a1 at its step `write`
    When a1 writes notes.txt, or CHANGELOG.md
    Then the first is stopped with the step's sentence, and the second goes through, and the
    record gains nothing"""
    recorded_now(log, START, TIE)
    given = move("call", g.e.write(os.path.join(g.e.cwd, name), WRITER), WRITER, "write")
    assert call_made(given) == said
    assert gained(log) == []


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


@pytest.mark.supports("test_a_step_marked_done_with_a_file_unread_is_stopped_with_the_file")
def test_report_made_of_a_step_whose_rules_break_gives_the_sentence_and_marks_nothing(
    g: Play, log: str
):
    """Given the writer tied to a1, which read nothing and marked no item
    When it reports the step `write` done
    Then the answer stops it with the sentence of reads_whole, and the record gains nothing"""
    recorded_now(log, START, TIE)
    said = report_made(report_move(g, "step", "write"))
    assert said == Answer(True, reads_whole_of("write", ["NOTES.md"], ["NOTES.md from its line 1"]))
    assert gained(log) == []


@pytest.mark.supports("test_steps_marked_in_their_order_hold_and_the_end_goes_through")
def test_report_made_of_a_step_whose_rules_hold_adds_its_mark(g: Play, log: str):
    """Given the writer tied to a1, which read NOTES.md whole and marked each item of `write`
    When it reports the step `write` done
    Then the answer is empty, and the record gains a1's mark of `write` by its role"""
    items = [
        {"kind": "mark", "run": "r1", "agent_id": "a1", "step": "write", "item": each}
        for each in ("dated", "linked")
    ]
    read: Entry = lane_entries.read("a1", "NOTES.md", 1, 6)
    recorded_now(log, START, TIE, read, *items)
    assert report_made(report_move(g, "step", "write")) == Answer()
    assert gained(log) == [
        {"kind": "mark", "step": "write", "run": "r1", "role": "log:writer", "agent_id": "a1"}
    ]


@pytest.mark.supports("test_a_step_marked_once_each_item_is_done_holds")
@pytest.mark.parametrize(
    "kind, words, entry",
    [
        (
            "item",
            ("write", "dated"),
            {"kind": "mark", "step": "write", "item": "dated", "role": "log:writer"},
        ),
        ("result", ("written",), {"kind": "result", "result": "written", "role": "log:writer"}),
    ],
)
def test_report_made_of_an_item_or_a_result_adds_it_though_its_step_breaks_its_rules(
    g: Play, log: str, kind: str, words: tuple[str, ...], entry: Entry
):
    """Given the writer tied to a1, which read nothing and marked no item, so that a mark of
    `write` would break its rules
    When it reports the item `dated` of `write`, or the result `written`
    Then the answer is empty, and the record gains a1's mark of the item, or its result, by its
    role"""
    recorded_now(log, START, TIE)
    assert report_made(report_move(g, kind, *words)) == Answer()
    assert gained(log) == [{**entry, "run": "r1", "agent_id": "a1"}]


@pytest.mark.supports("test_an_end_with_no_result_is_stopped_with_the_results_it_may_give")
def test_subagent_ended_with_no_result_is_stopped(g: Play, log: str):
    """Given the writer tied to a1, with no result
    When it ends
    Then the answer stops it with the result rule of `report`, and the record gains nothing"""
    recorded_now(log, START, TIE)
    said = subagent_ended(move("end", g.e.ended(WRITER), WRITER, "write"))
    assert said == Answer(True, no_result("report", ["written"]))
    assert gained(log) == []


@pytest.mark.supports("test_steps_marked_in_their_order_hold_and_the_end_goes_through")
def test_subagent_ended_that_holds_answers_nothing_and_adds_nothing(g: Play, log: str):
    """Given the writer tied to a1, which kept each step and gave `written`
    When it ends
    Then the answer is empty, and the record gains nothing"""
    marks: list[Entry] = [
        {"kind": "mark", "run": "r1", "agent_id": "a1", "step": "write"},
        {"kind": "mark", "run": "r1", "agent_id": "a1", "step": "report"},
        GAVE,
    ]
    recorded_now(log, START, TIE, *marks)
    assert subagent_ended(move("end", g.e.ended(WRITER), WRITER, None)) == Answer()
    assert gained(log) == []


# written, by each event and class of answer.


@pytest.mark.supports("test_a_stopped_call_gives_the_step_left_and_what_to_do_instead")
def test_a_stop_at_pre_tool_use_is_a_deny_with_its_reason(g: Play):
    """Given the guard's stop with the step's sentence
    When it's written for a PreToolUse
    Then Claude Code reads a deny with the sentence as its reason, and nothing more"""
    out = written(g.e.write("/repo/notes.txt", WRITER), Answer(True, "Write CHANGELOG.md."))
    assert json.loads(out) == {
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "deny",
            "permissionDecisionReason": "Write CHANGELOG.md.",
        }
    }


@pytest.mark.supports("test_the_turns_end_while_the_commands_start_is_due_is_stopped_with_it")
@pytest.mark.parametrize(
    "event", ["stop", "subagent_stop", "post_tool_use", "user_prompt_submit", "expansion"]
)
def test_a_stop_at_another_event_is_a_block_with_its_reason(g: Play, event: str):
    """Given the guard's stop with the starts due
    When it's written for a Stop, a SubagentStop, a PostToolUse, a UserPromptSubmit, or a
    UserPromptExpansion
    Then Claude Code reads a block with them as its reason, and nothing more"""
    given = {
        "stop": g.e.stop(),
        "subagent_stop": g.e.ended(WRITER),
        "post_tool_use": g.e.bash_ran("lane-step write", "", WRITER),
        "user_prompt_submit": g.e.reached(WRITER, "toolu_1"),
        "expansion": g.e.typed("log:retry"),
    }[event]
    out = written(given, Answer(True, "Start log:writer."))
    assert json.loads(out) == {"decision": "block", "reason": "Start log:writer."}


@pytest.mark.supports("test_a_result_reaching_the_main_conversation_gives_the_starts_due_after_it")
@pytest.mark.parametrize(
    "event, name",
    [("reached", "UserPromptSubmit"), ("bash", "PreToolUse"), ("expansion", "UserPromptExpansion")],
)
def test_what_the_guard_says_without_a_stop_is_additional_context(g: Play, event: str, name: str):
    """Given the guard's answer that stops nothing and gives the starts due
    When it's written for the UserPromptSubmit of a task-notification, the PreToolUse of a Bash
    call, or the UserPromptExpansion of a command
    Then Claude Code reads them as additional context of that event, and nothing more"""
    given = {
        "reached": g.e.reached(WRITER, "toolu_1"),
        "bash": g.e.bash("git status"),
        "expansion": g.e.typed("log:retry"),
    }[event]
    out = written(given, Answer(False, "Start log:reviewer."))
    assert json.loads(out) == {
        "hookSpecificOutput": {"hookEventName": name, "additionalContext": "Start log:reviewer."}
    }


@pytest.mark.supports("test_work_outside_a_run_of_a_plugin_with_rules_is_left_alone")
@pytest.mark.parametrize("event", ["stop", "bash"])
def test_an_empty_answer_is_written_as_nothing(g: Play, event: str):
    """Given the guard's empty answer
    When it's written for a Stop, or a PreToolUse
    Then the guard writes nothing"""
    given = g.e.stop() if event == "stop" else g.e.bash("git status")
    assert written(given, Answer()) == ""
