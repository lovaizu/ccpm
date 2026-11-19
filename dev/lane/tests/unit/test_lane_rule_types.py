"""The unit cases of hooks/lane/rule_types/: each rule type's judge, one for each class of the call,
the mark, or the end it judges, with the edges of a path's folder and of a file's lines, the values
of a rule at one and several, a value that nearly matches a named one, and the marks, reads, and
results of another start or of the main conversation, which a judge leaves alone, and a Grep whose
search reaches a file never to read or doesn't, beside a Glob, which goes through; the sentence
that lists a rule's values; and the order in which rule_types/__init__.py asks them, one for each
combination of rules that a move breaks, with roles of no step, of one, and of three, a result rule
on a step that isn't the last, a result that ends the start at its first, a middle, or its last
step, and the main conversation's turn's end. Each Then gives the whole sentence, as Lane's
rules-and-adapters.md words it."""

from __future__ import annotations

import copy
import dataclasses
import json
import os
from typing import Any

import lane_bench
import lane_entries
import pytest
import rule_types
from lane_events import Event, Events, Subagent
from lane_sentences import (
    at,
    check_fails,
    checklist_of,
    comes_before,
    ends_before,
    never_reads,
    no_result,
    reads_whole_of,
    runs_only,
    work_undone,
    writes_only,
)
from place import Move
from record import Entry, Run
from repo_files import write_files
from report import Report
from rule_types import check, checklist, commands, order, reads_none, reads_whole, result, writes
from rule_types.words import listed
from rules import Rule, Rules, Step

# log's rules as Lane reads them from rules.json, so that no string of them is the one object that a
# literal of Lane's code is.
RULES: Rules = json.loads(json.dumps(lane_bench.RULES))
WRITE: Step = RULES["roles"]["log:writer"]["steps"][0]
REPORT: Step = RULES["roles"]["log:writer"]["steps"][1]
REVIEW: Step = RULES["roles"]["log:reviewer"]["steps"][0]
WRITER = Subagent("a1", "log:writer")
OTHER = Subagent("a2", "log:writer")
REVIEWER = Subagent("a3", "log:reviewer")


def rule(step: Step, kind: str) -> Rule:
    """The step's rule of the type."""
    return next(each for each in step["rules"] if each["type"] == kind)


@pytest.fixture
def e(cwd: str) -> Events:
    return Events(cwd, os.path.join(os.path.dirname(cwd), "transcripts", "session-1.jsonl"))


def mark(step: str, agent: Subagent | None = WRITER, item: str | None = None) -> Entry:
    """A mark of the step, or of its item, by the agent, or by the main conversation for None."""
    entry: Entry = {"kind": "mark", "run": "r1", "agent_id": agent.id if agent else None}
    entry["step"] = step
    if item:
        entry["item"] = item
    return entry


def read(path: str, first: int, last: int, agent: Subagent | None = WRITER) -> Entry:
    return lane_entries.read(agent.id if agent else None, path, first, last)


def gave(value: str, agent: Subagent | None = WRITER) -> Entry:
    return {
        "kind": "result",
        "run": "r1",
        "agent_id": agent.id if agent else None,
        "role": agent.type if agent else "log:up",
        "result": value,
    }


def move(
    kind: str,
    event: Event,
    *entries: Entry,
    step: str | None = "write",
    report: Report | None = None,
    agent: Subagent = WRITER,
) -> Move:
    """The move of the kind by the agent, at the step, on a run whose writer a1 and a2 are tied
    and whose record holds the entries after."""
    head: list[Entry] = [
        {"kind": "run", "run": "r1", "skill": "log:up", "words": "1.2.0"},
        lane_entries.start("u1"),
        lane_entries.tie("u1", "a1"),
        lane_entries.start("u2"),
        lane_entries.tie("u2", "a2"),
    ]
    run = Run("r1", "session-1", "log:up", "1.2.0", "/plugins/log", [*head, *entries])
    steps = RULES["roles"][agent.type]["steps"]
    return Move(kind, event, run, agent.type, agent.id, None, steps, step, report)


def held(given: Move, rules: Rules) -> Move:
    """The move, held to the writer's steps of the rules."""
    return dataclasses.replace(given, steps=rules["roles"]["log:writer"]["steps"])


def holding(given: Move, steps: list[Step]) -> Move:
    """The move, held to the steps."""
    return dataclasses.replace(given, steps=steps)


def main(given: Move, steps: list[Step]) -> Move:
    """The move, made by the main conversation in the run of log:up, held to the steps."""
    return dataclasses.replace(given, role="log:up", agent_id=None, steps=steps)


def marked(step: str) -> Report:
    return {"kind": "step", "step": step}


# words


@pytest.mark.supports("test_a_write_of_a_file_that_its_step_doesnt_name_is_stopped_with_the_step")
@pytest.mark.parametrize(
    "values, said",
    [
        (["CHANGELOG.md"], "CHANGELOG.md"),
        (["CHANGELOG.md", "docs/changes/"], "CHANGELOG.md and docs/changes/"),
        (["a", "b", "c"], "a, b and c"),
        (["a", "b", "c", "d"], "a, b, c and d"),
    ],
)
def test_values_are_listed_in_their_order_the_last_two_joined_by_and(values: list[str], said: str):
    """Given one value, two, three, or four
    When a sentence lists them
    Then they come in their order, the last two joined by `and` and the rest by commas"""
    assert listed(values) == said


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
    "path",
    [
        "notes.txt",
        "docs/changes-old.md",
        "docs/changes",
        "docs/CHANGELOG.md",
        "CHANGELOG.md.bak",
        "../CHANGELOG.md",
    ],
)
def test_a_write_of_another_file_gives_the_steps_sentence(e: Events, cwd: str, path: str):
    """Given the step `write`, which writes CHANGELOG.md and docs/changes/
    When the writer writes another file, one whose name only begins as the folder's, a file named
    as the folder without its /, one of the named name in another folder, one whose name begins
    with the named one's, or one outside the conversation's folder
    Then the rule gives the step's sentence, naming the step, the files it writes, and the file"""
    call = move("call", e.write(os.path.normpath(os.path.join(cwd, path)), WRITER))
    said = writes.judge_call(rule(WRITE, "writes"), WRITE, call)
    assert said == writes_only("write", ["CHANGELOG.md", "docs/changes/"], path)


@pytest.mark.supports("test_a_write_of_a_file_that_its_step_doesnt_name_is_stopped_with_the_step")
def test_a_path_that_doesnt_close_with_a_slash_names_no_file_under_it(e: Events, cwd: str):
    """Given a step whose rule of the files it writes names `docs`, with no closing /
    When the writer writes docs/a.md
    Then the rule gives the step's sentence, as only a path that closes with / names a folder"""
    docs: Rule = {"type": "writes", "paths": ["docs"]}
    step: Step = {"name": "write", "rules": [docs]}
    call = move("call", e.write(os.path.join(cwd, "docs", "a.md"), WRITER))
    assert writes.judge_call(docs, step, call) == writes_only("write", ["docs"], "docs/a.md")


@pytest.mark.supports("test_an_edit_of_a_file_that_its_step_doesnt_name_is_stopped")
def test_an_edit_of_another_file_gives_the_steps_sentence(e: Events, cwd: str):
    """Given the step `write`
    When the writer edits README.md
    Then the rule gives the step's sentence, naming README.md"""
    call = move("call", e.write(os.path.join(cwd, "README.md"), WRITER, tool="Edit"))
    said = writes.judge_call(rule(WRITE, "writes"), WRITE, call)
    assert said == writes_only("write", ["CHANGELOG.md", "docs/changes/"], "README.md")


@pytest.mark.supports("test_the_main_conversations_write_in_a_run_is_held_to_its_skills_step")
def test_the_sentence_names_the_role_that_the_move_holds(e: Events, cwd: str):
    """Given the main conversation in the run of log:up, at its step `lead`, which writes
    .log/up.md
    When it writes notes.txt
    Then the rule gives the sentence of `lead` of log:up"""
    lead: Step = RULES["roles"]["log:up"]["steps"][0]
    call = main(move("call", e.write(os.path.join(cwd, "notes.txt")), step="lead"), [lead])
    said = writes.judge_call(rule(lead, "writes"), lead, call)
    assert said == writes_only("lead", [".log/up.md"], "notes.txt", "log:up")


@pytest.mark.supports("test_a_write_of_a_file_that_its_step_doesnt_name_is_stopped_with_the_step")
def test_a_write_through_a_link_is_judged_by_the_file_it_reaches(e: Events, cwd: str):
    """Given the step `write`, and a link CHANGELOG.md in the conversation's folder that reaches
    notes.txt
    When the writer writes CHANGELOG.md
    Then the rule gives the step's sentence, naming notes.txt"""
    write_files(cwd, {"notes.txt": "x\n"})
    os.remove(os.path.join(cwd, "CHANGELOG.md"))
    os.symlink(os.path.join(cwd, "notes.txt"), os.path.join(cwd, "CHANGELOG.md"))
    call = move("call", e.write(os.path.join(cwd, "CHANGELOG.md"), WRITER))
    said = writes.judge_call(rule(WRITE, "writes"), WRITE, call)
    assert said == writes_only("write", ["CHANGELOG.md", "docs/changes/"], "notes.txt")


# reads_none


@pytest.mark.supports("test_a_read_of_a_file_under_a_folder_never_to_read_is_stopped_with_the_step")
@pytest.mark.parametrize("path", ["secrets/key.txt", "secrets/a/b.txt", ".env"])
def test_a_read_of_a_file_never_to_read_gives_the_steps_sentence(e: Events, cwd: str, path: str):
    """Given the step `write`, which never reads secrets/ nor .env
    When the writer reads a file in the folder, one deeper in it, or the named file
    Then the rule gives the step's sentence, naming the step, the files it never reads, and the
    file"""
    call = move("call", e.read(os.path.join(cwd, path), WRITER))
    said = reads_none.judge_call(rule(WRITE, "reads_none"), WRITE, call)
    assert said == never_reads("write", ["secrets/", ".env"], path)


@pytest.mark.supports("test_a_read_of_another_file_goes_through")
@pytest.mark.parametrize(
    "path", ["NOTES.md", "secrets-old/key.txt", "secrets", ".env.example", "../secrets/key.txt"]
)
def test_a_read_of_another_file_holds(e: Events, cwd: str, path: str):
    """Given the step `write`, which never reads secrets/ nor .env
    When the writer reads another file, one in a folder whose name only begins as the rule's, a
    file named as the folder without its /, one whose name only begins as a named file's, or one
    under a folder of that name outside the conversation's folder
    Then the rule finds nothing"""
    call = move("call", e.read(os.path.normpath(os.path.join(cwd, path)), WRITER))
    assert reads_none.judge_call(rule(WRITE, "reads_none"), WRITE, call) is None


def searched(e: Events, tool: str, path: str | None, agent: Subagent = WRITER) -> Event:
    """The PreToolUse of the agent's Grep or Glob, with the `pattern` and the `path`, where one is
    given, of the tool's input as Claude Code's tools reference gives them; made from a Read's
    recorded event until a record of a Grep and a Glob exists."""
    event = e.read(os.path.join(e.cwd, "NOTES.md"), agent)
    event["tool_name"] = tool
    event["tool_input"] = {"pattern": "key" if tool == "Grep" else "**/*.txt"}
    if path is not None:
        event["tool_input"]["path"] = path
    return event


# Where a search reaches a file never to read, from the conversation's folder: in a folder never
# read, at the folder, at a file never read, at a folder that holds them, and with no path, at the
# conversation's folder, which holds them.
REACHES = ["secrets/a", "secrets", ".env", ".", None]
# Where a search reaches none: a folder beside one never read, whose name begins as its, and a
# folder that holds none.
BESIDE = ["secrets-old", "docs"]
# What the step's sentence of a search opens with.
NEVER_READS = f"{at('write')}, which never reads secrets/ and .env.\n"


def search_path(cwd: str, path: str | None) -> str | None:
    return None if path is None else os.path.normpath(os.path.join(cwd, path))


@pytest.mark.supports("test_a_read_of_a_file_under_a_folder_never_to_read_is_stopped_with_the_step")
@pytest.mark.parametrize("path", REACHES)
@pytest.mark.xfail(
    strict=True,
    reason="reads_none.judge_call judges a Grep by its `path`, or by the event's `cwd` where it"
    " names none, and gives the step's sentence asking for a path outside the files never read",
)
def test_a_grep_whose_search_reaches_a_file_never_to_read_gives_the_steps_sentence(
    e: Events, cwd: str, path: str | None
):
    """Given the step `write`, which never reads secrets/ nor .env
    When the writer greps in a folder under secrets/, in secrets/ itself, in .env, in the
    conversation's folder, which holds them, or with no path, in that folder
    Then the rule gives the step's sentence, naming the step and the files it never reads, and
    asking for a path outside them"""
    call = move("call", searched(e, "Grep", search_path(cwd, path)))
    said = reads_none.judge_call(rule(WRITE, "reads_none"), WRITE, call)
    assert said is not None
    assert said.startswith(NEVER_READS)


@pytest.mark.supports("test_a_read_of_another_file_goes_through")
@pytest.mark.parametrize("path", BESIDE)
@pytest.mark.xfail(
    strict=True,
    reason="reads_none.judge_call judges a Grep by its `path`, which names no `file_path`",
)
def test_a_grep_whose_search_reaches_no_file_never_to_read_holds(e: Events, cwd: str, path: str):
    """Given the step `write`, which never reads secrets/ nor .env
    When the writer greps in secrets-old/, whose name begins as secrets/, or in docs/
    Then the rule finds nothing"""
    call = move("call", searched(e, "Grep", search_path(cwd, path)))
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
    assert said == runs_only("write", ["git log"])


@pytest.mark.supports("test_a_named_command_with_more_words_after_it_goes_through")
@pytest.mark.parametrize(
    "command",
    [
        "git log --oneline -5",
        "head NOTES.md",
        "git log | head -5",
        "git log; head NOTES.md",
        "git log && head NOTES.md",
        "git log || head NOTES.md",
        "  git log  ",
    ],
)
def test_each_command_opening_with_a_named_commands_words_holds(e: Events, command: str):
    """Given a step whose rule of commands names `git log` and `head`
    When the writer runs a named command with more words after it, the second named command, a
    pipeline of named ones, named ones split by `;`, `&&`, or `||`, or a named one with spaces
    around it
    Then the rule finds nothing"""
    named: Rule = {"type": "commands", "commands": ["git log", "head"]}
    step: Step = {"name": "write", "rules": [named]}
    assert commands.judge_call(named, step, move("call", e.bash(command, WRITER))) is None


@pytest.mark.supports("test_a_command_chained_after_a_named_one_is_stopped")
@pytest.mark.parametrize(
    "command",
    [
        "git log && git push",
        "git log || git push",
        "git log; git push",
        "git log | sh",
        "git push && git log",
        "git log && lane-step write && git push",
    ],
)
def test_a_command_chained_beside_a_named_one_gives_the_steps_sentence(e: Events, command: str):
    """Given the step `write`, which runs `git log`
    When the writer runs another command after `git log`, split by `&&`, `||`, `;`, or `|`, one
    before it, or one after a reporter
    Then the rule gives the step's sentence, naming `git log`"""
    said = commands.judge_call(
        rule(WRITE, "commands"), WRITE, move("call", e.bash(command, WRITER))
    )
    assert said == runs_only("write", ["git log"])


@pytest.mark.supports("test_a_command_that_its_step_doesnt_name_is_stopped_with_the_step")
@pytest.mark.parametrize("command", ["git", "git logs", "git -C /repo log", "echo git log"])
def test_a_command_that_doesnt_open_with_a_named_commands_words_gives_the_steps_sentence(
    e: Events, command: str
):
    """Given the step `write`, which runs `git log`
    When the writer runs fewer words than the named command's, a word that only begins as its
    last word, its words with another between them, or its words after another
    Then the rule gives the step's sentence"""
    call = move("call", e.bash(command, WRITER))
    assert commands.judge_call(rule(WRITE, "commands"), WRITE, call) == runs_only(
        "write", ["git log"]
    )


@pytest.mark.supports("test_a_command_that_its_step_doesnt_name_is_stopped_with_the_step")
def test_the_sentence_of_several_commands_names_each(e: Events):
    """Given a step whose rule of commands names `git log`, `head`, and `wc -l`
    When the writer runs `git push`
    Then the rule gives the step's sentence, naming the three in their order"""
    named: Rule = {"type": "commands", "commands": ["git log", "head", "wc -l"]}
    step: Step = {"name": "write", "rules": [named]}
    said = commands.judge_call(named, step, move("call", e.bash("git push", WRITER)))
    assert said == runs_only("write", ["git log", "head", "wc -l"])


@pytest.mark.supports("test_a_reporter_of_lanes_goes_through_though_no_step_names_it")
@pytest.mark.parametrize(
    "command",
    [
        "lane-step write",
        "lane-item write dated",
        "lane-result written",
        "git log && lane-result written",
    ],
)
def test_a_reporter_holds_though_the_rule_doesnt_name_it(e: Events, command: str):
    """Given the step `write`, whose rule names no reporter
    When the writer runs a reporter of Lane's, alone or after `git log`
    Then the rule finds nothing"""
    call = move("call", e.bash(command, WRITER))
    assert commands.judge_call(rule(WRITE, "commands"), WRITE, call) is None


@pytest.mark.supports("test_a_reporter_of_lanes_goes_through_though_no_step_names_it")
@pytest.mark.parametrize("command", ["lane-steps write", "lane write", "echo lane-step write"])
def test_a_command_that_nearly_matches_a_reporter_gives_the_steps_sentence(e: Events, command: str):
    """Given the step `write`, which runs `git log`
    When the writer runs a word that begins as a reporter's, a word that a reporter's begins with,
    or a reporter's word after another
    Then the rule gives the step's sentence"""
    call = move("call", e.bash(command, WRITER))
    assert commands.judge_call(rule(WRITE, "commands"), WRITE, call) == runs_only(
        "write", ["git log"]
    )


@pytest.mark.supports("test_a_command_that_its_step_doesnt_name_is_stopped_with_the_step")
def test_a_rule_that_names_no_command_stops_each_but_a_reporter(e: Events):
    """Given a step whose rule of commands names none
    When the writer runs `git log`, and then `lane-step write`
    Then the rule gives the step's sentence, saying it runs no command, for the first, and nothing
    for the reporter"""
    none: Rule = {"type": "commands", "commands": []}
    step: Step = {"name": "write", "rules": [none]}
    said = commands.judge_call(none, step, move("call", e.bash("git log", WRITER)))
    assert said == runs_only("write", [])
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
@pytest.mark.parametrize(
    "before",
    [[], [mark("write", OTHER)], [mark("write", None)], [mark("write", item="dated")]],
)
def test_a_mark_before_the_step_before_gives_the_step_due(e: Events, before: list[Entry]):
    """Given the writer a1 that marked no step, alone or beside a2 that marked `write`, the main
    conversation that marked `write`, or a1's mark of an item of `write`
    When a1 marks `report`
    Then the rule gives the sentence of `write` due before `report`"""
    marking = move("report", e.bash("lane-step report", WRITER), *before, report=marked("report"))
    said = order.judge_mark(rule(REPORT, "order"), REPORT, marking)
    assert said == comes_before("write", "report")


# A role of three steps, each held in order, its first with a result rule and its last ending.
THREE: list[Step] = [
    {"name": "draft", "rules": [{"type": "order"}, {"type": "result", "results": ["drafted"]}]},
    {"name": "write", "rules": [{"type": "order"}]},
    {"name": "report", "rules": [{"type": "order"}, {"type": "result", "results": ["written"]}]},
]


@pytest.mark.supports("test_a_step_marked_before_the_step_before_it_is_stopped_with_the_step_due")
@pytest.mark.parametrize(
    "marks, due",
    [
        ((), "draft"),
        (("draft",), "write"),
        (("write",), "draft"),
        (("draft", "write"), None),
    ],
)
def test_a_mark_of_the_third_step_gives_the_first_step_before_it_not_done(
    e: Events, marks: tuple[str, ...], due: str | None
):
    """Given a writer of three steps, `draft`, `write`, and `report`, that marked none of the two
    before `report`, `draft` alone, `write` alone, or both
    When it marks `report`
    Then the rule gives the sentence of `draft` due, of `write` due, of `draft` due, or nothing"""
    marking = holding(
        move(
            "report",
            e.bash("lane-step report", WRITER),
            *[mark(each) for each in marks],
            report=marked("report"),
        ),
        THREE,
    )
    said = order.judge_mark(rule(THREE[2], "order"), THREE[2], marking)
    assert said == (comes_before(due, "report") if due else None)


@pytest.mark.supports("test_steps_marked_in_their_order_hold_and_the_end_goes_through")
def test_an_end_with_the_step_marked_holds(e: Events):
    """Given the writer that marked `report`
    When it ends
    Then the rule of `report` finds nothing"""
    end = move("end", e.ended(WRITER), mark("write"), mark("report"))
    assert order.judge_end(rule(REPORT, "order"), REPORT, end) is None


@pytest.mark.supports("test_an_end_before_each_step_is_done_is_stopped_with_the_step_left")
@pytest.mark.parametrize(
    "entries",
    [[mark("write")], [mark("write"), mark("report", OTHER)], [mark("report", item="dated")]],
)
def test_an_end_with_the_step_unmarked_gives_the_steps_sentence(e: Events, entries: list[Entry]):
    """Given the writer that marked `write` alone, beside a2 that marked `report`, or marked an item
    of `report` alone
    When it ends
    Then the rule of `report` gives its sentence"""
    end = move("end", e.ended(WRITER), *entries)
    assert order.judge_end(rule(REPORT, "order"), REPORT, end) == ends_before("report")


# reads_whole


def marking_write(e: Events, *entries: Entry) -> Move:
    return move("report", e.bash("lane-step write", WRITER), *entries, report=marked("write"))


@pytest.mark.supports("test_reads_in_parts_that_cover_each_line_read_the_file_whole")
@pytest.mark.parametrize(
    "reads",
    [
        [read("NOTES.md", 1, 6)],
        [read("NOTES.md", 1, 3), read("NOTES.md", 4, 6)],
        [read("NOTES.md", 4, 6), read("NOTES.md", 1, 4)],
        [read("NOTES.md", 1, 1), read("NOTES.md", 2, 2), read("NOTES.md", 3, 6)],
        [read("NOTES.md", 1, 9)],
    ],
)
def test_reads_that_cover_each_line_hold(e: Events, reads: list[Entry]):
    """Given the writer's reads of NOTES.md, of its 6 lines whole, in two parts, in two parts that
    overlap, the later first, in three parts, or past its last line
    When it marks `write`
    Then the rule finds nothing"""
    assert (
        reads_whole.judge_mark(rule(WRITE, "reads_whole"), WRITE, marking_write(e, *reads)) is None
    )


@pytest.mark.supports("test_a_step_marked_done_after_a_read_in_part_names_the_lines_not_read")
@pytest.mark.parametrize(
    "reads, first_unread",
    [
        ([read("NOTES.md", 1, 2)], 3),
        ([read("NOTES.md", 1, 5)], 6),
        ([read("NOTES.md", 2, 6)], 1),
        ([read("NOTES.md", 1, 2), read("NOTES.md", 4, 6)], 3),
        ([read("NOTES.md", 1, 1), read("NOTES.md", 3, 3), read("NOTES.md", 5, 5)], 2),
    ],
)
def test_reads_that_leave_a_line_give_the_first_line_not_read(
    e: Events, reads: list[Entry], first_unread: int
):
    """Given the writer's reads of NOTES.md that leave lines 3 to 6, its last line 6 alone, its
    first line 1 alone, its line 3 between two parts, or the lines 2, 4, and 6
    When it marks `write`
    Then the rule gives the step's sentence, naming NOTES.md from the first line not read"""
    said = reads_whole.judge_mark(rule(WRITE, "reads_whole"), WRITE, marking_write(e, *reads))
    assert said == reads_whole_of("write", ["NOTES.md"], [f"NOTES.md from its line {first_unread}"])


@pytest.mark.supports("test_a_step_marked_done_with_a_file_unread_is_stopped_with_the_file")
@pytest.mark.parametrize(
    "reads",
    [
        [],
        [read("NOTES.md", 1, 6, OTHER)],
        [read("NOTES.md", 1, 6, None)],
        [read("CHANGELOG.md", 1, 6)],
        [read("docs/NOTES.md", 1, 6)],
    ],
)
def test_no_read_of_the_file_by_the_start_gives_the_steps_sentence(e: Events, reads: list[Entry]):
    """Given no read of NOTES.md, a read of it whole by another writer or by the main
    conversation, or a read of another file, or of a file of its name in another folder
    When the writer a1 marks `write`
    Then the rule gives the step's sentence, naming NOTES.md from its line 1"""
    said = reads_whole.judge_mark(rule(WRITE, "reads_whole"), WRITE, marking_write(e, *reads))
    assert said == reads_whole_of("write", ["NOTES.md"], ["NOTES.md from its line 1"])


# A rule of two files to read whole.
BOTH: Rule = {"type": "reads_whole", "paths": ["NOTES.md", "CHANGELOG.md"]}


@pytest.mark.supports("test_a_step_marked_done_with_a_file_unread_is_stopped_with_the_file")
@pytest.mark.parametrize(
    "reads, unread",
    [
        ([], ["NOTES.md from its line 1", "CHANGELOG.md from its line 1"]),
        ([read("NOTES.md", 1, 6)], ["CHANGELOG.md from its line 1"]),
        (
            [read("CHANGELOG.md", 1, 4)],
            ["NOTES.md from its line 1", "CHANGELOG.md from its line 5"],
        ),
        ([read("NOTES.md", 1, 6), read("CHANGELOG.md", 1, 6)], None),
    ],
)
def test_a_rule_of_two_files_names_each_not_read_whole(
    e: Events, reads: list[Entry], unread: list[str] | None
):
    """Given a step whose rule reads whole NOTES.md and CHANGELOG.md, each of 6 lines, and the
    writer's reads of neither, of NOTES.md whole, of CHANGELOG.md in part, or of both whole
    When it marks the step
    Then the rule gives the step's sentence, naming both files and each not read whole from its
    first line not read, or nothing"""
    step: Step = {"name": "write", "rules": [BOTH]}
    said = reads_whole.judge_mark(BOTH, step, marking_write(e, *reads))
    assert said == (reads_whole_of("write", BOTH["paths"], unread) if unread else None)


@pytest.mark.supports("test_a_step_marked_done_after_a_read_in_part_names_the_lines_not_read")
@pytest.mark.parametrize("last, first_unread", [(2, None), (1, 2)])
def test_a_file_with_no_last_newline_counts_its_last_line_alone(
    e: Events, cwd: str, last: int, first_unread: int | None
):
    """Given TWO.md of 2 lines with no newline after its last, and the writer's read of it to its
    line 2, or to its line 1
    When it marks the step that reads it whole
    Then the rule finds nothing, or names TWO.md from its line 2"""
    write_files(cwd, {"TWO.md": "a\nb"})
    two: Rule = {"type": "reads_whole", "paths": ["TWO.md"]}
    step: Step = {"name": "write", "rules": [two]}
    said = reads_whole.judge_mark(two, step, marking_write(e, read("TWO.md", 1, last)))
    expected = reads_whole_of("write", ["TWO.md"], [f"TWO.md from its line {first_unread}"])
    assert said == (expected if first_unread else None)


# checklist


@pytest.mark.supports("test_a_step_marked_once_each_item_is_done_holds")
@pytest.mark.parametrize(
    "items, entries",
    [
        ([], []),
        (["dated"], [mark("write", item="dated")]),
        (["dated", "linked"], [mark("write", item="dated"), mark("write", item="linked")]),
        (["dated", "linked"], [mark("write", item="linked"), mark("write", item="dated")]),
    ],
)
def test_a_step_with_no_item_or_each_item_marked_holds(
    e: Events, items: list[str], entries: list[Entry]
):
    """Given a step with no item, one item marked, or each of two marked, in their order or not
    When the writer marks `write`
    Then the rule finds nothing"""
    marking = marking_write(e, *entries)
    assert checklist.judge_mark({"type": "checklist", "items": items}, WRITE, marking) is None


@pytest.mark.supports("test_a_step_marked_before_its_items_names_each_item_not_done")
@pytest.mark.parametrize(
    "entries, unmarked",
    [
        ([], ["dated", "linked"]),
        ([mark("write", item="dated")], ["linked"]),
        ([mark("write", item="linked")], ["dated"]),
        ([mark("write", OTHER, "dated"), mark("report", item="linked")], ["dated", "linked"]),
        ([mark("write", None, "dated"), mark("write", item="date")], ["dated", "linked"]),
        ([mark("write")], ["dated", "linked"]),
    ],
)
def test_items_not_marked_give_the_steps_sentence_naming_each(
    e: Events, entries: list[Entry], unmarked: list[str]
):
    """Given no item marked, `dated` alone, `linked` alone, `dated` by another writer and `linked`
    of another step, `dated` by the main conversation and `date`, which nearly matches it, or a
    mark of the step with no item
    When the writer a1 marks `write`
    Then the rule gives the step's sentence, naming each item not marked, in their order, and no
    other"""
    marking = marking_write(e, *entries)
    said = checklist.judge_mark(rule(WRITE, "checklist"), WRITE, marking)
    assert said == checklist_of("write", unmarked)


@pytest.mark.supports("test_a_step_marked_once_each_item_is_done_holds")
def test_the_main_conversations_items_count_for_its_own_mark(e: Events):
    """Given the main conversation at its step `lead`, whose checklist names `noted`, which it
    marked
    When it marks `lead`
    Then the rule finds nothing"""
    noted: Rule = {"type": "checklist", "items": ["noted"]}
    lead: Step = {"name": "lead", "rules": [noted]}
    marking = main(
        move(
            "report",
            e.bash("lane-step lead"),
            mark("lead", None, "noted"),
            step="lead",
            report=marked("lead"),
        ),
        [lead],
    )
    assert checklist.judge_mark(noted, lead, marking) is None


# result


@pytest.mark.supports("test_a_result_reaching_the_main_conversation_gives_the_starts_due_after_it")
@pytest.mark.parametrize(
    "entries, latest",
    [
        ([], None),
        ([gave("written")], "written"),
        ([gave("unclear"), gave("written")], "written"),
        ([gave("written"), gave("unclear")], "unclear"),
        ([gave("written"), gave("good", OTHER)], "written"),
        ([gave("good", OTHER)], None),
        ([gave("good", None)], None),
    ],
)
def test_the_start_gave_its_latest_result(e: Events, entries: list[Entry], latest: str | None):
    """Given the writer a1 that gave no result, one, two in either order, one while a2 gave a later
    one, none while a2 gave one, or none while the main conversation gave one
    When Lane reads the result that a1 gave
    Then it's the latest of a1's, or none"""
    assert result.given(move("end", e.ended(WRITER), *entries)) == latest


@pytest.mark.supports("test_the_reviewers_more_makes_the_writer_due_again")
@pytest.mark.parametrize("value", ["good", "more", "split"])
def test_an_end_with_a_named_result_holds(e: Events, value: str):
    """Given the reviewer that gave a result its rule names
    When it ends
    Then the rule finds nothing"""
    end = move("end", e.ended(REVIEWER), gave(value, REVIEWER), step="review", agent=REVIEWER)
    assert result.judge_end(rule(REVIEW, "result"), REVIEW, end) is None


@pytest.mark.supports("test_an_end_with_no_result_is_stopped_with_the_results_it_may_give")
@pytest.mark.parametrize(
    "entries",
    [
        [],
        [gave("fine", REVIEWER)],
        [gave("goo", REVIEWER)],
        [gave("good", OTHER)],
        [gave("good", REVIEWER), gave("fine", REVIEWER)],
    ],
)
def test_an_end_with_no_named_result_gives_the_results_it_may_give(e: Events, entries: list[Entry]):
    """Given the reviewer a3 that gave no result, one its rule doesn't name, one that nearly
    matches a named one, none while a2 gave one, or a named one and then another
    When it ends
    Then the rule gives the step's sentence, naming each result it may give"""
    end = move("end", e.ended(REVIEWER), *entries, step="review", agent=REVIEWER)
    said = result.judge_end(rule(REVIEW, "result"), REVIEW, end)
    assert said == no_result("review", ["good", "more", "split"], "log:reviewer")


@pytest.mark.supports(
    "test_a_result_that_ends_the_start_at_its_step_lets_it_end_with_later_steps_undone"
)
@pytest.mark.parametrize(
    "rule_, value",
    [
        ({"type": "result", "ends": ["unclear"]}, "unclear"),
        ({"type": "result", "results": ["written"], "ends": ["unclear"]}, "unclear"),
        ({"type": "result", "results": ["written"], "ends": ["unclear"]}, "written"),
    ],
)
def test_an_end_with_a_result_of_either_kind_holds_its_rule(e: Events, rule_: Rule, value: str):
    """Given a rule of results that names only `unclear` among those that end the start, or
    `written` beside it
    When the writer that gave `unclear`, or `written`, ends
    Then the rule finds nothing"""
    step: Step = {"name": "write", "rules": [rule_]}
    assert result.judge_end(rule_, step, move("end", e.ended(WRITER), gave(value))) is None


@pytest.mark.supports("test_an_end_with_no_result_is_stopped_with_the_results_it_may_give")
@pytest.mark.parametrize("entries", [[], [gave("fine")], [gave("unclear", OTHER)]])
def test_an_end_at_a_step_whose_rule_names_only_results_that_end_the_start_says_to_mark_it(
    e: Events, entries: list[Entry]
):
    """Given a rule of results that names only `unclear`, among those that end the start
    When the writer that gave no result, one the rule doesn't name, or none while a2 gave
    `unclear`, ends at its step
    Then the rule gives the step's sentence, telling it to mark the step done, and naming
    `unclear` as a result only where it can't go on"""
    ends: Rule = {"type": "result", "ends": ["unclear"]}
    step: Step = {"name": "write", "rules": [ends]}
    said = result.judge_end(ends, step, move("end", e.ended(WRITER), *entries))
    assert said == work_undone("write", ["unclear"])


@pytest.mark.supports("test_an_end_with_a_result_that_the_rule_doesnt_name_is_stopped")
def test_an_end_with_a_result_of_neither_kind_names_each_result_it_may_give(e: Events):
    """Given a rule of results that names `written`, and `unclear` among those that end the start
    When the writer that gave `fine` ends
    Then the rule gives the step's sentence, naming `written` and then `unclear`"""
    both: Rule = {"type": "result", "results": ["written"], "ends": ["unclear"]}
    step: Step = {"name": "report", "rules": [both]}
    said = result.judge_end(both, step, move("end", e.ended(WRITER), gave("fine")))
    assert said == no_result("report", ["written", "unclear"])


# check


def check_rule(command: str) -> Rule:
    return {"type": "check", "check": command}


@pytest.mark.supports("test_an_end_that_the_plugins_check_passes_goes_through")
@pytest.mark.parametrize("command", [None, "echo all good; echo fine >&2"])
def test_an_end_that_the_check_passes_holds(e: Events, command: str | None):
    """Given the conversation's CHANGELOG.md holding the entry of 1.2.0, and the check of `report`,
    or a check that exits 0 after saying something
    When the writer ends
    Then the check finds nothing"""
    given = rule(REPORT, "check") if command is None else check_rule(command)
    end = move("end", e.ended(WRITER), step="report")
    assert check.judge_end(given, REPORT, end) is None


@pytest.mark.supports("test_an_end_that_the_plugins_check_doesnt_pass_is_stopped_with_what_it_said")
def test_an_end_that_the_check_doesnt_pass_gives_the_steps_sentence_and_what_it_said(
    e: Events, cwd: str
):
    """Given the conversation's CHANGELOG.md holding no entry of 1.2.0
    When the writer ends
    Then the check of `report` gives the step's sentence, closed by what the check said"""
    write_files(cwd, {"CHANGELOG.md": "# Changelog\n"})
    end = move("end", e.ended(WRITER), step="report")
    said = check.judge_end(rule(REPORT, "check"), REPORT, end)
    assert said == check_fails("report", lane_bench.CHECK_SAYS)


@pytest.mark.supports("test_an_end_that_the_plugins_check_doesnt_pass_is_stopped_with_what_it_said")
@pytest.mark.parametrize(
    "command, said",
    [
        ("echo 'no entry'; exit 2", "no entry"),
        ("echo 'no entry' >&2; exit 1", "no entry"),
        ("echo 'no entry'; echo 'no date' >&2; exit 1", "no entry\nno date"),
        ("printf '\\n  no entry  \\n\\n'; exit 1", "no entry"),
        ("exit 3", ""),
    ],
)
def test_a_check_that_exits_other_than_0_gives_what_it_said_on_either_output(
    e: Events, command: str, said: str
):
    """Given a check that exits 2 after saying `no entry`, says it on standard error alone, says
    `no date` on standard error after it, says it among blank lines and spaces, or exits 3 saying
    nothing
    When the writer ends
    Then the check gives the step's sentence, closed by what it said, its standard output first,
    with the blank lines and spaces around it left out"""
    end = move("end", e.ended(WRITER), step="report")
    assert check.judge_end(check_rule(command), REPORT, end) == check_fails("report", said)


@pytest.mark.supports("test_the_plugins_check_runs_in_the_worktree_the_conversation_works_in")
def test_the_check_runs_in_the_events_folder(e: Events, tmp_path: Any):
    """Given an event whose folder holds no CHANGELOG.md, though the case's own folder might
    When the writer ends
    Then the check of `report` gives its sentence with what it said, and then what grep said of
    the file it lacks, as it runs in the event's folder"""
    other = os.path.join(str(tmp_path), "worktree")
    os.makedirs(other)
    end = move("end", Events(other, e.transcript).ended(WRITER), step="report")
    said = check.judge_end(rule(REPORT, "check"), REPORT, end)
    assert said is not None
    assert said.startswith(check_fails("report", f"{lane_bench.CHECK_SAYS}\ngrep: CHANGELOG.md"))


@pytest.mark.supports("test_an_end_that_the_plugins_check_doesnt_pass_is_stopped_with_what_it_said")
def test_a_check_that_cant_be_run_is_refused(e: Events, tmp_path: Any):
    """Given an event whose folder isn't there
    When the writer ends
    Then the check refuses with OSError"""
    gone = Events(os.path.join(str(tmp_path), "gone"), e.transcript)
    end = move("end", gone.ended(WRITER), step="report")
    with pytest.raises(OSError):
        check.judge_end(rule(REPORT, "check"), REPORT, end)


# The order of the rules: a call.


@pytest.mark.supports("test_a_write_of_a_file_that_its_step_doesnt_name_is_stopped_with_the_step")
@pytest.mark.parametrize("event", ["write", "edit", "read", "bash"])
def test_a_call_is_judged_by_the_rule_of_its_kind(e: Events, cwd: str, event: str):
    """Given the writer at its step `write`
    When it writes notes.txt, edits it, reads secrets/key.txt, or runs `git push`
    Then the sentence is the one of writes, of writes, of reads_none, or of commands"""
    given, said = {
        "write": (
            e.write(os.path.join(cwd, "notes.txt"), WRITER),
            writes_only("write", ["CHANGELOG.md", "docs/changes/"], "notes.txt"),
        ),
        "edit": (
            e.write(os.path.join(cwd, "notes.txt"), WRITER, tool="Edit"),
            writes_only("write", ["CHANGELOG.md", "docs/changes/"], "notes.txt"),
        ),
        "read": (
            e.read(os.path.join(cwd, "secrets/key.txt"), WRITER),
            never_reads("write", ["secrets/", ".env"], "secrets/key.txt"),
        ),
        "bash": (e.bash("git push", WRITER), runs_only("write", ["git log"])),
    }[event]
    assert rule_types.judge_call(move("call", given)) == said


@pytest.mark.supports("test_a_read_of_a_file_under_a_folder_never_to_read_is_stopped_with_the_step")
@pytest.mark.parametrize("path", REACHES)
@pytest.mark.xfail(
    strict=True,
    reason="rule_types.judge_call judges a Grep by the rule of the files never to read, not by"
    " NotImplementedError",
)
def test_a_grep_that_reaches_a_file_never_to_read_is_judged_by_reads_none(
    e: Events, cwd: str, path: str | None
):
    """Given the writer at its step `write`, which never reads secrets/ nor .env
    When it greps where the search reaches one of them
    Then the sentence is the one of reads_none"""
    said = rule_types.judge_call(move("call", searched(e, "Grep", search_path(cwd, path))))
    assert said is not None
    assert said.startswith(NEVER_READS)


@pytest.mark.supports("test_a_read_of_another_file_goes_through")
@pytest.mark.parametrize("path", [*REACHES, *BESIDE])
@pytest.mark.xfail(
    strict=True,
    reason="rule_types.judge_call lets each Glob through, as it reads no file's content, not by"
    " NotImplementedError",
)
def test_a_glob_breaks_no_rule_wherever_it_looks(e: Events, cwd: str, path: str | None):
    """Given the writer at its step `write`, which never reads secrets/ nor .env
    When it globs in a folder under secrets/, in secrets/, at .env, in the conversation's folder,
    with no path, in secrets-old/, or in docs/
    Then it breaks no rule, as a Glob reads no file's content"""
    assert rule_types.judge_call(move("call", searched(e, "Glob", search_path(cwd, path)))) is None


@pytest.mark.supports("test_a_read_of_another_file_goes_through")
@pytest.mark.parametrize("path", BESIDE)
@pytest.mark.xfail(
    strict=True,
    reason="rule_types.judge_call judges a Grep by the rule of the files never to read, not by"
    " NotImplementedError",
)
def test_a_grep_that_reaches_no_file_never_to_read_breaks_no_rule(e: Events, cwd: str, path: str):
    """Given the writer at its step `write`, which never reads secrets/ nor .env
    When it greps in secrets-old/ or in docs/
    Then it breaks no rule"""
    assert rule_types.judge_call(move("call", searched(e, "Grep", search_path(cwd, path)))) is None


@pytest.mark.supports(
    "test_a_bash_command_that_reads_a_file_never_to_read_is_stopped_by_its_commands"
)
def test_a_bash_command_that_reaches_a_file_never_to_read_is_judged_by_commands(e: Events):
    """Given the writer at its step `write`, which never reads secrets/ and runs `git log`
    When it runs `cat secrets/key.txt`
    Then the sentence is the one of commands, as reads_none judges no Bash call"""
    said = rule_types.judge_call(move("call", e.bash("cat secrets/key.txt", WRITER)))
    assert said == runs_only("write", ["git log"])


@pytest.mark.supports("test_a_step_is_held_only_to_the_types_its_rules_pick")
def test_a_call_that_breaks_no_rule_or_whose_step_judges_no_call_holds(e: Events, cwd: str):
    """Given the writer at its step `write`, and the reviewer at its step `review`, which has no
    rule that judges a call
    When the writer writes CHANGELOG.md, and the reviewer writes notes.txt
    Then neither breaks a rule"""
    assert (
        rule_types.judge_call(move("call", e.write(os.path.join(cwd, "CHANGELOG.md"), WRITER)))
        is None
    )
    review = move(
        "call", e.write(os.path.join(cwd, "notes.txt"), REVIEWER), step="review", agent=REVIEWER
    )
    assert rule_types.judge_call(review) is None


@pytest.mark.supports("test_a_step_is_held_only_to_the_types_its_rules_pick")
@pytest.mark.parametrize("step", ["report", None])
def test_a_call_is_judged_by_the_rules_of_its_own_step_alone(e: Events, cwd: str, step: str | None):
    """Given the writer at its step `report`, whose rules judge no call, or with each step marked
    done
    When it writes notes.txt, reads secrets/key.txt, and runs `git push`, each of which a rule of
    `write` stops
    Then none breaks a rule"""
    for given in (
        e.write(os.path.join(cwd, "notes.txt"), WRITER),
        e.read(os.path.join(cwd, "secrets/key.txt"), WRITER),
        e.bash("git push", WRITER),
    ):
        assert rule_types.judge_call(move("call", given, step=step)) is None


@pytest.mark.supports("test_a_step_is_held_only_to_the_types_its_rules_pick")
def test_a_call_of_a_tool_that_no_rule_type_judges_holds(e: Events, cwd: str):
    """Given the writer at its step `write`, which writes CHANGELOG.md and docs/changes/
    When it calls NotebookEdit on notes.ipynb
    Then it breaks no rule, as no rule type judges that tool"""
    given = e.write(os.path.join(cwd, "notes.ipynb"), WRITER, tool="NotebookEdit")
    assert rule_types.judge_call(move("call", given)) is None


# A step with two rules of the files it writes.
TWICE: list[Step] = [
    {
        "name": "write",
        "rules": [
            {"type": "writes", "paths": ["CHANGELOG.md"]},
            {"type": "writes", "paths": ["docs/"]},
        ],
    }
]


@pytest.mark.supports("test_a_step_is_held_only_to_the_types_its_rules_pick")
@pytest.mark.parametrize(
    "path, said",
    [
        ("docs/a.md", writes_only("write", ["CHANGELOG.md"], "docs/a.md")),
        ("CHANGELOG.md", writes_only("write", ["docs/"], "CHANGELOG.md")),
    ],
)
def test_a_call_is_judged_by_each_rule_of_its_kind_and_gives_the_first_it_breaks(
    e: Events, cwd: str, path: str, said: str
):
    """Given a step whose first rule writes CHANGELOG.md, and second docs/
    When the writer writes docs/a.md, which breaks the first, or CHANGELOG.md, which breaks the
    second
    Then the sentence is the first rule's, or the second's"""
    call = holding(move("call", e.write(os.path.join(cwd, path), WRITER)), TWICE)
    assert rule_types.judge_call(call) == said


# The order of the rules: a mark.


@pytest.mark.supports("test_a_mark_is_checked_for_the_step_due_before_the_files_it_reads_whole")
def test_a_mark_is_judged_by_order_before_its_reads(e: Events):
    """Given the writer at its step `write` that marked no step and read nothing
    When it marks `report`
    Then the sentence is order's, naming `write` due before `report`, as the rules of the step it
    marks judge it"""
    marking = move(
        "report", e.bash("lane-step report", WRITER), step="write", report=marked("report")
    )
    assert rule_types.judge_mark(marking) == comes_before("write", "report")


@pytest.mark.supports("test_a_mark_is_checked_for_the_files_it_reads_whole_before_its_items")
def test_a_mark_is_judged_by_its_reads_before_its_items(e: Events):
    """Given the writer that read nothing and marked no item
    When it marks `write`
    Then the sentence is reads_whole's, naming NOTES.md, and no item"""
    said = rule_types.judge_mark(marking_write(e))
    assert said == reads_whole_of("write", ["NOTES.md"], ["NOTES.md from its line 1"])


@pytest.mark.supports("test_a_mark_is_checked_for_the_files_it_reads_whole_before_its_items")
def test_a_mark_is_judged_by_its_items_once_its_reads_hold(e: Events):
    """Given the writer that read NOTES.md whole and marked `dated` alone
    When it marks `write`
    Then the sentence is checklist's, naming `linked`"""
    said = rule_types.judge_mark(
        marking_write(e, read("NOTES.md", 1, 6), mark("write", item="dated"))
    )
    assert said == checklist_of("write", ["linked"])


# A step whose rules list the types that judge a mark in the order opposite to the one Lane asks.
REVERSED: list[Step] = [
    {"name": "write", "rules": []},
    {
        "name": "report",
        "rules": [
            {"type": "checklist", "items": ["dated"]},
            {"type": "reads_whole", "paths": ["CHANGELOG.md"]},
            {"type": "order"},
        ],
    },
]


@pytest.mark.supports("test_a_mark_is_checked_for_the_step_due_before_the_files_it_reads_whole")
@pytest.mark.parametrize(
    "entries, said",
    [
        ((), comes_before("write", "report")),
        (
            (mark("write"),),
            reads_whole_of("report", ["CHANGELOG.md"], ["CHANGELOG.md from its line 1"]),
        ),
        ((mark("write"), read("CHANGELOG.md", 1, 6)), checklist_of("report", ["dated"])),
    ],
)
def test_a_mark_is_judged_by_order_reads_and_items_whatever_order_its_rules_list(
    e: Events, entries: tuple[Entry, ...], said: str
):
    """Given a step `report` whose rules list a checklist, then a read whole, then order, and the
    writer that marked nothing, `write` alone, or `write` and read CHANGELOG.md whole
    When it marks `report`
    Then the sentence is order's, reads_whole's, or checklist's"""
    marking = holding(
        move(
            "report",
            e.bash("lane-step report", WRITER),
            *entries,
            step="report",
            report=marked("report"),
        ),
        REVERSED,
    )
    assert rule_types.judge_mark(marking) == said


@pytest.mark.supports("test_a_step_marked_once_each_item_is_done_holds")
def test_a_mark_that_breaks_no_rule_holds(e: Events):
    """Given the writer that read NOTES.md whole and marked each item
    When it marks `write`
    Then no rule finds anything"""
    entries = (read("NOTES.md", 1, 6), mark("write", item="dated"), mark("write", item="linked"))
    assert rule_types.judge_mark(marking_write(e, *entries)) is None


@pytest.mark.supports("test_a_step_is_held_only_to_the_types_its_rules_pick")
def test_a_mark_of_a_step_that_the_role_lacks_holds(e: Events):
    """Given the writer that marked nothing
    When it marks `draft`, which the writer's steps don't name
    Then no rule finds anything"""
    marking = move("report", e.bash("lane-step draft", WRITER), report=marked("draft"))
    assert rule_types.judge_mark(marking) is None


# The order of the rules: an end.


def with_check(rules: Rules, command: str = "touch ran; exit 1") -> Rules:
    """The rules, the check of the writer's `report` changed to the command."""
    changed = copy.deepcopy(rules)
    rule(changed["roles"]["log:writer"]["steps"][1], "check")["check"] = command
    return changed


@pytest.mark.supports("test_an_end_with_no_result_names_the_result_before_the_check")
def test_an_end_is_judged_by_its_result_before_its_steps_and_its_check(e: Events, cwd: str):
    """Given a check that leaves a file where it runs, and the writer that marked each step and gave
    no result
    When it ends
    Then the sentence is the result rule's of `report`, and the check didn't run"""
    ended = move("end", e.ended(WRITER), mark("write"), mark("report"))
    said = rule_types.judge_end(held(ended, with_check(RULES)))
    assert said == no_result("report", ["written"])
    assert not os.path.exists(os.path.join(cwd, "ran"))


@pytest.mark.supports("test_an_end_with_a_step_undone_names_the_step_before_the_check")
def test_an_end_is_judged_by_its_steps_before_its_check(e: Events, cwd: str):
    """Given a check that leaves a file where it runs, and the writer that gave `written` and
    marked `write` alone
    When it ends
    Then the sentence is order's of `report`, and the check didn't run"""
    ended = held(move("end", e.ended(WRITER), gave("written"), mark("write")), with_check(RULES))
    assert rule_types.judge_end(ended) == ends_before("report")
    assert not os.path.exists(os.path.join(cwd, "ran"))


@pytest.mark.supports("test_an_end_that_the_plugins_check_doesnt_pass_is_stopped_with_what_it_said")
def test_an_end_whose_result_and_steps_hold_is_judged_by_its_check(e: Events, cwd: str):
    """Given the writer that gave `written` and marked each step, its CHANGELOG.md holding no
    entry of 1.2.0
    When it ends
    Then the sentence is the check's of `report`, with what it said"""
    write_files(cwd, {"CHANGELOG.md": "# Changelog\n"})
    end = move("end", e.ended(WRITER), gave("written"), mark("write"), mark("report"))
    assert rule_types.judge_end(end) == check_fails("report", lane_bench.CHECK_SAYS)


@pytest.mark.supports("test_an_end_that_the_plugins_check_passes_goes_through")
def test_an_end_that_breaks_no_rule_holds(e: Events):
    """Given the writer that gave `written` and marked each step, its CHANGELOG.md holding the
    entry
    When it ends
    Then no rule finds anything"""
    end = move("end", e.ended(WRITER), gave("written"), mark("write"), mark("report"))
    assert rule_types.judge_end(end) is None


@pytest.mark.supports("test_an_end_with_no_result_is_stopped_with_the_results_it_may_give")
@pytest.mark.parametrize(
    "entries, said",
    [
        ((), no_result("review", ["good", "more", "split"], "log:reviewer")),
        ((gave("good", REVIEWER),), None),
    ],
)
def test_an_end_of_a_role_of_one_step_is_judged_by_its_result(
    e: Events, entries: tuple[Entry, ...], said: str | None
):
    """Given the reviewer of one step `review`, which marked nothing, with no result or `good`
    When it ends
    Then the sentence is the result rule's of `review`, or there's none"""
    end = move("end", e.ended(REVIEWER), *entries, step="review", agent=REVIEWER)
    assert rule_types.judge_end(end) == said


@pytest.mark.supports("test_a_step_is_held_only_to_the_types_its_rules_pick")
def test_an_end_of_a_role_of_no_step_holds(e: Events):
    """Given a writer whose role has no step, which gave no result
    When it ends
    Then no rule finds anything"""
    assert rule_types.judge_end(holding(move("end", e.ended(WRITER), step=None), [])) is None


@pytest.mark.supports("test_an_end_with_no_result_names_the_result_before_the_check")
@pytest.mark.parametrize(
    "entries, said",
    [
        ((), no_result("draft", ["drafted"])),
        ((gave("drafted"),), ends_before("draft")),
        ((mark("draft"), gave("drafted")), no_result("report", ["written"])),
        ((mark("draft"), mark("report"), gave("written")), ends_before("write")),
        (
            (mark("draft"), mark("write"), mark("report"), gave("drafted")),
            no_result("report", ["written"]),
        ),
        ((mark("draft"), mark("write"), mark("report"), gave("written")), None),
    ],
)
def test_an_end_of_a_role_of_three_steps_is_judged_by_the_result_rule_of_the_step_due_or_the_last(
    e: Events, entries: tuple[Entry, ...], said: str | None
):
    """Given a writer of three steps, `draft`, whose result rule names `drafted`, `write`, with no
    result rule, and `report`, whose result rule names `written`, each held in order; and the
    writer that marked nothing and gave nothing; gave `drafted` alone; marked `draft` and gave
    `drafted`; marked all but `write` and gave `written`; marked each and gave `drafted`; or marked
    each and gave `written`
    When it ends
    Then the sentence is the result rule's of `draft`, the step due; order's of `draft`; the result
    rule's of `report`, the last, as `write`, the step due, has none; order's of `write`, the
    first step not done; the result rule's of `report`; or there's none"""
    end = holding(move("end", e.ended(WRITER), *entries), THREE)
    assert rule_types.judge_end(end) == said


def ending(at_steps: dict[int, str], checks: bool = True) -> list[Step]:
    """THREE, with each step at an index naming the result among those that end the start there,
    and, where `checks` says so, a check of each step that leaves a file of the step's name where it
    runs and fails."""
    steps = copy.deepcopy(THREE)
    for i, value in at_steps.items():
        steps[i]["rules"].append({"type": "result", "ends": [value]})
    if checks:
        for step in steps:
            name = step["name"]
            step["rules"].append(check_rule(f"touch {name}; echo '{name} fails'; exit 1"))
    return steps


@pytest.mark.supports(
    "test_a_result_that_ends_the_start_at_its_step_lets_it_end_with_later_steps_undone"
)
def test_an_end_with_a_result_that_ends_the_start_at_its_first_step_holds_with_later_ones_undone(
    e: Events, cwd: str
):
    """Given a writer of three steps whose first, `draft`, names `unclear` among the results that
    end the start, each step with a check that fails, and the writer that marked no step and gave
    `unclear`
    When it ends
    Then no rule finds anything, and no check ran, as the start ends at `draft`"""
    end = holding(move("end", e.ended(WRITER), gave("unclear")), ending({0: "unclear"}))
    assert rule_types.judge_end(end) is None
    assert not [
        name for name in ("draft", "write", "report") if os.path.exists(os.path.join(cwd, name))
    ]


@pytest.mark.supports(
    "test_a_result_that_ends_the_start_at_a_later_step_leaves_the_steps_before_it_held"
)
@pytest.mark.parametrize(
    "entries, said",
    [
        ((gave("unclear"),), ends_before("draft")),
        ((mark("draft"), gave("unclear")), check_fails("draft", "draft fails")),
    ],
)
def test_an_end_with_a_result_that_ends_the_start_at_a_middle_step_holds_the_steps_before_it(
    e: Events, cwd: str, entries: tuple[Entry, ...], said: str
):
    """Given a writer of three steps whose middle one, `write`, names `unclear` among the results
    that end the start, each step with a check that fails, and the writer that gave `unclear`
    having marked no step, or `draft`
    When it ends
    Then the sentence is order's of `draft`, or the check's of `draft`, and the checks of `write`
    and `report` didn't run"""
    end = holding(move("end", e.ended(WRITER), *entries), ending({1: "unclear"}))
    assert rule_types.judge_end(end) == said
    assert not os.path.exists(os.path.join(cwd, "write"))
    assert not os.path.exists(os.path.join(cwd, "report"))


@pytest.mark.supports(
    "test_a_result_that_ends_the_start_at_a_later_step_leaves_the_steps_before_it_held"
)
def test_an_end_with_a_result_that_ends_the_start_at_its_last_step_runs_no_check_of_that_step(
    e: Events, cwd: str
):
    """Given a writer of three steps whose last, `report`, names `blocked` among the results that
    end the start, a check of `report` alone that fails, and the writer that marked `draft` and
    `write` and gave `blocked`
    When it ends
    Then no rule finds anything, and the check of `report` didn't run, as `report` isn't done"""
    steps = ending({2: "blocked"}, checks=False)
    steps[2]["rules"].append(check_rule("touch report; exit 1"))
    end = holding(
        move("end", e.ended(WRITER), mark("draft"), mark("write"), gave("blocked")), steps
    )
    assert rule_types.judge_end(end) is None
    assert not os.path.exists(os.path.join(cwd, "report"))


@pytest.mark.supports(
    "test_a_result_that_ends_the_start_at_its_step_lets_it_end_with_later_steps_undone"
)
def test_a_result_that_two_steps_name_as_ending_the_start_ends_it_at_the_first(e: Events):
    """Given a writer of three steps whose first and last both name `unclear` among the results
    that end the start, and the writer that marked no step and gave `unclear`
    When it ends
    Then no rule finds anything, as the start ends at the first"""
    steps = ending({0: "unclear", 2: "unclear"}, checks=False)
    assert (
        rule_types.judge_end(holding(move("end", e.ended(WRITER), gave("unclear")), steps)) is None
    )


@pytest.mark.supports("test_an_end_that_the_plugins_check_doesnt_pass_is_stopped_with_what_it_said")
def test_an_end_is_judged_by_the_check_of_each_step_in_their_order(e: Events):
    """Given a writer of three steps, each with a check that fails, which marked each and gave
    `written`
    When it ends
    Then the sentence is the check's of `draft`, the first"""
    entries = (mark("draft"), mark("write"), mark("report"), gave("written"))
    end = holding(move("end", e.ended(WRITER), *entries), ending({}))
    assert rule_types.judge_end(end) == check_fails("draft", "draft fails")


# The main conversation's turn's end.


@pytest.mark.supports(
    "test_the_turns_end_in_a_run_of_a_plugin_with_no_order_is_held_to_its_skills_check"
)
@pytest.mark.parametrize("there, stops", [(False, True), (True, False)])
def test_the_main_conversations_turn_end_is_judged_by_its_skills_check(
    e: Events, cwd: str, there: bool, stops: bool
):
    """Given the skill's step `lead`, whose check passes once .log/up.md is there, with or without
    it
    When the main conversation ends its turn
    Then the sentence is the check's of `lead` of log:up, with what it said, or there's none"""
    lead: Step = {
        "name": "lead",
        "rules": [{"type": "check", "check": "test -f .log/up.md || { echo 'no up.md'; exit 1; }"}],
    }
    if there:
        write_files(cwd, {".log/up.md": "x\n"})
    ended = main(move("turn_end", e.stop(), step="lead"), [lead])
    said = rule_types.judge_end(ended)
    assert said == (check_fails("lead", "no up.md", "log:up") if stops else None)


@pytest.mark.supports("test_a_read_of_the_main_conversation_counts_for_no_subagent")
@pytest.mark.parametrize(
    "entries, said",
    [
        ((mark("lead", None),), None),
        ((mark("lead", WRITER),), ends_before("lead", "log:up")),
        ((), ends_before("lead", "log:up")),
    ],
)
def test_the_main_conversations_turn_end_counts_its_own_marks_alone(
    e: Events, entries: tuple[Entry, ...], said: str | None
):
    """Given the skill's step `lead`, held in order, and the main conversation's mark of it, the
    writer a1's mark of a step of that name, or none
    When the main conversation ends its turn
    Then there's no sentence, or order's of `lead` of log:up"""
    lead: Step = {"name": "lead", "rules": [{"type": "order"}]}
    ended = main(move("turn_end", e.stop(), *entries, step="lead"), [lead])
    assert rule_types.judge_end(ended) == said
