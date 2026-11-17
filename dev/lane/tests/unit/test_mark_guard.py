"""The unit cases of how the guard and lay.py meet a role's Steps: guard.py's `handle` of a run of
step.py or item.py, before it runs and at its PostToolUse, and of a Read's PostToolUse; form.py's
adapter of a step's items, read and written; and lay.py's `check.check` of a Proposal whose Lanes
of reads_whole and keeps_items need keeps_steps and the adapter of a step's items, and `show.render`
of the lane types of steps."""

from __future__ import annotations

import json
import os
import sys
import tempfile
from dataclasses import replace
from typing import Any

import lane_data as d
import pytest
import walkthrough as w
from form import Adapters, read_lanes, read_proposal, write_lanes
from guard import handle
from lay.check import Checked, Faults, check
from lay.show import render
from lay.steps import read_steps
from run_record import Called, Marked, Read, Started, Tied, add, lines, record_path

ITEMS = "hooks/adapters/items.py"
GIVES = (
    "import json, sys\njson.load(sys.stdin)\nprint(json.dumps({'items': ['dated', 'linked']}))\n"
)
FAILS = "import sys\nsys.exit('CHECKLIST.md is not there')\n"
WRITER_LANES = (d.READS_WHOLE, d.READS_NONE, d.KEEPS_ITEMS, d.KEEPS_STEPS)


@pytest.fixture
def plugin(tmp_path: Any, monkeypatch: pytest.MonkeyPatch) -> str:
    """changelog's folder in tally, a worktree whose top holds .git and CHANGELOG.md of 7 lines,
    and the system's temporary folder set to the case's own."""
    monkeypatch.setenv("TMPDIR", str(tmp_path / "temp"))
    monkeypatch.setattr(tempfile, "tempdir", None)
    os.makedirs(tmp_path / "temp")
    os.makedirs(tmp_path / "tally" / ".git")
    (tmp_path / "tally" / "CHANGELOG.md").write_text(
        "# Changelog\n\n## 0.1.0\n\n- Counts lines.\n- Reads standard input.\n"
    )
    os.makedirs(tmp_path / "tally" / "changelog" / ".claude-plugin")
    os.makedirs(tmp_path / "tally" / "changelog" / "hooks")
    (tmp_path / "tally" / "changelog" / ".claude-plugin" / "plugin.json").write_text(
        '{"name": "changelog"}'
    )
    return str(tmp_path / "tally" / "changelog")


def laid(plugin: str, adapter: str | None = GIVES, lanes: tuple[Any, ...] = WRITER_LANES) -> str:
    """Writes the walkthrough's lanes.json with writer's Lanes of its Steps and, where `adapter`
    gives its Python, an adapter of a step's items; adds write's Run with writer's Start tied to
    a01; and gives the run record's path."""
    items = None
    if adapter:
        items = ITEMS
        path = os.path.join(plugin, ITEMS)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            f.write(f"#!{sys.executable}\n{adapter}")
        os.chmod(path, 0o755)
    given = d.lanes_file()
    proposal = replace(
        given.proposal,
        lanes=(*given.proposal.lanes, *lanes),
        adapters=Adapters(None, None, items),
    )
    write_lanes(os.path.join(plugin, "hooks", "lanes.json"), replace(given, proposal=proposal))
    record = record_path("changelog", d.SESSION)
    for line in (
        Called("r1", "write", ""),
        Started("r1", "writer", "Carry out your steps", {}, "t1", False),
        Tied("r1", "t1", "a01"),
    ):
        add(record, line)
    return record


def writers(plugin: str, name: str, command: str, **fields: Any) -> Any:
    """a01's event of a Bash call of the command, in tally."""
    return d.event(
        name,
        cwd=os.path.dirname(plugin),
        agent_id="a01",
        agent_type="changelog:writer",
        tool_name="Bash",
        tool_input={"command": command},
        tool_use_id="t5",
        **fields,
    )


def step(plugin: str, role: str, n: int) -> str:
    return f"python3 {plugin}/hooks/lane/step.py {role} {n}"


def item(plugin: str, role: str, given: str) -> str:
    return f"python3 {plugin}/hooks/lane/item.py {role} {given}"


def sentence(plugin: str) -> str:
    return (
        f"As each step ends, run `python3 {plugin}/hooks/lane/step.py writer <n>` as a command of"
        " its own, with the step's number."
    )


@pytest.mark.supports("test_a_step_with_no_lane_on_it_is_marked_on_its_turn_alone")
def test_a_run_of_step_py_of_the_step_due_goes_and_adds_nothing_before_it_runs(
    plugin: str,
) -> None:
    """Given: changelog laid with writer's Lanes of its Steps, and writer's Start tied to a01,
    which marked Step 1.
    When: handle answers a01's PreToolUse of step.py writer 2, whose Step holds no Lane that
    checks a Mark.
    Then: it lets it through, says nothing, and adds no line."""
    record = laid(plugin)
    add(record, Marked("r1", "writer", 1, None, "a01"))
    before = lines(record)
    answer = handle(writers(plugin, "PreToolUse", step(plugin, "writer", 2)), plugin)
    assert (answer.stop, answer.words) == (False, "")
    assert lines(record) == before


@pytest.mark.supports("test_a_step_marked_in_its_turn_is_added_for_the_subagents_start")
def test_the_post_tool_use_of_step_py_adds_the_mark_for_the_subagents_start(plugin: str) -> None:
    """Given: changelog laid with writer's Lanes of its Steps, and writer's Start tied to a01,
    which marked Step 1.
    When: handle answers the PostToolUse of a01's step.py writer 2.
    Then: it adds the Mark of writer's Step 2 with a01."""
    record = laid(plugin)
    add(record, Marked("r1", "writer", 1, None, "a01"))
    event = writers(plugin, "PostToolUse", step(plugin, "writer", 2), tool_response={"stdout": ""})
    assert not handle(event, plugin).stop
    assert lines(record)[-1] == Marked("r1", "writer", 2, None, "a01")


@pytest.mark.supports("test_a_step_marked_out_of_order_is_stopped_with_the_step_due")
@pytest.mark.parametrize(
    "command, lanes",
    [
        (lambda p: step(p, "writer", 3), WRITER_LANES),
        (lambda p: step(p, "reviewer", 1), WRITER_LANES),
        (lambda p: step(p, "writer", 1), (d.READS_NONE,)),
    ],
    ids=["a Step not due", "another role's Step", "a role with no keeps_steps"],
)
def test_a_run_of_step_py_that_marks_no_step_due_is_stopped(
    plugin: str, command: Any, lanes: tuple[Any, ...]
) -> None:
    """Given: changelog laid with writer's Lanes, with or without keeps_steps, and writer's Start
    tied to a01, which marked Step 1.
    When: handle answers a01's PreToolUse of step.py for writer's Step 3, for reviewer, or for a
    writer that keeps no Steps.
    Then: it stops it, opened by the plugin's name, and adds no line."""
    record = laid(plugin, lanes=lanes)
    add(record, Marked("r1", "writer", 1, None, "a01"))
    before = lines(record)
    answer = handle(writers(plugin, "PreToolUse", command(plugin)), plugin)
    assert answer.stop and answer.words.startswith("changelog: ")
    assert lines(record) == before


@pytest.mark.supports("test_a_step_marked_out_of_order_is_stopped_with_the_step_due")
def test_a_step_not_due_is_stopped_with_keeps_steps_sentence_and_the_step_due(plugin: str) -> None:
    """Given: changelog laid with writer's Lanes of its Steps, and writer's Start tied to a01,
    which marked Step 1.
    When: handle answers a01's PreToolUse of step.py writer 3.
    Then: it stops it with the sentence of keeps_steps and Step 2 due."""
    record = laid(plugin)
    add(record, Marked("r1", "writer", 1, None, "a01"))
    answer = handle(writers(plugin, "PreToolUse", step(plugin, "writer", 3)), plugin)
    assert answer.stop and sentence(plugin) in answer.words
    assert "2" in answer.words.replace(sentence(plugin), "")


@pytest.mark.supports("test_a_step_marked_before_its_file_is_read_whole_goes_back_to_the_step")
@pytest.mark.parametrize(
    "reports, stop",
    [((), True), ((Read("r1", "writer", "CHANGELOG.md", 1, 7, "a01"),), False)],
    ids=["not read", "read whole"],
)
def test_a_run_of_step_py_is_checked_by_the_lanes_on_its_step(
    plugin: str, reports: tuple[Any, ...], stop: bool
) -> None:
    """Given: changelog laid with writer's reads_whole Lane for CHANGELOG.md on its step 1, and
    writer's Start tied to a01, with or without a Read of each line of CHANGELOG.md.
    When: handle answers a01's PreToolUse of step.py writer 1.
    Then: it stops it with reads_whole's sentence where CHANGELOG.md wasn't read whole, and lets
    it through where it was."""
    record = laid(plugin)
    for each in reports:
        add(record, each)
    answer = handle(writers(plugin, "PreToolUse", step(plugin, "writer", 1)), plugin)
    assert answer.stop is stop
    if stop:
        assert answer.words.startswith("changelog: Read `CHANGELOG.md` whole.")


@pytest.mark.supports("test_a_step_with_an_item_left_goes_back_to_the_step")
def test_a_run_of_step_py_asks_the_adapter_for_its_items_and_names_those_left(
    plugin: str,
) -> None:
    """Given: changelog laid with writer's keeps_items Lane on its step 3 and an adapter of a
    step's items that gives `dated` and `linked`, and writer's Start tied to a01, which marked
    Steps 1 and 2 and the Item `dated`.
    When: handle answers a01's PreToolUse of step.py writer 3.
    Then: it stops it with keeps_items' sentence and the Item left, `linked`."""
    record = laid(plugin)
    for each in (
        Marked("r1", "writer", 1, None, "a01"),
        Marked("r1", "writer", 2, None, "a01"),
        Marked("r1", "writer", 3, "dated", "a01"),
    ):
        add(record, each)
    answer = handle(writers(plugin, "PreToolUse", step(plugin, "writer", 3)), plugin)
    assert answer.stop and "item.py writer <id>" in answer.words
    assert "linked" in answer.words


@pytest.mark.supports(
    "test_an_adapter_of_a_steps_items_that_fails_stops_the_mark_with_who_must_fix_it"
)
@pytest.mark.parametrize(
    "command",
    [lambda p: step(p, "writer", 3), lambda p: item(p, "writer", "dated")],
    ids=["step.py", "item.py"],
)
def test_a_mark_whose_adapter_fails_is_stopped_with_who_must_fix_it(
    plugin: str, command: Any
) -> None:
    """Given: changelog laid with an adapter of a step's items that exits 1, and writer's Start
    tied to a01, which marked Steps 1 and 2.
    When: handle answers a01's PreToolUse of step.py writer 3, or of item.py writer dated.
    Then: it stops it with why and that changelog's developer must fix its adapter."""
    record = laid(plugin, adapter=FAILS)
    add(record, Marked("r1", "writer", 1, None, "a01"))
    add(record, Marked("r1", "writer", 2, None, "a01"))
    answer = handle(writers(plugin, "PreToolUse", command(plugin)), plugin)
    assert answer.stop and "CHECKLIST.md is not there" in answer.words
    assert "The developer of changelog must fix its adapter" in answer.words


@pytest.mark.supports("test_an_item_not_of_the_step_due_is_stopped_with_the_items_left")
@pytest.mark.parametrize(
    "given, adapter, stop",
    [("dated", GIVES, False), ("undated", GIVES, True), ("dated", None, True)],
    ids=["an Item of the Step due", "an ID it doesn't give", "no adapter of a step's items"],
)
def test_a_run_of_item_py_goes_only_for_an_item_of_the_step_due(
    plugin: str, given: str, adapter: str | None, stop: bool
) -> None:
    """Given: changelog laid with or without an adapter of a step's items that gives `dated` and
    `linked`, and writer's Start tied to a01, which marked Steps 1 and 2.
    When: handle answers a01's PreToolUse of item.py writer with an ID.
    Then: it lets `dated` through where the adapter gives it, and else stops it with the Items
    left, adding no line."""
    record = laid(plugin, adapter=adapter)
    add(record, Marked("r1", "writer", 1, None, "a01"))
    add(record, Marked("r1", "writer", 2, None, "a01"))
    before = lines(record)
    answer = handle(writers(plugin, "PreToolUse", item(plugin, "writer", given)), plugin)
    assert answer.stop is stop and lines(record) == before
    if stop:
        assert answer.words.startswith("changelog: ")


@pytest.mark.supports("test_an_item_of_the_step_due_is_marked")
def test_the_post_tool_use_of_item_py_adds_the_items_mark_with_the_step_due(plugin: str) -> None:
    """Given: changelog laid with an adapter of a step's items, and writer's Start tied to a01,
    which marked Steps 1 and 2.
    When: handle answers the PostToolUse of a01's item.py writer dated.
    Then: it adds the Mark of the Item `dated` of Step 3, the Step due, with a01."""
    record = laid(plugin)
    add(record, Marked("r1", "writer", 1, None, "a01"))
    add(record, Marked("r1", "writer", 2, None, "a01"))
    event = writers(plugin, "PostToolUse", item(plugin, "writer", "dated"), tool_response={})
    assert not handle(event, plugin).stop
    assert lines(record)[-1] == Marked("r1", "writer", 3, "dated", "a01")


@pytest.mark.supports("test_only_a_read_of_a_path_reads_whole_names_is_kept")
@pytest.mark.parametrize(
    "name, kept", [("CHANGELOG.md", True), ("README.md", False)], ids=["its path", "another"]
)
def test_the_post_tool_use_of_a_read_adds_it_where_reads_whole_names_its_path(
    plugin: str, name: str, kept: bool
) -> None:
    """Given: changelog laid with writer's reads_whole Lane for CHANGELOG.md, and writer's Start
    tied to a01.
    When: handle answers the PostToolUse of a01's Read of lines 1 to 7 of a file of tally.
    Then: it adds the Read, with the path as the Lane names it, for CHANGELOG.md, and nothing for
    another file."""
    record = laid(plugin)
    before = lines(record)
    path = os.path.join(os.path.dirname(plugin), name)
    response = {"type": "text", "file": {"filePath": path, "content": "", "numLines": 7}}
    response["file"].update(startLine=1, totalLines=7)
    event = d.event(
        "PostToolUse",
        cwd=os.path.dirname(plugin),
        agent_id="a01",
        agent_type="changelog:writer",
        tool_name="Read",
        tool_input={"file_path": path},
        tool_use_id="t6",
        tool_response=response,
    )
    assert not handle(event, plugin).stop
    added = list(lines(record)[len(before) :])
    assert added == ([Read("r1", "writer", "CHANGELOG.md", 1, 7, "a01")] if kept else [])


@pytest.mark.supports("test_lay_writes_the_adapter_of_a_steps_items_into_lanes_json")
def test_the_adapter_of_a_steps_items_is_read_and_written(tmp_path: Any) -> None:
    """Given: a Proposal as up writes it, naming the adapter of a step's items.
    When: read_proposal reads it, and write_lanes writes it into lanes.json that read_lanes reads.
    Then: each gives the adapter of a step's items as named."""
    proposal = dict(d.proposal_json(), adapters={"items": ITEMS})
    read = read_proposal(json.dumps(proposal))
    assert read.adapters == Adapters(None, None, ITEMS)
    path = str(tmp_path / "lanes.json")
    write_lanes(path, replace(d.lanes_file(), proposal=read))
    assert read_lanes(path).proposal.adapters == Adapters(None, None, ITEMS)


@pytest.fixture
def changelog(tmp_path: Any, monkeypatch: pytest.MonkeyPatch) -> str:
    """changelog with writer's Steps held, and its adapter of a step's items."""
    monkeypatch.setenv("TMPDIR", str(tmp_path / "temp"))
    monkeypatch.setattr(tempfile, "tempdir", None)
    os.makedirs(tmp_path / "temp")
    files = dict(w.FILES, **{"agents/writer.md": w.MARKED_WRITER, ITEMS: w.ITEMS_ADAPTER})
    w.write_files(str(tmp_path / "changelog"), files)
    return str(tmp_path / "changelog")


def with_writers(*lanes: Any, items: str | None = ITEMS) -> Any:
    proposal = d.proposal()
    return replace(proposal, lanes=(*proposal.lanes, *lanes), adapters=Adapters(None, None, items))


@pytest.mark.supports("test_a_proposal_of_the_lane_types_of_steps_shows_each_steps_sentence")
def test_a_proposal_of_the_lane_types_of_steps_with_its_adapter_can_stand(changelog: str) -> None:
    """Given: changelog with writer's Steps held, and its adapter of a step's items in
    hooks/adapters/.
    When: check checks the Proposal with writer's four Lanes of its Steps and that adapter, and
    render shows it.
    Then: check gives each sentence, keeps_steps' on writer's step 4, and render shows each."""
    proposal = with_writers(*WRITER_LANES)
    checked = check(changelog, proposal, read_steps(changelog))
    assert isinstance(checked, Checked)
    assert "step.py writer <n>" in checked.sentences[("agents/writer.md", 4)]
    shown = render(proposal, read_steps(changelog), "b9fd8fd8", "changelog")
    assert "Never read `tally.py`." in shown and "item.py writer <id>" in shown


@pytest.mark.supports("test_a_lane_that_only_keeps_steps_bounds_goes_back_to_up")
@pytest.mark.parametrize(
    "lanes, items, named",
    [
        ((d.READS_WHOLE,), ITEMS, "keeps_steps"),
        ((d.KEEPS_ITEMS,), ITEMS, "keeps_steps"),
        ((d.KEEPS_ITEMS, d.KEEPS_STEPS), None, "items"),
    ],
    ids=[
        "reads_whole with no keeps_steps",
        "keeps_items with no keeps_steps",
        "keeps_items with no adapter of a step's items",
    ],
)
def test_a_lane_of_a_step_with_what_bounds_it_missing_is_ups_to_mend(
    changelog: str, lanes: tuple[Any, ...], items: str | None, named: str
) -> None:
    """Given: changelog with writer's Steps held.
    When: check checks the Proposal with writer's Lane of reads_whole or keeps_items and no Lane
    of keeps_steps, or keeps_items with no adapter of a step's items.
    Then: it gives Faults for up to mend, naming writer and what it lacks, none for the user."""
    if items is None:
        os.remove(os.path.join(changelog, ITEMS))
    faults = check(changelog, with_writers(*lanes, items=items), read_steps(changelog))
    assert isinstance(faults, Faults) and not faults.plugin
    assert any("writer" in f and named in f for f in faults.proposal)
