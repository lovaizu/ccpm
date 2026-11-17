"""The unit cases of run_record.py, the run record's layout, through `record_path`, `add`, and
`lines`: where one conversation's record lies, each kind of line kept as added, and a record that
isn't there, can't be read, or can't be written."""

from __future__ import annotations

import datetime
import os
import tempfile
from typing import Any

import pytest
from run_record import (
    Called,
    Ended,
    Gave,
    Prompted,
    Started,
    TextFailed,
    TextGiven,
    Tied,
    Unreadable,
    add,
    lines,
    record_path,
)

EACH_LINE = [
    Called("r1", "write", "0.2.0"),
    Prompted("r1", "/changelog:pause"),
    Started("r1", "writer", "Carry out your steps", {"version": "0.2.0"}, "toolu_1", False),
    Tied("r1", "toolu_1", "a01"),
    Gave("r1", "writer", "written", "a01"),
    Gave("r1", "write", "good", None),
    Ended("r1", "a01", True),
    TextFailed("r1"),
    TextGiven("r1"),
]


@pytest.fixture
def temp(tmp_path: Any, monkeypatch: pytest.MonkeyPatch) -> str:
    """The system's temporary folder, set to the case's own."""
    monkeypatch.setenv("TMPDIR", str(tmp_path))
    monkeypatch.setattr(tempfile, "tempdir", None)
    return str(tmp_path)


@pytest.mark.supports("test_a_run_goes_on_after_compact")
def test_a_conversations_record_lies_under_its_plugin_and_day(temp: str) -> None:
    """Given: the plugin changelog, and a conversation's session_id.
    When: record_path gives where its record lies.
    Then: the record lies in `changelog/<yyyymmdd>-<session_id>/` of the temporary folder."""
    path = record_path("changelog", "4f7c")
    day = datetime.date.today().strftime("%Y%m%d")
    assert os.path.dirname(path) == os.path.join(temp, "changelog", f"{day}-4f7c")


@pytest.mark.supports("test_a_run_goes_on_after_compact")
def test_a_record_begun_on_an_earlier_day_keeps_its_folder(temp: str) -> None:
    """Given: the conversation's record, first written yesterday.
    When: record_path gives where its record lies today.
    Then: it gives the record of yesterday's folder."""
    yesterday = (datetime.date.today() - datetime.timedelta(days=1)).strftime("%Y%m%d")
    folder = os.path.join(temp, "changelog", f"{yesterday}-4f7c")
    os.makedirs(folder)
    assert os.path.dirname(record_path("changelog", "4f7c")) == folder


@pytest.mark.supports("test_a_run_goes_on_after_compact")
@pytest.mark.parametrize("line", EACH_LINE, ids=lambda line: type(line).__name__)
def test_each_kind_of_line_is_read_as_added(temp: str, line: Any) -> None:
    """Given: an empty record.
    When: add adds one line of a kind, and lines reads the record.
    Then: it gives that line back, equal to the one added."""
    path = record_path("changelog", "4f7c")
    add(path, line)
    assert lines(path) == (line,)


@pytest.mark.supports("test_the_walkthroughs_run_moves_in_the_order_the_user_set")
def test_lines_come_in_the_order_added(temp: str) -> None:
    """Given: an empty record.
    When: add adds each kind of line in turn.
    Then: lines gives them in that order."""
    path = record_path("changelog", "4f7c")
    for line in EACH_LINE:
        add(path, line)
    assert lines(path) == tuple(EACH_LINE)


@pytest.mark.supports("test_a_new_conversation_without_an_adapter_starts_over")
def test_a_record_not_yet_written_has_no_lines(temp: str) -> None:
    """Given: a conversation whose record isn't there.
    When: lines reads it.
    Then: it gives no lines."""
    assert lines(record_path("changelog", "new")) == ()


@pytest.mark.supports("test_a_call_the_guard_cant_check_is_stopped_with_who_must_fix_it")
def test_a_line_out_of_form_is_unreadable(temp: str) -> None:
    """Given: a record whose second line isn't one of the run record's lines.
    When: lines reads it.
    Then: it raises Unreadable, naming the record."""
    path = record_path("changelog", "4f7c")
    add(path, EACH_LINE[0])
    with open(path, "a", encoding="utf-8") as f:
        f.write("{not a line\n")
    with pytest.raises(Unreadable, match="changelog"):
        lines(path)


@pytest.mark.supports("test_a_call_the_guard_cant_check_is_stopped_with_who_must_fix_it")
def test_a_record_that_cant_be_written_is_refused(temp: str) -> None:
    """Given: a file where the record's folder must go.
    When: add adds a line.
    Then: it raises OSError."""
    path = record_path("changelog", "4f7c")
    os.makedirs(os.path.dirname(os.path.dirname(path)), exist_ok=True)
    with open(os.path.dirname(path), "w", encoding="utf-8") as f:
        f.write("")
    with pytest.raises(OSError):
        add(path, EACH_LINE[0])
