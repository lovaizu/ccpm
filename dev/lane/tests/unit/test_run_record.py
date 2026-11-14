"""The unit cases of domain/run_record.py: where a conversation's run record lies, and its lines
written, added, and read back, through `path`, `dumps`, `loads`, `load`, and `add`."""

from __future__ import annotations

import os
import re
from typing import Any

import pytest
from domain.fault import Fault
from domain.run_record import (
    PRINTED,
    Called,
    Noted,
    Result,
    Start,
    Tied,
    add,
    dumps,
    load,
    loads,
    path,
)
from lane_parts import SESSION, WRITER_GAVE_WRITTEN, WRITER_RUNNING, keep

pytestmark = pytest.mark.xfail(
    strict=True, reason="Lane's parts are skeletons, their bodies unbuilt"
)


@pytest.mark.supports("test_after_compact_the_run_goes_on_with_the_start_due")
def test_the_run_record_lies_in_the_plugins_folder_of_the_temporary_folder_by_day_and_id():
    """Given the temporary folder /tmp/t, the plugin `changelog`, and a conversation's ID
    When the path of its run record is asked
    Then it is /tmp/t/changelog/<yyyymmdd>-<the ID>/run.jsonl"""
    found = path("/tmp/t", "changelog", SESSION)
    assert re.fullmatch(rf"/tmp/t/changelog/\d{{8}}-{SESSION}/run\.jsonl", found), found


@pytest.mark.supports("test_after_compact_the_run_goes_on_with_the_start_due")
def test_each_kind_of_line_written_reads_back_equal_in_order():
    """Given a skill's call, a Start with its skill and run values, its tie, a Result, and a line
    that a command printed
    When each is written by dumps and the text read by loads
    Then they read back equal, in order, each from one line of the text"""
    given = (
        Called("write", "person"),
        Start(1, "writer", "Write section 1", {"section": "1"}, skill="write"),
        Tied(1, "a1"),
        Result("writer", "written", "a1"),
        Noted(PRINTED, "a1", "d417d74 Add --lines"),
    )
    text = "".join(dumps(line) for line in given)
    assert text.count("\n") == len(given)
    assert loads(text, "run.jsonl") == given


@pytest.mark.supports("test_after_compact_the_run_goes_on_with_the_start_due")
def test_a_start_line_holds_neither_its_subagent_nor_whether_it_runs():
    """Given a Start of writer that names subagent a1 as running
    When it's written by dumps and read back
    Then it reads back with no subagent and not running, as the Tied and Noted lines tell those"""
    written = dumps(Start(1, "writer", "Carry out your steps", agent="a1", running=True))
    assert loads(written, "run.jsonl") == (Start(1, "writer", "Carry out your steps"),)


@pytest.mark.supports(
    "test_a_call_that_the_guard_cant_check_is_stopped_with_why_and_who_must_fix_it"
)
def test_text_that_isnt_lines_of_a_run_record_raises_a_fault_naming_the_file():
    """Given the text `not a run` followed by a newline
    When it's read as run.jsonl
    Then a Fault names run.jsonl, with Lane to fix it"""
    with pytest.raises(Fault, match="run.jsonl") as raised:
        loads("not a run\n", "run.jsonl")
    assert raised.value.who == "Lane"


@pytest.mark.supports("test_runs_of_two_skills_go_on_side_by_side_each_moved_by_its_own_results")
def test_a_last_line_cut_short_by_a_hook_that_still_writes_is_left_out():
    """Given the text of a skill's call and the first half of a Start's line, with no newline
    When it's read
    Then it reads as the skill's call alone"""
    whole = dumps(Called("write", "person"))
    half = dumps(Start(1, "writer", "Carry out your steps", skill="write"))[:12]
    assert loads(whole + half, "run.jsonl") == (Called("write", "person"),)


@pytest.mark.supports(
    "test_without_an_adapter_of_the_records_a_new_conversation_starts_the_run_over"
)
def test_a_conversation_with_no_run_record_has_no_lines(tmp_path: Any):
    """Given a temporary folder that holds no run record
    When the lines of `changelog` in a conversation are loaded
    Then there are none"""
    assert load(str(tmp_path), "changelog", SESSION) == ()


@pytest.mark.supports("test_after_compact_the_run_goes_on_with_the_start_due")
def test_lines_added_load_back_in_order_making_the_folder(tmp_path: Any):
    """Given a temporary folder with no folder of `changelog`
    When the lines of a Run in which writer runs are added one by one, and loaded
    Then the folder is made, and they load back in the order added"""
    keep(str(tmp_path), *WRITER_RUNNING)
    assert os.path.isdir(os.path.join(str(tmp_path), "changelog"))
    assert load(str(tmp_path), "changelog", SESSION) == WRITER_RUNNING


@pytest.mark.supports("test_runs_of_two_skills_go_on_side_by_side_each_moved_by_its_own_results")
def test_a_line_added_leaves_every_line_before_it_as_it_was(tmp_path: Any):
    """Given the lines of a Run in which writer runs, added
    When writer's Result and its end are added
    Then the record holds the lines before, unchanged, and the new ones after them"""
    keep(str(tmp_path), *WRITER_RUNNING)
    for line in WRITER_GAVE_WRITTEN[len(WRITER_RUNNING) :]:
        add(line, str(tmp_path), "changelog", SESSION)
    assert load(str(tmp_path), "changelog", SESSION) == WRITER_GAVE_WRITTEN
