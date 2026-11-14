"""The cases of the compatibility test, as Lane's architecture says under Test strategy: the
recorder holds a scenario for each record of a run in recorded/, and recorder/compare.py decides
whether a record that the recorder made again on a new version of Claude Code agrees with the record
whose lines the double gives. Each case of the comparison compares lines of the records in
recorded/, changed as its Given says."""

from __future__ import annotations

import copy
import json
import os
import re
from typing import Any

import pytest
from claude_code import RECORDED, record_lines
from recorder import compare, record

pytestmark = pytest.mark.xfail(strict=True, reason="the comparison is a skeleton, its body unbuilt")

TWO = "claude-code-2.1.325-two-subagents.jsonl"
COMPACT_WHILE = "claude-code-2.1.325-compact-while-subagent.jsonl"


def run(record: str, number: int) -> list[dict[str, Any]]:
    """A copy of each line of the run of the record whose events end `, in run <number>`."""
    end = f", in run {number}"
    return [copy.deepcopy(x) for x in record_lines(record) if x["event"].endswith(end)]


def held(record: str) -> list[dict[str, Any]]:
    """A copy of each line of the record that holds a payload."""
    return [copy.deepcopy(x) for x in record_lines(record) if "payload" in x]


def test_a_record_compared_with_itself_differs_in_nothing():
    """Given the record of /compact while a subagent runs
    When it's compared with itself
    Then no difference comes"""
    assert compare.differences(held(COMPACT_WHILE), held(COMPACT_WHILE)) == []


def test_runs_that_differ_in_values_and_interleave_their_callers_otherwise_differ_in_nothing():
    """Given runs 1 and 2 of two subagents started in one message, whose IDs differ and whose two
    subagents end in the other order
    When run 2 is compared with run 1
    Then no difference comes, as each caller's events come in the same order"""
    assert compare.differences(run(TWO, 1), run(TWO, 2)) == []


def test_a_field_that_the_new_record_adds_to_an_event_is_a_difference_naming_it():
    """Given the record of /compact while a subagent runs, and a copy whose PreCompact holds the
    field `reason` besides
    When the copy is compared with the record
    Then a difference names the PreCompact's event and `reason`"""
    new = held(COMPACT_WHILE)
    precompact = next(x for x in new if x["payload"]["hook_event_name"] == "PreCompact")
    precompact["payload"]["reason"] = "manual"
    found = compare.differences(held(COMPACT_WHILE), new)
    assert len(found) == 1
    assert precompact["event"] in found[0] and "reason" in found[0]


def test_a_field_that_the_new_record_lacks_in_a_tool_response_is_a_difference_naming_it():
    """Given the record of /compact while a subagent runs, and a copy whose PostToolUse of the Agent
    call lacks `outputFile` in its `tool_response`
    When the copy is compared with the record
    Then a difference names that event and `outputFile`"""
    new = held(COMPACT_WHILE)
    started = next(
        x
        for x in new
        if x["payload"].get("tool_name") == "Agent" and "tool_response" in x["payload"]
    )
    del started["payload"]["tool_response"]["outputFile"]
    found = compare.differences(held(COMPACT_WHILE), new)
    assert len(found) == 1
    assert started["event"] in found[0] and "outputFile" in found[0]


def test_an_event_that_the_new_record_lacks_is_a_difference_naming_it():
    """Given the record of /compact while a subagent runs, and a copy without the compaction
    summary's SubagentStop
    When the copy is compared with the record
    Then a difference names that event"""
    new = [x for x in held(COMPACT_WHILE) if x["event"] != "the compaction's summary ends"]
    found = compare.differences(held(COMPACT_WHILE), new)
    assert len(found) == 1 and "the compaction's summary ends" in found[0]


def test_an_event_that_the_new_record_adds_is_a_difference():
    """Given the record of /compact while a subagent runs, and a copy with a second SessionStart
    after the first
    When the copy is compared with the record
    Then one difference comes"""
    new = held(COMPACT_WHILE)
    first = next(i for i, x in enumerate(new) if x["payload"]["hook_event_name"] == "SessionStart")
    new.insert(first + 1, copy.deepcopy(new[first]))
    assert len(compare.differences(held(COMPACT_WHILE), new)) == 1


def test_two_events_of_one_caller_in_another_order_are_a_difference():
    """Given run 1 of two subagents started in one message, and a copy in which the main
    conversation's Stop comes before its second Agent call
    When the copy is compared with run 1
    Then a difference comes"""
    new = run(TWO, 1)
    events = [x["event"] for x in new]
    stop = new.pop(events.index("the main conversation stops after the request, in run 1"))
    new.insert(
        events.index("the main conversation starts sleeper two in the background, in run 1"), stop
    )
    assert compare.differences(run(TWO, 1), new) != []


def write(path: str, lines: list[dict[str, Any]]) -> str:
    with open(path, "w", encoding="utf-8") as f:
        f.writelines(json.dumps(x) + "\n" for x in lines)
    return path


def test_the_script_exits_0_and_prints_nothing_where_the_records_agree(tmp_path: Any):
    """Given run 2 of two subagents written to a file
    When compare.py compares it with the record of two subagents' run 1, written to a file
    Then it exits 0 and prints nothing"""
    old = write(str(tmp_path / "old.jsonl"), run(TWO, 1))
    new = write(str(tmp_path / "new.jsonl"), run(TWO, 2))
    assert compare.main([old, new]) == (0, "", "")


def test_the_script_exits_1_and_prints_each_difference_where_they_differ(tmp_path: Any):
    """Given a copy of the record of /compact while a subagent runs without the compaction
    summary's SubagentStop, written to a file
    When compare.py compares it with the record
    Then it exits 1, and prints a line that names that event"""
    lines = [x for x in held(COMPACT_WHILE) if x["event"] != "the compaction's summary ends"]
    new = write(str(tmp_path / "new.jsonl"), lines)
    code, out, _ = compare.main([os.path.join(RECORDED, COMPACT_WHILE), new])
    assert code == 1 and "the compaction's summary ends" in out


def test_the_script_exits_2_with_why_where_a_file_cant_be_read(tmp_path: Any):
    """Given a path where no file lies
    When compare.py compares it with the record of /compact while a subagent runs
    Then it exits 2, and says which file it couldn't read"""
    missing = str(tmp_path / "missing.jsonl")
    code, _, err = compare.main([os.path.join(RECORDED, COMPACT_WHILE), missing])
    assert code == 2 and missing in err


def test_each_record_of_a_run_names_a_scenario_that_the_recorder_runs_again():
    """Given each record of a run of Claude Code in recorded/,
    `claude-code-<version>[-<what>].jsonl`
    When the recorder's scenarios are listed
    Then each record's `<what>`, or `run` where it has none, names one, so that the compatibility
    test records each state again on a new version"""
    found = set()
    for name in os.listdir(RECORDED):
        each = re.fullmatch(r"claude-code-\d+(?:\.\d+)+(?:-(.+))?\.jsonl", name)
        if each:
            found.add(each[1] or "run")
    assert found - set(record.SCENARIOS) == set()
