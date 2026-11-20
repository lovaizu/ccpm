"""The property-based tests of each rule type's check, as Lane's Test strategy names them: an AI
names a file whole, from the top, or through a link, chains commands in any way, marks its steps
and items in any order, reads a file in any parts, and gives its results in any order, beside the
moves of another start of its role and of the main conversation. Each check must judge each such
move as plugins/lane/docs/rules-and-adapters.md says, by a model plainer than the rule type, since
a check that judges wrongly leaves a step unnoticed or stops a right move."""

from __future__ import annotations

import os
import posixpath
import tempfile
from collections.abc import Iterator
from typing import Any

import lane_entries
import pytest
from hypothesis import given
from hypothesis import strategies as st
from lane_events import Events, Subagent
from place import Move
from record import Entry, Run
from rule_types import checklist, commands, order, reads_none, reads_whole, result, writes
from rules import Rule, Step

WRITER = Subagent("a1", "log:writer")
OTHER = Subagent("a2", "log:writer")
# Parts of a path, some of which nearly match one another, as a plugin's files do.
PART = st.sampled_from(["docs", "changes", "changes-old", "CHANGELOG.md", "a.md", ".log", "名前"])
PARTS = st.lists(PART, min_size=1, max_size=3)
# A path of a rule, a folder's closing with /.
RULE_PATH = st.builds(
    lambda parts, folder: "/".join(parts) + ("/" if folder else ""), PARTS, st.booleans()
)
# A file from the top of the conversation's folder, or outside it.
FILE = st.builds(lambda up, parts: "../" * up + "/".join(parts), st.integers(0, 1), PARTS)
# The forms in which an AI names a path from the top: as it is, after ./, whole, and whole through
# a link to the conversation's folder.
FORMS = ("top", "dot", "whole", "link")
NAME = st.text("abcdefgh", min_size=1, max_size=6)
# Who marks, reads, or gives a result: the writer, another start of its role, or the main
# conversation.
WHO = st.sampled_from([WRITER.id, OTHER.id, None])


@pytest.fixture(scope="module")
def folder() -> Iterator[tuple[str, str]]:
    """The folder that the conversation works in, whole with each link followed, and a link to
    it."""
    with tempfile.TemporaryDirectory() as tmp:
        cwd = os.path.realpath(os.path.join(tmp, "repo"))
        os.makedirs(cwd)
        link = os.path.join(tmp, "link")
        os.symlink(cwd, link)
        yield cwd, link


def named_as(form: str, path: str, folder: tuple[str, str]) -> str:
    """The path from the top, named in the form."""
    cwd, link = folder
    if form == "dot":
        return "./" + path
    if form == "whole":
        return posixpath.normpath(posixpath.join(cwd, path))
    if form == "link":
        return posixpath.join(link, path)
    return path


def names(paths: list[str], file: str) -> bool:
    """The model of a rule's paths: whether one is the file, or a folder that it lies under."""
    return any(path == file or (path.endswith("/") and file.startswith(path)) for path in paths)


def holds(searched: str, path: str) -> bool:
    """The model of a search's reach: whether the folder searched, from the top, is the rule's
    path or holds it."""
    inside = posixpath.relpath(
        posixpath.join("/c/w", path.rstrip("/")), posixpath.join("/c/w", searched)
    )
    return not inside.startswith("..")


def move(
    kind: str, event: dict[str, Any], steps: list[Step], entries: list[Entry], **fields: Any
) -> Move:
    """The writer's move on a run r1 whose two starts of log:writer are tied to a1 and a2, held
    to the steps, its record holding the entries after."""
    head: list[Entry] = [
        {"kind": "run", "run": "r1", "skill": "log:up", "words": "1.2.0"},
        lane_entries.start("u1"),
        lane_entries.tie("u1", WRITER.id),
        lane_entries.start("u2"),
        lane_entries.tie("u2", OTHER.id),
    ]
    run = Run("r1", "session-1", "log:up", "1.2.0", "/plugins/log", [*head, *entries])
    return Move(
        kind,
        event,
        run,
        "log:writer",
        WRITER.id,
        None,
        steps,
        fields.get("step"),
        fields.get("report"),
    )


def events(cwd: str) -> Events:
    return Events(cwd, os.path.join(os.path.dirname(cwd), "transcripts", "session-1.jsonl"))


def one_step(rule: Rule, name: str = "write") -> Step:
    return {"name": name, "rules": [rule]}


@pytest.mark.supports("test_a_write_of_a_file_that_its_step_doesnt_name_is_stopped_with_the_step")
@given(
    st.lists(RULE_PATH, max_size=4),
    FILE,
    st.sampled_from(FORMS),
    st.sampled_from(["Write", "Edit", "NotebookEdit"]),
)
def test_a_write_is_judged_by_the_file_it_names_in_any_form(
    folder: tuple[str, str], paths: list[str], file: str, form: str, tool: str
):
    """Given any paths of a rule of the files a step writes, none among them, and any file inside
    the conversation's folder or outside it
    When the writer writes the file by Write, Edit, or NotebookEdit, naming it from the top, after
    ./, whole, or whole through a link to the folder
    Then the rule stops the call exactly where no path of the rule is the file or a folder that it
    lies under
    (Model-based and metamorphic, resting on S1, the Strategy of a folder that lets through each
    file under it, and named_files.of_call's Gives.)"""
    e = events(folder[0])
    named = named_as(form, file, folder)
    event = e.notebook(named, WRITER) if tool == "NotebookEdit" else e.write(named, WRITER, tool)
    rule: Rule = {"type": "writes", "paths": paths}
    said = writes.judge_call(rule, one_step(rule), move("call", event, [one_step(rule)], []))
    assert (said is None) == names(paths, posixpath.normpath(file))


SEARCHED = st.one_of(
    st.none(),
    st.builds(
        lambda up, parts: posixpath.normpath("../" * up + "/".join(parts)),
        st.integers(0, 1),
        st.lists(PART, max_size=2),
    ),
)


@pytest.mark.supports(
    "test_a_grep_whose_search_reaches_a_file_never_to_read_is_stopped_with_the_step"
)
@given(st.lists(RULE_PATH, min_size=1, max_size=3), FILE, SEARCHED, st.sampled_from(FORMS))
def test_a_read_or_a_search_is_judged_by_the_files_never_to_read_in_any_form(
    folder: tuple[str, str], paths: list[str], file: str, searched: str | None, form: str
):
    """Given any paths of a rule of the files a step never reads, any file, and any folder or file
    to search, or none, which searches the conversation's folder
    When the writer reads the file, and greps the path, each named from the top, after ./, whole,
    or whole through a link to the folder
    Then the rule stops the Read exactly where a path of the rule is the file or a folder that it
    lies under, and the Grep exactly where the path searched is such a file, or a path of the rule,
    or a folder that holds one
    (Model-based and metamorphic, resting on S2 and named_files.reaches's Gives.)"""
    e = events(folder[0])
    rule: Rule = {"type": "reads_none", "paths": paths}
    steps = [one_step(rule)]
    read = move("call", e.read(named_as(form, file, folder), WRITER), steps, [])
    assert (reads_none.judge_call(rule, steps[0], read) is None) == (
        not names(paths, posixpath.normpath(file))
    )
    given_path = None if searched is None else named_as(form, searched, folder)
    grep = move("call", e.search("Grep", given_path, WRITER), steps, [])
    top = searched or "."
    reached = names(paths, top) or any(holds(top, path) for path in paths)
    assert (reads_none.judge_call(rule, steps[0], grep) is None) == (not reached)


WORD = st.sampled_from(["git", "log", "status", "push", "--oneline", "npm", "test", "ls"])
REPORTER = st.sampled_from(["lane-step", "lane-item", "lane-result"])
# A part of a command: none, any words, or a reporter with its words, with any spaces about it.
PART_OF_COMMAND = st.tuples(
    st.one_of(
        st.lists(WORD, max_size=4),
        st.builds(lambda first, rest: [first, *rest], REPORTER, st.lists(WORD, max_size=2)),
    ),
    st.sampled_from(["", " ", "  "]),
)
SEPARATOR = st.sampled_from(["|", " | ", "&&", " && ", "||", " || ", ";", "; ", "\n"])


@pytest.mark.supports("test_a_command_chained_after_a_named_one_is_stopped")
@given(
    st.lists(st.lists(WORD, min_size=1, max_size=2).map(" ".join), max_size=3),
    st.lists(PART_OF_COMMAND, min_size=1, max_size=4),
    st.data(),
)
def test_a_bash_call_is_judged_by_each_command_it_chains(
    folder: tuple[str, str],
    named: list[str],
    parts: list[tuple[list[str], str]],
    data: st.DataObject,
):
    """Given any commands of a rule, none among them, and any Bash call of any commands, Lane's
    reporters and blank ones among them, chained by |, &&, ||, ;, and newlines
    When the writer runs the call
    Then the rule stops it exactly where a command of it that isn't blank opens with the words of
    no named command and is no reporter
    (Model-based, resting on S4 and rule_types/commands.py's Gives.)"""
    pieces = [f"{pad}{' '.join(words)}{pad}" for words, pad in parts]
    command = pieces[0]
    for piece in pieces[1:]:
        command += data.draw(SEPARATOR) + piece
    rule: Rule = {"type": "commands", "commands": named}
    call = move("call", events(folder[0]).bash(command, WRITER), [one_step(rule)], [])
    left = [
        words
        for words, _ in parts
        if words
        and words[0] not in ("lane-step", "lane-item", "lane-result")
        and not any(words[: len(each.split())] == each.split() for each in named)
    ]
    assert (commands.judge_call(rule, one_step(rule), call) is None) == (not left)


def mark(who: str | None, step: str, item: str | None = None) -> Entry:
    entry: Entry = {"kind": "mark", "run": "r1", "agent_id": who, "step": step}
    if item:
        entry["item"] = item
    return entry


STEP_NAMES = st.lists(NAME, min_size=1, max_size=5, unique=True)


@pytest.mark.supports("test_a_step_marked_before_the_step_before_it_is_stopped_with_the_step_due")
@given(STEP_NAMES, st.data())
def test_a_step_is_held_to_each_step_before_it_by_the_writers_own_marks(
    folder: tuple[str, str], names_: list[str], data: st.DataObject
):
    """Given any steps of the writer, each with a rule of order, and any marks of steps and items
    in any order, by the writer, by another start of its role, and by the main conversation
    When the writer marks any of its steps done, and when it ends
    Then the mark is stopped exactly where a step before it has no mark of the writer, with the
    first such step due, and the end exactly where the step has none
    (Model-based, resting on S5 and rule_types/order.py's Gives.)"""
    steps: list[Step] = [{"name": name, "rules": [{"type": "order"}]} for name in names_]
    entries = data.draw(
        st.lists(
            st.builds(mark, WHO, st.sampled_from(names_), st.one_of(st.none(), NAME)), max_size=8
        )
    )
    done = {
        each["step"] for each in entries if each["agent_id"] == WRITER.id and "item" not in each
    }
    at = data.draw(st.integers(0, len(steps) - 1))
    step = steps[at]
    e = events(folder[0])
    marking = move(
        "report",
        e.bash(f"lane-step {step['name']}", WRITER),
        steps,
        entries,
        step=step["name"],
        report={"kind": "step", "step": step["name"]},
    )
    due = next((name for name in names_[:at] if name not in done), None)
    expected = due and (
        f"You're at the step `{due}` of log:writer, which comes before `{step['name']}`.\n"
        f"Do `{due}` and mark it done with lane-step {due} first."
    )
    assert order.judge_mark(step["rules"][0], step, marking) == expected
    end = move("end", e.ended(WRITER), steps, entries, step=step["name"])
    undone = step["name"] not in done and (
        f"You end before the step `{step['name']}` of log:writer is done.\n"
        f"Do it and mark it done with lane-step {step['name']}."
    )
    assert order.judge_end(step["rules"][0], step, end) == (undone or None)


def listed(values: list[str], joined: str = "and") -> str:
    """The values as rules-and-adapters.md's sentences list them, the last two joined."""
    return values[0] if len(values) == 1 else f"{', '.join(values[:-1])} {joined} {values[-1]}"


@pytest.mark.supports("test_a_step_marked_before_its_items_names_each_item_not_done")
@given(st.lists(NAME, min_size=1, max_size=4, unique=True), st.data())
def test_a_step_is_held_to_each_item_of_its_checklist_by_the_writers_own_marks(
    folder: tuple[str, str], items: list[str], data: st.DataObject
):
    """Given any items of the checklist of the writer's step `write`, and any marks of those items
    in any order, by the writer, by another start of its role, and by the main conversation, of
    `write` and of another step
    When the writer marks `write` done
    Then the mark is stopped exactly where an item has no mark of the writer at `write`, naming
    each such item in the rule's order
    (Model-based, resting on S6 and rule_types/checklist.py's Gives.)"""
    entries = data.draw(
        st.lists(
            st.builds(mark, WHO, st.sampled_from(["write", "report"]), st.sampled_from(items)),
            max_size=8,
        )
    )
    done = {
        each["item"]
        for each in entries
        if each["agent_id"] == WRITER.id and each["step"] == "write"
    }
    rule: Rule = {"type": "checklist", "items": items}
    step = one_step(rule)
    marking = move(
        "report",
        events(folder[0]).bash("lane-step write", WRITER),
        [step],
        entries,
        step="write",
        report={"kind": "step", "step": "write"},
    )
    undone = [item for item in items if item not in done]
    expected = undone and (
        f"You're at the step `write` of log:writer, whose checklist isn't done: {listed(undone)}.\n"
        "Do each and mark it done with lane-item write <item> first."
    )
    assert checklist.judge_mark(rule, step, marking) == (expected or None)


READ = st.tuples(st.integers(1, 12), st.integers(0, 12))


@pytest.mark.supports("test_reads_in_parts_that_cover_each_line_read_the_file_whole")
@given(st.integers(1, 10), st.booleans(), st.lists(st.tuples(WHO, READ), max_size=6))
def test_a_file_counts_as_read_whole_only_where_the_writers_reads_cover_each_line(
    folder: tuple[str, str],
    lines: int,
    newline: bool,
    reads: list[tuple[str | None, tuple[int, int]]],
):
    """Given NOTES.md of any lines, with or without a last newline, as Read counts its lines, the
    empty line after a last newline among them, and any reads of it in any parts, in any order,
    overlapping or past its end, by the writer, by another start of its role, and by the main
    conversation
    When the writer marks its step done, which reads NOTES.md whole
    Then the mark is stopped exactly where a line of the file lies in no read of the writer,
    naming the first such line
    (Model-based, resting on S3 and rule_types/reads_whole.py's Gives.)"""
    cwd = folder[0]
    text = "\n".join(f"line {n}" for n in range(1, lines + 1)) + ("\n" if newline else "")
    with open(os.path.join(cwd, "NOTES.md"), "w", encoding="utf-8") as f:
        f.write(text)
    entries: list[Entry] = [
        {
            "kind": "read",
            "run": "r1",
            "agent_id": who,
            "path": "NOTES.md",
            "first_line": first,
            "last_line": first + more,
        }
        for who, (first, more) in reads
    ]
    read = {
        n
        for who, (first, more) in reads
        if who == WRITER.id
        for n in range(first, first + more + 1)
    }
    unread = [n for n in range(1, len(text.split("\n")) + 1) if n not in read]
    rule: Rule = {"type": "reads_whole", "paths": ["NOTES.md"]}
    step = one_step(rule)
    marking = move(
        "report",
        events(cwd).bash("lane-step write", WRITER),
        [step],
        entries,
        step="write",
        report={"kind": "step", "step": "write"},
    )
    expected = unread and (
        "You're at the step `write` of log:writer, which reads whole NOTES.md.\n"
        f"Read NOTES.md from its line {unread[0]} before you mark it done."
    )
    assert reads_whole.judge_mark(rule, step, marking) == (expected or None)


RESULT = st.sampled_from(["written", "Written", "writ", "written ", "blocked", "more"])


@pytest.mark.supports("test_an_end_with_a_result_that_the_rule_doesnt_name_is_stopped")
@given(
    st.lists(RESULT, max_size=3, unique=True),
    st.lists(RESULT, max_size=2, unique=True),
    st.lists(st.tuples(WHO, RESULT), max_size=5),
)
def test_an_end_is_judged_by_the_writers_latest_result(
    folder: tuple[str, str],
    results: list[str],
    ends: list[str],
    given_: list[tuple[str | None, str]],
):
    """Given any results and results that end the start of a rule of the writer's step `write`,
    one list at least, and any results given in any order, by the writer, by another start of its
    role, and by the main conversation
    When the writer ends
    Then the end is stopped exactly where the writer's latest result is none that the rule names,
    offering, where the rule names results, each result it may give, the last two joined by `or`
    (Model-based, resting on S7, P1.2, and rule_types/result.py's Gives.)"""
    rule: Rule = {"type": "result"}
    if results:
        rule["results"] = results
    if ends:
        rule["ends"] = ends
    if not (results or ends):
        rule["results"] = ["written"]
    entries: list[Entry] = [
        {
            "kind": "result",
            "run": "r1",
            "agent_id": who,
            "role": "log:up" if who is None else "log:writer",
            "result": value,
        }
        for who, value in given_
    ]
    latest = next((value for who, value in reversed(given_) if who == WRITER.id), None)
    may = [*rule.get("results", []), *rule.get("ends", [])]
    step = one_step(rule)
    said = result.judge_end(
        rule, step, move("end", events(folder[0]).ended(WRITER), [step], entries, step="write")
    )
    assert (said is None) == (latest in may)
    if said is not None and "results" in rule:
        assert said == (
            "You end the step `write` of log:writer with no result it may give.\n"
            f"Give {listed(may, 'or')} with lane-result first."
        )
