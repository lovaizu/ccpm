"""The unit cases of guard.py and of the entries that Claude Code and up run, hook.py, result.py,
and lay.py's command line, through `guard.handle`, `hook.main`, `result.main`, step.py and item.py
as the shell runs them, and `command.main`: an event in and outside a Run, a lanes.json the guard
can't read, each exit code that result.py, step.py, item.py, and lay.py give, and each call that
they refuse."""

from __future__ import annotations

import importlib.util
import io
import json
import os
import runpy
import sys
import tempfile
from dataclasses import replace
from typing import Any

import lane_data as d
import pytest
from events import NotAnEvent
from form import Adapters, After, Move, write_lanes
from guard import handle
from lay.command import main as lay_main
from run_record import (
    Called,
    Ended,
    Gave,
    Marked,
    Started,
    TextFailed,
    TextGiven,
    Tied,
    add,
    lines,
    record_path,
)

LANE = os.path.join(os.path.dirname(d.__file__), *[".."] * 3, "plugins", "lane")


def entry(name: str) -> Any:
    """The module of one of Lane's entries in hooks/lane/, by its file's name."""
    path = os.path.join(LANE, "hooks", "lane", f"{name}.py")
    spec = importlib.util.spec_from_file_location(f"lane_{name}", path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture
def plugin(tmp_path: Any, monkeypatch: pytest.MonkeyPatch) -> str:
    """changelog's folder, with its plugin.json and hooks/, and the system's temporary folder set to
    the case's own."""
    monkeypatch.setenv("TMPDIR", str(tmp_path / "temp"))
    monkeypatch.setattr(tempfile, "tempdir", None)
    os.makedirs(tmp_path / "temp")
    os.makedirs(tmp_path / "changelog" / ".claude-plugin")
    os.makedirs(tmp_path / "changelog" / "hooks")
    (tmp_path / "changelog" / ".claude-plugin" / "plugin.json").write_text('{"name": "changelog"}')
    return str(tmp_path / "changelog")


def laid(plugin: str) -> str:
    """Writes the walkthrough's lanes.json into the plugin, and gives its run record's path."""
    write_lanes(os.path.join(plugin, "hooks", "lanes.json"), d.lanes_file())
    return record_path("changelog", d.SESSION)


@pytest.mark.supports("test_calls_outside_the_run_go_unchecked")
def test_an_event_outside_every_run_goes_and_adds_nothing(plugin: str) -> None:
    """Given: changelog laid, and a conversation with no Run.
    When: handle answers the main conversation's Bash call `git status`.
    Then: it doesn't stop it, says nothing, and adds nothing to the run record."""
    path = laid(plugin)
    event = d.event("PreToolUse", tool_name="Bash", tool_input={"command": "git status"})
    answer = handle(event, plugin)
    assert (answer.stop, answer.words) == (False, "")
    assert lines(path) == ()


@pytest.mark.supports("test_the_walkthroughs_run_moves_in_the_order_the_user_set")
def test_a_skills_call_adds_a_run_and_gives_the_first_start(plugin: str) -> None:
    """Given: changelog laid, and a conversation with no Run.
    When: handle answers the UserPromptExpansion of /changelog:write.
    Then: it adds the call of write's Run, and gives writer's start due."""
    path = laid(plugin)
    event = d.event("UserPromptExpansion", command_name="changelog:write", command_args="")
    answer = handle(event, plugin)
    assert not answer.stop
    assert answer.words == "changelog: Start `changelog:writer` with `Carry out your steps`."
    ((called,),) = [[line for line in lines(path) if isinstance(line, Called)]]
    assert called.skill == "write"


@pytest.mark.supports("test_a_call_the_guard_cant_check_is_stopped_with_who_must_fix_it")
def test_an_event_with_lanes_json_unreadable_is_stopped_with_who_must_fix_it(plugin: str) -> None:
    """Given: changelog whose hooks/lanes.json isn't JSON, and write's Run with writer tied to
    a01.
    When: handle answers a01's Bash call.
    Then: it stops the call, saying lanes.json can't be read and who must fix it."""
    path = record_path("changelog", d.SESSION)
    for line in (
        Called("r1", "write", ""),
        Started("r1", "writer", "Carry out your steps", {}, "t1", False),
        Tied("r1", "t1", "a01"),
    ):
        add(path, line)
    with open(os.path.join(plugin, "hooks", "lanes.json"), "w", encoding="utf-8") as f:
        f.write("{")
    event = d.event("PreToolUse", agent_id="a01", tool_name="Bash", tool_input={"command": "ls"})
    answer = handle(event, plugin)
    assert answer.stop and "lanes.json" in answer.words


WAITING = "0.2.0 waits for your approval"


def laid_with_adapter(plugin: str, gives: str) -> str:
    """Writes the walkthrough's lanes.json into the plugin, with an adapter of a start's text that
    prints what `gives` names for writer, `none` or `text`, and gives the run record's path."""
    printed = {"none": {"none": WAITING}, "text": {"text": "Carry out your steps"}}[gives]
    return laid_with_program(plugin, f"json.load(sys.stdin)\nprint(json.dumps({printed!r}))\n")


def laid_with_program(plugin: str, body: str) -> str:
    """Writes the walkthrough's lanes.json into the plugin, with an adapter of a start's text whose
    Python, after `import json, sys`, is the body, and gives the run record's path."""
    adapter = os.path.join(plugin, "hooks", "adapters", "text.py")
    os.makedirs(os.path.dirname(adapter), exist_ok=True)
    with open(adapter, "w", encoding="utf-8") as f:
        f.write(f"#!{sys.executable}\nimport json, sys\n{body}")
    os.chmod(adapter, 0o755)
    lanes = d.lanes_file()
    adapters = Adapters("hooks/adapters/text.py", None)
    proposal = replace(lanes.proposal, adapters=adapters)
    write_lanes(os.path.join(plugin, "hooks", "lanes.json"), replace(lanes, proposal=proposal))
    return record_path("changelog", d.SESSION)


@pytest.mark.supports("test_a_start_no_work_waits_for_is_left_out_and_the_turn_ends")
def test_a_skills_call_gives_why_in_place_of_a_start_no_work_waits_for(plugin: str) -> None:
    """Given: changelog laid with an adapter of a start's text that gives, for writer, that no work
    waits for it, and a conversation with no Run.
    When: handle answers the UserPromptExpansion of /changelog:write.
    Then: it adds the call of write's Run, lets the call run, and gives why in place of writer's
    start."""
    path = laid_with_adapter(plugin, "none")
    event = d.event(
        "UserPromptExpansion", cwd=plugin, command_name="changelog:write", command_args=""
    )
    answer = handle(event, plugin)
    assert not answer.stop
    assert WAITING in answer.words and "Start `changelog:writer`" not in answer.words
    assert [x.skill for x in lines(path) if isinstance(x, Called)] == ["write"]


@pytest.mark.supports("test_a_start_no_work_waits_for_is_left_out_and_the_turn_ends")
def test_a_start_of_a_role_no_work_waits_for_is_stopped(plugin: str) -> None:
    """Given: changelog laid with an adapter of a start's text that gives, for writer, that no work
    waits for it, and write's Run called.
    When: handle answers the main conversation's Agent call of changelog:writer.
    Then: it stops the start, and adds no Start."""
    path = laid_with_adapter(plugin, "none")
    add(path, Called("r1", "write", ""))
    tool_input = {"subagent_type": "changelog:writer", "prompt": "Carry out your steps"}
    event = d.event(
        "PreToolUse", cwd=plugin, tool_name="Agent", tool_input=tool_input, tool_use_id="t1"
    )
    answer = handle(event, plugin)
    assert answer.stop
    assert not [x for x in lines(path) if isinstance(x, Started)]


@pytest.mark.supports("test_a_start_no_work_waits_for_is_left_out_and_the_turn_ends")
@pytest.mark.parametrize(
    "gives, stops", [("text", True), ("none", False)], ids=["writer's start due", "left out"]
)
def test_the_main_conversations_end_stops_only_for_a_start_due(
    plugin: str, gives: str, stops: bool
) -> None:
    """Given: changelog laid with an adapter of a start's text that gives writer its text, or that
    no work waits for it, and handle has answered the UserPromptExpansion of /changelog:write, with
    no subagent started.
    When: handle answers the main conversation's Stop.
    Then: it stops the end where writer's start is due, and lets it end where the start is left
    out."""
    laid_with_adapter(plugin, gives)
    called = {"command_name": "changelog:write", "command_args": ""}
    handle(d.event("UserPromptExpansion", cwd=plugin, **called), plugin)
    answer = handle(d.event("Stop", cwd=plugin, last_message="Waiting."), plugin)
    assert answer.stop is stops


# An adapter's body that fails, as one whose steps haven't yet made what it reads.
FAILS = "sys.exit('no version to write yet')\n"
# An adapter's body that gives writer the text and value of each version that no Start that runs
# holds, and that no work waits for writer once each has its Start.
BY_VERSION = """held = {s["values"].get("version") for s in json.load(sys.stdin)["running"]}
waiting = [v for v in ("0.2.0", "0.3.0") if v not in held]
if waiting:
    print(json.dumps({"text": f"Write {waiting[0]}", "values": {"version": waiting[0]}}))
else:
    print(json.dumps({"none": "each version has its writer"}))
"""


def called(plugin: str) -> Any:
    """The UserPromptExpansion of /changelog:write, in the plugin's folder."""
    return d.event(
        "UserPromptExpansion", cwd=plugin, command_name="changelog:write", command_args=""
    )


def posted(plugin: str, tool_name: str = "Bash", **fields: Any) -> Any:
    """The PostToolUse of a call of the main conversation, `git status` by default."""
    given: dict[str, Any] = {
        "tool_input": {"command": "git status"},
        "tool_use_id": "t9",
        "tool_response": {"stdout": "", "stderr": ""},
    }
    given.update(fields)
    return d.event("PostToolUse", cwd=plugin, tool_name=tool_name, **given)


@pytest.mark.supports(
    "test_a_start_whose_adapter_failed_at_the_call_is_given_once_it_gives_its_text"
)
def test_a_skills_call_whose_adapter_fails_keeps_that_it_failed(plugin: str) -> None:
    """Given: changelog laid with an adapter of a start's text that fails, and no Run.
    When: handle answers the UserPromptExpansion of /changelog:write.
    Then: it lets the call run, and adds the call of write's Run and that the text failed."""
    path = laid_with_program(plugin, FAILS)
    answer = handle(called(plugin), plugin)
    assert not answer.stop and "no version to write yet" in answer.words
    (call, failed) = lines(path)
    assert isinstance(call, Called) and failed == TextFailed(call.run)


@pytest.mark.supports(
    "test_a_start_whose_adapter_failed_at_the_call_is_given_once_it_gives_its_text"
)
def test_a_later_call_gives_the_start_once_the_adapter_gives_its_text(plugin: str) -> None:
    """Given: changelog laid with an adapter of a start's text that failed at the call of
    /changelog:write, and since gives writer `Write 0.2.0`.
    When: handle answers the PostToolUse of the main conversation's `git status`, twice.
    Then: it gives writer's start with that text the first time, adding that the text was given,
    and says nothing the second."""
    path = laid_with_program(plugin, FAILS)
    handle(called(plugin), plugin)
    laid_with_program(plugin, BY_VERSION)
    first = handle(posted(plugin), plugin)
    assert (first.stop, first.words) == (
        False,
        "changelog: Start `changelog:writer` with `Write 0.2.0`.",
    )
    assert lines(path)[-1] == TextGiven(lines(path)[0].run)
    second = handle(posted(plugin), plugin)
    assert (second.stop, second.words) == (False, ""), "the start is given once"


@pytest.mark.supports(
    "test_a_start_whose_adapter_failed_at_the_call_is_given_once_it_gives_its_text"
)
def test_a_later_call_while_the_adapter_still_fails_says_nothing(plugin: str) -> None:
    """Given: changelog laid with an adapter of a start's text that failed at the call of
    /changelog:write, and still fails.
    When: handle answers the PostToolUse of the main conversation's `git status`.
    Then: it lets it through, says nothing, and adds no line."""
    path = laid_with_program(plugin, FAILS)
    handle(called(plugin), plugin)
    before = lines(path)
    answer = handle(posted(plugin), plugin)
    assert (answer.stop, answer.words) == (False, "")
    assert lines(path) == before


@pytest.mark.supports(
    "test_a_start_whose_adapter_failed_at_the_call_is_given_once_it_gives_its_text"
)
def test_a_subagents_call_asks_no_adapter_again(plugin: str) -> None:
    """Given: changelog laid with an adapter of a start's text that failed at the call of
    /changelog:write, and since gives writer `Write 0.2.0`; writer's Start tied to a01.
    When: handle answers the PostToolUse of a01's `git status`.
    Then: it says nothing, and adds no line, as only the main conversation's calls follow the
    skill's own steps."""
    path = laid_with_program(plugin, FAILS)
    add(path, Called("r1", "write", ""))
    add(path, TextFailed("r1"))
    add(path, Started("r1", "writer", "Write 0.2.0", {}, "t1", False))
    add(path, Tied("r1", "t1", "a01"))
    laid_with_program(plugin, BY_VERSION)
    before = lines(path)
    answer = handle(posted(plugin, agent_id="a01", agent_type="changelog:writer"), plugin)
    assert (answer.stop, answer.words) == (False, "")
    assert lines(path) == before


def started(plugin: str, text: str, tool_use_id: str = "t2") -> Any:
    """The main conversation's Agent call of changelog:writer with the text."""
    tool_input = {"subagent_type": "changelog:writer", "prompt": text}
    return d.event(
        "PreToolUse", cwd=plugin, tool_name="Agent", tool_input=tool_input, tool_use_id=tool_use_id
    )


def agent_posted(plugin: str) -> Any:
    """The PostToolUse of the main conversation's Agent call t1, naming agentId a01."""
    tool_input = {"subagent_type": "changelog:writer", "prompt": "Write 0.2.0"}
    return posted(
        plugin, "Agent", tool_input=tool_input, tool_use_id="t1", tool_response={"agentId": "a01"}
    )


def writer_running(plugin: str, body: str | None) -> str:
    """changelog laid with an adapter of a start's text whose body is given, or none, and write's
    Run with writer's Start for 0.2.0 running; gives the record's path."""
    path = laid_with_program(plugin, body) if body else laid(plugin)
    add(path, Called("r1", "write", ""))
    text = "Write 0.2.0" if body else "Carry out your steps"
    values = {"version": "0.2.0"} if body else {}
    add(path, Started("r1", "writer", text, values, "t1", False))
    return path


@pytest.mark.supports("test_a_start_stays_due_beside_a_start_of_its_role_with_another_text")
def test_a_start_tied_gives_its_roles_start_beside_it_with_another_text(plugin: str) -> None:
    """Given: changelog laid with an adapter of a start's text that gives writer `Write 0.3.0`
    while a Start for 0.2.0 runs, and writer's Start for 0.2.0 by the call t1.
    When: handle answers the PostToolUse of t1, naming agentId a01.
    Then: it ties the Start to a01, and gives writer's start for 0.3.0 due beside it."""
    path = writer_running(plugin, BY_VERSION)
    answer = handle(agent_posted(plugin), plugin)
    assert (answer.stop, answer.words) == (
        False,
        "changelog: Start `changelog:writer` with `Write 0.3.0`.",
    )
    assert lines(path)[-1] == Tied("r1", "t1", "a01")


@pytest.mark.supports("test_a_start_stays_due_beside_a_start_of_its_role_with_another_text")
@pytest.mark.parametrize(
    "body",
    [
        "json.load(sys.stdin)\nprint(json.dumps({'text': 'Write 0.2.0'}))\n",
        "json.load(sys.stdin)\nprint(json.dumps({'none': 'each version has its writer'}))\n",
        None,
    ],
    ids=["the text of the Start that runs", "none", "no adapter, Lane's text"],
)
def test_a_start_tied_says_nothing_where_no_other_text_waits(plugin: str, body: str | None) -> None:
    """Given: changelog laid with an adapter of a start's text that gives writer the text of its
    Start that runs, or that no work waits for it, or with no adapter, and writer's Start by the
    call t1.
    When: handle answers the PostToolUse of t1, naming agentId a01.
    Then: it ties the Start, and says nothing, as no start of writer waits beside it."""
    path = writer_running(plugin, body)
    answer = handle(agent_posted(plugin), plugin)
    assert (answer.stop, answer.words) == (False, "")
    assert lines(path)[-1] == Tied("r1", "t1", "a01")


@pytest.mark.supports("test_a_start_stays_due_beside_a_start_of_its_role_with_another_text")
def test_a_start_beside_one_of_its_role_with_another_text_is_added(plugin: str) -> None:
    """Given: changelog laid with an adapter of a start's text that gives writer `Write 0.3.0`
    while a Start for 0.2.0 runs, and writer's Start for 0.2.0 running.
    When: handle answers the main conversation's Agent call of changelog:writer with `Write
    0.3.0`.
    Then: it lets the start through, and adds writer's Start for 0.3.0 with its value."""
    path = writer_running(plugin, BY_VERSION)
    answer = handle(started(plugin, "Write 0.3.0"), plugin)
    assert (answer.stop, answer.words) == (False, "")
    assert lines(path)[-1] == Started(
        "r1", "writer", "Write 0.3.0", {"version": "0.3.0"}, "t2", False
    )


@pytest.mark.supports("test_a_start_stays_due_beside_a_start_of_its_role_with_another_text")
@pytest.mark.parametrize(
    "body, text",
    [
        ("json.load(sys.stdin)\nprint(json.dumps({'text': 'Write 0.2.0'}))\n", "Write 0.2.0"),
        (None, "Carry out your steps"),
    ],
    ids=["the adapter's text again", "no adapter, Lane's text"],
)
def test_a_start_with_the_text_of_one_of_its_role_that_runs_is_stopped(
    plugin: str, body: str | None, text: str
) -> None:
    """Given: changelog laid with an adapter of a start's text that gives writer the text of its
    Start that runs, or with no adapter, and writer's Start running.
    When: handle answers the main conversation's Agent call of changelog:writer with that text.
    Then: it stops the start, and adds no Start."""
    path = writer_running(plugin, body)
    before = lines(path)
    answer = handle(started(plugin, text), plugin)
    assert answer.stop
    assert lines(path) == before


# The adapter of changelog's records' body that gives writer's `written`, then reviewer's `more`.
WRITTEN_THEN_MORE = (
    "json.load(sys.stdin)\n"
    "print(json.dumps({'results': [{'role': 'writer', 'result': 'written'},"
    " {'role': 'reviewer', 'result': 'more'}]}))\n"
)
# The adapter of changelog's records' body that gives writer's `written`.
WRITTEN = (
    "json.load(sys.stdin)\n"
    "print(json.dumps({'results': [{'role': 'writer', 'result': 'written'}]}))\n"
)


def adapter(plugin: str, name: str, body: str) -> str:
    """Writes the adapter of hooks/adapters/<name>.py whose Python, after `import json, sys`, is
    the body, and gives its path under the plugin."""
    path = os.path.join(plugin, "hooks", "adapters", f"{name}.py")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(f"#!{sys.executable}\nimport json, sys\n{body}")
    os.chmod(path, 0o755)
    return f"hooks/adapters/{name}.py"


def laid_resuming(plugin: str, records: str, text: str | None = None) -> str:
    """Writes the walkthrough's lanes.json into the plugin, with the Route after reviewer's `more`
    resuming writer, an adapter of the plugin's records whose body is given, and an adapter of a
    start's text where its body is given; gives the run record's path."""
    lanes = d.lanes_file()
    more = d.route(After("result", role="reviewer", result="more"), Move("resume", role="writer"))
    routes = tuple(more if r.after == more.after else r for r in lanes.proposal.routes)
    adapters = Adapters(
        adapter(plugin, "text", text) if text else None, adapter(plugin, "records", records)
    )
    proposal = replace(lanes.proposal, routes=routes, adapters=adapters)
    write_lanes(os.path.join(plugin, "hooks", "lanes.json"), replace(lanes, proposal=proposal))
    return record_path("changelog", d.SESSION)


@pytest.mark.supports("test_a_resume_due_of_a_role_never_started_here_is_due_as_its_start")
def test_a_pick_up_gives_a_resume_of_a_role_never_started_as_its_start(plugin: str) -> None:
    """Given: changelog laid with the Route after reviewer's `more` resuming writer, and an adapter
    of its records that gives writer's `written`, then reviewer's `more`; no Run.
    When: handle answers the UserPromptExpansion of /changelog:write.
    Then: it lets the call run, giving writer's start with Lane's text, not its resume."""
    laid_resuming(plugin, WRITTEN_THEN_MORE)
    answer = handle(called(plugin), plugin)
    assert not answer.stop
    assert "changelog: Start `changelog:writer` with `Carry out your steps`." in answer.words
    assert "Resume `changelog:writer`" not in answer.words


@pytest.mark.supports("test_a_run_with_an_adapter_goes_on_after_compact")
def test_a_call_whose_run_the_record_holds_asks_no_adapter_of_records(plugin: str) -> None:
    """Given: changelog laid with an adapter of its records that exits 1, and write's Run in the
    record, with writer's start due, as after /compact.
    When: handle answers the UserPromptExpansion of /changelog:write.
    Then: it lets the call run with writer's start due, as the record holds the Run."""
    path = laid_resuming(plugin, "sys.exit(1)\n")
    add(path, Called("r1", "write", ""))
    answer = handle(called(plugin), plugin)
    assert not answer.stop
    assert answer.words == "changelog: Start `changelog:writer` with `Carry out your steps`."


def picked_up_run(path: str) -> None:
    """Adds write's Run r1, picked up from writer's `written` and reviewer's `more`, with no
    Start."""
    for line in (
        Called("r1", "write", ""),
        Gave("r1", "writer", "written", None),
        Gave("r1", "reviewer", "more", None),
    ):
        add(path, line)


def run_with_starts(path: str) -> None:
    """Adds write's Run r1 in which writer, tied to a01, gave `written`, and reviewer, tied to a02,
    gave `more`, each ended."""
    for line in (
        Called("r1", "write", ""),
        Started("r1", "writer", "Carry out your steps", {}, "t1", False),
        Tied("r1", "t1", "a01"),
        Gave("r1", "writer", "written", "a01"),
        Ended("r1", "a01", False),
        Started("r1", "reviewer", "Carry out your steps", {}, "t2", False),
        Tied("r1", "t2", "a02"),
        Gave("r1", "reviewer", "more", "a02"),
        Ended("r1", "a02", False),
    ):
        add(path, line)


@pytest.mark.supports("test_a_resume_due_of_a_role_never_started_here_is_due_as_its_start")
@pytest.mark.parametrize(
    "run, said",
    [
        (picked_up_run, "changelog: Start `changelog:writer` with `Carry out your steps`."),
        (run_with_starts, "changelog: Resume `changelog:writer` by SendMessage."),
    ],
    ids=["writer never started here", "writer started here"],
)
def test_the_end_stops_with_a_resume_only_where_its_role_was_started(
    plugin: str, run: Any, said: str
) -> None:
    """Given: changelog laid with the Route after reviewer's `more` resuming writer, and write's Run
    after reviewer's `more`, picked up with no Start of writer, or with writer's Start tied to
    a01.
    When: handle answers the main conversation's Stop.
    Then: it stops the end, with writer's start due where the Run never started writer, and its
    resume where it did."""
    path = laid_resuming(plugin, WRITTEN_THEN_MORE)
    run(path)
    answer = handle(d.event("Stop", cwd=plugin, last_message="Waiting."), plugin)
    assert answer.stop and said in answer.words


@pytest.mark.supports("test_a_resume_due_of_a_role_never_started_here_is_due_as_its_start")
def test_a_start_of_a_role_whose_resume_is_due_never_started_is_added(plugin: str) -> None:
    """Given: changelog laid with the Route after reviewer's `more` resuming writer, and write's Run
    picked up after reviewer's `more`, with no Start of writer.
    When: handle answers the main conversation's Agent call t2 of changelog:writer with Lane's
    text.
    Then: it lets the start through, and adds writer's Start, resuming none."""
    path = laid_resuming(plugin, WRITTEN_THEN_MORE)
    picked_up_run(path)
    answer = handle(started(plugin, "Carry out your steps"), plugin)
    assert (answer.stop, answer.words) == (False, "")
    assert lines(path)[-1] == Started("r1", "writer", "Carry out your steps", {}, "t2", False)


@pytest.mark.supports("test_the_turns_end_goes_while_the_adapter_cant_give_a_starts_text_yet")
@pytest.mark.parametrize(
    "body, stops",
    [
        (FAILS, False),
        (BY_VERSION, True),
    ],
    ids=["the adapter still fails", "the adapter gives the text now"],
)
def test_the_end_after_the_adapter_failed_at_the_call_stops_only_for_a_text(
    plugin: str, body: str, stops: bool
) -> None:
    """Given: changelog laid with an adapter of a start's text that failed at the call of
    /changelog:write, and that still fails, or since gives writer `Write 0.2.0`; no subagent
    started.
    When: handle answers the main conversation's Stop.
    Then: it lets the end go while the adapter can't give writer's text, and stops it with
    writer's start and its text once the adapter gives it."""
    laid_with_program(plugin, FAILS)
    handle(called(plugin), plugin)
    laid_with_program(plugin, body)
    answer = handle(d.event("Stop", cwd=plugin, last_message="Which version?"), plugin)
    assert answer.stop is stops
    if stops:
        assert "changelog: Start `changelog:writer` with `Write 0.2.0`." in answer.words


@pytest.mark.supports("test_a_pick_up_whose_adapter_fails_at_the_call_lets_the_call_run")
def test_a_pick_up_whose_adapter_fails_keeps_that_it_failed(plugin: str) -> None:
    """Given: changelog laid with an adapter of its records that gives writer's `written`, and an
    adapter of a start's text that fails with `no version to write yet`; no Run.
    When: handle answers the UserPromptExpansion of /changelog:write.
    Then: it lets the call run, giving reviewer's start with why; and adds the call of write's
    Run, writer's `written`, and that the text failed."""
    path = laid_resuming(plugin, WRITTEN, FAILS)
    answer = handle(called(plugin), plugin)
    assert not answer.stop
    assert "changelog:reviewer" in answer.words and "no version to write yet" in answer.words
    (call, written, failed) = lines(path)
    assert isinstance(call, Called)
    assert (written, failed) == (Gave(call.run, "writer", "written", None), TextFailed(call.run))


def writer_tied(plugin: str) -> str:
    """changelog laid, and write's Run with writer's Start tied to a01; gives the record's path."""
    path = laid(plugin)
    for line in (
        Called("r1", "write", ""),
        Started("r1", "writer", "Carry out your steps", {}, "t1", False),
        Tied("r1", "t1", "a01"),
    ):
        add(path, line)
    return path


@pytest.mark.supports("test_a_second_skills_run_beside_the_first_keeps_its_own_routes")
def test_a_resume_lies_on_the_run_that_holds_its_subagent(plugin: str) -> None:
    """Given: changelog laid, and two Runs of write, the second with writer's Start tied to a02,
    which gave `written` and ended.
    When: handle answers the main conversation's SendMessage to a02.
    Then: it lets it through, and adds writer's Start again in the second Run, tied to a02."""
    path = laid(plugin)
    for line in (
        Called("r1", "write", ""),
        Called("r2", "write", ""),
        Started("r2", "writer", "Carry out your steps", {}, "t1", False),
        Tied("r2", "t1", "a02"),
        Gave("r2", "writer", "written", "a02"),
        Ended("r2", "a02", False),
    ):
        add(path, line)
    tool_input = {"to": "a02", "message": "Which version?", "summary": "Ask"}
    event = d.event("PreToolUse", tool_name="SendMessage", tool_input=tool_input, tool_use_id="t2")
    assert not handle(event, plugin).stop
    resumed = [x for x in lines(path) if isinstance(x, Started) and x.resumed]
    assert [(x.run, x.tool_use_id) for x in resumed] == [("r2", "t2")]


@pytest.mark.supports("test_calls_outside_the_run_go_unchecked")
def test_a_resume_of_a_subagent_of_a_run_that_ended_goes_and_adds_nothing(plugin: str) -> None:
    """Given: changelog laid, write's Run r1 with writer's Start tied to a01, ended by write's
    `good` after reviewer's `good`, and write's Run r2 going.
    When: handle answers the main conversation's SendMessage to a01.
    Then: it lets it through and adds nothing, as the Run that held a01 has ended."""
    path = laid(plugin)
    for line in (
        Called("r1", "write", ""),
        Started("r1", "writer", "Carry out your steps", {}, "t1", False),
        Tied("r1", "t1", "a01"),
        Gave("r1", "writer", "written", "a01"),
        Gave("r1", "reviewer", "good", None),
        Gave("r1", "write", "good", None),
        Called("r2", "write", ""),
    ):
        add(path, line)
    before = lines(path)
    tool_input = {"to": "a01", "message": "Thanks.", "summary": "Thank"}
    event = d.event("PreToolUse", tool_name="SendMessage", tool_input=tool_input, tool_use_id="t2")
    assert not handle(event, plugin).stop
    assert lines(path) == before


def end(plugin: str) -> str:
    """The stop of writer's end, its result script named by the plugin's folder, as the README
    shows a stop."""
    result = f"python3 {plugin}/hooks/lane/result.py writer written"
    return f"changelog: End by running `{result}`, as a command of its own."


@pytest.mark.supports("test_a_subagents_start_of_a_role_is_stopped")
def test_a_subagents_start_of_a_role_is_stopped_with_its_last_lanes_sentence(plugin: str) -> None:
    """Given: changelog laid, and write's Run with writer's Start tied to a01.
    When: handle answers a01's Agent call of changelog:reviewer.
    Then: it stops the start with the sentence of the Lane on writer's last Step, and adds no
    Start."""
    path = writer_tied(plugin)
    tool_input = {"subagent_type": "changelog:reviewer", "prompt": "Carry out your steps"}
    event = d.event(
        "PreToolUse", agent_id="a01", tool_name="Agent", tool_input=tool_input, tool_use_id="t2"
    )
    answer = handle(event, plugin)
    assert answer.stop and answer.words == end(plugin)
    assert [x for x in lines(path) if isinstance(x, Started)] == [
        Started("r1", "writer", "Carry out your steps", {}, "t1", False)
    ]


@pytest.mark.supports("test_a_subagents_start_of_a_role_is_stopped")
def test_a_subagents_start_of_an_agent_not_the_plugins_goes_and_adds_nothing(plugin: str) -> None:
    """Given: changelog laid, and write's Run with writer's Start tied to a01.
    When: handle answers a01's Agent call of Explore, which isn't changelog's.
    Then: it lets the start through, says nothing, and adds nothing to the run record."""
    path = writer_tied(plugin)
    before = lines(path)
    tool_input = {"subagent_type": "Explore", "prompt": "Find the tests"}
    event = d.event(
        "PreToolUse", agent_id="a01", tool_name="Agent", tool_input=tool_input, tool_use_id="t2"
    )
    answer = handle(event, plugin)
    assert (answer.stop, answer.words) == (False, "")
    assert lines(path) == before


@pytest.mark.supports("test_a_result_is_added_for_the_subagents_start")
def test_a_roles_result_the_main_conversation_gives_adds_no_result(plugin: str) -> None:
    """Given: changelog laid, and write's Run with writer's Start tied to a01.
    When: handle answers the PostToolUse of the main conversation's run of result.py writer
    written.
    Then: it lets it through, says nothing, and adds no Result to the run record, as only writer's
    subagent gives writer's Result."""
    path = writer_tied(plugin)
    before = lines(path)
    command = f"python3 {plugin}/hooks/lane/result.py writer written"
    event = d.event(
        "PostToolUse",
        tool_name="Bash",
        tool_input={"command": command},
        tool_use_id="t2",
        tool_response={"stdout": "", "stderr": ""},
    )
    answer = handle(event, plugin)
    assert (answer.stop, answer.words) == (False, "")
    assert lines(path) == before


@pytest.mark.supports("test_an_end_with_no_result_is_stopped_with_its_last_steps_sentence")
def test_a_subagents_end_with_no_result_is_stopped_with_its_last_lanes_sentence(
    plugin: str,
) -> None:
    """Given: changelog laid, and write's Run with writer's Start tied to a01, which gave no
    Result.
    When: handle answers a01's SubagentStop.
    Then: it stops the end with the sentence of the Lane on writer's last Step, then that the
    script runs as a command of its own."""
    writer_tied(plugin)
    event = d.event(
        "SubagentStop", agent_id="a01", agent_type="changelog:writer", last_message="Done."
    )
    answer = handle(event, plugin)
    alone = "Run it as a command of its own: result.py run inside a longer command gives no Result."
    assert answer.stop and answer.words == f"{end(plugin)}\n{alone}"


@pytest.mark.supports("test_a_call_the_guard_cant_check_is_stopped_with_who_must_fix_it")
def test_the_hook_refuses_what_isnt_an_event(plugin: str) -> None:
    """Given: standard input that isn't JSON.
    When: hook.py's main reads it.
    Then: it raises NotAnEvent, so the hook fails and its entry's onFailure stops the call."""
    with pytest.raises(NotAnEvent):
        entry("hook").main("not json", plugin)


@pytest.mark.supports("test_calls_outside_the_run_go_unchecked")
def test_the_hook_answers_an_event_outside_every_run_with_nothing(plugin: str) -> None:
    """Given: changelog laid, and a conversation with no Run.
    When: hook.py's main answers the main conversation's PreToolUse of `git status`.
    Then: it exits 0 and denies nothing."""
    laid(plugin)
    text = d.payload("PreToolUse", tool_name="Bash", tool_input={"command": "git status"})
    out = entry("hook").main(text, plugin)
    assert out.code == 0 and "deny" not in out.stdout


@pytest.mark.supports("test_a_result_the_role_may_not_give_is_refused")
@pytest.mark.parametrize(
    "result, code", [("written", 0), ("good", 1)], ids=["one it may give", "one it may not"]
)
def test_result_py_takes_only_a_result_the_role_may_give(
    plugin: str, result: str, code: int
) -> None:
    """Given: changelog laid, and write's Run with writer's Start tied to a01.
    When: result.py's main takes writer's `written`, or `good`.
    Then: it gives 0 for `written`, and 1 with `written` as what writer may give for `good`."""
    writer_tied(plugin)
    env = {"CLAUDE_CODE_SESSION_ID": d.SESSION}
    given, out, err = entry("result").main(["writer", result], env, plugin)
    assert given == code
    if code:
        assert "written" in out + err


@pytest.mark.supports("test_the_skills_result_with_its_step_unmarked_is_refused")
@pytest.mark.parametrize("marked, code", [(False, 1), (True, 0)], ids=["unmarked", "marked"])
def test_result_py_holds_the_skills_result_until_its_steps_are_marked(
    plugin: str, marked: bool, code: int
) -> None:
    """Given: changelog laid with keeps_steps on write's step 1, and write's Run after reviewer's
    `good`, its Step 1 unmarked or marked by the main conversation.
    When: result.py's main takes write's `good`.
    Then: it gives 0 where Step 1 is marked; else 1, with write's keeps_steps sentence and Step 1
    due."""
    lanes = d.lanes_file()
    skills = d.lane("write", "skills/write/SKILL.md", 1, "keeps_steps")
    proposal = replace(lanes.proposal, lanes=(*lanes.proposal.lanes, skills))
    write_lanes(os.path.join(plugin, "hooks", "lanes.json"), replace(lanes, proposal=proposal))
    path = record_path("changelog", d.SESSION)
    for line in (
        Called("r1", "write", ""),
        Started("r1", "reviewer", "Carry out your steps", {}, "t1", False),
        Tied("r1", "t1", "a01"),
        Gave("r1", "reviewer", "good", "a01"),
        Ended("r1", "a01", False),
    ):
        add(path, line)
    if marked:
        add(path, Marked("r1", "write", 1, None, None))
    env = {"CLAUDE_CODE_SESSION_ID": d.SESSION}
    given, out, _ = entry("result").main(["write", "good"], env, plugin)
    sentence = (
        f"As each step ends, run `python3 {plugin}/hooks/lane/step.py write <n>` as a command of"
        " its own, with the step's number."
    )
    assert (given, out) == (code, f"result.py: {sentence}\nStep 1 is due.\n" if code else "")


@pytest.mark.supports("test_a_result_the_role_may_not_give_is_refused")
@pytest.mark.parametrize(
    "argv, env",
    [
        (["writer"], {"CLAUDE_CODE_SESSION_ID": d.SESSION}),
        (["writer", "written", "more"], {"CLAUDE_CODE_SESSION_ID": d.SESSION}),
        (["writer", "written"], {}),
    ],
    ids=["one argument", "three arguments", "no session"],
)
def test_result_py_refuses_a_call_it_cant_read(
    plugin: str, argv: list[str], env: dict[str, str]
) -> None:
    """Given: changelog laid.
    When: result.py's main takes other than two arguments, or no CLAUDE_CODE_SESSION_ID.
    Then: it gives 2 with why."""
    laid(plugin)
    code, _, err = entry("result").main(argv, env, plugin)
    assert code == 2 and err


@pytest.mark.supports("test_a_call_the_guard_cant_check_is_stopped_with_who_must_fix_it")
def test_result_py_without_lanes_json_gives_2(plugin: str) -> None:
    """Given: changelog with no hooks/lanes.json.
    When: result.py's main takes writer's `written`.
    Then: it gives 2, naming lanes.json."""
    code, _, err = entry("result").main(
        ["writer", "written"], {"CLAUDE_CODE_SESSION_ID": d.SESSION}, plugin
    )
    assert code == 2 and "lanes.json" in err


@pytest.mark.supports("test_types_give_each_lane_type_and_the_form_of_a_proposal")
def test_lay_types_gives_the_types_and_the_form(plugin: str) -> None:
    """Given: Lane's folder.
    When: lay.py's main runs `types`.
    Then: it gives 0 with JSON of each type and the Proposal's form."""
    code, out, _ = lay_main(["types"], io.StringIO(""), LANE)
    given = json.loads(out)
    assert code == 0 and given["proposal"]["required"] == ["lanes", "routes", "adapters"]
    assert "ends_by_result" in {each["name"] for each in given["types"]}


@pytest.mark.supports("test_steps_give_each_step_of_each_role")
def test_lay_steps_gives_the_steps_and_notes(tmp_path: Any) -> None:
    """Given: a copy of the walkthrough's changelog.
    When: lay.py's main runs `steps` on it.
    Then: it gives 0 with JSON of eight Steps and no notes."""
    import walkthrough

    walkthrough.write_files(str(tmp_path / "changelog"), walkthrough.FILES)
    code, out, _ = lay_main(["steps", str(tmp_path / "changelog")], io.StringIO(""), LANE)
    given = json.loads(out)
    assert code == 0 and len(given["steps"]) == 8 and given["notes"] == []


@pytest.mark.supports("test_a_proposal_that_cant_stand_goes_back_to_up")
def test_lay_print_of_a_proposal_out_of_form_gives_1(tmp_path: Any) -> None:
    """Given: a copy of the walkthrough's changelog.
    When: lay.py's main runs `print` with standard input that isn't JSON.
    Then: it gives 1 with what's wrong."""
    import walkthrough

    walkthrough.write_files(str(tmp_path / "changelog"), walkthrough.FILES)
    code, out, err = lay_main(["print", str(tmp_path / "changelog")], io.StringIO("{"), LANE)
    assert code == 1 and (out + err)


@pytest.mark.supports("test_lay_of_an_id_no_proposal_has_is_refused")
@pytest.mark.parametrize(
    "argv",
    [[], ["lay"], ["steps"], ["write", "changelog"], ["types", "more"]],
    ids=[
        "nothing",
        "an unknown command",
        "steps with no plugin",
        "write with no ID",
        "a word more",
    ],
)
def test_lay_refuses_a_command_line_it_cant_read(argv: list[str]) -> None:
    """Given: Lane's folder.
    When: lay.py's main runs a command line that isn't one of its commands.
    Then: it gives 2 with how to call lay.py."""
    code, _, err = lay_main(argv, io.StringIO(""), LANE)
    assert code == 2 and "lay.py" in err


def run_script(
    name: str, argv: list[str], monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> tuple[int, str]:
    """The exit code and the words of one of Lane's scripts in hooks/lane/, run as the shell runs
    it, with the arguments and an environment that names no conversation."""
    path = os.path.join(LANE, "hooks", "lane", f"{name}.py")
    monkeypatch.setattr(sys, "argv", [path, *argv])
    monkeypatch.delenv("CLAUDE_CODE_SESSION_ID", raising=False)
    with pytest.raises(SystemExit) as exited:
        runpy.run_path(path, run_name="__main__")
    said = capsys.readouterr()
    return int(exited.value.code or 0), said.out + said.err


@pytest.mark.supports("test_a_step_marked_in_its_turn_is_added_for_the_subagents_start")
def test_step_py_exits_0_with_no_words(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    """Given: an environment that names no conversation.
    When: step.py runs with writer and Step 1, as the shell runs it.
    Then: it exits 0 with no words, as the guard checked the Mark at its call."""
    assert run_script("step", ["writer", "1"], monkeypatch, capsys) == (0, "")


@pytest.mark.supports("test_an_item_of_the_step_due_is_marked")
def test_item_py_exits_0_with_no_words(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    """Given: an environment that names no conversation.
    When: item.py runs with writer and the Item `dated`, as the shell runs it.
    Then: it exits 0 with no words, as the guard checked the Mark at its call."""
    assert run_script("item", ["writer", "dated"], monkeypatch, capsys) == (0, "")
