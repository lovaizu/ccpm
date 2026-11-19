"""The unit cases of hooks/lane/rule_types/: each rule type's judge, one for each class of the call,
the mark, or the end it judges, with the edges of a path's folder and of a file's lines; and the
order in which rule_types/__init__.py asks them, one for each combination of rules that a move
breaks."""

from __future__ import annotations

import copy
import os
from typing import Any

import lane_bench
import pytest
import rule_types
from lane_events import Event, Events, Subagent
from place import Move
from record import Entry, Run
from report import Report
from rule_types import check, checklist, commands, order, reads_none, reads_whole, result, writes
from rules import Rule, Rules, Step

pytestmark = pytest.mark.xfail(strict=True, reason="Lane's parts have no bodies yet")

RULES: Rules = copy.deepcopy(lane_bench.RULES)
WRITE: Step = RULES["roles"]["log:writer"]["steps"][0]
REPORT: Step = RULES["roles"]["log:writer"]["steps"][1]
REVIEW: Step = RULES["roles"]["log:reviewer"]["steps"][0]
WRITER = Subagent("a1", "log:writer")
OTHER = Subagent("a2", "log:writer")


def rule(step: Step, kind: str) -> Rule:
    """The step's rule of the type."""
    return next(each for each in step["rules"] if each["type"] == kind)


@pytest.fixture
def e(cwd: str) -> Events:
    return Events(cwd, os.path.join(os.path.dirname(cwd), "transcripts", "session-1.jsonl"))


def mark(step: str, agent: Subagent = WRITER, item: str | None = None) -> Entry:
    entry: Entry = {"kind": "mark", "run": "r1", "agent_id": agent.id, "step": step}
    if item:
        entry["item"] = item
    return entry


def read(path: str, first: int, last: int, agent: Subagent = WRITER) -> Entry:
    return {
        "kind": "read",
        "run": "r1",
        "agent_id": agent.id,
        "path": path,
        "first_line": first,
        "last_line": last,
    }


def gave(value: str, agent: Subagent = WRITER) -> Entry:
    return {
        "kind": "result",
        "run": "r1",
        "agent_id": agent.id,
        "role": agent.type,
        "result": value,
    }


def move(
    kind: str,
    event: Event,
    *entries: Entry,
    step: str = "write",
    report: Report | None = None,
    agent: Subagent = WRITER,
) -> Move:
    """The move of the kind by the agent, at the step, on a run whose writer a1 and a2 are tied
    and whose record holds the entries after."""
    head: list[Entry] = [
        {"kind": "run", "run": "r1", "skill": "log:up", "words": "1.2.0"},
        {"kind": "start", "run": "r1", "role": "log:writer", "tool_use_id": "u1"},
        {"kind": "tie", "run": "r1", "tool_use_id": "u1", "agent_id": "a1"},
        {"kind": "start", "run": "r1", "role": "log:writer", "tool_use_id": "u2"},
        {"kind": "tie", "run": "r1", "tool_use_id": "u2", "agent_id": "a2"},
    ]
    run = Run("r1", "session-1", "log:up", "1.2.0", "/plugins/log", [*head, *entries])
    return Move(kind, event, run, agent.type, agent.id, None, step, report)


def marked(step: str) -> Report:
    return {"kind": "step", "step": step}


# writes


@pytest.mark.supports("test_a_write_of_a_file_that_its_step_names_goes_through")
@pytest.mark.parametrize("path", ["CHANGELOG.md", "docs/changes/1.2.0.md", "docs/changes/a/b.md"])
def test_a_write_of_a_named_file_or_one_under_a_named_folder_holds(e: Events, cwd: str, path: str):
    """Given the step `write`, which writes CHANGELOG.md and docs/changes/
    When the writer writes the named file, a file in the folder, or one deeper in it
    Then the rule finds nothing"""
    call = move("call", e.write(os.path.join(cwd, path), WRITER))
    assert writes.judge_call(rule(WRITE, "writes"), WRITE, call) is None


@pytest.mark.supports("test_a_write_of_a_file_that_its_step_doesnt_name_is_stopped_with_the_step")
@pytest.mark.parametrize(
    "path", ["notes.txt", "docs/changes-old.md", "docs/CHANGELOG.md", "../CHANGELOG.md"]
)
def test_a_write_of_another_file_gives_the_steps_sentence(e: Events, cwd: str, path: str):
    """Given the step `write`
    When the writer writes another file, one whose name only begins as the folder's, one of the
    named name in another folder, or one outside the conversation's folder
    Then the rule gives the step's sentence, naming the step and the files it writes"""
    call = move("call", e.write(os.path.normpath(os.path.join(cwd, path)), WRITER))
    said = writes.judge_call(rule(WRITE, "writes"), WRITE, call)
    assert said is not None
    for named in ("write", "CHANGELOG.md", "docs/changes/"):
        assert named in said


@pytest.mark.supports("test_an_edit_of_a_file_that_its_step_doesnt_name_is_stopped")
def test_an_edit_of_another_file_gives_the_steps_sentence(e: Events, cwd: str):
    """Given the step `write`
    When the writer edits README.md
    Then the rule gives the step's sentence"""
    call = move("call", e.write(os.path.join(cwd, "README.md"), WRITER, tool="Edit"))
    assert writes.judge_call(rule(WRITE, "writes"), WRITE, call) is not None


# reads_none


@pytest.mark.supports("test_a_read_of_a_file_under_a_folder_never_to_read_is_stopped_with_the_step")
@pytest.mark.parametrize("path", ["secrets/key.txt", "secrets/a/b.txt", ".env"])
def test_a_read_of_a_file_never_to_read_gives_the_steps_sentence(e: Events, cwd: str, path: str):
    """Given the step `write`, which never reads secrets/ nor .env
    When the writer reads a file in the folder, one deeper in it, or the named file
    Then the rule gives the step's sentence, naming the step and the files it never reads"""
    call = move("call", e.read(os.path.join(cwd, path), WRITER))
    said = reads_none.judge_call(rule(WRITE, "reads_none"), WRITE, call)
    assert said is not None
    for named in ("write", "secrets/", ".env"):
        assert named in said


@pytest.mark.supports("test_a_read_of_another_file_goes_through")
@pytest.mark.parametrize("path", ["NOTES.md", "secrets-old/key.txt", ".env.example"])
def test_a_read_of_another_file_holds(e: Events, cwd: str, path: str):
    """Given the step `write`
    When the writer reads another file, one in a folder whose name only begins as the rule's, or
    one whose name only begins as a named file's
    Then the rule finds nothing"""
    call = move("call", e.read(os.path.join(cwd, path), WRITER))
    assert reads_none.judge_call(rule(WRITE, "reads_none"), WRITE, call) is None


# commands


@pytest.mark.supports("test_a_command_that_its_step_names_goes_through")
def test_a_named_command_holds(e: Events):
    """Given the step `write`, which runs `git log`
    When the writer runs `git log`
    Then the rule finds nothing"""
    call = move("call", e.bash("git log", WRITER))
    assert commands.judge_call(rule(WRITE, "commands"), WRITE, call) is None


@pytest.mark.supports("test_a_command_that_its_step_doesnt_name_is_stopped_with_the_step")
def test_another_command_gives_the_steps_sentence(e: Events):
    """Given the step `write`
    When the writer runs `git push`
    Then the rule gives the step's sentence, naming the step and `git log`"""
    call = move("call", e.bash("git push", WRITER))
    said = commands.judge_call(rule(WRITE, "commands"), WRITE, call)
    assert said is not None
    assert "write" in said
    assert "git log" in said


@pytest.mark.supports("test_a_command_that_its_step_names_goes_through")
@pytest.mark.parametrize(
    "command", ["git log --oneline -5", "git log | head -5", "git log; head NOTES.md"]
)
def test_each_command_opening_with_a_named_commands_words_holds(e: Events, command: str):
    """Given a step whose rule of commands names `git log` and `head`
    When the writer runs a named command with more words after it, a pipeline of named ones, or
    named ones one after another
    Then the rule finds nothing"""
    named: Rule = {"type": "commands", "commands": ["git log", "head"]}
    step: Step = {"name": "write", "rules": [named]}
    assert commands.judge_call(named, step, move("call", e.bash(command, WRITER))) is None


@pytest.mark.supports("test_a_command_chained_after_a_named_one_is_stopped")
@pytest.mark.parametrize(
    "command",
    ["git log && git push", "git log || git push", "git log; git push", "git log | sh"],
)
def test_a_command_chained_after_a_named_one_gives_the_steps_sentence(e: Events, command: str):
    """Given the step `write`, which runs `git log`
    When the writer runs another command after `git log`, split by `&&`, `||`, `;`, or `|`
    Then the rule gives the step's sentence, naming `git log`"""
    said = commands.judge_call(
        rule(WRITE, "commands"), WRITE, move("call", e.bash(command, WRITER))
    )
    assert said is not None
    assert "git log" in said


@pytest.mark.supports("test_a_command_that_its_step_doesnt_name_is_stopped_with_the_step")
@pytest.mark.parametrize("command", ["git", "git logs", "git -C /repo log"])
def test_a_command_that_doesnt_open_with_a_named_commands_words_gives_the_steps_sentence(
    e: Events, command: str
):
    """Given the step `write`, which runs `git log`
    When the writer runs fewer words than the named command's, a word that only begins as its
    last word, or its words with another between them
    Then the rule gives the step's sentence"""
    call = move("call", e.bash(command, WRITER))
    assert commands.judge_call(rule(WRITE, "commands"), WRITE, call) is not None


@pytest.mark.supports("test_a_reporter_of_lanes_goes_through_though_no_step_names_it")
@pytest.mark.parametrize(
    "command", ["lane-step write", "lane-item write dated", "lane-result written"]
)
def test_a_reporter_holds_though_the_rule_doesnt_name_it(e: Events, command: str):
    """Given the step `write`, whose rule names no reporter
    When the writer runs a reporter of Lane's
    Then the rule finds nothing"""
    call = move("call", e.bash(command, WRITER))
    assert commands.judge_call(rule(WRITE, "commands"), WRITE, call) is None


@pytest.mark.supports("test_a_command_that_its_step_doesnt_name_is_stopped_with_the_step")
def test_a_rule_that_names_no_command_stops_each_but_a_reporter(e: Events):
    """Given a step whose rule of commands names none
    When the writer runs `git log`, and then `lane-step write`
    Then the rule gives the step's sentence for the first, and nothing for the reporter"""
    none: Rule = {"type": "commands", "commands": []}
    step: Step = {"name": "write", "rules": [none]}
    assert commands.judge_call(none, step, move("call", e.bash("git log", WRITER))) is not None
    assert commands.judge_call(none, step, move("call", e.bash("lane-step write", WRITER))) is None


# order


@pytest.mark.supports("test_steps_marked_in_their_order_hold_and_the_end_goes_through")
def test_a_mark_of_the_first_step_holds(e: Events):
    """Given the writer with no step marked
    When it marks the step `write`
    Then the rule finds nothing, as no step comes before it"""
    marking = move("report", e.bash("lane-step write", WRITER), report=marked("write"))
    assert order.judge_mark(rule(WRITE, "order"), WRITE, marking) is None


@pytest.mark.supports("test_steps_marked_in_their_order_hold_and_the_end_goes_through")
def test_a_mark_after_the_step_before_holds(e: Events):
    """Given the writer that marked `write`
    When it marks `report`
    Then the rule finds nothing"""
    marking = move(
        "report",
        e.bash("lane-step report", WRITER),
        mark("write"),
        step="report",
        report=marked("report"),
    )
    assert order.judge_mark(rule(REPORT, "order"), REPORT, marking) is None


@pytest.mark.supports("test_a_step_marked_before_the_step_before_it_is_stopped_with_the_step_due")
@pytest.mark.parametrize("before", [[], [mark("write", OTHER)]])
def test_a_mark_before_the_step_before_gives_the_step_due(e: Events, before: list[Entry]):
    """Given the writer a1 that marked no step, alone or beside a2 that marked `write`
    When a1 marks `report`
    Then the rule gives the sentence of `report`, naming `write` as the step due"""
    marking = move("report", e.bash("lane-step report", WRITER), *before, report=marked("report"))
    said = order.judge_mark(rule(REPORT, "order"), REPORT, marking)
    assert said is not None
    assert "write" in said


@pytest.mark.supports("test_steps_marked_in_their_order_hold_and_the_end_goes_through")
def test_an_end_with_the_step_marked_holds(e: Events):
    """Given the writer that marked `report`
    When it ends
    Then the rule of `report` finds nothing"""
    end = move("end", e.ended(WRITER), mark("write"), mark("report"))
    assert order.judge_end(rule(REPORT, "order"), REPORT, end) is None


@pytest.mark.supports("test_an_end_before_each_step_is_done_is_stopped_with_the_step_left")
def test_an_end_with_the_step_unmarked_gives_the_steps_sentence(e: Events):
    """Given the writer that marked `write` alone
    When it ends
    Then the rule of `report` gives its sentence"""
    end = move("end", e.ended(WRITER), mark("write"))
    said = order.judge_end(rule(REPORT, "order"), REPORT, end)
    assert said is not None
    assert "report" in said


# reads_whole


def marking_write(e: Events, *entries: Entry) -> Move:
    return move("report", e.bash("lane-step write", WRITER), *entries, report=marked("write"))


@pytest.mark.supports("test_a_read_whole_holds_the_mark")
@pytest.mark.parametrize(
    "reads",
    [
        [read("NOTES.md", 1, 6)],
        [read("NOTES.md", 1, 3), read("NOTES.md", 4, 6)],
        [read("NOTES.md", 4, 6), read("NOTES.md", 1, 4)],
    ],
)
def test_reads_that_cover_each_line_hold(e: Events, reads: list[Entry]):
    """Given the writer's reads of NOTES.md, of its 6 lines whole, in two parts, or in two parts
    that overlap, the later first
    When it marks `write`
    Then the rule finds nothing"""
    assert (
        reads_whole.judge_mark(rule(WRITE, "reads_whole"), WRITE, marking_write(e, *reads)) is None
    )


@pytest.mark.supports("test_a_step_marked_done_after_a_read_in_part_names_the_lines_not_read")
@pytest.mark.parametrize(
    "reads, first_unread",
    [
        ([read("NOTES.md", 1, 2)], "3"),
        ([read("NOTES.md", 1, 5)], "6"),
        ([read("NOTES.md", 2, 6)], "1"),
    ],
)
def test_reads_that_leave_a_line_give_the_lines_not_read(
    e: Events, reads: list[Entry], first_unread: str
):
    """Given the writer's read of NOTES.md that leaves lines 3 to 6, its last line 6 alone, or its
    first line 1 alone
    When it marks `write`
    Then the rule gives the step's sentence, naming NOTES.md and the line not read"""
    said = reads_whole.judge_mark(rule(WRITE, "reads_whole"), WRITE, marking_write(e, *reads))
    assert said is not None
    assert "NOTES.md" in said
    assert first_unread in said


@pytest.mark.supports("test_a_step_marked_done_with_a_file_unread_is_stopped_with_the_file")
@pytest.mark.parametrize(
    "reads", [[], [read("NOTES.md", 1, 6, OTHER)], [read("CHANGELOG.md", 1, 6)]]
)
def test_no_read_of_the_file_by_the_start_gives_the_steps_sentence(e: Events, reads: list[Entry]):
    """Given no read of NOTES.md, a read of it whole by another writer, or a read of another file
    When the writer a1 marks `write`
    Then the rule gives the step's sentence, naming NOTES.md"""
    said = reads_whole.judge_mark(rule(WRITE, "reads_whole"), WRITE, marking_write(e, *reads))
    assert said is not None
    assert "NOTES.md" in said


# checklist


@pytest.mark.supports("test_a_step_marked_once_each_item_is_done_holds")
@pytest.mark.parametrize(
    "items, entries",
    [([], []), (["dated", "linked"], [mark("write", item="dated"), mark("write", item="linked")])],
)
def test_a_step_with_no_item_or_each_item_marked_holds(
    e: Events, items: list[str], entries: list[Entry]
):
    """Given a step with no item, or each item marked
    When the writer marks `write`
    Then the rule finds nothing"""
    marking = marking_write(e, *entries)
    assert checklist.judge_mark(rule(WRITE, "checklist"), WRITE, marking, items) is None


@pytest.mark.supports("test_a_step_marked_before_its_items_names_each_item_not_done")
@pytest.mark.parametrize(
    "entries, unmarked",
    [
        ([], ["dated", "linked"]),
        ([mark("write", item="dated")], ["linked"]),
        ([mark("write", OTHER, "dated"), mark("report", item="linked")], ["dated", "linked"]),
    ],
)
def test_items_not_marked_give_the_steps_sentence_naming_each(
    e: Events, entries: list[Entry], unmarked: list[str]
):
    """Given no item marked, `dated` alone, or `dated` by another writer and `linked` of another
    step
    When the writer a1 marks `write`
    Then the rule gives the step's sentence, naming each item not marked, and no other"""
    marking = marking_write(e, *entries)
    said = checklist.judge_mark(rule(WRITE, "checklist"), WRITE, marking, ["dated", "linked"])
    assert said is not None
    for item in ("dated", "linked"):
        assert (item in said) == (item in unmarked)


# result


@pytest.mark.supports("test_the_reviewers_more_makes_the_writer_due_again")
@pytest.mark.parametrize("value", ["good", "more", "split"])
def test_an_end_with_a_named_result_holds(e: Events, value: str):
    """Given the reviewer that gave a result its rule names
    When it ends
    Then the rule finds nothing"""
    reviewer = Subagent("a3", "log:reviewer")
    end = move("end", e.ended(reviewer), gave(value, reviewer), step="review", agent=reviewer)
    assert result.judge_end(rule(REVIEW, "result"), REVIEW, end) is None


@pytest.mark.supports("test_an_end_with_no_result_is_stopped_with_the_results_it_may_give")
@pytest.mark.parametrize("entries", [[], [gave("fine")], [gave("good", OTHER)]])
def test_an_end_with_no_named_result_gives_the_results_it_may_give(e: Events, entries: list[Entry]):
    """Given the reviewer a1 that gave no result, one its rule doesn't name, or none while a2 gave
    one
    When it ends
    Then the rule gives the step's sentence, naming each result it may give"""
    end = move("end", e.ended(WRITER), *entries, step="review")
    said = result.judge_end(rule(REVIEW, "result"), REVIEW, end)
    assert said is not None
    for value in ("good", "more", "split"):
        assert value in said


# check


@pytest.mark.supports("test_an_end_that_the_plugins_check_passes_goes_through")
def test_an_end_that_the_check_passes_holds(e: Events):
    """Given the conversation's CHANGELOG.md holding the entry of 1.2.0
    When the writer ends
    Then the check of `report` finds nothing"""
    end = move("end", e.ended(WRITER), step="report")
    assert check.judge_end(rule(REPORT, "check"), REPORT, end) is None


@pytest.mark.supports("test_an_end_that_the_plugins_check_doesnt_pass_is_stopped_with_what_it_said")
def test_an_end_that_the_check_doesnt_pass_gives_the_steps_sentence_and_what_it_said(
    e: Events, cwd: str
):
    """Given the conversation's CHANGELOG.md holding no entry of 1.2.0
    When the writer ends
    Then the check of `report` gives the step's sentence and what the check said"""
    with open(os.path.join(cwd, "CHANGELOG.md"), "w", encoding="utf-8") as f:
        f.write("# Changelog\n")
    end = move("end", e.ended(WRITER), step="report")
    said = check.judge_end(rule(REPORT, "check"), REPORT, end)
    assert said is not None
    assert "report" in said
    assert lane_bench.CHECK_SAYS in said


@pytest.mark.supports("test_the_plugins_check_runs_in_the_worktree_the_conversation_works_in")
def test_the_check_runs_in_the_events_folder(e: Events, tmp_path: Any):
    """Given an event whose folder holds no CHANGELOG.md, though the case's own folder might
    When the writer ends
    Then the check of `report` gives its sentence, as it runs in the event's folder"""
    other = os.path.join(str(tmp_path), "worktree")
    os.makedirs(other)
    end = move("end", Events(other, e.transcript).ended(WRITER), step="report")
    assert check.judge_end(rule(REPORT, "check"), REPORT, end) is not None


@pytest.mark.supports("test_an_end_that_the_plugins_check_doesnt_pass_is_stopped_with_what_it_said")
def test_a_check_that_cant_be_run_is_refused(e: Events, tmp_path: Any):
    """Given an event whose folder isn't there
    When the writer ends
    Then the check refuses with OSError"""
    gone = Events(os.path.join(str(tmp_path), "gone"), e.transcript)
    end = move("end", gone.ended(WRITER), step="report")
    with pytest.raises(OSError):
        check.judge_end(rule(REPORT, "check"), REPORT, end)


# The order of the rules.


@pytest.mark.supports("test_a_write_of_a_file_that_its_step_doesnt_name_is_stopped_with_the_step")
@pytest.mark.parametrize(
    "event, named",
    [
        ("write", "docs/changes/"),
        ("read", ".env"),
        ("bash", "git log"),
    ],
)
def test_a_call_is_judged_by_the_rule_of_its_kind(e: Events, cwd: str, event: str, named: str):
    """Given the writer at its step `write`
    When it writes notes.txt, reads secrets/key.txt, or runs `git push`
    Then the sentence is the one of writes, of reads_none, or of commands"""
    given = {
        "write": e.write(os.path.join(cwd, "notes.txt"), WRITER),
        "read": e.read(os.path.join(cwd, "secrets/key.txt"), WRITER),
        "bash": e.bash("git push", WRITER),
    }[event]
    said = rule_types.judge_call(RULES, move("call", given))
    assert said is not None
    assert named in said


@pytest.mark.supports(
    "test_a_bash_command_that_reads_a_file_never_to_read_is_stopped_by_its_commands"
)
def test_a_bash_command_that_reaches_a_file_never_to_read_is_judged_by_commands(e: Events):
    """Given the writer at its step `write`, which never reads secrets/ and runs `git log`
    When it runs `cat secrets/key.txt`
    Then the sentence is the one of commands, as reads_none judges no Bash call"""
    said = rule_types.judge_call(RULES, move("call", e.bash("cat secrets/key.txt", WRITER)))
    assert said is not None
    assert "git log" in said
    assert "secrets/" not in said


@pytest.mark.supports("test_a_write_of_a_file_that_its_step_names_goes_through")
def test_a_call_that_breaks_no_rule_or_whose_step_judges_no_call_holds(e: Events, cwd: str):
    """Given the writer at its step `write`, and the reviewer at its step `review`, which has no
    rule that judges a call
    When the writer writes CHANGELOG.md, and the reviewer writes notes.txt
    Then neither breaks a rule"""
    reviewer = Subagent("a3", "log:reviewer")
    assert (
        rule_types.judge_call(
            RULES, move("call", e.write(os.path.join(cwd, "CHANGELOG.md"), WRITER))
        )
        is None
    )
    review = move(
        "call", e.write(os.path.join(cwd, "notes.txt"), reviewer), step="review", agent=reviewer
    )
    assert rule_types.judge_call(RULES, review) is None


@pytest.mark.supports("test_a_mark_is_checked_for_the_step_due_before_the_files_it_reads_whole")
def test_a_mark_is_judged_by_order_before_its_reads(e: Events):
    """Given the writer that marked no step and read nothing
    When it marks `report`
    Then the sentence is order's, naming `write`, and not CHANGELOG.md"""
    marking = move(
        "report", e.bash("lane-step report", WRITER), step="write", report=marked("report")
    )
    said = rule_types.judge_mark(RULES, marking, [])
    assert said is not None
    assert "CHANGELOG.md" not in said


@pytest.mark.supports("test_a_mark_is_checked_for_the_files_it_reads_whole_before_its_items")
def test_a_mark_is_judged_by_its_reads_before_its_items(e: Events):
    """Given the writer that read nothing and marked no item
    When it marks `write`
    Then the sentence is reads_whole's, naming NOTES.md, and no item"""
    said = rule_types.judge_mark(RULES, marking_write(e), ["dated", "linked"])
    assert said is not None
    assert "NOTES.md" in said
    assert "dated" not in said


@pytest.mark.supports("test_a_step_marked_once_each_item_is_done_holds")
def test_a_mark_that_breaks_no_rule_holds(e: Events):
    """Given the writer that read NOTES.md whole and marked each item
    When it marks `write`
    Then no rule finds anything"""
    entries = (read("NOTES.md", 1, 6), mark("write", item="dated"), mark("write", item="linked"))
    assert rule_types.judge_mark(RULES, marking_write(e, *entries), ["dated", "linked"]) is None


@pytest.mark.supports("test_an_end_with_no_result_names_the_result_before_the_check")
def test_an_end_is_judged_by_its_result_before_its_steps_and_its_check(e: Events, cwd: str):
    """Given a check that leaves a file where it runs, and the writer that gave no result and
    marked no step
    When it ends
    Then the sentence names `written`, and the check didn't run"""
    rules = copy.deepcopy(RULES)
    rule(rules["roles"]["log:writer"]["steps"][1], "check")["check"] = "touch ran; exit 1"
    said = rule_types.judge_end(rules, move("end", e.ended(WRITER)))
    assert said is not None
    assert "written" in said
    assert not os.path.exists(os.path.join(cwd, "ran"))


@pytest.mark.supports("test_an_end_with_a_step_undone_names_the_step_before_the_check")
def test_an_end_is_judged_by_its_steps_before_its_check(e: Events, cwd: str):
    """Given a check that leaves a file where it runs, and the writer that gave `written` and
    marked `write` alone
    When it ends
    Then the sentence names `report`, and the check didn't run"""
    rules = copy.deepcopy(RULES)
    rule(rules["roles"]["log:writer"]["steps"][1], "check")["check"] = "touch ran; exit 1"
    said = rule_types.judge_end(rules, move("end", e.ended(WRITER), gave("written"), mark("write")))
    assert said is not None
    assert "report" in said
    assert not os.path.exists(os.path.join(cwd, "ran"))


@pytest.mark.supports("test_an_end_that_the_plugins_check_doesnt_pass_is_stopped_with_what_it_said")
def test_an_end_whose_result_and_steps_hold_is_judged_by_its_check(e: Events, cwd: str):
    """Given the writer that gave `written` and marked each step, its CHANGELOG.md holding no
    entry of 1.2.0
    When it ends
    Then the sentence is the check's, with what it said"""
    with open(os.path.join(cwd, "CHANGELOG.md"), "w", encoding="utf-8") as f:
        f.write("# Changelog\n")
    end = move("end", e.ended(WRITER), gave("written"), mark("write"), mark("report"))
    said = rule_types.judge_end(RULES, end)
    assert said is not None
    assert lane_bench.CHECK_SAYS in said


@pytest.mark.supports("test_an_end_that_the_plugins_check_passes_goes_through")
def test_an_end_that_breaks_no_rule_holds(e: Events):
    """Given the writer that gave `written` and marked each step, its CHANGELOG.md holding the
    entry
    When it ends
    Then no rule finds anything"""
    end = move("end", e.ended(WRITER), gave("written"), mark("write"), mark("report"))
    assert rule_types.judge_end(RULES, end) is None
