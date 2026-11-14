"""The unit cases of domain/run_record.py: where a conversation's run record lies, and its Run
written and read back, through `path`, `dumps`, `loads`, `load`, and `save`."""

from __future__ import annotations

import os
import re
from typing import Any

import pytest
from domain.event import COMMAND, Call
from domain.fault import Fault
from domain.run_record import Result, Start, dumps, load, loads, path, save
from lane_parts import SESSION, run, writer_gave_written

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
def test_a_run_written_reads_back_equal():
    """Given a Run with a Start, a Call, a Result, the moves open, and a text kept
    When it's written by dumps and read by loads
    Then it reads back equal"""
    given = writer_gave_written()
    given.calls.append(("a1", Call(COMMAND, command="git log --oneline")))
    given.printed["a1"] = ["d417d74 Add --lines"]
    assert loads(dumps(given), "run.jsonl") == given


@pytest.mark.supports(
    "test_a_call_that_the_guard_cant_check_is_stopped_with_why_and_who_must_fix_it"
)
def test_text_that_isnt_a_run_raises_a_fault_naming_the_file():
    """Given the text `not a run`
    When it's read as run.jsonl
    Then a Fault names run.jsonl, with Lane to fix it"""
    with pytest.raises(Fault, match="run.jsonl") as raised:
        loads("not a run", "run.jsonl")
    assert raised.value.who == "Lane"


@pytest.mark.supports(
    "test_without_an_adapter_of_the_records_a_new_conversation_starts_the_run_over"
)
def test_a_conversation_with_no_run_record_has_no_run(tmp_path: Any):
    """Given a temporary folder that holds no run record
    When the Run of `changelog` in a conversation is loaded
    Then there is none"""
    assert load(str(tmp_path), "changelog", SESSION) is None


@pytest.mark.supports("test_after_compact_the_run_goes_on_with_the_start_due")
def test_a_run_saved_loads_back_equal_making_its_folder(tmp_path: Any):
    """Given a temporary folder with no folder of `changelog`
    When a Run of the conversation is saved, and loaded
    Then the folder is made, and the Run loads back equal"""
    given = run(starts=[Start(1, "writer", "Carry out your steps", agent="a1", running=True)])
    save(given, str(tmp_path))
    assert os.path.isdir(os.path.join(str(tmp_path), "changelog"))
    assert load(str(tmp_path), "changelog", SESSION) == given


@pytest.mark.supports("test_the_skills_own_result_where_a_move_starts_no_more_ends_the_run")
def test_a_run_saved_again_replaces_the_one_before(tmp_path: Any):
    """Given a Run of the conversation saved
    When the Run with a Result added and ended is saved again, and loaded
    Then the second loads"""
    first = run()
    save(first, str(tmp_path))
    second = run(results=[Result("write", "good")], ended=True)
    save(second, str(tmp_path))
    assert load(str(tmp_path), "changelog", SESSION) == second
